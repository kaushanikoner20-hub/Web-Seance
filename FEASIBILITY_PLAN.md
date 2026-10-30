# Feasibility Plan: Web Séance (Stage 1)

Date: 2026-10-29
Status: Stage 1 testing is complete. Results are in `results/FEASIBILITY_REPORT.md`.

## Research question

Can a small tool built by a beginner, using only free software on one Windows 11 computer, do all three of these things before the October 31, 2026 deadline?

1. Find archived historical personal websites in the Internet Archive.
2. Extract genuine outgoing hyperlinks from those archived pages, with evidence that can be traced back to the source page.
3. Use a local Gemma model to explain that evidence without inventing unsupported claims.

## Hypothesis

- The Internet Archive CDX lookup will return usable capture records for well-known early websites.
- Archived page HTML can be downloaded and its links extracted using only Python's built-in tools.
- Local `gemma3:4b` can summarize a very small amount of evidence and cite evidence IDs, but it may add details that the evidence does not support. Its output will therefore need guardrails.

## Methodology

- Step A: check Python, pip, Ollama, and the local model from PowerShell.
- Step B: create the project structure and `scripts/check_environment.py`.
- Step C: `scripts/test_archive_access.py` asks the CDX API for up to 3 records per candidate site and saves the real answers to `data/archive_results.json`.
- Step D: `scripts/test_link_extraction.py` downloads the first capture of up to 4 sites using the raw (`id_`) address form, extracts the page title and links, and saves them with evidence IDs (for example `P2-L3`) to `data/link_evidence.json`.
- Step E: `scripts/test_gemma.py` gives Gemma one page's evidence and strict rules, then saves the answer to `data/gemma_test_result.json`. The answer is read by a human and compared with the evidence.

## Constraints

- Free tools only. No paid services and no API keys.
- No remote AI. Gemma runs locally through Ollama.
- Standard-library Python only. Nothing was installed.
- Small archive request budget: at most 8 requests per script run, a 3-second pause between requests, no retries, and an immediate stop on HTTP 403 or 429 or after two failures in a row.
- No crawling of whole websites.
- No frontend, dashboard, website, or deployment in Stage 1.
- Real hyperlinks and AI-inferred relationships must stay clearly separate.
- A hyperlink alone is never proof that two website owners knew each other.
- No fabricated URLs, results, or AI answers. Untested items are labelled pending.

## Success criteria

The experiment is successful enough to consider full development if:

1. Some useful historical archive records can be retrieved.
2. Enough archived content can be inspected to extract genuine hyperlinks.
3. Evidence supporting the connections can be preserved.
4. Local Gemma can be tested, or its absence is documented with a realistic fallback.
5. A small, polished demo remains achievable before October 31, 2026.

The outcome against these criteria is in the report.