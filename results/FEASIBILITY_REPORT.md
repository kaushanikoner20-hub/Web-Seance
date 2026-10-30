# Feasibility Report: Web Séance, Stage 1

Date: 2026-10-29
Recommendation: **CONDITIONAL GO**

Every number below comes from output that was actually shown by the scripts, or from files the scripts saved. Items not done are marked PENDING.

## 1. Summary

| Question | Result |
|---|---|
| Can the computer run the scripts? | Yes. Python 3.11.9 ran all four scripts. |
| Can useful archive records be retrieved? | Yes. 15 capture records came back for 5 candidate sites. |
| Can archived HTML be inspected for links? | Yes for 4 of 4 pages. 31 links were extracted. |
| Were links verified independently? | PENDING. See section 8. |
| Does local Gemma run? | Yes, in one test. |
| Does Gemma avoid unsupported claims? | No, not fully. See section 6. |
| Were connections between archived sites shown? | No. None of the 4 sample sites linked to another sample site. |

## 2. Environment check results

- Python 3.11.9, pip 26.0.1.
- Ollama 0.40.12 installed and responding on localhost.
- `gemma3:4b` is downloaded. `qwen2.5-coder:7b` is also installed and was not used.
- `scripts/check_environment.py` ran and reported Ollama responding and `gemma3:4b` found.
- The script reported the operating system as "Windows 10". This is a labelling quirk of Python on Windows 11 and has no effect.

## 3. Archive requests actually attempted

- Step C: 5 CDX requests, one each for jwz.org, catb.org/~esr, zombo.com, jodi.org and w3.org/People/Berners-Lee. All 5 returned records. No failures. The backup candidates were not needed.
- Step D: 4 archived pages downloaded, and the run was done twice (8 downloads). The second run was needed to fix a labelling bug (section 7).
- Total: 13 requests to the Internet Archive.
- Safeguards used: 3-second pauses, no retries, stop rules for HTTP 403 and 429. No errors, rate limiting, or blocks occurred.

## 4. Capture records actually retrieved

15 records in total (3 per site), for the years 1996 to 2008. Four pages were inspected:

| Page | Site | Capture date (UTC) | Title | Links |
|---|---|---|---|---|
| P1 | jwz.org | 1998-12-02 | Jamie Zawinski | 6 |
| P2 | catb.org/~esr | 2003-01-24 | Eric Raymond's Home Page | 24 |
| P3 | zombo.com | 1999-11-28 | ZOMBO | 0 |
| P4 | jodi.org | 1996-11-08 | //www.jodi.org/ | 1 |

## 5. Archived HTML inspection and hyperlinks

- Archived HTML was retrieved and parsed for 4 of 4 pages.
- For every page, the final address matched the capture that was requested (no redirect to a different capture).
- 0 archive-generated links were skipped, which is consistent with the raw (`id_`) address form returning unmodified HTML. That address form is described in third-party documentation. It was not confirmed in the Archive's official documentation.
- 31 unique hyperlinks were extracted. 24 were labelled same-site and 7 external. All 7 external links came from P2.
- P3 produced 0 links and P4 produced 1. The reason was not investigated.
- Each link has an evidence ID (for example `P2-L3`) that traces it to its source page and capture.
- None of the 7 external links pointed to another sample site.
- A link in this data only shows that a web address was present in that page's HTML in that capture. It does not show that the website owners knew each other.

## 6. Local Gemma test

- Ran: yes. Model `gemma3:4b`. One run, using the 7 external links from P2.
- Response time: about 88.5 seconds. This probably includes model loading and was not separated from answer time.
- Technical errors: none.
- Followed the requested format and cited only evidence IDs that exist. No invented dates, people or IDs.
- The "confirmed facts" matched the evidence.
- Unsupported content in the interpretations section:
  - It described Mutt as an email client and PNG as image compression. These descriptions came from the model's own knowledge, not from the evidence, which only contained web addresses.
  - It described O'Reilly as "online learning", which the evidence does not support.
  - It suggested "involvement in research or development", which is a large leap from a list of web addresses.
  - It cited a blog link (P2-L16) for claims the link does not support.
  - It wrote "not known" rather than "insufficient evidence".
- The automatic checks found no problems and missed all of the issues above. Only a human reading found them.
- This was a single tiny test. It does not measure the model's accuracy.

## 7. Errors and limitations found

- Labelling bug: the archive records addresses with `:80`. This made one same-site link (`www.catb.org/esr/jargon`) look external. It was fixed and the script re-run. The external count went from 8 to 7.
- Only 4 pages from 4 sites were inspected. This is far too small to measure how reliable the pipeline is.
- Page encodings were not tested. Pages are decoded as UTF-8 or the declared character set, with replacement characters for bad bytes.
- Pages larger than 500 KB would be cut off. None was reported cut off.
- The Internet Archive's official CDX documentation and full terms of use were not opened during this work. The request limits used were cautious guesses based on third-party reports.

## 8. Tests that remain incomplete

- PENDING: manual comparison of extracted links against the archived page in a browser. Until done, the 31 links are "extracted from the HTML of the stated capture", not independently verified.
- PENDING: why P3 and P4 gave so few links.
- PENDING: whether any archived sites in a small set link to each other. This is the core of the idea.
- PENDING: repeated Gemma runs, and Gemma with guardrails.
- PENDING: reading the Internet Archive's official terms of use and CDX documentation before any larger use.

## 9. Recommendation: CONDITIONAL GO

Why not GO: the key idea is showing a connection between archived sites, backed by evidence. This test did not show one. Gemma also added unsupported content, so it cannot be trusted to write the explanations unaided.

Why not NO-GO: the archive lookup, the page download, the link extraction with evidence IDs, and local Gemma all worked. The deadline is October 31, 2026 and this report is dated October 29, so only a very small demo is realistic, and I cannot say that it will fit.

Conditions for going ahead:

1. Keep the scope tiny, for example a handful of pages.
2. Build the "confirmed facts" part directly from the saved data, not from Gemma.
3. If Gemma is used, show its text clearly labelled as AI interpretation, and keep it short and tied to evidence IDs. This guardrail is a suggestion and is not yet tested.
4. Never present a hyperlink as proof of a relationship.

## 10. Smallest recommended next step

Do one more small test before building anything: take the 7 sites that P2 links to, check whether archived captures from around 2003 exist for them (about 7 CDX requests, with the same polite settings), and check whether any of those pages link to each other or back to catb.org.

- If yes, build the tiny demo around that small set of pages.
- If no, build the demo around single pages instead: one archived page, its outgoing links with evidence IDs, and a clearly labelled AI note.

Stage 2 does not start until this report has been reviewed and the next stage is explicitly approved.