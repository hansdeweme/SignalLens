#osint_reverse_search.py
# Copyright (c) 2025, 2026 Hans De Weme
# Licensed under the MIT License (https://opensource.org/licenses/MIT).
# Part of the SignalLens project evaluating signals of AI-generated and/or AI-enhanced Photo Imgages#
#
from __future__ import annotations
import hashlib
import json
import mimetypes
import os
import webbrowser
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

# ------------------------------------------------------------
# dataclasses
# ------------------------------------------------------------

@dataclass
class ReverseSearchMatch:
    provider: str
    title: str = ""
    page_url: str = ""
    image_url: str = ""
    thumbnail_url: str = ""
    domain: str = ""
    source_type: str = "unknown"   # unknown / stock / ai_gallery / social / news / marketplace / other
    similarity_score: Optional[float] = None
    first_seen_estimate: Optional[str] = None
    notes: str = ""


@dataclass
class ReverseSearchQueryLinks:
    google_lens_url: str = "https://lens.google.com/"
    google_images_url: str = "https://images.google.com/"
    yandex_url: str = "https://yandex.com/images/"
    tineye_url: str = "https://tineye.com/"
    bing_visual_url: str = "https://www.bing.com/visualsearch"


@dataclass
class ReverseSearchResult:
    success: bool
    image_path: str
    image_sha256: str
    file_size_bytes: int
    mime_type: str
    started_at_utc: str
    completed_at_utc: str

    mode: str = "manual"
    analyst_reviewed: bool = False
    analyst_notes: List[str] = field(default_factory=list)

    providers_attempted: List[str] = field(default_factory=list)
    providers_succeeded: List[str] = field(default_factory=list)
    providers_failed: List[Dict[str, str]] = field(default_factory=list)

    query_links: ReverseSearchQueryLinks = field(default_factory=ReverseSearchQueryLinks)
    matches: List[ReverseSearchMatch] = field(default_factory=list)

    matches_found: bool = False
    best_match_url: str = ""
    best_match_title: str = ""
    best_match_similarity: Optional[float] = None

    possible_original_found: bool = False
    derivative_detected: bool = False
    ai_source_context_detected: bool = False
    stock_source_context_detected: bool = False
    news_source_context_detected: bool = False

    dominant_source_type: str = "unknown"
    first_seen_estimate: Optional[str] = None
    manual_entry_count: int = 0

    review_status: str = "not_reviewed"  # not_reviewed / reviewed_no_match / reviewed_matches_found
    summary: str = ""
    notes: List[str] = field(default_factory=list)


