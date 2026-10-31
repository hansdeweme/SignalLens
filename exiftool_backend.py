#exiftool_backend.py
# Copyright (c) 2025, 2026 Hans De Weme
# Licensed under the MIT License (https://opensource.org/licenses/MIT).
#Part of the SignalLens project evaluating signals of AI-generated and/or AI-enhanced Photo Imgages
#
"""
exiftool_backend.py
Phase 1 metadata/provenance extractor for Signal Class 1:
static metadata checks for declarative or intentional signals.
Design goals:
- Use ExifTool as canonical metadata backend
- Preserve raw watchlist hits
- Interpret signals conservatively
- Serialize findings to exif_signals.json
Tested conceptually for:
- JPEG / TIFF / HEIC / PNG / WebP
- EXIF / XMP / PNG text / possible C2PA presence
"""

from __future__ import annotations
import json
import hashlib
import shutil
import sys, subprocess
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# local imports
from exif_config import (
    WATCH_TAGS,
    TOOL_RULES,
    DECLARATIVE_GENERATION_TERMS,
    DECLARATIVE_ENHANCEMENT_TERMS,
    TEXT_LIKE_TAG_HINTS,
    GENERATION_PROMPT_TAGS
)

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------

EXIFTOOL_COMMAND = "exiftool"

# ----------------------------------------------------------------------
# Dataclasses
# ----------------------------------------------------------------------

@dataclass
class Signal:
    id: str
    severity: str
    confidence: float
    status: str
    summary: str
    evidence: Optional[List[Dict[str, Any]]] = None

@dataclass
class ExtractorInfo:
    tool: str
    version: str
    command: List[str]
    extracted_at: str

# ----------------------------------------------------------------------
# Utility helpers
# ----------------------------------------------------------------------
def max_rule_confidence(items: List[Dict[str, Any]], default: float = 0.5) -> float:
    if not items:
        return default
    return max(safe_float(item.get("rule_confidence", default), default) for item in items)

def max_rule_severity(items: List[Dict[str, Any]], default: str = "medium") -> str:
    if not items:
        return default
    rank = {"low": 1, "medium": 2, "high": 3}
    best = default
    best_rank = rank.get(default, 2)
    for item in items:
        sev = item.get("rule_severity", default)
        sev_rank = rank.get(sev, 2)
        if sev_rank > best_rank:
            best = sev
            best_rank = sev_rank
    return best

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()

def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        try:
            return json.dumps(value, ensure_ascii=False).lower()
        except Exception:
            return str(value).lower()
    return str(value).lower()

def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default

def ensure_exiftool_available(exiftool_cmd: str = EXIFTOOL_COMMAND) -> None:
    if shutil.which(exiftool_cmd) is None:
        raise FileNotFoundError(
            f"ExifTool not found in PATH: '{exiftool_cmd}'. "
            f"Install ExifTool and ensure it is available on the command line."
        )

def split_group_and_tag(raw_key: str) -> Tuple[str, str]:
    """
    Example:
        'XMP-xmp:CreatorTool' -> ('XMP-xmp', 'CreatorTool')
        'Software' -> ('', 'Software')
    """
    if ":" in raw_key:
        group, tag = raw_key.split(":", 1)
        return group, tag
    return "", raw_key

def is_text_like_tag(tag_name: str) -> bool:
    tag_l = tag_name.lower()
    return any(hint in tag_l for hint in TEXT_LIKE_TAG_HINTS)

def contains_any(text: str, terms: List[str]) -> List[str]:
    hits = []
    for term in terms:
        if term in text:
            hits.append(term)
    return hits

def deduplicate_match_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    result = []
    for item in items:
        key = (
            item.get("group"),
            item.get("tag"),
            json.dumps(item.get("value"), sort_keys=True, ensure_ascii=False)
            if isinstance(item.get("value"), (dict, list))
            else str(item.get("value")),
            tuple(item.get("matched_terms", [])),
            item.get("category"),
        )
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result

