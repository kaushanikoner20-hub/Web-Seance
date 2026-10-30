"""
Unit tests for core/ai_historian.py.
Verifies prompt construction, citation auditing, hallucination detection, and error handling.
"""

import unittest
from core.ai_historian import AIHistorian


class TestAIHistorian(unittest.TestCase):

    def setUp(self):
        self.historian = AIHistorian()
        self.sample_page = {
            "page_id": "P1",
            "source_url": "http://www.jwz.org/",
            "capture_timestamp": "19981202075235",
            "title": "Jamie Zawinski",
            "content_summary": "Hacks, gruntles, and early Netscape memories."
        }
        self.sample_links = [
            {
                "evidence_id": "P1-L1",
                "scope": "same_site",
                "destination_url": "http://www.jwz.org/contact.html",
                "anchor_text": "Contact"
            },
            {
                "evidence_id": "P1-L2",
                "scope": "external",
                "destination_url": "http://www.dnalounge.com/",
                "anchor_text": "DNA Lounge"
            }
        ]

    def test_format_evidence_payload(self):
        payload = self.historian.format_evidence_payload(self.sample_page, self.sample_links)
        self.assertIn("ARCHIVAL EVIDENCE DOSSIER", payload)
        self.assertIn("P1", payload)
        self.assertIn("Jamie Zawinski", payload)
        self.assertIn("P1-L1", payload)
        self.assertIn("P1-L2", payload)
        self.assertIn("http://www.dnalounge.com/", payload)

    def test_validate_response_valid_citations(self):
        valid_ids = ["P1-L1", "P1-L2"]
        ai_response = (
            "1. VERIFIED FACTS: The page links to contact info [P1-L1] and DNA Lounge [P1-L2].\n"
            "2. HYPOTHESES: The author may be affiliated with the venue.\n"
            "3. UNKNOWNS: Insufficient evidence to determine the exact role or date of founding."
        )
        audit = self.historian.validate_response(ai_response, valid_ids)
        self.assertTrue(audit["cites_only_valid_ids"])
        self.assertTrue(audit["acknowledged_limits"])
        self.assertTrue(audit["integrity_passed"])
        self.assertEqual(len(audit["invalid_citations"]), 0)

    def test_validate_response_catches_hallucinated_citations(self):
        valid_ids = ["P1-L1", "P1-L2"]
        # AI hallucinating an unprovided ID P1-L99
        ai_response = "The page mentions a secret link [P1-L99] to a forum."
        audit = self.historian.validate_response(ai_response, valid_ids)
        self.assertFalse(audit["cites_only_valid_ids"])
        self.assertFalse(audit["integrity_passed"])
        self.assertIn("P1-L99", audit["invalid_citations"])

    def test_status_check(self):
        status = self.historian.check_status()
        self.assertIn("ollama_running", status)
        self.assertIn("model_available", status)
        self.assertIn("available_models", status)


if __name__ == "__main__":
    unittest.main()
