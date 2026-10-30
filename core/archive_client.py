"""
Internet Archive Client Module for Web Séance.
Safely queries the CDX API and fetches authentic historical page HTML via raw Wayback replay.
Includes polite rate limiting, timeout safety, and comprehensive error handling.
"""

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Dict, List, Optional, Tuple

import config


class ArchiveClient:
    """Polite client for querying CDX API and fetching raw archived captures."""

    def __init__(
        self,
        user_agent: str = config.ARCHIVE_USER_AGENT,
        timeout: int = config.CDX_TIMEOUT_SECONDS,
        request_delay: float = config.POLITE_REQUEST_DELAY
    ):
        self.user_agent = user_agent
        self.timeout = timeout
        self.request_delay = request_delay
        self.last_request_time = 0.0

    def _throttle(self):
        """Enforce polite pause between consecutive requests to avoid overwhelming the archive."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.request_delay:
            time.sleep(self.request_delay - elapsed)
        self.last_request_time = time.time()

    def query_cdx(
        self,
        url: str,
        limit: int = 5,
        from_year: str = "1995",
        to_year: str = "2008"
    ) -> Dict:
        """
        Queries the Internet Archive CDX Server for historical captures of a URL.
        Returns a dictionary with status, captures found, and metadata.
        """
        self._throttle()

        params = {
            "url": url,
            "output": "json",
            "fl": "timestamp,original,statuscode,mimetype,digest,length",
            "filter": "statuscode:200",
            "from": from_year,
            "to": to_year,
            "limit": str(limit),
        }
        query_url = f"{config.CDX_API_URL}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(query_url, headers={"User-Agent": self.user_agent})

        result = {
            "candidate_url": url,
            "query_url": query_url,
            "status": "pending",
            "http_status": None,
            "error": None,
            "captures": []
        }

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                result["http_status"] = resp.status
                body = resp.read().decode("utf-8", errors="replace").strip()
        except urllib.error.HTTPError as err:
            result["status"] = "error"
            result["http_status"] = err.code
            result["error"] = f"HTTP {err.code}: {err.reason}"
            return result
        except urllib.error.URLError as err:
            result["status"] = "error"
            result["error"] = f"Connection error: {err.reason}"
            return result
        except TimeoutError:
            result["status"] = "error"
            result["error"] = "Archive request timed out."
            return result
        except Exception as err:
            result["status"] = "error"
            result["error"] = str(err)
            return result

        if not body:
            result["status"] = "no_captures"
            return result

        try:
            rows = json.loads(body)
        except Exception:
            result["status"] = "malformed_response"
            result["error"] = "CDX response was not valid JSON."
            return result

        if not isinstance(rows, list) or len(rows) <= 1:
            result["status"] = "no_captures"
            return result

        header = rows[0]
        for row in rows[1:]:
            item = dict(zip(header, row))
            ts = item.get("timestamp", "")
            orig = item.get("original", url)
            capture_url = f"https://web.archive.org/web/{ts}/{orig}"
            raw_url = f"https://web.archive.org/web/{ts}id_/{orig}"
            result["captures"].append({
                "timestamp": ts,
                "original_url": orig,
                "status_code": item.get("statuscode", "200"),
                "mime_type": item.get("mimetype", "text/html"),
                "digest": item.get("digest", ""),
                "length": item.get("length", ""),
                "capture_url": capture_url,
                "raw_fetch_url": raw_url
            })

        result["status"] = "captures_found" if result["captures"] else "no_captures"
        return result

    def fetch_raw_capture(
        self,
        timestamp: str,
        original_url: str,
        timeout: Optional[int] = None
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Fetches the raw, unadorned HTML of an archived page using the 'id_' modifier.
        Returns: (success: bool, html_content: str, error_message: Optional[str])
        """
        self._throttle()
        fetch_timeout = timeout or config.CAPTURE_TIMEOUT_SECONDS
        raw_url = f"https://web.archive.org/web/{timestamp}id_/{original_url}"
        req = urllib.request.Request(raw_url, headers={"User-Agent": self.user_agent})

        try:
            with urllib.request.urlopen(req, timeout=fetch_timeout) as resp:
                content_bytes = resp.read()
                # Attempt to determine charset from headers
                charset = resp.headers.get_content_charset() or "utf-8"
                try:
                    html_text = content_bytes.decode(charset)
                except (UnicodeDecodeError, LookupError):
                    html_text = content_bytes.decode("utf-8", errors="replace")
                return True, html_text, None
        except urllib.error.HTTPError as err:
            return False, "", f"HTTP {err.code}: {err.reason}"
        except urllib.error.URLError as err:
            return False, "", f"Network error: {err.reason}"
        except TimeoutError:
            return False, "", "Timed out retrieving archived page."
        except Exception as err:
            return False, "", str(err)
