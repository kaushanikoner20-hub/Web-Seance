"""Step E: ask local Gemma to explain a tiny amount of REAL evidence."""

import json
import re
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "gemma3:4b"
TIMEOUT_SECONDS = 300  # the first answer can be slow while the model loads

ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = ROOT / "data" / "link_evidence.json"
OUTPUT_FILE = ROOT / "data" / "gemma_test_result.json"

SYSTEM_RULES = """You are a careful research assistant. You will be given EVIDENCE about one archived web page.

Rules:
1. Use ONLY the evidence. Do not use outside knowledge about people, websites or history.
2. Cite evidence IDs for every claim: the page ID (for example P2) for page facts, and link IDs (for example P2-L3) for links.
3. A link only shows that a web address appeared in the page's HTML in that capture. It does NOT prove the site owners knew each other or had any relationship.
4. If something cannot be known from the evidence, write "insufficient evidence".
5. Do NOT invent dates, people, communities or relationships.

Answer in exactly three sections:
CONFIRMED FACTS (only what the evidence directly shows)
POSSIBLE INTERPRETATIONS (at most 3, each clearly marked as an interpretation, not a fact)
WHAT IS NOT KNOWN"""


def load_evidence_page():
    if not INPUT_FILE.exists():
        print("data/link_evidence.json is missing. Run Step D first.")
        return None
    try:
        with open(INPUT_FILE, encoding="utf-8") as f:
            data = json.load(f)
    except ValueError:
        print("data/link_evidence.json is not valid JSON.")
        return None

    best, best_count = None, 0
    for page in data.get("pages", []):
        if page.get("outcome") != "ok":
            continue
        count = sum(1 for l in page.get("links", []) if l.get("scope") == "external")
        if count > best_count:
            best, best_count = page, count
    if best is None:
        print("No page with external links was found in the evidence file.")
    return best


def build_evidence_text(page):
    ts = page["capture_timestamp"]
    date = f"{ts[0:4]}-{ts[4:6]}-{ts[6:8]}"
    external = [l for l in page["links"] if l["scope"] == "external"]
    lines = [
        "EVIDENCE",
        f"Page {page['page_id']}:",
        f"- Source URL recorded by the archive: {page['source_url']}",
        f"- Capture date (from timestamp {ts}, UTC): {date}",
        f"- Page title: {page['title']}",
        f"Links found in the archived HTML of {page['page_id']} that point to other websites:",
    ]
    for link in external:
        lines.append(f"- {link['evidence_id']}: {link['destination_url']}")
    return "\n".join(lines), [l["evidence_id"] for l in external]


def ask_gemma(evidence_text):
    payload = {
        "model": MODEL_NAME,
        "stream": False,
        "options": {"temperature": 0.2, "num_predict": 700},
        "messages": [
            {"role": "system", "content": SYSTEM_RULES},
            {"role": "user",
             "content": evidence_text + "\n\nNow write your answer in the three sections."},
        ],
    }
    request = urllib.request.Request(
        OLLAMA_CHAT_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    started = time.time()
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        return None, time.time() - started, f"HTTP {err.code}: {err.reason}"
    except urllib.error.URLError as err:
        return None, time.time() - started, f"Could not reach Ollama: {err.reason}"
    except TimeoutError:
        return None, time.time() - started, "Gemma took longer than the time limit."
    except ValueError:
        return None, time.time() - started, "Ollama's reply was not valid JSON."

    try:
        answer = data["message"]["content"]
    except (KeyError, TypeError):
        return None, time.time() - started, "Reply had no answer text."
    return answer, time.time() - started, None


def crude_checks(answer, evidence_text, valid_ids):
    """Very rough machine checks. They do NOT replace reading the answer."""
    cited = sorted(set(re.findall(r"P\d+-L\d+", answer)))
    year_pattern = r"\b(?:19|20)\d{2}\b"
    return {
        "evidence_ids_cited": cited,
        "cited_ids_not_in_evidence": [i for i in cited if i not in valid_ids],
        "years_in_answer_not_in_evidence": sorted(
            set(re.findall(year_pattern, answer))
            - set(re.findall(year_pattern, evidence_text))),
        "says_insufficient_evidence": "insufficient evidence" in answer.lower(),
    }


def main():
    page = load_evidence_page()
    if page is None:
        return

    evidence_text, valid_ids = build_evidence_text(page)
    print("Sending this evidence to", MODEL_NAME, "on your own computer:")
    print("-" * 40)
    print(evidence_text)
    print("-" * 40)
    print("Waiting for Gemma (the first answer can take a minute or more)...")

    started = datetime.now(timezone.utc).isoformat(timespec="seconds")
    answer, seconds, error = ask_gemma(evidence_text)

    result = {
        "status": "TESTED - FAILED" if error else "TESTED",
        "model": MODEL_NAME,
        "run_started_utc": started,
        "response_seconds": round(seconds, 1),
        "error": error,
        "evidence_sent": evidence_text,
        "gemma_answer": answer,
        "crude_checks": crude_checks(answer, evidence_text, valid_ids) if answer else None,
        "note": ("One small test only. It can reveal obvious problems but does not "
                 "measure how accurate the model is. The answer must be read by a human."),
    }
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print()
    print("===== RESULT =====")
    if error:
        print("Gemma test FAILED:", error)
    else:
        print(f"Gemma answered in about {seconds:.1f} seconds.")
        print()
        print(answer)
        print()
        print("Crude checks:", json.dumps(result["crude_checks"], indent=2))
    print("Saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    main()