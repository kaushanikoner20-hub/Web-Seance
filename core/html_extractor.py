"""
HTML Extractor Module for Web Séance.
Extracts titles, text excerpts, and verified outgoing hyperlinks from raw archived HTML.
Filters Wayback toolbar artifacts and standardizes evidence structures.
"""

import hashlib
import re
import urllib.parse
from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup

SKIP_PREFIXES = ("mailto:", "javascript:", "tel:", "data:", "#", "irc:", "news:", "gopher:")


def normalize_host(url: str) -> str:
    """Extract and normalize hostname from URL, stripping www. and port."""
    try:
        parsed = urllib.parse.urlparse(url)
        host = (parsed.hostname or "").lower()
        if host.startswith("www."):
            host = host[4:]
        return host
    except Exception:
        return ""


def clean_url(url: str) -> str:
    """Normalize URL by stripping default port :80, fragments, and trailing whitespace."""
    try:
        parsed = urllib.parse.urlparse(url)
        netloc = parsed.netloc
        # Strip default HTTP port 80 or HTTPS port 443
        if parsed.scheme == "http" and netloc.endswith(":80"):
            netloc = netloc[:-3]
        elif parsed.scheme == "https" and netloc.endswith(":443"):
            netloc = netloc[:-4]

        # Rebuild without fragment
        normalized = urllib.parse.urlunparse((
            parsed.scheme,
            netloc,
            parsed.path or "/",
            parsed.params,
            parsed.query,
            ""  # strip fragment
        ))
        return normalized.strip()
    except Exception:
        return url.strip()


def is_archive_injected_url(href: str) -> bool:
    """Identify if a URL points to Wayback toolbar or internal archive machinery."""
    href_lower = href.lower()
    if "web.archive.org/web/" in href_lower or "archive.org/web/" in href_lower:
        return True
    if href_lower.startswith("/web/") or href_lower.startswith("//web.archive.org"):
        return True
    if "wayback-toolbar" in href_lower or "wm-dis-banner" in href_lower:
        return True
    return False


def extract_content_excerpt(soup: BeautifulSoup, max_chars: int = 350) -> str:
    """Extract a clean readable text excerpt from parsed HTML, removing script and style tags."""
    # Clone soup or copy elements to avoid destroying original
    text_elements = []
    for elem in soup.find_all(["p", "h1", "h2", "h3", "h4", "li", "blockquote", "td", "font"]):
        # skip elements inside script or style
        if elem.find_parent(["script", "style", "noscript"]):
            continue
        t = elem.get_text(separator=" ", strip=True)
        if t and len(t) > 10:
            text_elements.append(t)

    if not text_elements:
        # Fallback to body text
        body = soup.find("body") or soup
        text = body.get_text(separator=" ", strip=True)
        # Collapse whitespace
        text = re.sub(r"\s+", " ", text)
        return text[:max_chars].strip() + ("..." if len(text) > max_chars else "")

    combined = " ".join(text_elements)
    combined = re.sub(r"\s+", " ", combined)
    if len(combined) > max_chars:
        return combined[:max_chars].rsplit(" ", 1)[0] + "..."
    return combined


def extract_page_evidence(
    html_content: str,
    original_url: str,
    page_id: str,
    capture_timestamp: str,
    archive_capture_url: str,
    max_links: int = 150
) -> Dict:
    """
    Parses raw HTML, extracts title, excerpt, and verified outgoing hyperlinks.
    Every link is given a unique evidence ID and scope tag.
    """
    content_bytes = html_content.encode("utf-8", errors="replace")
    content_sha256 = hashlib.sha256(content_bytes).hexdigest()

    soup = BeautifulSoup(html_content, "html.parser")

    # Extract title
    raw_title = soup.title.string if soup.title else ""
    title = re.sub(r"\s+", " ", raw_title).strip() if raw_title else "Untitled Page"

    # Extract content excerpt
    content_summary = extract_content_excerpt(soup)

    source_host = normalize_host(original_url)

    seen_destinations = set()
    links = []
    archive_injected_count = 0
    raw_href_count = 0

    link_counter = 1

    # Find all anchor tags
    for a in soup.find_all("a", href=True):
        raw_href = a["href"].strip()
        raw_href_count += 1

        if not raw_href or raw_href.lower().startswith(SKIP_PREFIXES):
            continue

        if is_archive_injected_url(raw_href):
            archive_injected_count += 1
            continue

        # Resolve relative URL
        try:
            absolute = urllib.parse.urljoin(original_url, raw_href)
            normalized_url = clean_url(absolute)
            parts = urllib.parse.urlparse(normalized_url)
        except Exception:
            continue

        if parts.scheme not in ("http", "https"):
            continue

        dest_host = normalize_host(normalized_url)
        if not dest_host:
            continue

        # Determine scope: same_site vs external
        scope = "same_site" if (dest_host == source_host or dest_host.endswith(f".{source_host}")) else "external"

        # Deduplicate per page
        if normalized_url in seen_destinations:
            continue
        seen_destinations.add(normalized_url)

        anchor_text = a.get_text(separator=" ", strip=True)
        if len(anchor_text) > 80:
            anchor_text = anchor_text[:77] + "..."

        evidence_id = f"{page_id}-L{link_counter}"
        links.append({
            "evidence_id": evidence_id,
            "source_page_id": page_id,
            "source_url": clean_url(original_url),
            "destination_url": normalized_url,
            "destination_host": dest_host,
            "anchor_text": anchor_text or "[No anchor text]",
            "scope": scope,
            "capture_timestamp": capture_timestamp,
            "archive_capture_url": archive_capture_url,
            "link_type": "hyperlink_in_archived_html",
            "extraction_method": "beautifulsoup4_html_parser",
            "ai_inferred": False
        })
        link_counter += 1

        if len(links) >= max_links:
            break

    return {
        "page_id": page_id,
        "title": title,
        "source_url": clean_url(original_url),
        "source_host": source_host,
        "capture_timestamp": capture_timestamp,
        "archive_capture_url": archive_capture_url,
        "content_sha256": content_sha256,
        "content_length_bytes": len(content_bytes),
        "content_summary": content_summary,
        "raw_hrefs_found": raw_href_count,
        "archive_injected_skipped": archive_injected_count,
        "unique_links_recorded": len(links),
        "links": links
    }
