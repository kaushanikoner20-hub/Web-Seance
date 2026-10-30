"""Step D: fetch a few archived pages and extract their real outgoing links."""

import hashlib
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

USER_AGENT = "WebSeanceFeasibilityTest/0.1 (student hobby project; Hacktoberfest 2026)"

MAX_PAGES = 4            # pages to fetch in total
PAUSE_SECONDS = 3        # wait between requests
TIMEOUT_SECONDS = 25     # give up on a slow request
MAX_BYTES = 500_000      # read at most 500 KB per page
MAX_LINKS_RECORDED = 100 # links saved per page

ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = ROOT / "data" / "archive_results.json"
OUTPUT_FILE = ROOT / "data" / "link_evidence.json"

SKIP_PREFIXES = ("mailto:", "javascript:", "tel:", "data:", "#")


class PageParser(HTMLParser):
    """Reads HTML and collects the page title and every <a href="...">."""

    def __init__(self):
        super().__init__()
        self.title = ""
        self.in_title = False
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self.in_title = True
        elif tag == "a":
            for name, value in attrs:
                if name == "href" and value:
                    self.hrefs.append(value.strip())

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data


def load_captures():
    """Pick the first capture of each site that Step C found."""
    if not INPUT_FILE.exists():
        print("data/archive_results.json is missing. Run Step C first.")
        return None
    try:
        with open(INPUT_FILE, encoding="utf-8") as f:
            data = json.load(f)
    except ValueError:
        print("data/archive_results.json is not valid JSON.")
        return None
    if str(data.get("status", "")).startswith("NOT TESTED"):
        print("Step C has not been run yet. Nothing to inspect.")
        return None

    captures = []
    for result in data.get("results", []):
        if result.get("outcome") == "captures_found" and result.get("captures"):
            captures.append(result["captures"][0])
    return captures[:MAX_PAGES]


def extract_links(html_text, original_url):
    parser = PageParser()
    parser.feed(html_text)
    parser.close()

    own_host = (urllib.parse.urlparse(original_url).hostname or "").removeprefix("www.")
    seen = set()
    links = []
    archive_skipped = 0

    for href in parser.hrefs:
        if href.lower().startswith(SKIP_PREFIXES):
            continue
        try:
            absolute = urllib.parse.urljoin(original_url, href).split("#")[0]
            parts = urllib.parse.urlparse(absolute)
        except ValueError:
            continue
        if parts.scheme not in ("http", "https"):
            continue

        host = parts.hostname or ""
        # Links that point back into the archive are archive-made, not original.
        if host.endswith("archive.org") and parts.path.startswith("/web/"):
            archive_skipped += 1
            continue
        if absolute in seen:
            continue
        seen.add(absolute)

        scope = "same_site" if host.removeprefix("www.") == own_host else "external"
        links.append({"destination_url": absolute, "scope": scope})

    title = " ".join(parser.title.split())
    return title, links, len(parser.hrefs), archive_skipped


