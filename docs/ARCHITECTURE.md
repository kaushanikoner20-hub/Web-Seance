# Web Séance — Technical Architecture

This document outlines the system architecture, component contracts, data flow, and security boundaries of **Web Séance**.

---

## 1. System Topology

```
+-----------------------------------------------------------------------------------+
|                                  USER BROWSER                                     |
|                       (Streamlit Frontend & D3.js Visualizer)                     |
+-----------------------------------------------------------------------------------+
                                          |
                                          | HTTP (localhost:8501)
                                          v
+-----------------------------------------------------------------------------------+
|                             WEB SÉANCE CORE RUNTIME                               |
|                                                                                   |
|   +-----------------------+     +------------------------+                        |
|   |   ArchiveClient       |     |   HTMLExtractor        |                        |
|   |   - CDX Query API     | --> |   - BeautifulSoup4     |                        |
|   |   - Raw `id_` Replay  |     |   - Link Filtering     |                        |
|   |   - Polite Throttling |     |   - Scope Classifier   |                        |
|   +-----------------------+     +------------------------+                        |
|               |                             |                                     |
|               v                             v                                     |
|   +------------------------------------------------------+                        |
|   |                     EvidenceStore                    |                        |
|   |   - Local JSON Persistence (`data/*.json`)           |                        |
|   |   - Unique Evidence IDs (`P#-L#`)                    |                        |
|   |   - Topological Graph Projection                     |                        |
|   +------------------------------------------------------+                        |
|                              |                                                    |
|                              v                                                    |
|   +------------------------------------------------------+                        |
|   |                     AIHistorian                      |                        |
|   |   - Strict Grounding System Prompt                   |                        |
|   |   - Evidence Dossier Serialization                   |                        |
|   |   - Automated Citation Audit Engine                  |                        |
|   +------------------------------------------------------+                        |
+-----------------------------------------------------------------------------------+
             |                                             |
             | HTTP (Port 11434)                           | HTTPS (Polite Rate Throttled)
             v                                             v
+-----------------------------+               +-------------------------------------+
|        LOCAL OLLAMA         |               |      INTERNET ARCHIVE WAYBACK       |
|    Model: `gemma3:4b`       |               |    - CDX API (`/cdx/search/cdx`)    |
| (100% On-Device, Private)   |               |    - Verbatim Raw Replay (`id_`)    |
+-----------------------------+               +-------------------------------------+
```

---

## 2. Core Components

### 2.1 `core/archive_client.py` (`ArchiveClient`)
- **Mission**: Communicates with the Internet Archive safely, politely, and robustly.
- **CDX API Query**: Formats queries against `https://web.archive.org/cdx/search/cdx` specifying `filter=statuscode:200` to retrieve verified historical captures.
- **Verbatim Replay**: Appends `id_` to capture timestamps (e.g., `/web/19981202075235id_/`). The `id_` flag instructs the Wayback Machine to return the raw, unedited HTML payload, completely eliminating the modern Wayback banner and navigation scripts.
- **Polite Rate Limiting**: Enforces a minimum 2.0-second delay between requests to protect community archive infrastructure. Handles HTTP 403, 429, timeouts, and connection disconnects gracefully.

### 2.2 `core/html_extractor.py` (`HTMLExtractor`)
- **Mission**: Extracts clean text excerpts and authentic outgoing hyperlinks from raw HTML.
- **Cleaning & Normalization**:
  - Resolves relative URLs (`about.html`, `../projects`) to absolute addresses using the capture's base URL.
  - Strips URL fragments (`#section`).
  - Strips historical default port artifacts (`:80` and `:443`).
  - Identifies and discards archive-internal links (`/web/`, `archive.org/web/`).
  - Excludes non-HTTP pseudo-protocols (`mailto:`, `javascript:`, `tel:`).
- **Scope Detection**:
  - `same_site`: Host matches the source domain or is a recognized subdomain.
  - `external`: Host points to a separate third-party website.
- **Hashing**: Computes a SHA-256 fingerprint for every raw HTML payload to establish provenance.

### 2.3 `core/evidence_store.py` (`EvidenceStore`)
- **Mission**: Central repository for page metadata and link records.
- **Traceability Contract**: Every extracted hyperlink is assigned a deterministic, unique Evidence ID (e.g., `P1-L1`, `P2-L14`).
- **Graph Projection**: Compiles source pages and external target domains into nodes and directed edges for the D3.js force visualizer. Every edge stores the complete list of supporting Evidence IDs.
- **Persistence**: Serializes data to `data/archive_pages.json` and `data/link_evidence.json`.

### 2.4 `core/ai_historian.py` (`AIHistorian`)
- **Mission**: Interfaces with local Ollama (`gemma3:4b`) to provide scholarly interpretations grounded strictly in the Evidence Dossier.
- **Prompt Guardrails**:
  - Requires the model to use *only* provided evidence.
  - Enforces the **Hyperlink Principle**: a link proves only presence in HTML, never social friendship or collaboration.
  - Requires three distinct sections: Confirmed Facts, Plausible Hypotheses, and Missing Information.
  - Mandates the phrase *"Insufficient evidence"* whenever proof is lacking.
- **Automated Citation Audit**:
  - Regular-expression parser extracts all cited `P#-L#` IDs.
  - Validates cited IDs against the active dossier.
  - Flags any hallucinated Evidence IDs with clear visual warnings in the UI.

---

## 3. Data Flow & Lifecycles

1. **Ingestion Lifecycle**:
   `CDX API` -> `ArchiveClient` -> `Raw HTML` -> `HTMLExtractor` -> `EvidenceStore` -> `Disk Persistence`.
2. **Investigation Lifecycle**:
   `User Selects Page` -> `EvidenceStore.get_page()` & `get_links_for_page()` -> `Forensic UI Panels`.
3. **Inference Lifecycle**:
   `User Query` + `Evidence Dossier` -> `AIHistorian.consult()` -> `Local Ollama` -> `Audit Engine` -> `Structured Historian Assessment`.

---

## 4. Privacy & Responsible AI Safeguards

- **100% Local Inference**: Zero prompts, user questions, or evidence records are transmitted across the internet to remote LLM providers.
- **No Synthetic Historical Data**: Web Séance does not invent web pages, capture timestamps, or outgoing hyperlinks.
- **Epistemological Honesty**: Hypotheses are explicitly marked with warning badges to ensure users never confuse AI speculation with historical archival fact.