# ----------------------------------------------------------------------
# ExifTool execution
# ----------------------------------------------------------------------
def run_hidden_subprocess(command, **kwargs) -> subprocess.CompletedProcess:
    startupinfo = None
    creationflags = 0
    if sys.platform.startswith("win"):
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0
        creationflags = subprocess.CREATE_NO_WINDOW
    try:
        return subprocess.run(
            command,
            startupinfo=startupinfo,
            creationflags=creationflags,
            **kwargs,
        )
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr if exc.stderr else ""
        stdout = exc.stdout if exc.stdout else ""
        raise RuntimeError(
            f"External command failed:\n"
            f"Command: {command}\n"
            f"Return code: {exc.returncode}\n"
            f"STDOUT: {stdout}\n"
            f"STDERR: {stderr}"
        ) from exc

def get_exiftool_version(exiftool_cmd: str = EXIFTOOL_COMMAND) -> str:
    result = run_hidden_subprocess(
        [exiftool_cmd, "-ver"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()

def run_exiftool_json(file_path: Path, exiftool_cmd: str = EXIFTOOL_COMMAND) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Returns:
        records: parsed JSON list from exiftool
        command: command used
    """
    command = [
        exiftool_cmd,
        "-j",
        "-G1",
        "-a",
        "-u",
        "-struct",
        "-api",
        "RequestAll=2",
        str(file_path),
    ]

    result = run_hidden_subprocess(
        command,
        check=True,
        capture_output=True,
        text=True,
        timeout=20,
    )

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Failed to parse ExifTool JSON output: {exc}") from exc
    if not isinstance(data, list) or not data:
        raise RuntimeError("ExifTool returned empty or unexpected JSON structure.")
    return data, command

# ----------------------------------------------------------------------
# Metadata parsing and watchlist extraction
# ----------------------------------------------------------------------

def extract_watchlist_hits(record: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Extracts metadata hits grouped into evidence families.
    Purpose:
    - Route high-value metadata tags into semantically meaningful buckets
    - Preserve watchlist hits for later interpretation
    - Preserve broad text-like fields for secondary scanning
    """
    hits: Dict[str, List[Dict[str, Any]]] = {
        "software": [],
        "creator_tool": [],
        "history": [],
        "derived_from": [],
        "container_text": [],
        "c2pa": [],
        "other_watchlist": [],
        "broad_text_scan": [],
        "generation_prompt": [],
    }
    for raw_key, value in record.items():
        group, tag = split_group_and_tag(raw_key)
        tag_l = tag.lower().strip()
        group_l = group.lower().strip()
        entry = {
            "raw_key": raw_key,
            "group": group,
            "tag": tag,
            "value": value,
        }
        # ------------------------------------------------------------------
        # High-priority semantic routing
        # ------------------------------------------------------------------
        # Software attribution / processing identity
        if tag_l in {"software", "processingsoftware", "hostcomputer"}:
            hits["software"].append(entry)
            continue
        # XMP creator tool
        if tag_l in {"creator", "artist", "author", "copyright"}:
            hits.setdefault("creator_identity", []).append(entry)
            continue
        # XMP prompt info
        if tag_l in {"prompt", "parameters", "workflow"}:
            hits["generation_prompt"].append(entry)
            continue        
        # XMP history / resource-event style tags
        if tag_l.startswith("history"):
            hits["history"].append(entry)
            continue
        # XMP media-management lineage / derivation tags
        if tag_l.startswith("derivedfrom"):
            hits["derived_from"].append(entry)
            continue
        # C2PA / JUMBF / manifest-related metadata
        if (
            tag_l in {"jumbf", "c2pa", "manifest", "claimgenerator", "actions"}
            or "c2pa" in group_l
            or "jumbf" in group_l
        ):
            hits["c2pa"].append(entry)
            continue
        # ------------------------------------------------------------------
        # Container text / free-text style metadata
        # ------------------------------------------------------------------
        if tag_l in {"comment", "source", "warning", "xmlcomadobexmp", "prompt", "parameters", "description", "imagedescription", "caption", "xpcomment", "usercomment", }:
            hits["container_text"].append(entry)
            continue
        # ------------------------------------------------------------------
        # Configured watchlist fallback
        # ------------------------------------------------------------------
        if tag_l in WATCH_TAGS:
            hits["other_watchlist"].append(entry)
            continue
        # ------------------------------------------------------------------
        # Broad secondary scan for text-like tags
        # ------------------------------------------------------------------
        if is_text_like_tag(tag):
            hits["broad_text_scan"].append(entry)
    return hits

def assess_camera_metadata_richness(record: dict[str, object], hits: dict[str, list[dict[str, object]]] | None = None,) -> Optional[Signal]:
    def has_any_suffix(*suffixes: str) -> bool:
        suffixes_l = tuple(s.lower() for s in suffixes)
        for key in record.keys():
            k = str(key).lower()
            if k.endswith(suffixes_l):
                return True
        return False
    found: list[str] = []
    tag_groups = [
        ("make", ("make",)),
        ("model", ("model", "camera model name")),
        ("lens", ("lens model", "lens id")),
        ("exposure", ("exposure time",)),
        ("aperture", ("f number", "aperture", "aperture value")),
        ("iso", ("iso",)),
        ("capture_time", ("date/time original", "createdate", "create date")),
        ("scene_type", ("scene type",)),
        ("gps", ("gps latitude", "gps longitude", "gps date/time")),
    ]
    for label, suffixes in tag_groups:
        if has_any_suffix(*suffixes):
            found.append(label)
    # Optional vendor / smartphone enrichers
    vendor_markers = 0
    if any(str(k).startswith("OnePlus:") for k in record.keys()):
        vendor_markers += 1
    if any(str(k).startswith("Google:") for k in record.keys()):
        vendor_markers += 1
    if len(found) >= 4:
        confidence = 0.78 if vendor_markers == 0 else 0.84
        return Signal(
            id="CAMERA_METADATA_RICH",
            severity="low",
            confidence=confidence,
            status="supporting",
            summary=(
                "Metadata contains multiple camera-acquisition fields consistent "
                "with a real photographic pipeline."
            ),
            evidence=[{
                "fields_detected": found,
                "vendor_markers": vendor_markers,
            }],
        )
    return None

# ----------------------------------------------------------------------
# Evidence interpretation
# ----------------------------------------------------------------------
def collect_textual_evidence(hits: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    Flatten selected evidence buckets into a single list that can be scanned.
    """
    evidence = []
    for bucket_name in (
        "software",
        "creator_tool",
        "history",
        "derived_from",
        "container_text",
        "c2pa",
        "other_watchlist",
        "broad_text_scan",
        "generation_prompt"
    ):
        evidence.extend(hits.get(bucket_name, []))
    return evidence

def find_term_matches(hits: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Scan evidence text for tool names and declarative phrases.
    Uses unified TOOL_RULES loaded from exif_rules.json.
    """
    evidence = collect_textual_evidence(hits)
    result = {
        "generation_tools": [],
        "enhancement_tools": [],
        "generic_editing_tools": [],
        "declarative_generation_terms": [],
        "declarative_enhancement_terms": [],
    }
    for item in evidence:
        text = f"{item.get('tag', '')} {normalize_text(item.get('value'))}"
        # Tool rules
        for rule in TOOL_RULES:
            term = rule.get("term", "").lower().strip()
            aliases = [a.lower().strip() for a in rule.get("aliases", [])]
            category = rule.get("category", "").strip()
            confidence = safe_float(rule.get("confidence", 0.5))
            severity = rule.get("severity", "medium")
            candidate_terms = [term] + aliases
            matched_terms = [t for t in candidate_terms if t and t in text]
            if not matched_terms:
                continue
            enriched = {
                **item,
                "matched_terms": matched_terms,
                "rule_term": term,
                "category": category,
                "rule_confidence": confidence,
                "rule_severity": severity,
            }
            if category == "generation":
                result["generation_tools"].append(enriched)
            elif category == "enhancement":
                result["enhancement_tools"].append(enriched)
            elif category == "generic_editing":
                result["generic_editing_tools"].append(enriched)

        # Declarative phrases
        dec_gen_hits = contains_any(text, DECLARATIVE_GENERATION_TERMS)
        dec_enh_hits = contains_any(text, DECLARATIVE_ENHANCEMENT_TERMS)
        if dec_gen_hits:
            result["declarative_generation_terms"].append(
                {**item, "matched_terms": dec_gen_hits}
            )
        if dec_enh_hits:
            result["declarative_enhancement_terms"].append(
                {**item, "matched_terms": dec_enh_hits}
            )
        for key in result:
            result[key] = deduplicate_match_items(result[key])       
    return result

def build_signals(
    file_path: Path,
    record: Dict[str, Any],
    hits: Dict[str, List[Dict[str, Any]]],
    matches: Dict[str, List[Dict[str, Any]]],
) -> List[Signal]:
    signals: List[Signal] = []

    # 0. Generator prompt
    generation_prompt_evidence = hits.get("generation_prompt", [])
    if generation_prompt_evidence:
        signals.append(
            Signal(
                id="EMBEDDED_GENERATION_PROMPT",
                severity="high",
                confidence=0.98,
                status="hit",
                summary=(
                    "Image metadata contains an embedded generation prompt or workflow, "
                    "which is strong declarative evidence of synthetic image generation."
                ),
                evidence=generation_prompt_evidence,
            )
        )
    # 1. Creator
    creator_identity = hits.get("creator_identity", [])
    if creator_identity:
        signals.append(
            Signal(
                id="CREATOR_IDENTITY_PRESENT",
                severity="low",
                confidence=0.65,
                status="supporting",
                summary="Metadata contains creator or authorship information.",
                evidence=creator_identity,
            )
        )

    # 2. Software trace
    software_evidence = hits["software"] + hits["creator_tool"]
    if software_evidence:
        signals.append(
            Signal(
                id="SOFTWARE_TRACE_PRESENT",
                severity="medium",
                confidence=0.70,
                status="hit",
                summary="Image metadata contains explicit software attribution.",
                evidence=software_evidence,
            )
        )
    # 3. Edit history
    if hits["history"]:
        signals.append(
            Signal(
                id="EDIT_HISTORY_PRESENT",
                severity="medium",
                confidence=0.80,
                status="hit",
                summary="XMP edit-history/resource-event style fields are present.",
                evidence=hits["history"],
            )
        )
    # 4. Derivation lineage
    if hits["derived_from"]:
        signals.append(
            Signal(
                id="DERIVATION_LINEAGE_PRESENT",
                severity="medium",
                confidence=0.75,
                status="hit",
                summary="Metadata indicates that this file may derive from another managed asset.",
                evidence=hits["derived_from"],
            )
        )
    # 5. PNG/WebP or container textual metadata
    if hits["container_text"]:
        signals.append(
            Signal(
                id="CONTAINER_TEXTUAL_METADATA_PRESENT",
                severity="low",
                confidence=0.60,
                status="hit",
                summary="Textual/container metadata fields are present and may contain workflow clues.",
                evidence=hits["container_text"],
            )
        )
    # 6. C2PA presence
    if hits["c2pa"]:
        signals.append(
            Signal(
                id="C2PA_PRESENT",
                severity="medium",
                confidence=0.85,
                status="hit",
                summary="Potential C2PA/JUMBF provenance-related metadata is present; separate verification is required.",
                evidence=hits["c2pa"],
            )
        )
    # 7. Explicit AI generation tool name match
    if matches["generation_tools"]:
        signals.append(
            Signal(
                id="AI_TOOL_NAME_MATCH",
                severity=max_rule_severity(matches["generation_tools"], default="high"),
                confidence=max_rule_confidence(matches["generation_tools"], default=0.88),
                status="hit",
                summary="Metadata contains one or more tool names associated with AI image generation workflows.",
                evidence=matches["generation_tools"],
            )
        )
    # 8. Explicit AI enhancement tool name match
    if matches["enhancement_tools"]:
        signals.append(
            Signal(
                id="ENHANCEMENT_TOOL_NAME_MATCH",
                severity="high",
                confidence=0.86,
                status="hit",
                summary="Metadata contains one or more tool names associated with AI enhancement or upscaling workflows.",
                evidence=matches["enhancement_tools"],
            )
        )
    # 9. Explicit declarative generation wording
    if matches["declarative_generation_terms"]:
        signals.append(
            Signal(
                id="DECLARED_SYNTHETIC",
                severity="high",
                confidence=0.92,
                status="hit",
                summary="Metadata contains explicit wording suggestive of synthetic or AI-generated origin.",
                evidence=matches["declarative_generation_terms"],
            )
        )
    # 10. Explicit declarative enhancement wording
    if matches["declarative_enhancement_terms"]:
        signals.append(
            Signal(
                id="DECLARED_ENHANCEMENT",
                severity="high",
                confidence=0.90,
                status="hit",
                summary="Metadata contains explicit wording suggestive of enhancement, restoration, upscaling, or generative editing.",
                evidence=matches["declarative_enhancement_terms"],
            )
        )
    # 11. Generic editing software only
    if (
        matches["generic_editing_tools"]
        and not matches["generation_tools"]
        and not matches["enhancement_tools"]
        and not matches["declarative_generation_terms"]
        and not matches["declarative_enhancement_terms"]
    ):
        signals.append(
            Signal(
                id="GENERIC_EDITING_SOFTWARE_PRESENT",
                severity=max_rule_severity(matches["generic_editing_tools"], default="low"),
                confidence=max_rule_confidence(matches["generic_editing_tools"], default=0.55),
                status="hit",
                summary="Generic image-editing software is present in metadata, but no explicit AI-specific declaration was found.",
                evidence=matches["generic_editing_tools"],
            )
        )
    # 11. Camera info present - strong counter signal!
    camera_signal = assess_camera_metadata_richness(record, hits)
    if camera_signal:
        signals.append(camera_signal)
    # 12. Sparse metadata heuristic
    sparse_indicator = assess_metadata_sparsity(record, hits)
    if sparse_indicator is not None:
        signals.append(sparse_indicator)
    # 13. Inconclusive fallback
    if not signals:
        signals.append(
            Signal(
                id="METADATA_INCONCLUSIVE",
                severity="low",
                confidence=0.40,
                status="inconclusive",
                summary="No meaningful declarative or provenance-related metadata signals were found.",
                evidence=None,
            )
        )
    return signals

def _has_meaningful_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        v = value.strip()
        if not v:
            return False
        if v.lower() in {"srgb", "rgb", "xyz", "acsp", "unknown ()"}:
            return False
        return True
    if isinstance(value, (list, dict)):
        return len(value) > 0
    return True

def _count_semantic_hits(hits: Dict[str, List[Dict[str, Any]]]) -> int:
    semantic_buckets = (
        "software",
        "creator_tool",
        "history",
        "derived_from",
        "container_text",
        "c2pa",
        "other_watchlist",
        # intentionally exclude broad_text_scan
    )
    count = 0
    for bucket in semantic_buckets:
        for item in hits.get(bucket, []):
            tag = str(item.get("tag", "")).strip()
            value = item.get("value")
            # ignore known non-provenance boilerplate even if they leaked in
            if tag in {"SourceFile", "ExifToolVersion", "ProfileDescription"}:
                continue
            if _has_meaningful_value(value):
                count += 1
                # print(f"meanigful value: {value}")
    return count


def assess_metadata_sparsity(record: Dict[str, Any], hits: Dict[str, List[Dict[str, Any]]]) -> Optional[Signal]:
    """
    Conservative sparse-metadata heuristic.
    Distinguish provenance-bearing metadata from technical/container metadata.
    """

    ignored_prefixes = {
        "SourceFile",
        "ExifTool:ExifToolVersion",
        "ExifTool:Now",
        "ExifTool:NewGUID",
        "ExifTool:FileSequence",
        "ExifTool:ProcessingTime",
        "System:FileName",
        "System:BaseName",
        "System:Directory",
        "System:FilePath",
        "System:FileSize",
        "System:ZoneIdentifier",
        "System:FileModifyDate",
        "System:FileAccessDate",
        "System:FileCreateDate",
        "System:FilePermissions",
        "System:FileAttributes",
        "System:FileDeviceNumber",
        "System:FileInodeNumber",
        "System:FileHardLinks",
        "System:FileUserID",
        "System:FileGroupID",
        "System:FileDeviceID",
        "System:FileBlockSize",
        "System:FileBlockCount",
        "File:FileType",
        "File:FileTypeExtension",
        "File:MIMEType",
    }

    technical_prefixes = (
        "JFIF:",
        "ICC-header:",
        "ICC_Profile:",
        "Composite:",
    )

    technical_exact = {
        "File:ExifByteOrder",
        "File:ImageWidth",
        "File:ImageHeight",
        "File:EncodingProcess",
        "File:BitsPerSample",
        "File:ColorComponents",
        "File:YCbCrSubSampling",
        "IFD0:XResolution",
        "IFD0:YResolution",
        "IFD0:ResolutionUnit",
        "IFD0:YCbCrPositioning",
        "IFD0:ProfileCopyright",
    }

    provenance_suffixes = (
        "Make",
        "Model",
        "LensModel",
        "LensID",
        "ExposureTime",
        "FNumber",
        "ISO",
        "DateTimeOriginal",
        "CreateDate",
        "Software",
        "CreatorTool",
        "History",
        "DerivedFrom",
        "Comment",
        "Description",
        "ImageDescription",
        "UserComment",
        "Prompt",
        "Parameters",
        "Manifest",
        "JUMBF",
        "C2PA",
        "ClaimGenerator",
        "Actions",
    )

    provenance_keys = []
    technical_keys = []

    for key in record.keys():
        if key in ignored_prefixes:
            continue
        if key in technical_exact or key.startswith(technical_prefixes):
            technical_keys.append(key)
            continue
        if any(key.endswith(suffix) for suffix in provenance_suffixes):
            provenance_keys.append(key)
            continue

        # unknown remainder: keep but do not count strongly
        # you can decide later whether to track these separately

    semantic_hit_count = _count_semantic_hits(hits)   
    if semantic_hit_count == 0:
        return Signal(
            id="METADATA_STRIPPED_OR_SPARSE",
            severity="low",
            confidence=0.55,
            status="weak_hit",
            summary=(
                "Metadata appears sparse or stripped of provenance-bearing fields; "
                "technical/container metadata may still be present."
            ),
            evidence=[{
                "provenance_keys_detected": provenance_keys,
                "technical_keys_detected_count": len(technical_keys),
            }],
        )            
    return None


def derive_classification(signals: List[Signal]) -> Dict[str, Any]:
    signal_ids = {s.id for s in signals}
    declared_generation = ("EMBEDDED_GENERATION_PROMPT" in signal_ids or "DECLARED_SYNTHETIC" in signal_ids or "AI_TOOL_NAME_MATCH" in signal_ids)
    declared_enhancement = "DECLARED_ENHANCEMENT" in signal_ids or "ENHANCEMENT_TOOL_NAME_MATCH" in signal_ids
    stripped = "METADATA_STRIPPED_OR_SPARSE" in signal_ids
    provenance_present = "C2PA_PRESENT" in signal_ids
    provenance_verified = False  # reserved for later dedicated C2PA validator
    if declared_generation:
        metadata_status = "declared_synthetic_candidate"
    elif declared_enhancement:
        metadata_status = "declared_enhancement_candidate"
    elif provenance_present:
        metadata_status = "provenance_present_unverified"
    elif "GENERIC_EDITING_SOFTWARE_PRESENT" in signal_ids:
        metadata_status = "edited_or_processed_but_inconclusive"
    elif "METADATA_STRIPPED_OR_SPARSE" in signal_ids:
        metadata_status = "sparse_or_stripped"
    elif "CAMERA_METADATA_RICH" in signal_ids:
        metadata_status = "camera_metadata_present"        
    else:
        metadata_status = "inconclusive"
    # print(f"Exiftool: metadata classificatie: {metadata_status}")
    return {
        "metadata_status": metadata_status,
        "stripped": stripped,
        "declared_generation": declared_generation,
        "declared_enhancement": declared_enhancement,
        "provenance_present": provenance_present,
        "provenance_verified": provenance_verified,
    }

# ----------------------------------------------------------------------
# Main orchestration
# ----------------------------------------------------------------------

def build_output_payload(
    file_path: Path,
    record: Dict[str, Any],
    extractor_info: ExtractorInfo,
    hits: Dict[str, List[Dict[str, Any]]],
    matches: Dict[str, List[Dict[str, Any]]],
    signals: List[Signal],
) -> Dict[str, Any]:
    return {
        "file": {
            "path": str(file_path),
            "name": file_path.name,
            "format": record.get("File:FileType"),
            "mime_type": record.get("File:MIMEType"),
            "filesize_bytes": file_path.stat().st_size,
            "sha256": sha256_file(file_path),
        },
        "extractor": asdict(extractor_info),
        "raw_watchlist_hits": hits,
        "term_matches": matches,
        "signals": [asdict(s) for s in signals],
        "classification": derive_classification(signals),
        "notes": [
            "Metadata alone does not prove AI generation or enhancement.",
            "C2PA presence should be verified separately in a dedicated provenance step.",
            "Absence of metadata is weak context only and may result from export, stripping, or recompression.",
        ],
    }

def analyze_file_with_exiftool(
    file_path: Path,
    output_json_path: Optional[Path] = None,
    exiftool_cmd: str = EXIFTOOL_COMMAND,
) -> Dict[str, Any]:
    if not file_path.exists():
        raise FileNotFoundError(f"File does not exist: {file_path}")
    ensure_exiftool_available(exiftool_cmd=exiftool_cmd)
    version = get_exiftool_version(exiftool_cmd=exiftool_cmd)
    records, command = run_exiftool_json(file_path=file_path, exiftool_cmd=exiftool_cmd)

    # ExifTool returns a list with one record for one file
    record = records[0]
    hits = extract_watchlist_hits(record)
    matches = find_term_matches(hits)
    signals = build_signals(file_path, record, hits, matches)
    extractor_info = ExtractorInfo(
        tool="exiftool",
        version=version,
        command=command,
        extracted_at=utc_now_iso(),
    )
    payload = build_output_payload(
        file_path=file_path,
        record=record,
        extractor_info=extractor_info,
        hits=hits,
        matches=matches,
        signals=signals,
    )
    if output_json_path is not None:
        output_json_path.parent.mkdir(parents=True, exist_ok=True)
        output_json_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    return payload


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------

def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Extract declarative/provenance-oriented metadata signals using ExifTool.")
    parser.add_argument("image_path", type=str, help="Path to the image file")
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="exif_signals.json",
        help="Path to output JSON file",
    )
    parser.add_argument(
        "--exiftool",
        type=str,
        default=EXIFTOOL_COMMAND,
        help="ExifTool command or full path",
    )

    args = parser.parse_args()
    image_path = Path(args.image_path).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()
    payload = analyze_file_with_exiftool(file_path=image_path, output_json_path=output_path, exiftool_cmd=args.exiftool,)
    print(f"[OK] Wrote metadata signal report to: {output_path}")
    print(f"[INFO] metadata_status = {payload['classification']['metadata_status']}")
    print(f"[INFO] declared_generation = {payload['classification']['declared_generation']}")
    print(f"[INFO] declared_enhancement = {payload['classification']['declared_enhancement']}")
    print(f"[INFO] provenance_present = {payload['classification']['provenance_present']}")

if __name__ == "__main__":
    main()