def inspect_capture(page_number, capture):
    page_id = f"P{page_number}"
    original = capture["original_url"]
    timestamp = capture["timestamp"]
    record = {
        "page_id": page_id,
        "source_url": original,
        "capture_timestamp": timestamp,
        "fetch_url": f"https://web.archive.org/web/{timestamp}id_/{original}",
        "final_url": None,
        "outcome": None,
        "http_status": None,
        "error": None,
        "content_type": None,
        "content_sha256": None,
        "title": None,
        "hrefs_found_in_html": 0,
        "archive_generated_links_skipped": 0,
        "unique_links_total": 0,
        "links_recorded": 0,
        "links": [],
        "limitations": [],
    }

    request = urllib.request.Request(
        record["fetch_url"], headers={"User-Agent": USER_AGENT}
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            record["final_url"] = response.geturl()
            record["http_status"] = response.status
            record["content_type"] = response.headers.get("Content-Type", "")
            charset = response.headers.get_content_charset() or "utf-8"
            raw = response.read(MAX_BYTES + 1)
    except urllib.error.HTTPError as err:
        record["outcome"] = "http_error"
        record["http_status"] = err.code
        record["error"] = f"HTTP {err.code}: {err.reason}"
        return record
    except urllib.error.URLError as err:
        if isinstance(err.reason, TimeoutError):
            record["outcome"] = "timeout"
            record["error"] = "The request timed out."
        else:
            record["outcome"] = "network_error"
            record["error"] = f"Could not connect: {err.reason}"
        return record
    except TimeoutError:
        record["outcome"] = "timeout"
        record["error"] = "The reply took too long."
        return record

    if not raw:
        record["outcome"] = "empty_response"
        record["error"] = "The archive returned an empty page."
        return record

    if len(raw) > MAX_BYTES:
        raw = raw[:MAX_BYTES]
        record["limitations"].append("Page larger than 500 KB; only the start was read.")
    record["content_sha256"] = hashlib.sha256(raw).hexdigest()

    if "html" not in record["content_type"].lower():
        record["outcome"] = "not_html"
        record["limitations"].append("Content type is not HTML, so no links were extracted.")
        return record

    if timestamp not in (record["final_url"] or ""):
        record["limitations"].append(
            "The archive redirected to a different capture than the one requested.")

    try:
        html_text = raw.decode(charset, errors="replace")
    except LookupError:
        html_text = raw.decode("utf-8", errors="replace")

    try:
        title, links, href_count, archive_skipped = extract_links(html_text, original)
    except Exception as err:  # a broken page should not crash the whole test
        record["outcome"] = "parse_error"
        record["error"] = f"Could not read the HTML: {err}"
        return record

    record["outcome"] = "ok"
    record["title"] = title or None
    record["hrefs_found_in_html"] = href_count
    record["archive_generated_links_skipped"] = archive_skipped
    record["unique_links_total"] = len(links)
    if not links:
        record["limitations"].append(
            "No links found; the page may use frames, images or scripts for navigation.")

    for number, link in enumerate(links[:MAX_LINKS_RECORDED], start=1):
        record["links"].append({
            "evidence_id": f"{page_id}-L{number}",
            "link_type": "hyperlink_in_archived_html",
            "ai_inferred": False,
            "destination_url": link["destination_url"],
            "scope": link["scope"],
        })
    record["links_recorded"] = len(record["links"])
    if len(links) > MAX_LINKS_RECORDED:
        record["limitations"].append(
            f"Only the first {MAX_LINKS_RECORDED} of {len(links)} links were saved.")
    return record


def main():
    captures = load_captures()
    if not captures:
        return

    started = datetime.now(timezone.utc).isoformat(timespec="seconds")
    pages = []
    stop_reason = None
    failures_in_a_row = 0

    for number, capture in enumerate(captures, start=1):
        if pages:
            time.sleep(PAUSE_SECONDS)
        print(f"Fetching P{number}:", capture["original_url"], capture["timestamp"])
        record = inspect_capture(number, capture)
        pages.append(record)
        print("   ->", record["outcome"], record["error"] or "")

        if record["http_status"] in (403, 429):
            stop_reason = (f"Archive answered HTTP {record['http_status']}. "
                           "Stopped on purpose, no retry.")
            break
        if record["outcome"] in ("http_error", "timeout", "network_error"):
            failures_in_a_row += 1
        else:
            failures_in_a_row = 0
        if failures_in_a_row >= 2:
            stop_reason = "Two failed requests in a row. Stopped on purpose."
            break

    output = {
        "status": "TESTED - STOPPED EARLY" if stop_reason else "TESTED",
        "run_started_utc": started,
        "pages_attempted": len(pages),
        "stopped_early_reason": stop_reason,
        "note": ("Each link shows only that the URL appeared in the archived HTML of "
                 "that page. It does NOT show the site owners knew each other. "
                 "Nothing in this file is AI-inferred."),
        "pages": pages,
    }
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    ok_pages = [p for p in pages if p["outcome"] == "ok"]
    total_links = sum(p["unique_links_total"] for p in ok_pages)
    external = sum(1 for p in ok_pages for l in p["links"] if l["scope"] == "external")

    print()
    print("===== SUMMARY =====")
    print("Pages attempted:", len(pages))
    print("Pages read OK:", len(ok_pages))
    print("Pages with a problem:", len(pages) - len(ok_pages))
    print("Unique links found (pages read OK):", total_links)
    print("External links among the saved ones:", external)
    for p in pages:
        title = (p["title"] or "(no title)")[:50].encode("ascii", "replace").decode()
        print(f"  {p['page_id']}: {p['outcome']}, {p['unique_links_total']} links, title: {title}")
    if stop_reason:
        print("Stopped early:", stop_reason)
    print("Saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    main()