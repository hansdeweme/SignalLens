"""Explicit, bounded source retrieval. No detector, source claim or origin verdict.

Only this module issues local authenticated receipts. Receipt authentication is
an application integrity boundary, not publisher authentication or C2PA.
"""
from __future__ import annotations

import hashlib
import hmac
import http.client
import io
import ipaddress
import json
import os
import queue
import secrets
import socket
import ssl
import threading
import time
import warnings
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit

import cv2
import numpy as np
from PIL import Image, ImageOps

VERSION = 'source-image-v1'
_ISSUER_KEY = secrets.token_bytes(32)
MAX_BYTES = 20 * 1024 * 1024
MAX_PIXELS = 24_000_000
MAX_CANDIDATES = 4
LIMITS = ['Image identity does not authenticate creation, metadata, authorship, first publication or source independence.',
          'Visual metrics are deterministic similarity measurements, not probabilities.',
          'Crops, low-detail images and unsupported geometric transformations require analyst review.']


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()


def bounded_read(path, limit=MAX_BYTES):
    with Path(path).open('rb') as stream:
        data = stream.read(limit + 1)
    if len(data) > limit:
        raise ValueError('Retained evidence exceeds size limit')
    return data


def write_once(path, data):
    """Exclusive creation, flush before publication; remove only our failed write."""
    try:
        stream = path.open('xb')
    except FileExistsError:
        if bounded_read(path) != data:
            raise ValueError('Existing verification artifact differs from expected bytes')
        return
    try:
        with stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
    except Exception:
        path.unlink(missing_ok=True)
        raise


def checked_url(url):
    if not isinstance(url, str) or len(url) > 4096 or any(ord(c) < 33 for c in url):
        raise ValueError('Invalid source URL')
    parsed = urlsplit(url)
    if parsed.scheme not in {'http', 'https'} or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError('Only credential-free HTTP(S) source URLs are supported')
    if parsed.port not in {None, 80, 443}:
        raise ValueError('Only standard HTTP(S) ports are supported')
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path or '/', parsed.query, ''))


def public_addresses(host, port, timeout):
    # getaddrinfo has no portable timeout. A daemon lookup cannot hold the GUI
    # or process open; no connection is made if resolution misses the deadline.
    result = queue.Queue(maxsize=1)
    def resolve():
        try:
            result.put(socket.getaddrinfo(host, port, type=socket.SOCK_STREAM))
        except Exception as exc:
            result.put(exc)
    threading.Thread(target=resolve, daemon=True).start()
    try:
        records = result.get(timeout=timeout)
    except queue.Empty:
        raise TimeoutError('DNS resolution timed out') from None
    if isinstance(records, Exception):
        raise records
    addresses = list(dict.fromkeys(r[4][0] for r in records))
    if not addresses or any(not ipaddress.ip_address(a).is_global or
                            ipaddress.ip_address(a).is_multicast or
                            ipaddress.ip_address(a).is_reserved for a in addresses):
        raise ValueError('Source destination is not a public unicast address')
    return addresses


