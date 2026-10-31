"""
Evidence Store Module for Web Séance.
Maintains verified historical page records and extracted outgoing hyperlink evidence.
Ensures strict traceability: every link has a unique evidence ID pointing to its capture.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import config


class EvidenceStore:
    """Repository for archival evidence with support for queries, graph projections, and persistence."""

    def __init__(
        self,
        pages_file: Path = config.ARCHIVE_PAGES_FILE,
        links_file: Path = config.LINK_EVIDENCE_FILE
    ):
        self.pages_file = pages_file
        self.links_file = links_file
        self.pages: Dict[str, Dict] = {}
        self.links_by_page: Dict[str, List[Dict]] = {}
        self.all_links: List[Dict] = []
        self.evidence_id_index: Dict[str, Dict] = {}
        self.load()

    
        """Loads evidence from disk if present."""
        self.pages = {}
        self.links_by_page = {}
        self.all_links = []
        self.evidence_id_index = {}

        # 1. Load pages file if exists
        if self.pages_file.exists():
            try:
                with open(self.pages_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for p in data.get("pages", []):
                        pid = p["page_id"]
                        self.pages[pid] = p
            except Exception as e:
                print(f"Warning: Failed to load {self.pages_file}: {e}")

        # 2. Load link evidence file
        if self.links_file.exists():
            try:
                with open(self.links_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for p in data.get("pages", []):
                        pid = p.get("page_id")
                        if not pid:
                            continue
                        # If page metadata not already loaded, populate from link evidence
                        if pid not in self.pages:
                            self.pages[pid] = {
                                "page_id": pid,
                                "title": p.get("title", "Untitled Page"),
                                "source_url": p.get("source_url", ""),
                                "capture_timestamp": p.get("capture_timestamp", ""),
                                "archive_capture_url": p.get("archive_capture_url") or p.get("fetch_url", ""),
                                "content_sha256": p.get("content_sha256", ""),
                                "content_summary": p.get("content_summary", ""),
                                "unique_links_recorded": len(p.get("links", []))
                            }
                        
                        page_links = []
                        for l in p.get("links", []):
                            # Ensure required fields
                            evidence_id = l.get("evidence_id")
                            if not evidence_id:
                                continue
                            link_record = {
                                "evidence_id": evidence_id,
                                "source_page_id": pid,
                                "source_url": l.get("source_url", self.pages[pid]["source_url"]),
                                "destination_url": l.get("destination_url", ""),
                                "destination_host": l.get("destination_host", ""),
                                "anchor_text": l.get("anchor_text", ""),
                                "scope": l.get("scope", "external"),
                                "capture_timestamp": l.get("capture_timestamp", self.pages[pid]["capture_timestamp"]),
                                "archive_capture_url": l.get("archive_capture_url", self.pages[pid]["archive_capture_url"]),
                                "link_type": l.get("link_type", "hyperlink_in_archived_html"),
                                "extraction_method": l.get("extraction_method", "html_parser"),
                                "ai_inferred": False
                            }
                            page_links.append(link_record)
                            self.all_links.append(link_record)
                            self.evidence_id_index[evidence_id] = link_record
                        self.links_by_page[pid] = page_links
            except Exception as e:
                print(f"Warning: Failed to load {self.links_file}: {e}")

    def save(self):
        """Persists pages and link evidence to disk."""
        self.pages_file.parent.mkdir(parents=True, exist_ok=True)
        self.links_file.parent.mkdir(parents=True, exist_ok=True)

        pages_data = {
            "version": "1.0",
            "total_pages": len(self.pages),
            "pages": list(self.pages.values())
        }
        with open(self.pages_file, "w", encoding="utf-8") as f:
            json.dump(pages_data, f, indent=2, ensure_ascii=False)

        links_data = {
            "status": "VERIFIED_EVIDENCE",
            "note": "Each link record originates strictly from extracted HTML of the specified historical capture. Zero AI inference.",
            "pages": []
        }
        for pid, page_info in self.pages.items():
            links = self.links_by_page.get(pid, [])
            page_entry = dict(page_info)
            page_entry["links"] = links
            links_data["pages"].append(page_entry)

        with open(self.links_file, "w", encoding="utf-8") as f:
            json.dump(links_data, f, indent=2, ensure_ascii=False)

    def add_page_evidence(self, page_dict: Dict):
        """Adds a newly extracted page and its links into the evidence store and saves."""
        pid = page_dict["page_id"]
        links = page_dict.get("links", [])

        # Store page record
        self.pages[pid] = {
            "page_id": pid,
            "title": page_dict.get("title", "Untitled"),
            "source_url": page_dict.get("source_url", ""),
            "source_host": page_dict.get("source_host", ""),
            "capture_timestamp": page_dict.get("capture_timestamp", ""),
            "archive_capture_url": page_dict.get("archive_capture_url", ""),
            "content_sha256": page_dict.get("content_sha256", ""),
            "content_length_bytes": page_dict.get("content_length_bytes", 0),
            "content_summary": page_dict.get("content_summary", ""),
            "unique_links_recorded": len(links)
        }

        # Store links
        self.links_by_page[pid] = links
        for l in links:
            eid = l["evidence_id"]
            self.evidence_id_index[eid] = l
            # Remove old link with same eid if present
            self.all_links = [old for old in self.all_links if old["evidence_id"] != eid]
            self.all_links.append(l)

        self.save()

    def get_all_pages(self) -> List[Dict]:
        """Returns all archived pages ordered by ID."""
        return sorted(list(self.pages.values()), key=lambda p: p["page_id"])

    def get_page(self, page_id: str) -> Optional[Dict]:
        """Returns metadata for a specific page."""
        return self.pages.get(page_id)

    def get_links_for_page(self, page_id: str, scope: Optional[str] = None) -> List[Dict]:
        """Returns outgoing hyperlinks for a given page, optionally filtered by scope."""
        links = self.links_by_page.get(page_id, [])
        if scope:
            return [l for l in links if l.get("scope") == scope]
        return links

    def get_evidence_record(self, evidence_id: str) -> Optional[Dict]:
        """Retrieves a single link evidence record by its unique evidence ID."""
        return self.evidence_id_index.get(evidence_id)

    def get_stats(self) -> Dict:
        """Returns overall statistical summary of the evidence collection."""
        total_links = len(self.all_links)
        external_links = [l for l in self.all_links if l.get("scope") == "external"]
        same_site_links = [l for l in self.all_links if l.get("scope") == "same_site"]
        unique_dest_hosts = set(l.get("destination_host") for l in external_links if l.get("destination_host"))

        timestamps = [p.get("capture_timestamp") for p in self.pages.values() if p.get("capture_timestamp")]
        earliest = min(timestamps) if timestamps else "N/A"
        latest = max(timestamps) if timestamps else "N/A"

        return {
            "total_pages": len(self.pages),
            "total_links": total_links,
            "external_links_count": len(external_links),
            "same_site_links_count": len(same_site_links),
            "unique_external_domains": len(unique_dest_hosts),
            "earliest_timestamp": earliest,
            "latest_timestamp": latest
        }

    def get_connection_graph(self) -> Dict:
        """
        Builds a verified relationship graph where:
        - Nodes represent either archived source pages or target external domains.
        - Edges represent verified outgoing hyperlinks extracted from HTML.
        - Every edge contains the list of supporting evidence IDs.
        No speculative edges are ever created.
        """
        nodes = []
        edges = []
        node_ids = set()

        # 1. Source page nodes
        for pid, page in self.pages.items():
            node_id = f"source:{pid}"
            nodes.append({
                "id": node_id,
                "label": f"{pid}: {page.get('title', pid)[:22]}",
                "full_title": page.get("title", ""),
                "type": "source_page",
                "url": page.get("source_url", ""),
                "capture_date": page.get("capture_timestamp", "")[:8],
                "color": "#00ff88",
                "size": 25
            })
            node_ids.add(node_id)

        # 2. Aggregated external domain targets
        target_domain_map: Dict[str, Dict] = {}

        for l in self.all_links:
            if l.get("scope") != "external":
                continue
            dest_host = l.get("destination_host")
            if not dest_host:
                continue

            target_node_id = f"target:{dest_host}"
            if target_node_id not in node_ids:
                nodes.append({
                    "id": target_node_id,
                    "label": dest_host,
                    "type": "target_domain",
                    "color": "#38bdf8",
                    "size": 15
                })
                node_ids.add(target_node_id)

            edge_key = (f"source:{l['source_page_id']}", target_node_id)
            if edge_key not in target_domain_map:
                target_domain_map[edge_key] = {
                    "source": edge_key[0],
                    "target": edge_key[1],
                    "evidence_ids": [],
                    "sample_urls": [],
                    "link_count": 0
                }
            target_domain_map[edge_key]["evidence_ids"].append(l["evidence_id"])
            target_domain_map[edge_key]["link_count"] += 1
            if len(target_domain_map[edge_key]["sample_urls"]) < 3:
                target_domain_map[edge_key]["sample_urls"].append(l["destination_url"])

        for edge_info in target_domain_map.values():
            edges.append(edge_info)

        return {
            "nodes": nodes,
            "edges": edges,
            "total_connections": len(edges)
        }
