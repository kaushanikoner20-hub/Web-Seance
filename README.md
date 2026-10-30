# Web Séance 🕯️

### AI-Assisted Digital Archaeology for Exploring Forgotten Internet Culture

> **Hacktoberfest 2026 · Week 4 Challenge: Ghost in the Machine**
> *"The internet leaves traces. Web Séance helps us investigate them."*

---

## Demo

Web Séance includes an interactive, six-scene walkthrough of the project. It is an HTML page, not a recorded video. Step through it with the Previous, Next and Play controls, the scene dots, or the left and right arrow keys.

**[Open Interactive Demo](demo.html)**

The walkthrough covers:

- The digital archaeology mission and the separation of archival evidence from AI interpretation.
- The Archive Explorer and live Internet Archive CDX search.
- Forensic investigation of a capture and its outgoing hyperlinks, with Evidence IDs.
- The Connection Explorer, a graph of verified hyperlink trails.
- The local Gemma 3:4b historian with its citation audit.
- Responsible-AI design principles, plus how to run the app and tests.

The panels are simplified recreations, not live output. To see real data, run the app locally with `streamlit run app.py`. It serves at `http://localhost:8501` on your own machine only.

> GitHub shows `demo.html` as source code when you open it in the repository. To view it, download the file and open it in a browser, or serve it through GitHub Pages once that is enabled.

---

## 1. Problem Statement

The early World Wide Web (mid-1990s through mid-2000s) was a decentralized, vernacular ecosystem of hand-coded personal homepages, webrings, curated blogrolls, and grassroots directories. As platforms centralized and proprietary walled gardens emerged, vast swathes of this cultural landscape went dark.

While the **Internet Archive Wayback Machine** has preserved billions of snapshots, modern exploration tools face acute problems:

1. **Contamination**: Traditional Wayback replay injects modern JavaScript toolbars, navigation banners, and tracking scripts into the historical document, distorting original markup.
2. **AI Hallucination**: Generative AI tools frequently invent historical connections, fabricate URLs, misattribute dates, and hallucinate relationships between early web pioneers that never existed.
3. **The Hyperlink Fallacy**: An outgoing link from Site A to Site B is often mistakenly interpreted as proof of personal friendship, mutual collaboration, or community membership.

**Web Séance** addresses this with an evidence-grounded digital archaeology methodology.

---

## 2. What Web Séance Does

Web Séance is an open-source research workstation that allows users to:

- **Excavate authentic web captures** directly from the Internet Archive without modern toolbar contamination.
- **Extract verifiable outgoing hyperlinks** from raw historical HTML, categorizing them into same-site internal architecture and external web destinations.
- **Trace evidence records** where every hyperlink has a unique Evidence ID (e.g., `P2-L3`) tied to an exact capture timestamp and a SHA-256 hash.
- **Visualize topological link trails** through an interactive, verified-only network graph with no speculative edges.
- **Consult a locally running Gemma 3:4b model** via Ollama under strict guardrails that ask the model to cite Evidence IDs, distinguish facts from hypotheses, and state *"Insufficient evidence"* whenever proof is absent.

---

## 3. Key Features

- **🕯️ Atmospheric Séance Interface**: A tailored "digital archaeology" aesthetic featuring deep charcoal surfaces (`#0b0f0d`), phosphor-green terminal accents (`#00ff88`), and monospace technical dossiers.
- **📜 Curated Historical Vault**: Pre-indexed captures of five early web pioneers:
  - **P1**: Jamie Zawinski (`jwz.org`, 1998) — Netscape and open-source hacker.
  - **P2**: Eric S. Raymond (`catb.org/~esr/`, 2003) — Open Source Initiative co-founder and author of *The Cathedral and the Bazaar*.
  - **P3**: ZOMBO.com (`zombo.com`, 1999) — Legendary infinite Flash/audio greeting monument.
  - **P4**: JODI (`jodi.org`, 1996) — Seminal early net.art collective.
  - **P5**: Sir Tim Berners-Lee (`w3.org/People/Berners-Lee/`, 1997) — Inventor of the World Wide Web.
- **🛰️ Live Archive Excavator**: Polite live search against the Internet Archive CDX Server API with rate throttling, raw `id_` capture retrieval, and live extraction into the Evidence Vault.
- **🔬 Forensic Page Dossier**: In-depth inspection of page title, original URL, capture timestamp, content excerpt, and tabular outgoing links filterable by scope (`SAME-SITE` vs. `EXTERNAL`).
- **🕸️ Verified Connection Explorer**: Interactive D3.js force-directed graph displaying actual outgoing link trails. Every edge maps to supporting Evidence IDs, with a full Relationship Matrix.
- **🧠 Local AI Historian (`gemma3:4b`)**: Grounded local Ollama integration that splits answers into Confirmed Facts, Plausible Hypotheses, and What Is Unknown. Includes an automated citation audit that flags cited IDs that do not exist.
- **🛡️ Evidence Integrity Engine**: Deterministic parsing, port-80 stripping, archive-link exclusion, and SHA-256 verification.

