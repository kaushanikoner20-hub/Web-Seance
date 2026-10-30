# Web Séance — Archaeological & Technical Limitations

Responsible digital archaeology requires explicit disclosure of analytical, archival, and computational boundaries. This document outlines the key limitations of **Web Séance**.

---

## 1. Epistemological & Interpretive Limitations

### 1.1 The Hyperlink Fallacy
The most frequent error in internet history analysis is confusing a technical hyperlink with a social relationship:
- A link from Eric Raymond’s homepage to `mutt.org` proves only that Raymond’s HTML pointed to the Mutt email client. It does **not** prove he was a developer on Mutt, knew the author, or currently used the software.
- A link may be critical, ironic, oppositional, or purely informational.
- **Rule**: Outgoing hyperlinks establish connectivity, never social consensus or personal acquaintance.

### 1.2 Temporal Asymmetry
Web captures do not exist in uniform chronological slices:
- In Web Séance’s curated vault, JODI is analyzed from November 1996, Tim Berners-Lee from June 1997, Jamie Zawinski from December 1998, ZOMBO from November 1999, and Eric Raymond from January 2003.
- These captures span over six years of intense web evolution (Netscape 2 era through the dot-com aftermath). They must not be conflated as a simultaneous conversational community.

### 1.3 Survivorship and Crawl Bias
The Internet Archive’s historical crawlers (such as Alexa Internet in the 1990s) prioritized:
- Highly cited sites with numerous inbound links.
- Academic, institutional, and commercial domains.
- Ephemeral personal homepages hosted on free web hosts (GeoCities, Tripod, Angelfire) were crawled irregularly or only when linked from popular hubs.

---

## 2. Technical & Archival Limitations

### 2.1 Media and Embedded Asset Loss
Many early web artifacts relied on external assets that were never captured:
- **Flash / Shockwave**: ZOMBO.com (`P3`) relied on an embedded Shockwave Flash movie (`zombo.swf`) and an audio loop. While the HTML container was captured with 0 anchor tags, the interactive Flash media requires a specialized player.
- **Missing Inline Images**: Broken images (`IMG SRC`) frequently occur when image servers were hosted on separate subdomains not indexed during that crawl run.

### 2.2 Character Encoding Inconsistencies
Web markup prior to the universal adoption of UTF-8 was encoded in disparate regional character sets:
- Many early pages were authored in `ISO-8859-1`, `Windows-1252`, or lacked declared `charset` headers entirely.
- Web Séance decodes payloads with charset fallback heuristics, replacing unresolvable byte sequences with replacement characters.

### 2.3 Rate Throttling and Network Latency
The Internet Archive is a non-profit cultural institution serving global research traffic:
- Excessive parallel requests risk triggering HTTP 429 rate limiting or temporary IP blocks.
- Web Séance mandates polite 2.0-second pauses between requests, making bulk excavation deliberate and paced.

---

## 3. Local AI (`gemma3:4b`) Limitations

- **Parameter Size**: `gemma3:4b` is a compact 4-billion parameter model. While lightweight and capable of running locally without cloud telemetry, it possesses finite reasoning capacity compared to 70B+ cluster models.
- **Hallucination Tendency Without Guardrails**: As demonstrated in the Stage 1 feasibility study, unconstrained models tend to fill gaps in knowledge with plausible-sounding external assumptions (e.g., describing Mutt or LibPNG from pre-trained knowledge rather than citing text from the dossier).
- **Execution Speed**: Inference speed depends directly on the host machine’s CPU/GPU architecture. On entry-level systems, initial model loading and multi-token generation may take 30–60 seconds.
- **Fallback Guarantee**: If Ollama or Gemma is unavailable, the application degrades gracefully. It will never synthesize fictional AI text or pretend local inference occurred.
