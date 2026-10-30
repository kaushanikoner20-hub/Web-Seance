"""Step C: a small, polite test of the Internet Archive CDX API."""

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

CDX_URL = "https://web.archive.org/cdx/search/cdx"
USER_AGENT = "WebSeanceFeasibilityTest/0.1 (student hobby project; Hacktoberfest 2026)"

MAX_REQUESTS = 8        # hard limit for the whole run
PAUSE_SECONDS = 3       # wait between requests
TIMEOUT_SECONDS = 20    # give up on a slow request
CAPTURES_PER_URL = 3    # records to ask for per site

# Candidates only. We do NOT know yet whether the Archive has them.
MAIN_CANDIDATES = [
    "http://www.jwz.org/",
    "http://www.catb.org/~esr/",
    "http://www.zombo.com/",
    "http://www.jodi.org/",
    "http://www.w3.org/People/Berners-Lee/",
]
# Only used if fewer than 3 main candidates return records (max 2 used).
BACKUP_CANDIDATES = [
    "http://www.zompist.com/",
    "http://www.paulgraham.com/",
]

OUTPUT_FILE = Path(__file__).resolve().parent.parent / "data" / "archive_results.json"


def build_query_url(site_url):
    params = {
        "url": site_url,
        "output": "json",
        "fl": "timestamp,original,statuscode,mimetype",
        "filter": "statuscode:200",
        "from": "1996",
        "to": "2008",
        "limit": str(CAPTURES_PER_URL),
    }
    return CDX_URL + "?" + urllib.parse.urlencode(params)


def check_site(site_url):
    result = {
        "candidate_url": site_url,
        "query_url": build_query_url(site_url),
        "outcome": None,
        "http_status": None,
        "error": None,
        "captures": [],
    }
    request = urllib.request.Request(
        result["query_url"], headers={"User-Agent": USER_AGENT}
    )

    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as err:
        result["outcome"] = "http_error"
        result["http_status"] = err.code
        result["error"] = f"HTTP {err.code}: {err.reason}"
        return result
    except urllib.error.URLError as err:
        if isinstance(err.reason, TimeoutError):
            result["outcome"] = "timeout"
            result["error"] = "The request timed out."
        else:
            result["outcome"] = "network_error"
            result["error"] = f"Could not connect: {err.reason}"
        return result
    except TimeoutError:
        result["outcome"] = "timeout"
        result["error"] = "The reply took too long."
        return result
    except UnicodeDecodeError:
        result["outcome"] = "malformed_response"
        result["error"] = "Reply was not readable text."
        return result

    body = body.strip()
    if not body:
        result["outcome"] = "no_captures"
        return result

    try:
        rows = json.loads(body)
    except ValueError:
        result["outcome"] = "malformed_response"
        result["error"] = "Reply was not valid JSON."
        return result

    if not isinstance(rows, list):
        result["outcome"] = "malformed_response"
        result["error"] = "Reply JSON was not a list."
        return result

    # The first row is a header (field names). Real records start at row 2.
    for row in rows[1:]:
        if isinstance(row, list) and len(row) == 4:
            timestamp, original, status, mime = row
            result["captures"].append({
                "timestamp": timestamp,
                "original_url": original,
                "status_code": status,
                "mime_type": mime,
                "capture_url": f"https://web.archive.org/web/{timestamp}/{original}",
            })

    if result["captures"]:
        result["outcome"] = "captures_found"
    elif len(rows) <= 1:
        result["outcome"] = "no_captures"
    else:
        result["outcome"] = "malformed_response"
        result["error"] = "Rows were not in the expected shape."
    return result


def main():
    started = datetime.now(timezone.utc).isoformat(timespec="seconds")
    results = []
    stop_reason = None
    failures_in_a_row = 0
    backups_added = False
    queue = list(MAIN_CANDIDATES)

    while queue and len(results) < MAX_REQUESTS:
        if results:
            time.sleep(PAUSE_SECONDS)

        site = queue.pop(0)
        print("Checking:", site)
        result = check_site(site)
        results.append(result)
        print("   ->", result["outcome"], f"({len(result['captures'])} records)",
              result["error"] or "")

        if result["http_status"] in (403, 429):
            stop_reason = (f"Archive answered HTTP {result['http_status']} "
                           "(blocked or rate limited). Stopped on purpose, no retry.")
            break

        if result["outcome"] in ("http_error", "timeout", "network_error"):
            failures_in_a_row += 1
        else:
            failures_in_a_row = 0
        if failures_in_a_row >= 2:
            stop_reason = "Two failed requests in a row. Stopped on purpose."
            break

        if not queue and not backups_added:
            backups_added = True
            good = sum(1 for r in results if r["outcome"] == "captures_found")
            if good < 3:
                queue.extend(BACKUP_CANDIDATES[:2])

    found = [r for r in results if r["outcome"] == "captures_found"]
    empty = [r for r in results if r["outcome"] == "no_captures"]
    failed = [r for r in results if r["outcome"] not in ("captures_found", "no_captures")]
    total_records = sum(len(r["captures"]) for r in results)

    output = {
        "status": "TESTED - STOPPED EARLY" if stop_reason else "TESTED",
        "run_started_utc": started,
        "requests_made": len(results),
        "stopped_early_reason": stop_reason,
        "note": ("Real answers from the CDX API. Each capture_url was built from "
                 "the timestamp and original URL and has NOT been opened yet."),
        "results": results,
    }
    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print()
    print("===== SUMMARY =====")
    print("Requests made:", len(results), "of", MAX_REQUESTS, "allowed")
    print("Sites with records:", len(found))
    print("Sites with no records:", len(empty))
    print("Sites that failed:", len(failed))
    print("Total capture records:", total_records)
    if stop_reason:
        print("Stopped early:", stop_reason)
    print("Saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    main()