---

## 4. Architecture Overview

```
Web-Seance/
├── app.py                      # Main Streamlit forensic research workstation
├── config.py                   # Central configuration, paths, timeouts, and design tokens
├── requirements.txt            # Python dependencies (Streamlit, BeautifulSoup4, Requests, Pandas)
├── demo.html                   # Interactive six-scene walkthrough (open in a browser)
├── LICENSE                     # MIT License
├── .gitignore                  # Git exclusions for Python and temporary files
├── data/
│   ├── archive_pages.json      # Metadata of preserved historical captures
│   ├── link_evidence.json      # Outgoing hyperlinks with unique Evidence IDs
│   ├── archive_results.json    # Internet Archive CDX feasibility responses
│   └── gemma_test_result.json  # Preliminary AI grounding feasibility output
├── core/
│   ├── archive_client.py       # Polite CDX client and raw Wayback replay client
│   ├── html_extractor.py       # Deterministic HTML parser, link filter, and hasher
│   ├── evidence_store.py       # Repository manager, queries, and graph projections
│   └── ai_historian.py         # Ollama gemma3:4b client with citation audit
├── ui/
│   ├── theme.py                # Digital Séance phosphor-green custom styling
│   └── graph_component.py      # Interactive D3.js force-directed network visualizer
├── scripts/
│   ├── check_environment.py    # Environment and Ollama model validator
│   ├── collect_archives.py     # Archival evidence collector for pioneer captures
│   ├── test_archive_access.py  # CDX API accessibility verification script
│   ├── test_link_extraction.py # Raw HTML download and link extraction tester
│   └── test_gemma.py           # Single-run Gemma feasibility testing script
├── tests/
│   ├── test_extractor.py       # Unit tests for HTML parser, link filtering, and scope
│   ├── test_evidence.py        # Unit tests for evidence schema, integrity, and graph
│   └── test_ai_historian.py    # Unit tests for prompt formatting and citation audit
└── docs/
    ├── ARCHITECTURE.md         # Detailed technical design and module specifications
    ├── METHODOLOGY.md          # Methodology, provenance, and data ethics
    ├── LIMITATIONS.md          # Epistemological boundaries and known constraints
    └── DEMO_SCRIPT.md          # Step-by-step presentation walkthrough
```

---

## 5. Technologies Used

