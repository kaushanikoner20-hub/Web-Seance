"""
AI Historian Module for Web Séance.
Integrates with local Ollama running Gemma 3:4b with strict evidence grounding and safety guardrails.
Enforces separation of verified archival facts from speculative AI inferences.
"""

import json
import re
import urllib.error
import urllib.request
from typing import Dict, List, Optional, Tuple

import config


class AIHistorian:
    """Manages local LLM inference via Ollama with strict evidence grounding guardrails."""

    def __init__(
        self,
        base_url: str = config.OLLAMA_BASE_URL,
        model: str = config.DEFAULT_MODEL,
        timeout: int = config.OLLAMA_TIMEOUT_SECONDS
    ):
        self.base_url = base_url
        self.model = model
        self.timeout = timeout

    def check_status(self) -> Dict:
        """
        Verifies if the local Ollama server is running and whether the required model is installed.
        Returns a detailed status report.
        """
        status = {
            "ollama_running": False,
            "model_available": False,
            "available_models": [],
            "target_model": self.model,
            "message": ""
        }
        try:
            req = urllib.request.Request(f"{self.base_url}/api/tags")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                models = [m.get("name") for m in data.get("models", [])]
                status["ollama_running"] = True
                status["available_models"] = models

                # Check if target model or variant is installed
                if any(self.model in m for m in models):
                    status["model_available"] = True
                    status["message"] = f"Local model '{self.model}' is ready."
                else:
                    status["message"] = (
                        f"Ollama is running, but model '{self.model}' was not found. "
                        f"Install it by running: `ollama pull {self.model}`"
                    )
        except urllib.error.URLError:
            status["message"] = (
                "Ollama is not running on localhost:11434. "
                "Start Ollama on your system or run: `ollama serve`"
            )
        except Exception as e:
            status["message"] = f"Unable to connect to Ollama: {str(e)}"

        return status

    def format_evidence_payload(self, page: Dict, links: List[Dict], max_links: int = 14) -> str:
        """Formats verified page and link evidence into an unambiguous text payload."""
        lines = [
            "### ARCHIVAL EVIDENCE DOSSIER",
            f"Page Identifier: {page.get('page_id')}",
            f"Original URL: {page.get('source_url')}",
            f"Archival Capture Date: {page.get('capture_timestamp', '')[:8]} (UTC: {page.get('capture_timestamp', '')})",
            f"Archived Page Title: {page.get('title')}",
            f"Content Excerpt: \"{page.get('content_summary', '')[:280]}\"",
            "",
            "VERIFIED OUTGOING HYPERLINKS EXTRACTED FROM ARCHIVED HTML:"
        ]

        if not links:
            lines.append("No outgoing hyperlinks were detected in the archived HTML of this capture.")
        else:
            # External links are most relevant for archaeological inquiries about outbound connections
            external_links = [l for l in links if l.get("scope") == "external"]
            same_site_links = [l for l in links if l.get("scope") == "same_site"]
            selected_links = external_links + same_site_links[:max(0, max_links - len(external_links))]
            selected_links = selected_links[:max_links]

            for l in selected_links:
                scope_label = "EXTERNAL" if l.get("scope") == "external" else "SAME-SITE"
                dest = l.get("destination_url")
                anchor = l.get("anchor_text", "").strip()
                anchor_part = f" (Anchor: \"{anchor}\")" if anchor and anchor != "[No anchor text]" else ""
                lines.append(f"- [{l['evidence_id']}] [{scope_label}] -> {dest}{anchor_part}")

        lines.append("")
        lines.append("END OF EVIDENCE DOSSIER.")
        return "\n".join(lines)

    def validate_response(self, response_text: str, valid_evidence_ids: List[str]) -> Dict:
        """
        Audits the AI's response to check if all cited evidence IDs exist
        and checks for evidence-grounding integrity.
        """
        cited_ids = re.findall(r"P\d+-L\d+", response_text)
        unique_cited = sorted(list(set(cited_ids)))
        invalid_citations = [eid for eid in unique_cited if eid not in valid_evidence_ids]

        mentions_insufficient = (
            "insufficient evidence" in response_text.lower()
            or "not enough evidence" in response_text.lower()
            or "unknown" in response_text.lower()
        )

        return {
            "total_citations": len(cited_ids),
            "unique_citations": unique_cited,
            "invalid_citations": invalid_citations,
            "cites_only_valid_ids": len(invalid_citations) == 0,
            "acknowledged_limits": mentions_insufficient,
            "integrity_passed": len(invalid_citations) == 0
        }

    def consult(self, question: str, page: Dict, links: List[Dict]) -> Dict:
        """
        Sends evidence and query to local Gemma 3:4b via Ollama.
        Enforces strict system prompt rules and audits citations.
        """
        status = self.check_status()
        if not status["ollama_running"]:
            return {
                "success": False,
                "error": "OLLAMA_OFFLINE",
                "message": status["message"],
                "response": None,
                "audit": None
            }
        if not status["model_available"]:
            return {
                "success": False,
                "error": "MODEL_NOT_FOUND",
                "message": status["message"],
                "response": None,
                "audit": None
            }

        evidence_text = self.format_evidence_payload(page, links)
        valid_evidence_ids = [l["evidence_id"] for l in links]

        system_instruction = (
            "You are an AI research assistant for Web Séance, a digital archaeology project investigating historical web captures.\n"
            "STRICT RULES:\n"
            "1. You must base your answer EXCLUSIVELY on the provided Archival Evidence Dossier.\n"
            "2. Never fabricate people, dates, affiliations, or URLs not present in the dossier.\n"
            "3. An outgoing hyperlink proves ONLY that a URL appeared in the archived HTML. A link DOES NOT prove the website owners knew each other, collaborated, or had a social relationship. Never make that claim without explicit text evidence.\n"
            "4. Whenever citing a hyperlink, you MUST cite its Evidence ID in brackets (e.g. [P1-L3]).\n"
            "5. Structure your response into THREE clear sections:\n"
            "   - **1. VERIFIED FACTS**: Direct facts explicitly stated in the dossier, with evidence IDs.\n"
            "   - **2. PLAUSIBLE HYPOTHESES (AI INTERPRETATION)**: Cautious inferences about subject matter or topics, clearly identified as non-definitive hypotheses.\n"
            "   - **3. MISSING INFORMATION & UNKNOWNS**: Explicitly state what cannot be determined. Use the exact phrase 'Insufficient evidence' for unknown details.\n"
            "Keep your response concise, evidence-focused, and scholarly."
        )

        full_prompt = (
            f"{system_instruction}\n\n"
            f"{evidence_text}\n\n"
            f"INVESTIGATOR QUESTION: {question}\n\n"
            "HISTORIAN ASSESSMENT:"
        )

        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,  # Low temperature for factual grounding
                "top_p": 0.9,
                "num_predict": 350
            }
        }

        try:
            req_data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                f"{self.base_url}/api/generate",
                data=req_data,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                resp_json = json.loads(resp.read().decode("utf-8"))
                raw_answer = resp_json.get("response", "").strip()

            audit = self.validate_response(raw_answer, valid_evidence_ids)

            return {
                "success": True,
                "error": None,
                "response": raw_answer,
                "model": self.model,
                "audit": audit,
                "evidence_ids_provided": valid_evidence_ids
            }
        except TimeoutError:
            return {
                "success": False,
                "error": "TIMEOUT",
                "message": f"Local model did not respond within {self.timeout} seconds.",
                "response": None,
                "audit": None
            }
        except Exception as e:
            return {
                "success": False,
                "error": "INFERENCE_ERROR",
                "message": f"Error running local inference: {str(e)}",
                "response": None,
                "audit": None
            }
