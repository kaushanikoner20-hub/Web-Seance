"""
Data Collection Script for Web Séance.
Retrieves real historical captures from the Internet Archive for 5 seminal early web pages,
extracts authentic outgoing hyperlinks, and generates traceable evidence records.
"""

import json
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.archive_client import ArchiveClient
from core.html_extractor import extract_page_evidence
import config

TARGET_CAPTURES = [
    {
        "page_id": "P1",
        "url": "http://www.jwz.org:80/",
        "timestamp": "19981202075235",
        "name": "Jamie Zawinski (Netscape & Open Source Pioneer)"
    },
    {
        "page_id": "P2",
        "url": "http://www.catb.org:80/~esr/",
        "timestamp": "20030124110141",
        "name": "Eric Raymond's Home Page (Open Source Initiative)"
    },
    {
        "page_id": "P3",
        "url": "http://www.zombo.com:80/",
        "timestamp": "19991128095921",
        "name": "ZOMBO.com (Early Flash & Audio Legend)"
    },
    {
        "page_id": "P4",
        "url": "http://www.jodi.org:80/",
        "timestamp": "19961108051821",
        "name": "JODI.org (Seminal Early Net Art Collective)"
    },
    {
        "page_id": "P5",
        "url": "http://www.w3.org:80/People/Berners-Lee/",
        "timestamp": "19970605014858",
        "name": "Tim Berners-Lee (Inventor of the World Wide Web)"
    }
]


def main():
    print("=" * 60)
    print("WEB SÉANCE — ARCHIVAL EVIDENCE COLLECTION")
    print("=" * 60)

    client = ArchiveClient()
    pages_output = []
    links_output = []

    for item in TARGET_CAPTURES:
        pid = item["page_id"]
        url = item["url"]
        ts = item["timestamp"]
        label = item["name"]

        print(f"\n[+] Fetching {pid} ({label})...")
        print(f"    URL: {url} @ {ts}")
        archive_url = f"https://web.archive.org/web/{ts}/{url}"

        success, html_text, err = client.fetch_raw_capture(ts, url)
        if not success:
            print(f"    [!] Error fetching capture: {err}")
            continue

        print(f"    Downloaded {len(html_text)} characters. Extracting evidence...")
        evidence = extract_page_evidence(
            html_content=html_text,
            original_url=url,
            page_id=pid,
            capture_timestamp=ts,
            archive_capture_url=archive_url
        )

        page_meta = {
            "page_id": pid,
            "title": evidence["title"],
            "historical_figure": label,
            "source_url": evidence["source_url"],
            "source_host": evidence["source_host"],
            "capture_timestamp": ts,
            "archive_capture_url": archive_url,
            "content_sha256": evidence["content_sha256"],
            "content_length_bytes": evidence["content_length_bytes"],
            "content_summary": evidence["content_summary"],
            "raw_hrefs_found": evidence["raw_hrefs_found"],
            "archive_injected_skipped": evidence["archive_injected_skipped"],
            "unique_links_recorded": evidence["unique_links_recorded"],
            "retrieval_status": "AUTHENTIC_INTERNET_ARCHIVE_RECORD"
        }

        pages_output.append(page_meta)

        page_entry = dict(page_meta)
        page_entry["links"] = evidence["links"]
        links_output.append(page_entry)

        print(f"    Title: {evidence['title']}")
        print(f"    Extracted links: {evidence['unique_links_recorded']}")

    # Save to disk
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)

    pages_file = config.ARCHIVE_PAGES_FILE
    with open(pages_file, "w", encoding="utf-8") as f:
        json.dump({
            "version": "1.0",
            "curation": "Seminal Early Web Pioneers & Artifacts",
            "total_pages": len(pages_output),
            "pages": pages_output
        }, f, indent=2, ensure_ascii=False)
    print(f"\n[OK] Saved {len(pages_output)} pages to {pages_file}")

    links_file = config.LINK_EVIDENCE_FILE
    total_links = sum(len(p["links"]) for p in links_output)
    with open(links_file, "w", encoding="utf-8") as f:
        json.dump({
            "status": "VERIFIED_ARCHIVAL_EVIDENCE",
            "last_updated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "note": "Every link record originates from actual extracted HTML of the specified historical capture. No synthetic data. No AI inference in link extraction.",
            "total_pages": len(links_output),
            "total_links_recorded": total_links,
            "pages": links_output
        }, f, indent=2, ensure_ascii=False)
    print(f"[OK] Saved {total_links} verified links to {links_file}")
    print("=" * 60)


if __name__ == "__main__":
    main()