- **Language**: Python 3.11+
- **Frontend / Workstation**: [Streamlit](https://streamlit.io/) 1.66+
- **HTML Parsing & Extraction**: [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/)
- **Data Serialization & Tables**: [Pandas](https://pandas.pydata.org/)
- **Network Visualization**: [D3.js v7](https://d3js.org/) (embedded via Streamlit Components)
- **Local AI Inference**: [Ollama](https://ollama.com/) running [Gemma 3:4b](https://huggingface.co/google/gemma-3-4b-it)
- **Archive Source**: [Internet Archive CDX API](https://archive.org/help/wayback_api.php) & Wayback Raw Replay

---

## 6. Installation Instructions (Windows 10/11)

### Prerequisites

1. **Python 3.11+**: Ensure Python is installed and added to `PATH`.
2. **Ollama**: Optional for archive exploration; required for the AI Historian. Download and install from [ollama.com](https://ollama.com).

### Step-by-Step Setup

1. Open PowerShell and clone or navigate to the repository directory:

   ```
   git clone https://github.com/kaushanikoner20-hub/Web-Seance.git
   cd Web-Seance
   ```
2. (Optional but recommended) Create and activate a Python virtual environment:

   ```
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
3. Install required Python packages:

   ```
   python -m pip install -r requirements.txt
   ```
4. Verify your environment:

   ```
   python scripts/check_environment.py
   ```

---

## 7. How to Run the Application

Launch the Streamlit application using PowerShell:

```
streamlit run app.py
```

The app opens in your browser at `http://localhost:8501`. This address works only on the machine running the app.

---

## 8. How to Configure Ollama and Gemma 3:4b

AI inference in Web Séance runs on **local hardware** through Ollama, with no paid third-party AI API. Live archive search still needs an internet connection to reach the Internet Archive.

1. Start the Ollama background service (if not already running):

   ```
   ollama serve
   ```
2. Pull the `gemma3:4b` model weights:

   ```
   ollama pull gemma3:4b
   ```
3. Confirm the model is available:

   ```
   ollama list
   ```

   You should see `gemma3:4b` in the list.
4. If Ollama or the model is offline, the AI tab shows setup instructions instead of generating text. The archive and evidence features do not depend on it.

---

## 9. Data Sources and Methodology

1. **Archival Discovery**: The Internet Archive CDX API is queried for historical snapshots matching `filter=statuscode:200` between 1996 and 2008.
2. **Verbatim Replay**: HTML is retrieved via the `id_` syntax (e.g. `https://web.archive.org/web/19981202075235id_/http://www.jwz.org:80/`). This avoids Wayback headers, scripts, and analytics being injected.
3. **Deterministic Parsing**:
   - Strips anchor fragments (`#section`).
   - Normalizes ports (strips `:80` and `:443`).
   - Discards non-HTTP pseudo-schemes (`mailto:`, `javascript:`, `tel:`).
   - Skips Wayback machinery (`/web/`, `archive.org/web/`).
   - Resolves relative URLs to absolute targets.
   - Categorizes each link as `same_site` (internal host match) or `external` (outbound host).

---

## 10. Evidence-Integrity Safeguards

Every link record is saved in a traceable format:

```json
{
  "evidence_id": "P2-L3",
  "source_page_id": "P2",
  "source_url": "http://catb.org/~esr/",
  "destination_url": "http://www.opensource.org",
  "destination_host": "opensource.org",
  "anchor_text": "Open Source Initiative",
  "scope": "external",
  "capture_timestamp": "20030124110141",
  "archive_capture_url": "https://web.archive.org/web/20030124110141/http://catb.org:80/~esr/",
  "link_type": "hyperlink_in_archived_html",
  "extraction_method": "beautifulsoup4_html_parser",
  "ai_inferred": false
}
```

### Principles

- **No Fabricated Records**: Captured pages, dates, and links come from real Internet Archive responses.
- **Clear AI Separation**: Archival evidence is rendered in green badges; AI interpretation is rendered in amber badges.
- **Automated Citation Audit**: After the AI outputs text, the system checks whether cited Evidence IDs exist in the dossier and flags any that do not.
- **The Insufficient Evidence Rule**: If a user asks a question the dossier cannot support, the model is instructed to respond *"Insufficient evidence"*.

---

## 11. Known Limitations

- **Hyperlinks Do Not Prove Social Ties**: An outgoing link shows only that a URL existed in the HTML. It does not prove the website authors were friends, colleagues, or agreed ideologically.
- **Temporal Asymmetry**: Historical captures occurred on different dates across years. Comparing a 1996 capture with a 2003 capture represents different eras of the early web.
- **Survivorship Bias**: The Internet Archive crawled high-traffic and academic domains more frequently than ephemeral personal sites.
- **Missing Linked Targets**: Many outbound destinations from the late 1990s have succumbed to link rot and may not be preserved in the archive.
- **Small Local Model**: Gemma 3:4b is a small model. Its answers can still be wrong or incomplete, so the citation audit checks that cited IDs exist, not that the reasoning is correct.

---

## 12. Automated Testing Instructions

Run the automated test suite with Python's built-in `unittest` runner:

```
python -m unittest discover -s tests -v
```

### Test Coverage

- `tests/test_extractor.py`: URL normalization, relative link resolution, archive URL filtering, and scope detection.
- `tests/test_evidence.py`: Evidence schema validation, Evidence ID format (`P#-L#`), scope filtering, and graph integrity.
- `tests/test_ai_historian.py`: Evidence payload compilation, citation validation, hallucination detection, and Ollama status checks.

---

## 13. Screenshots

Screenshots have not been added yet. Planned file names under `docs/screenshots/`:

| Section                 | Description                                                 | File                                          |
|-------------------------|-------------------------------------------------------------|-----------------------------------------------|
| **Séance Chamber**      | Atmospheric digital archaeology landing page                | `docs/screenshots/01_seance_chamber.png`      |
| **Archive Explorer**    | Curated vault of historical web pioneer captures            | `docs/screenshots/02_archive_explorer.png`    |
| **Page Investigation**  | Forensic metadata, SHA-256 fingerprint, and verified links  | `docs/screenshots/03_page_investigation.png`  |
| **Connection Explorer** | Interactive D3.js topological map of verified hyperlinks    | `docs/screenshots/04_connection_explorer.png` |
| **AI Historian**        | Local Gemma 3:4b consultation with automated citation audit | `docs/screenshots/05_ai_historian.png`        |

---

## 14. Future Improvements

- **Webring Loop Detection**: Automated detection of cyclical link rings across early personal sites.
- **Wayback Timeline Scrubbing**: Visual comparison of how a pioneer's outgoing blogroll evolved across multiple capture years.
- **Static Artifact Exporter**: Single-click export of an entire archaeological dossier into a standalone PDF/Markdown research report with cryptographic signatures.

---

## 15. License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

The MIT License covers this project's own source code and documentation only. It does not automatically cover third-party dependencies (each keeps its own license), archived websites or other content retrieved from the Internet Archive (which remain the property of their original authors), or any other person's work.

Created for Hacktoberfest 2026.