# ------------------------------------------------------------
# utils
# ------------------------------------------------------------

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256_of_file(path: str | Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def guess_mime_type(path: str | Path) -> str:
    mime, _ = mimetypes.guess_type(str(path))
    return mime or "application/octet-stream"


def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def save_json(data: Dict[str, Any], out_path: str | Path) -> None:
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_json(path: str | Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def domain_from_url(url: str) -> str:
    try:
        return urlparse(url).netloc.lower()
    except Exception:
        return ""


def classify_source_type(url: str, title: str = "") -> str:
    hay = f"{url} {title}".lower()

    ai_markers = [
        "midjourney", "lexica", "civitai", "playgroundai",
        "openart", "stable diffusion", "dall-e", "firefly",
        "prompt", "dreamina", "mage.space"
    ]
    stock_markers = [
        "shutterstock", "gettyimages", "adobestock", "adobe stock",
        "istockphoto", "alamy", "dreamstime", "depositphotos",
        "pexels", "unsplash"
    ]
    social_markers = [
        "instagram", "reddit", "pinterest", "facebook",
        "x.com", "twitter", "tiktok", "imgur"
    ]
    news_markers = [
        "reuters", "apnews", "bbc", "cnn", "nytimes", "theguardian"
    ]
    marketplace_markers = [
        "etsy", "ebay", "amazon"
    ]

    if any(m in hay for m in ai_markers):
        return "ai_gallery"
    if any(m in hay for m in stock_markers):
        return "stock"
    if any(m in hay for m in social_markers):
        return "social"
    if any(m in hay for m in news_markers):
        return "news"
    if any(m in hay for m in marketplace_markers):
        return "marketplace"
    return "unknown"


def _sort_key(match: ReverseSearchMatch) -> float:
    return match.similarity_score if match.similarity_score is not None else -1.0


def summarize_matches(matches: List[ReverseSearchMatch], analyst_reviewed: bool) -> Dict[str, Any]:
    if not matches:
        if analyst_reviewed:
            return {
                "matches_found": False,
                "best_match_url": "",
                "best_match_title": "",
                "best_match_similarity": None,
                "possible_original_found": False,
                "derivative_detected": False,
                "ai_source_context_detected": False,
                "stock_source_context_detected": False,
                "news_source_context_detected": False,
                "dominant_source_type": "unknown",
                "first_seen_estimate": None,
                "manual_entry_count": 0,
                "review_status": "reviewed_no_match",
                "summary": "Manual reverse-image search was reviewed, but no meaningful online match was documented."
            }

        return {
            "matches_found": False,
            "best_match_url": "",
            "best_match_title": "",
            "best_match_similarity": None,
            "possible_original_found": False,
            "derivative_detected": False,
            "ai_source_context_detected": False,
            "stock_source_context_detected": False,
            "news_source_context_detected": False,
            "dominant_source_type": "unknown",
            "first_seen_estimate": None,
            "manual_entry_count": 0,
            "review_status": "not_reviewed",
            "summary": "No reverse-image OSINT review has yet been recorded for this image."
        }

    ranked = sorted(matches, key=_sort_key, reverse=True)
    best = ranked[0]

    source_type_counts: Dict[str, int] = {}
    for m in matches:
        source_type_counts[m.source_type] = source_type_counts.get(m.source_type, 0) + 1

    dominant_source_type = max(source_type_counts, key=source_type_counts.get)
    ai_source_context_detected = any(m.source_type == "ai_gallery" for m in matches)
    stock_source_context_detected = any(m.source_type == "stock" for m in matches)
    news_source_context_detected = any(m.source_type == "news" for m in matches)

    date_candidates = [m.first_seen_estimate for m in matches if m.first_seen_estimate]
    first_seen_estimate = min(date_candidates) if date_candidates else None

    best_sim = best.similarity_score
    possible_original_found = best_sim is not None and best_sim >= 0.90
    derivative_detected = any(
        m.similarity_score is not None and 0.55 <= m.similarity_score < 0.90
        for m in matches
    )

    parts = [f"{len(matches)} reverse-image match(es) documented."]
    parts.append(f"Best match source type: {best.source_type}.")
    if best_sim is not None:
        parts.append(f"Best normalized similarity: {best_sim:.2f}.")
    if first_seen_estimate:
        parts.append(f"Earliest observed date estimate: {first_seen_estimate}.")
    if possible_original_found:
        parts.append("A likely original or near-original online version may have been identified.")
    elif derivative_detected:
        parts.append("Online matches suggest derivative or related image reuse.")
    if ai_source_context_detected:
        parts.append("AI-related online source context detected.")
    if stock_source_context_detected:
        parts.append("Stock-image source context detected.")

    return {
        "matches_found": True,
        "best_match_url": best.page_url,
        "best_match_title": best.title,
        "best_match_similarity": best.similarity_score,
        "possible_original_found": possible_original_found,
        "derivative_detected": derivative_detected,
        "ai_source_context_detected": ai_source_context_detected,
        "stock_source_context_detected": stock_source_context_detected,
        "news_source_context_detected": news_source_context_detected,
        "dominant_source_type": dominant_source_type,
        "first_seen_estimate": first_seen_estimate,
        "manual_entry_count": len(matches),
        "review_status": "reviewed_matches_found",
        "summary": " ".join(parts)
    }


def dataclass_to_jsonable(result: ReverseSearchResult) -> Dict[str, Any]:
    return asdict(result)


# ------------------------------------------------------------
# persistence
# ------------------------------------------------------------

def create_empty_osint_result(image_path: str | Path) -> ReverseSearchResult:
    image_path = str(Path(image_path).resolve())
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    now = utc_now_iso()
    return ReverseSearchResult(
        success=True,
        image_path=image_path,
        image_sha256=sha256_of_file(image_path),
        file_size_bytes=os.path.getsize(image_path),
        mime_type=guess_mime_type(image_path),
        started_at_utc=now,
        completed_at_utc=now,
        mode="manual",
        analyst_reviewed=False,
        analyst_notes=[],
        summary="No reverse-image OSINT review has yet been recorded for this image."
    )


def save_osint_result(result: ReverseSearchResult, out_dir: str | Path) -> Path:
    out_dir = ensure_dir(out_dir)
    json_path = Path(out_dir) / "osint_results.json"
    result.completed_at_utc = utc_now_iso()
    save_json(dataclass_to_jsonable(result), json_path)
    return json_path


def load_osint_result(json_path: str | Path) -> ReverseSearchResult:
    raw = load_json(json_path)

    query_links = ReverseSearchQueryLinks(**raw.get("query_links", {}))
    matches = [ReverseSearchMatch(**m) for m in raw.get("matches", [])]

    result = ReverseSearchResult(
        success=raw.get("success", True),
        image_path=raw.get("image_path", ""),
        image_sha256=raw.get("image_sha256", ""),
        file_size_bytes=raw.get("file_size_bytes", 0),
        mime_type=raw.get("mime_type", "application/octet-stream"),
        started_at_utc=raw.get("started_at_utc", utc_now_iso()),
        completed_at_utc=raw.get("completed_at_utc", utc_now_iso()),
        mode=raw.get("mode", "manual"),
        analyst_reviewed=raw.get("analyst_reviewed", False),
        analyst_notes=raw.get("analyst_notes", []),
        providers_attempted=raw.get("providers_attempted", []),
        providers_succeeded=raw.get("providers_succeeded", []),
        providers_failed=raw.get("providers_failed", []),
        query_links=query_links,
        matches=matches,
        matches_found=raw.get("matches_found", False),
        best_match_url=raw.get("best_match_url", ""),
        best_match_title=raw.get("best_match_title", ""),
        best_match_similarity=raw.get("best_match_similarity", None),
        possible_original_found=raw.get("possible_original_found", False),
        derivative_detected=raw.get("derivative_detected", False),
        ai_source_context_detected=raw.get("ai_source_context_detected", False),
        stock_source_context_detected=raw.get("stock_source_context_detected", False),
        news_source_context_detected=raw.get("news_source_context_detected", False),
        dominant_source_type=raw.get("dominant_source_type", "unknown"),
        first_seen_estimate=raw.get("first_seen_estimate", None),
        manual_entry_count=raw.get("manual_entry_count", 0),
        review_status=raw.get("review_status", "not_reviewed"),
        summary=raw.get("summary", ""),
        notes=raw.get("notes", []),
    )
    return result


# ------------------------------------------------------------
# actions
# ------------------------------------------------------------

def initialize_osint_for_image(image_path: str | Path, out_dir: str | Path) -> ReverseSearchResult:
    result = create_empty_osint_result(image_path)
    save_osint_result(result, out_dir)
    return result


def open_reverse_search(provider: str, result: ReverseSearchResult | None = None) -> str:
    provider = provider.lower().strip()

    if result is not None:
        result.providers_attempted.append(provider)

    mapping = {
        "google": "https://lens.google.com/",
        "google_lens": "https://lens.google.com/",
        "google_images": "https://images.google.com/",
        "yandex": "https://yandex.com/images/",
        "tineye": "https://tineye.com/",
        "bing": "https://www.bing.com/visualsearch",
    }

    url = mapping.get(provider)
    if not url:
        raise ValueError(f"Unknown reverse-search provider: {provider}")

    webbrowser.open_new_tab(url)
    return url


def mark_reviewed_no_match(result: ReverseSearchResult) -> ReverseSearchResult:
    result.analyst_reviewed = True
    summary_fields = summarize_matches(result.matches, result.analyst_reviewed)
    _apply_summary_fields(result, summary_fields)
    return result


def add_manual_match(
    result: ReverseSearchResult,
    provider: str,
    page_url: str,
    title: str = "",
    image_url: str = "",
    thumbnail_url: str = "",
    similarity_score: Optional[float] = None,
    first_seen_estimate: Optional[str] = None,
    source_type: str = "unknown",
    notes: str = "",
) -> ReverseSearchResult:
    inferred_source_type = source_type
    if inferred_source_type == "unknown":
        inferred_source_type = classify_source_type(page_url, title)

    match = ReverseSearchMatch(
        provider=provider,
        title=title.strip(),
        page_url=page_url.strip(),
        image_url=image_url.strip(),
        thumbnail_url=thumbnail_url.strip(),
        domain=domain_from_url(page_url),
        source_type=inferred_source_type,
        similarity_score=similarity_score,
        first_seen_estimate=first_seen_estimate.strip() if first_seen_estimate else None,
        notes=notes.strip(),
    )

    result.matches.append(match)
    result.analyst_reviewed = True

    summary_fields = summarize_matches(result.matches, result.analyst_reviewed)
    _apply_summary_fields(result, summary_fields)
    return result


def replace_match(
    result: ReverseSearchResult,
    index: int,
    provider: str,
    page_url: str,
    title: str = "",
    image_url: str = "",
    thumbnail_url: str = "",
    similarity_score: Optional[float] = None,
    first_seen_estimate: Optional[str] = None,
    source_type: str = "unknown",
    notes: str = "",
) -> ReverseSearchResult:
    if not (0 <= index < len(result.matches)):
        raise IndexError("Match index out of range.")

    inferred_source_type = source_type
    if inferred_source_type == "unknown":
        inferred_source_type = classify_source_type(page_url, title)

    result.matches[index] = ReverseSearchMatch(
        provider=provider,
        title=title.strip(),
        page_url=page_url.strip(),
        image_url=image_url.strip(),
        thumbnail_url=thumbnail_url.strip(),
        domain=domain_from_url(page_url),
        source_type=inferred_source_type,
        similarity_score=similarity_score,
        first_seen_estimate=first_seen_estimate.strip() if first_seen_estimate else None,
        notes=notes.strip(),
    )

    result.analyst_reviewed = True
    summary_fields = summarize_matches(result.matches, result.analyst_reviewed)
    _apply_summary_fields(result, summary_fields)
    return result


def delete_match(result: ReverseSearchResult, index: int) -> ReverseSearchResult:
    if not (0 <= index < len(result.matches)):
        raise IndexError("Match index out of range.")

    del result.matches[index]
    summary_fields = summarize_matches(result.matches, result.analyst_reviewed)
    _apply_summary_fields(result, summary_fields)
    return result


def _apply_summary_fields(result: ReverseSearchResult, summary_fields: Dict[str, Any]) -> None:
    result.matches_found = summary_fields["matches_found"]
    result.best_match_url = summary_fields["best_match_url"]
    result.best_match_title = summary_fields["best_match_title"]
    result.best_match_similarity = summary_fields["best_match_similarity"]
    result.possible_original_found = summary_fields["possible_original_found"]
    result.derivative_detected = summary_fields["derivative_detected"]
    result.ai_source_context_detected = summary_fields["ai_source_context_detected"]
    result.stock_source_context_detected = summary_fields["stock_source_context_detected"]
    result.news_source_context_detected = summary_fields["news_source_context_detected"]
    result.dominant_source_type = summary_fields["dominant_source_type"]
    result.first_seen_estimate = summary_fields["first_seen_estimate"]
    result.manual_entry_count = summary_fields["manual_entry_count"]
    result.review_status = summary_fields["review_status"]
    result.summary = summary_fields["summary"]
    result.completed_at_utc = utc_now_iso()


def format_match_label(match: ReverseSearchMatch) -> str:
    sim_txt = "n/a" if match.similarity_score is None else f"{match.similarity_score:.2f}"
    domain = match.domain or "-"
    source_type = match.source_type or "unknown"
    provider = match.provider or "unknown"
    return f"[{provider}] {source_type} | sim={sim_txt} | {domain}"


def build_osint_summary_text(result: ReverseSearchResult | None) -> str:
    if result is None:
        return "OSINT: no data"

    if result.review_status == "not_reviewed":
        return "OSINT: not reviewed yet"

    if result.review_status == "reviewed_no_match":
        return "OSINT: reviewed, no documented match"

    if result.review_status == "reviewed_matches_found":
        parts = [f"OSINT: {result.manual_entry_count} finding(s)"]
        if result.dominant_source_type and result.dominant_source_type != "unknown":
            parts.append(f"dominant={result.dominant_source_type}")
        if result.best_match_similarity is not None:
            parts.append(f"best={result.best_match_similarity:.2f}")
        return " | ".join(parts)

    return "OSINT: status unknown"