"""
Unit tests for core/html_extractor.py.
Verifies URL normalization, link scope detection, archive toolbar filtering, and evidence ID assignment.
"""

import unittest
from core.html_extractor import (
    clean_url,
    extract_page_evidence,
    is_archive_injected_url,
    normalize_host
)


class TestHTMLExtractor(unittest.TestCase):

    def test_normalize_host(self):
        self.assertEqual(normalize_host("http://www.catb.org/~esr/"), "catb.org")
        self.assertEqual(normalize_host("http://catb.org:80/~esr/"), "catb.org")
        self.assertEqual(normalize_host("https://sub.domain.example.com/path"), "sub.domain.example.com")
        self.assertEqual(normalize_host("invalid-url"), "")

    def test_clean_url(self):
        self.assertEqual(clean_url("http://example.com:80/page.html#anchor"), "http://example.com/page.html")
        self.assertEqual(clean_url("https://example.com:443/page.html"), "https://example.com/page.html")
        self.assertEqual(clean_url("http://example.com/page?q=1#top"), "http://example.com/page?q=1")

    def test_is_archive_injected_url(self):
        self.assertTrue(is_archive_injected_url("https://web.archive.org/web/19981202/http://example.com"))
        self.assertTrue(is_archive_injected_url("/web/19981202075235js_/http://example.com"))
        self.assertTrue(is_archive_injected_url("//web.archive.org/static/css/banner.css"))
        self.assertFalse(is_archive_injected_url("http://opensource.org/licenses"))
        self.assertFalse(is_archive_injected_url("http://www.cern.ch/"))

    def test_extract_page_evidence_basic(self):
        sample_html = """
        <!DOCTYPE html>
        <html>
        <head><title>Pioneer Test Page</title></head>
        <body>
            <h1>Welcome to my website</h1>
            <p>This is a personal page from 1997 dedicated to open protocols.</p>
            <a href="about.html">About Me</a>
            <a href="/projects/index.html">My Projects</a>
            <a href="http://www.w3.org/History.html">W3 History</a>
            <a href="mailto:author@example.com">Send Email</a>
            <a href="javascript:void(0)">Click me</a>
            <a href="#section2">Jump to section</a>
            <a href="https://web.archive.org/web/2000/http://archive.org">Wayback Link</a>
        </body>
        </html>
        """
        evidence = extract_page_evidence(
            html_content=sample_html,
            original_url="http://pioneer.example.org:80/index.html",
            page_id="P99",
            capture_timestamp="19970512120000",
            archive_capture_url="https://web.archive.org/web/19970512120000/http://pioneer.example.org/"
        )

        self.assertEqual(evidence["page_id"], "P99")
        self.assertEqual(evidence["title"], "Pioneer Test Page")
        self.assertTrue("personal page from 1997" in evidence["content_summary"])
        self.assertIsNotNone(evidence["content_sha256"])

        links = evidence["links"]
        # Expected links: about.html (same-site), /projects/index.html (same-site), w3.org (external)
        # Skipped: mailto, javascript, #section2, archive injected
        self.assertEqual(len(links), 3)

        self.assertEqual(links[0]["evidence_id"], "P99-L1")
        self.assertEqual(links[0]["destination_url"], "http://pioneer.example.org/about.html")
        self.assertEqual(links[0]["scope"], "same_site")
        self.assertEqual(links[0]["anchor_text"], "About Me")
        self.assertFalse(links[0]["ai_inferred"])

        self.assertEqual(links[1]["evidence_id"], "P99-L2")
        self.assertEqual(links[1]["destination_url"], "http://pioneer.example.org/projects/index.html")
        self.assertEqual(links[1]["scope"], "same_site")

        self.assertEqual(links[2]["evidence_id"], "P99-L3")
        self.assertEqual(links[2]["destination_url"], "http://www.w3.org/History.html")
        self.assertEqual(links[2]["scope"], "external")
        self.assertEqual(links[2]["destination_host"], "w3.org")


if __name__ == "__main__":
    unittest.main()