class SafeHTTP:
    """No proxies, cookies, netrc, retries or ambient credentials; IP-pinned TLS."""
    def fetch(self, url, cancel, deadline):
        requested = checked_url(url)
        current = requested
        for hop in range(4):
            if cancel.is_set():
                raise InterruptedError('Verification cancelled')
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError('Total retrieval deadline exceeded')
            p = urlsplit(current)
            port = p.port or (443 if p.scheme == 'https' else 80)
            addresses = public_addresses(p.hostname, port, min(5, remaining))
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError('Total retrieval deadline exceeded')
            conn = http.client.HTTPConnection(p.hostname, port, timeout=min(5, remaining))
            # Numeric address only: never resolve the hostname again on connect.
            sock = socket.socket(socket.AF_INET6 if ':' in addresses[0] else socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(min(5, remaining))
            def abort():
                try:
                    sock.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                sock.close()
            timer = threading.Timer(remaining, abort)
            timer.daemon = True
            timer.start()
            try:
                sock.connect((addresses[0], port))
                if sock.getpeername()[0] not in addresses:
                    raise ValueError('Connection destination differs from validated DNS')
                if p.scheme == 'https':
                    sock = ssl.create_default_context().wrap_socket(sock, server_hostname=p.hostname)
                conn.sock = sock
                target = urlunsplit(('', '', p.path or '/', p.query, ''))
                conn.request('GET', target, headers={'Host': p.netloc, 'Accept': 'image/*,text/html;q=0.5',
                    'Accept-Encoding': 'identity', 'User-Agent': 'SignalLens/0.1 source-verification'})
                response = conn.getresponse()
                if response.status in {301, 302, 303, 307, 308}:
                    if hop == 3:
                        raise ValueError('Redirect limit exceeded')
                    location = response.getheader('Location')
                    if not location:
                        raise ValueError('Redirect has no destination')
                    current = checked_url(urljoin(current, location))
                    continue
                if response.status != 200:
                    raise OSError(f'HTTP {response.status}')
                if response.getheader('Content-Encoding', 'identity').lower() != 'identity':
                    raise ValueError('Encoded HTTP responses are unsupported')
                length = response.getheader('Content-Length')
                if length and (int(length) < 0 or int(length) > MAX_BYTES):
                    raise ValueError('Response size exceeds limit')
                chunks, size = [], 0
                while True:
                    if cancel.is_set():
                        raise InterruptedError('Verification cancelled')
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        raise TimeoutError('Total retrieval deadline exceeded')
                    sock.settimeout(min(5, remaining))
                    block = response.read1(min(65536, MAX_BYTES + 1 - size))
                    if not block:
                        break
                    chunks.append(block)
                    size += len(block)
                    if size > MAX_BYTES:
                        raise ValueError('Response size exceeds limit')
                if length and size != int(length):
                    raise OSError('Incomplete response')
                return current, response.getheader('Content-Type', '').split(';')[0].lower(), b''.join(chunks)
            finally:
                timer.cancel()
                conn.close()
                sock.close()
        raise ValueError('Redirect limit exceeded')


class Candidates(HTMLParser):
    def __init__(self, base):
        super().__init__()
        self.base, self.urls = base, []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        url = None
        if tag == 'meta' and (attrs.get('property') or attrs.get('name', '')).lower() in {'og:image', 'og:image:url', 'twitter:image'}:
            url = attrs.get('content')
        elif tag == 'img':
            url = attrs.get('src')
        elif tag == 'a' and urlsplit(attrs.get('href', '')).path.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            url = attrs.get('href')
        if url and len(self.urls) < MAX_CANDIDATES:
            try:
                url = checked_url(urljoin(self.base, url))
            except ValueError:
                return
            if url not in self.urls:
                self.urls.append(url)


def decode(data):
    if len(data) > MAX_BYTES:
        raise ValueError('Image byte limit exceeded')
    with warnings.catch_warnings():
        warnings.simplefilter('error', Image.DecompressionBombWarning)
        with Image.open(io.BytesIO(data)) as im:
            if im.format not in {'PNG', 'JPEG', 'WEBP', 'GIF', 'BMP', 'TIFF'}:
                raise ValueError('Unsupported image format')
            if im.width * im.height > MAX_PIXELS or max(im.size) > 12000 or getattr(im, 'n_frames', 1) != 1:
                raise ValueError('Image dimensions or frame count exceed limits')
            im.load()
            return ImageOps.exif_transpose(im).convert('RGB')


def compare(local, remote):
    """Conservative aligned full-frame matcher; ambiguous is the default.

    Every tile must agree, and distributed mutual ORB correspondences must
    support near-identity geometry. Shared backgrounds alone cannot pass.
    """
    if digest(local) == digest(remote):
        return 'byte_identical', {'method': 'sha256', 'sha256_equal': True}
    a, b = decode(local), decode(remote)
    metrics = {'method': 'aligned-tiles-orb-v1', 'sha256_equal': False,
               'local_dimensions': list(a.size), 'source_dimensions': list(b.size)}
    if min(*a.size, *b.size) < 128 or abs(a.width / a.height / (b.width / b.height) - 1) > .015:
        return 'ambiguous', metrics
    size = (512, max(128, min(768, round(512 * a.height / a.width))))
    aa, bb = [np.asarray(im.resize(size, Image.Resampling.LANCZOS)) for im in (a, b)]
    gray_a, gray_b = [cv2.cvtColor(im, cv2.COLOR_RGB2GRAY) for im in (aa, bb)]
    error = np.abs(aa.astype(float) - bb.astype(float)) / 255
    tiles = [float(t.mean()) for row in np.array_split(error, 4, axis=0) for t in np.array_split(row, 4, axis=1)]
    orb = cv2.ORB_create(nfeatures=1500)
    ka, da = orb.detectAndCompute(gray_a, None)
    kb, db = orb.detectAndCompute(gray_b, None)
    pairs = [] if da is None or db is None else cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True).match(da, db)
    good = [m for m in pairs if m.distance <= 32 and
            np.linalg.norm(np.array(ka[m.queryIdx].pt) - np.array(kb[m.trainIdx].pt)) <= 3]
    cells = {(min(3, int(ka[m.queryIdx].pt[0] * 4 / size[0])),
              min(3, int(ka[m.queryIdx].pt[1] * 4 / size[1]))) for m in good}
    local_cells = {(min(3, int(k.pt[0] * 4 / size[0])), min(3, int(k.pt[1] * 4 / size[1]))) for k in ka}
    quadrants = {(x // 2, y // 2) for x, y in cells}
    metrics.update(mean_absolute_error=float(error.mean()), worst_tile_error=max(tiles),
                   aligned_feature_count=len(good), occupied_grid_cells=len(cells),
                   feature_cell_coverage=len(cells) / max(1, len(local_cells)), quadrants=len(quadrants),
                   aligned_feature_fraction=len(good) / max(1, len(pairs)),
                   thresholds={'mean_error_max': .035, 'tile_error_max': .065,
                               'features_min': 60, 'grid_cells_min': 8, 'cell_coverage_min': .85,
                               'quadrants_min': 4, 'fraction_min': .65})
    if (error.mean() <= .035 and max(tiles) <= .065 and len(good) >= 60 and len(cells) >= 8
            and len(cells) / max(1, len(local_cells)) >= .85 and len(quadrants) == 4
            and len(good) / max(1, len(pairs)) >= .65):
        return 'visually_verified', metrics
    # Large whole-frame differences can reject full-frame association. Crops
    # never enter this branch because aspect/coverage was not established.
    return ('rejected' if error.mean() > .20 and len(good) < 8 else 'ambiguous'), metrics


def retrieve(local_path, local_sha, match, cancel=None, progress=lambda text: None, transport=None):
    cancel = cancel or threading.Event()
    transport = transport or SafeHTTP()
    local = bounded_read(local_path)
    if digest(local) != local_sha:
        raise ValueError('Local source image changed; select or analyze the current image again')
    decode(local)
    url = match.get('image_url') or match.get('page_url')
    deadline = time.monotonic() + 30
    results = []
    pending = [url]
    discovery = True
    while pending and len(results) < MAX_CANDIDATES:
        candidate = pending.pop(0)
        if cancel.is_set():
            raise InterruptedError('Verification cancelled')
        progress(f'Retrieving candidate {len(results) + 1}/{MAX_CANDIDATES}')
        record = {'version': VERSION, 'requested_url': candidate, 'local_sha256': local_sha,
                  'record_id': match.get('record_id'), 'source_image_url': match.get('image_url', ''),
                  'source_page_url': match.get('page_url', ''),
                  'retrieved_at': datetime.now(timezone.utc).isoformat(), 'limitations': LIMITS.copy(),
                  'association': 'unestablished', 'status': 'download_failed'}
        try:
            final, media, data = transport.fetch(candidate, cancel, deadline)
            record.update(final_url=final, media_type=media, byte_size=len(data))
            if media == 'text/html':
                if discovery:
                    parser = Candidates(final)
                    parser.feed(data[:1024 * 1024].decode('utf-8', errors='replace'))
                    pending = parser.urls
                    discovery = False
                    if pending:
                        continue
                record.update(status='unsupported_response', error='HTML page; no further supported image discovery')
            elif media.startswith('image/') or media == 'application/octet-stream':
                record['status'] = 'image_decode_failed'
                decode(data)
                record['status'] = 'verification_failed'
                association, metrics = compare(local, data)
                record.update(status='verification_completed', association=association,
                              source_sha256=digest(data), metrics=metrics)
                record['_issuer_mac'] = hmac.new(_ISSUER_KEY, canonical(record), 'sha256').hexdigest()
                results.append((record, data))
                continue
            else:
                record.update(status='unsupported_response', error='Response is not a supported image or HTML page')
        except InterruptedError:
            raise
        except Exception as exc:
            record['error'] = str(exc)
        results.append((record, None))
        discovery = False
    if cancel.is_set():
        raise InterruptedError('Verification cancelled')
    return results


def retain(root, result, data, match, session_id, revision):
    """Exclusive immutable receipt and content-addressed asset, only on acceptance."""
    if result.get('status') != 'verification_completed' or digest(data) != result.get('source_sha256'):
        raise ValueError('Cannot retain incomplete verification')
    issued = {k: v for k, v in result.items() if k != '_issuer_mac'}
    if not hmac.compare_digest(result.get('_issuer_mac', ''), hmac.new(_ISSUER_KEY, canonical(issued), 'sha256').hexdigest()):
        raise ValueError('Result was not issued by the current source verifier')
    if issued['record_id'] != match.get('record_id') or issued['source_image_url'] != match.get('image_url', ''):
        raise ValueError('Verification result belongs to a different source record or URL')
    root = Path(root).resolve() / 'verification'
    root.mkdir(exist_ok=True)
    existing = list(root.iterdir())
    if len(existing) >= 256 or sum(p.stat().st_size for p in existing if p.is_file()) + len(data) > 256 * 1024 * 1024:
        raise ValueError('Investigation verification storage limit reached (256 files / 256 MiB)')
    key_path = root / '.receipt-key'
    if not key_path.exists():
        write_once(key_path, secrets.token_bytes(32))
    asset = root / (digest(data) + '.image')
    write_once(asset, data)
    record = dict(issued, investigation_id=session_id,
                  evidence_revision=revision)
    key = bounded_read(key_path, 32)
    if len(key) != 32:
        raise ValueError('Invalid local receipt key')
    receipt = {'record': record, 'mac': hmac.new(key, canonical(record), 'sha256').hexdigest()}
    receipt_id = digest(canonical(receipt))
    path = root / (receipt_id + '.json')
    write_once(path, canonical(receipt))
    return {'root': str(root), 'receipt_id': receipt_id}


def validate(match, local_sha):
    """Reopen without network; reject forged/stale labels and altered artifacts."""
    ref = match.get('verification')
    if not isinstance(ref, dict) or match.get('image_association') == 'rejected':
        return None
    try:
        root = Path(ref['root'])
        # Never open a UNC/device/network path from imported annotations.
        if not root.is_absolute() or str(root).startswith(('\\\\', '//')) or '..' in root.parts:
            return None
        rid = ref['receipt_id']
        if root.name != 'verification' or len(rid) != 64 or any(c not in '0123456789abcdef' for c in rid):
            return None
        raw = bounded_read(root / (rid + '.json'), 64000)
        if len(raw) > 64000 or digest(raw) != rid:
            return None
        receipt = json.loads(raw)
        record = receipt['record']
        key = bounded_read(root / '.receipt-key', 32)
        if len(key) != 32 or not hmac.compare_digest(receipt['mac'], hmac.new(key, canonical(record), 'sha256').hexdigest()):
            return None
        if record['version'] != VERSION or record['local_sha256'] != local_sha or record['record_id'] != match.get('record_id'):
            return None
        if record['source_image_url'] != match.get('image_url', ''):
            return None
        sha = record['source_sha256']
        if len(sha) != 64 or any(c not in '0123456789abcdef' for c in sha):
            return None
        asset = root / (sha + '.image')
        if digest(bounded_read(asset)) != sha:
            return None
        if record['status'] != 'verification_completed':
            return None
        return record
    except (OSError, ValueError, KeyError, TypeError):
        return None
