# Web Séance — Demo Walkthrough Script

A concise, step-by-step demonstration script for recording a 3-minute video presentation or conducting a live judging walkthrough of **Web Séance**.

---

## Demo Overview
- **Project**: Web Séance (Hacktoberfest 2026 · Week 4: Ghost in the Machine)
- **Duration**: ~3 minutes
- **Environment**: Windows 11, Streamlit (`http://localhost:8501`), Ollama (`gemma3:4b`)

---

## Step 1: The Séance Chamber (0:00 – 0:35)

1. **Launch the Application**:
   - Open browser to `http://localhost:8501`.
   - Point out the dark digital-archaeology aesthetic: deep charcoal surfaces, glowing phosphor-green accents, and vintage monospace typography.
2. **Present the Mission**:
   - *"The early web was an open, handcrafted tapestry. Today, much of it is forgotten. Web Séance is an AI-assisted digital archaeology workstation that excavates authentic historical web captures, extracts verifiable outgoing hyperlinks, and grounds local AI interpretation in empirical evidence."*
3. **Highlight the Core Distinction**:
   - Point to the **Evidence Integrity Banner**:
     - 🟢 **Archival Evidence** = Immutable historical facts from the Internet Archive.
     - 🟡 **AI Interpretation** = Non-definitive hypotheses from local Gemma 3:4b.
     - *"A hyperlink proves presence in HTML, never social friendship or collaboration."*

---

## Step 2: Archive Explorer & Live Excavation (0:35 – 1:15)

1. **Navigate to "📜 Archive Explorer"**:
   - Show the curated vault of 5 web pioneer captures:
     - **P1**: Jamie Zawinski (`jwz.org`, 1998)
     - **P2**: Eric S. Raymond (`catb.org/~esr/`, 2003)
     - **P3**: ZOMBO.com (`zombo.com`, 1999)
     - **P4**: JODI.org (`jodi.org`, 1996)
     - **P5**: Tim Berners-Lee (`w3.org/People/Berners-Lee/`, 1997)
   - Highlight the **SHA-256 fingerprint** and **capture timestamp** on each card.
2. **Live CDX Excavator**:
   - Switch to the *"🛰️ Live Archive Excavator"* tab.
   - Enter `http://www.slashdot.org/` (1997 to 2002) and click **Query Internet Archive CDX**.
   - Show the live returned captures with real timestamps, demonstrating that live excavation works with polite rate throttling.

---

## Step 3: Forensic Page Investigation (1:15 – 1:55)

1. **Navigate to "🔬 Forensic Investigation"**:
   - Select **P2: Eric Raymond's Home Page (2003)**.
   - Show the archaeological excerpt and the technical metadata.
2. **Explore the Extracted Hyperlinks**:
   - Switch the filter to *"External Only (Outbound)"*.
   - Point to the unique **Evidence IDs** (e.g., `P2-L3` pointing to `opensource.org`, `P2-L10` to `mutt.org`, `P2-L13` to `oreilly.com`).
   - Reiterate that every link is traceable to the raw archived HTML, with zero archive toolbar pollution.

---

## Step 4: The Connection Explorer (1:55 – 2:30)

1. **Navigate to "🕸️ Connection Explorer"**:
   - Showcase the **Interactive D3.js Network Graph**:
     - Green nodes = Archived Pioneer Pages.
     - Blue nodes = External Linked Target Domains.
     - Directed arrows = Authenticated hyperlink trails.
   - Hover over a link or node to reveal the tooltip showing exact **Evidence IDs**.
2. **The Verified Relationship Matrix**:
   - Scroll down to the table. Point out that **zero speculative or hallucinated edges** are allowed; every connection is backed by an authenticated Evidence ID list.

---

## Step 5: Consult the Local AI Historian (2:30 – 3:15)

1. **Navigate to "🧠 Ask Local AI Historian"**:
   - Note the sidebar status: Ollama is running locally on port 11434 with `gemma3:4b`.
   - Select **P2** and choose the preset query:
     *"What other websites did it link to, and what domains appear in the HTML?"*
   - Click **Consult AI Historian**.
2. **Examine the Structured Output**:
   - Show how local Gemma divides its response into:
     - **1. CONFIRMED FACTS**: Citing specific Evidence IDs `[P2-L3]`, `[P2-L5]`, etc.
     - **2. PLAUSIBLE HYPOTHESES**: Cautious topic inferences, explicitly labeled as non-definitive.
     - **3. MISSING INFORMATION**: Stating *"Insufficient evidence"* for ungrounded details.
3. **Automated Evidence Audit**:
   - Point to the **Audit Panel**:
     - *Evidence IDs Cited*: Counts matching citations.
     - *Citation Audit Status*: Confirms all cited IDs genuinely exist in the dossier.

---

## Step 6: Closing & Methodology (3:15 – 3:30)

1. **Navigate to "🛡️ Methodology & Integrity"**:
   - Summarize the scientific safeguards: verbatim `id_` replay, deterministic parsing, local-only AI, and explicit limitation disclosures.
2. **Conclusion**:
   - *"Web Séance demonstrates that digital archaeology and generative AI can work together responsibly—by prioritizing evidence integrity, transparency, and empirical rigor."*
