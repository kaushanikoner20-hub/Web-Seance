"""
Unit tests for core/evidence_store.py.
Verifies evidence persistence, schema compliance, traceability, and graph projection.
"""

import unittest
from core.evidence_store import EvidenceStore


class TestEvidenceStore(unittest.TestCase):

    def setUp(self):
        self.store = EvidenceStore()

    def test_store_loads_pages_and_links(self):
        pages = self.store.get_all_pages()
        self.assertGreaterEqual(len(pages), 4, "Should have loaded at least 4 archived pages.")

        all_links = self.store.all_links
        self.assertGreaterEqual(len(all_links), 20, "Should have loaded historical links.")

    def test_evidence_integrity_schema(self):
        """Every link record must contain the mandated traceability fields."""
        required_fields = [
            "evidence_id",
            "source_page_id",
            "source_url",
            "destination_url",
            "capture_timestamp",
            "archive_capture_url",
            "extraction_method",
            "ai_inferred"
        ]
        for link in self.store.all_links:
            for field in required_fields:
                self.assertIn(field, link, f"Link {link.get('evidence_id')} missing field: {field}")
            # AI inferred must be False for archival records
            self.assertFalse(link["ai_inferred"], f"Link {link['evidence_id']} has ai_inferred=True")
            # Evidence ID must follow P#-L# pattern
            self.assertRegex(link["evidence_id"], r"^P\d+-L\d+$")

    def test_page_filtering_and_scope(self):
        # P2 is Eric Raymond's page which has both same-site and external links
        p2_links = self.store.get_links_for_page("P2")
        self.assertGreater(len(p2_links), 0)

        external_links = self.store.get_links_for_page("P2", scope="external")
        same_site_links = self.store.get_links_for_page("P2", scope="same_site")

        self.assertEqual(len(p2_links), len(external_links) + len(same_site_links))
        self.assertGreater(len(external_links), 0)

    def test_evidence_record_lookup(self):
        first_link = self.store.all_links[0]
        eid = first_link["evidence_id"]
        record = self.store.get_evidence_record(eid)
        self.assertIsNotNone(record)
        self.assertEqual(record["evidence_id"], eid)

    def test_graph_projection(self):
        graph = self.store.get_connection_graph()
        self.assertIn("nodes", graph)
        self.assertIn("edges", graph)
        self.assertGreater(len(graph["nodes"]), 0)

        # Every edge must have supporting evidence IDs
        for edge in graph["edges"]:
            self.assertIn("evidence_ids", edge)
            self.assertGreater(len(edge["evidence_ids"]), 0, "Graph edges must have supporting evidence IDs.")
            # Verify evidence IDs actually exist
            for eid in edge["evidence_ids"]:
                self.assertIsNotNone(self.store.get_evidence_record(eid))


if __name__ == "__main__":
    unittest.main()
