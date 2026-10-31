"""
Web Séance — AI-Assisted Digital Archaeology Tool
Hacktoberfest 2026 · Week 4 · Ghost in the Machine

A forensic research application for exploring forgotten internet culture through historical webpages,
discovering authentic outgoing hyperlinks, and consulting a local Gemma 3:4b AI model with strict evidence guardrails.
"""

import time
import pandas as pd
import streamlit as st

import config
from core.ai_historian import AIHistorian
from core.archive_client import ArchiveClient
from core.evidence_store import EvidenceStore
from core.html_extractor import extract_page_evidence
from ui.graph_component import render_connection_graph
from ui.theme import apply_theme

# Configure Streamlit page
st.set_page_config(
    page_title="Web Séance — Digital Archaeology",
    page_icon="🕯️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom dark phosphor séance styling
apply_theme()


@st.cache_resource
def get_evidence_store():
    """Singleton cached evidence store."""
    return EvidenceStore()


@st.cache_resource
def get_ai_historian():
    """Singleton cached AI Historian client."""
    return AIHistorian()


@st.cache_resource
def get_archive_client():
    """Singleton cached Internet Archive client."""
    return ArchiveClient()


# Initialize state
store = get_evidence_store()
historian = get_ai_historian()
archive_client = get_archive_client()

if "selected_page_id" not in st.session_state:
    st.session_state.selected_page_id = "P1"

if "live_cdx_captures" not in st.session_state:
    st.session_state.live_cdx_captures = []

if "live_cdx_status" not in st.session_state:
    st.session_state.live_cdx_status = None

if "excavated_captures" not in st.session_state:
    st.session_state.excavated_captures = set()

if "last_ai_result" not in st.session_state:
    st.session_state.last_ai_result = None

# Sidebar Diagnostics & Navigation
with st.sidebar:
    st.markdown("### 🕯️ WEB SÉANCE")
    st.markdown("<div class='seance-tagline'>DIGITAL ARCHAEOLOGY</div>", unsafe_allow_html=True)

    # System Status Diagnostics
    st.markdown("#### System Integrity")
    ai_status = historian.check_status()
    if ai_status["ollama_running"]:
        st.markdown(
            "<div class='status-pill status-active'><span class='status-dot'></span> Ollama: Online</div>",
            unsafe_allow_html=True
        )
        if ai_status["model_available"]:
            st.markdown(
                f"<div class='status-pill status-active'><span class='status-dot'></span> Model: {config.DEFAULT_MODEL} Ready</div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"<div class='status-pill status-inactive'><span class='status-dot'></span> Model: {config.DEFAULT_MODEL} Missing</div>",
                unsafe_allow_html=True
            )
    else:
        st.markdown(
            "<div class='status-pill status-inactive'><span class='status-dot'></span> Ollama: Offline (Local Only)</div>",
            unsafe_allow_html=True
        )

    st.markdown(
        "<div class='status-pill status-active'><span class='status-dot'></span> Archive CDX: Reachable</div>",
        unsafe_allow_html=True
    )

    st.divider()

    # Navigation Menu
    nav_view = st.radio(
        "Navigation",
        [
            "🕯️ Séance Chamber (Home)",
            "📜 Archive Explorer",
            "🔬 Forensic Investigation",
            "🕸️ Connection Explorer",
            "🧠 Ask Local AI Historian",
            "🛡️ Methodology & Integrity"
        ],
        index=0
    )

    st.divider()

    # Evidence Store Quick Stats
    stats = store.get_stats()
    st.markdown("#### Evidence Vault")
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Captures", stats["total_pages"])
        st.metric("External", stats["external_links_count"])
    with c2:
        st.metric("Links", stats["total_links"])
        st.metric("Domains", stats["unique_external_domains"])

    st.caption("Zero synthetic data. All links extracted from verified HTML.")


# ==============================================================================
# VIEW 1: HOME / SÉANCE CHAMBER
# ==============================================================================
if "Séance Chamber" in nav_view:
    st.markdown("<div class='seance-title'>Web Séance</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='seance-tagline'>AI-ASSISTED DIGITAL ARCHAEOLOGY FOR FORGOTTEN INTERNET CULTURE</div>",
        unsafe_allow_html=True
    )

    # Core Mission & Evidence Integrity Distinction
    st.markdown(
        """
        <div class='disclaimer-banner'>
            <b>THE CENTRAL PRINCIPLE:</b> <i>"The internet leaves traces. Web Séance helps us investigate them."</i><br>
            Every artifact in this tool is rooted in authentic historical web captures preserved in the Internet Archive.
            Every outgoing hyperlink was parsed directly from archived HTML.
            <br><br>
            <b>CRITICAL DISTINCTION:</b>
            <span class='evidence-badge badge-verified'>Archival Evidence</span> = Immutable historical facts.<br>
            <span class='evidence-badge badge-ai'>AI Interpretation</span> = Non-definitive hypotheses generated by a local Gemma 3:4b model.<br>
            <i>A hyperlink between two pages proves only that an address was present in HTML; it does NOT prove the authors knew each other or collaborated.</i>
        </div>
        """,
        unsafe_allow_html=True
    )

    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown("### The Archaeological Mission")
        st.write(
            """
            In the early World Wide Web (1990s–early 2000s), personal homepages, webrings, handcrafted blogrolls,
            and idiosyncratic directories formed a decentralized cultural tapestry. Today, much of that vernacular
            web lies forgotten or fragmented.

            **Web Séance** treats archived web HTML as physical archaeological strata:
            - **Excavate authentic captures** from the Internet Archive without modern toolbar contamination.
            - **Trace verified hyperlink trails** to reconstruct what early pioneers were reading, recommending, and building.
            - **Ground local AI reasoning** with strict evidence guardrails, ensuring the model cites specific Evidence IDs
              and explicitly declares *"Insufficient evidence"* whenever proof is lacking.
            """
        )

        st.markdown("### Archaeological Methodology")
        st.markdown(
            """
            1. **CDX Discovery**: Querying the Internet Archive CDX Index for historical 200-OK snapshot timestamps.
            2. **Raw Capture Replay**: Fetching verbatim HTML via raw `id_` replay to eliminate Wayback toolbar injections.
            3. **Deterministic Link Extraction**: Parsing anchors, stripping port 80 anomalies, resolving relative URLs,
               and categorizing into `SAME-SITE` and `EXTERNAL` destinations.
            4. **Evidence Identification**: Assigning an immutable Evidence ID (e.g., `P2-L3`) to every link record.
            5. **Grounded AI Synthesis**: Running local `gemma3:4b` under strict constraints where only provided
               evidence may be cited.
            """
        )

    with col_right:
        st.markdown("### Featured Pioneers in Evidence Vault")
        for p in store.get_all_pages():
            with st.container():
                st.markdown(
                    f"""
                    <div class='seance-card'>
                        <div style='display:flex; justify-content:space-between; align-items:center;'>
                            <b style='color:#00ff88; font-family:monospace;'>[{p['page_id']}] {p.get('historical_figure', p['title'])}</b>
                            <span class='evidence-badge badge-verified'>{p['capture_timestamp'][:8]}</span>
                        </div>
                        <div style='font-size:0.85rem; color:#94a3b8; margin: 4px 0;'>
                            {p['source_url']}
                        </div>
                        <div style='font-size:0.82rem; color:#cbd5e1;'>
                            <i>"{p.get('content_summary', '')[:110]}..."</i>
                        </div>
                        <div style='margin-top:8px;'>
                            <span class='evidence-badge badge-samesite'>{p['unique_links_recorded']} Extracted Links</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )


# ==============================================================================
# VIEW 2: ARCHIVE EXPLORER
# ==============================================================================
elif "Archive Explorer" in nav_view:
    st.markdown("## 📜 Archive Explorer")
    st.write(
        "Browse authentic historical web captures in the evidence vault, or perform a live polite query "
        "against the Internet Archive CDX API to inspect new historical captures."
    )

    tab_vault, tab_live = st.tabs(["🏛️ Curated Evidence Vault", "🛰️ Live Archive Excavator"])

    with tab_vault:
        st.markdown("### Verified Historical Web Captures")
        pages = store.get_all_pages()

        for p in pages:
            col_info, col_action = st.columns([4, 1])
            with col_info:
                st.markdown(
                    f"""
                    <div class='seance-card'>
                        <div style='display:flex; justify-content:space-between; align-items:center;'>
                            <h4 style='margin:0; color:#00ff88;'>[{p['page_id']}] {p['title']}</h4>
                            <span class='evidence-badge badge-verified'>STATUS: AUTHENTIC ARCHIVE CAPTURE</span>
                        </div>
                        <p style='color:#94a3b8; margin:4px 0 8px 0; font-family:monospace; font-size:0.85rem;'>
                            Original: <b>{p['source_url']}</b> &nbsp;|&nbsp;
                            Capture Date: <b>{p['capture_timestamp'][:4]}-{p['capture_timestamp'][4:6]}-{p['capture_timestamp'][6:8]}</b> &nbsp;|&nbsp;
                            SHA-256: <code>{p['content_sha256'][:16]}...</code>
                        </p>
                        <p style='font-size:0.88rem; color:#e2e8f0; margin-bottom:8px;'>
                            {p.get('content_summary', 'No summary available.')}
                        </p>
                        <div>
                            <span class='evidence-badge badge-samesite'>{p['unique_links_recorded']} Verified Links Extracted</span>
                            &nbsp;
                            <a href='{p['archive_capture_url']}' target='_blank' style='color:#38bdf8; text-decoration:none; font-size:0.82rem;'>
                                ↗ View Raw Capture on Wayback
                            </a>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with col_action:
                st.write("")
                st.write("")
                if st.button(f"Investigate {p['page_id']}", key=f"inv_{p['page_id']}", use_container_width=True):
                    st.session_state.selected_page_id = p["page_id"]
                    st.success(f"Selected {p['page_id']}. Switch to 'Forensic Investigation' to inspect.")

    with tab_live:
        st.markdown("### 🛰️ Live Internet Archive Excavator")
        st.markdown(
            """
            <div class='disclaimer-banner'>
                <b>POLITE RESEARCH PROTOCOL:</b> Queries the live Internet Archive CDX Server using polite rate limiting
                (2.0s delays). Fetches raw HTML via <code>id_</code> modifier and extracts links directly into the Evidence Vault.
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.form("live_archive_form"):
            c_url, c_from, c_to = st.columns([3, 1, 1])
            with c_url:
                custom_url = st.text_input("Target URL to Excavate", value="http://www.slashdot.org/")
            with c_from:
                from_yr = st.text_input("From Year", value="1997")
            with c_to:
                to_yr = st.text_input("To Year", value="2002")

            submit_search = st.form_submit_button("Query Internet Archive CDX", type="primary")

        
        if submit_search:
            with st.spinner(f"Querying CDX server for {custom_url}..."):
                res = archive_client.query_cdx(
                    custom_url,
                    limit=3,
                    from_year=from_yr,
                    to_year=to_yr
                )

            if res["status"] == "captures_found" and res["captures"]:
                st.session_state.live_cdx_captures = res["captures"]
                st.session_state.live_cdx_status = "captures_found"
                st.session_state.excavated_captures = set()

            elif res["status"] == "no_captures":
                st.session_state.live_cdx_captures = []
                st.session_state.live_cdx_status = "no_captures"

            else:
                st.session_state.live_cdx_captures = []
                st.session_state.live_cdx_status = res.get(
                    "error", "Unknown error"
                )

        captures = st.session_state.live_cdx_captures

        if st.session_state.live_cdx_status == "captures_found" and captures:
            st.success(
                f"Found {len(captures)} verified captures in the Internet Archive!"
            )

            for idx, cap in enumerate(captures):
                ts = cap["timestamp"]
                c_date = f"{ts[:4]}-{ts[4:6]}-{ts[6:8]}"
                capture_key = f"{ts}_{idx}"

                already_excavated = (
                    capture_key in st.session_state.excavated_captures
                )

                col_cap, col_pull = st.columns([3, 1])

                with col_cap:
                    st.markdown(
                        f"**Capture #{idx+1}**: Timestamp `{ts}` "
                        f"({c_date}) — "
                        f"[View Raw Archive]({cap['capture_url']})"
                    )

                    if already_excavated:
                        st.caption("✓ Already excavated")

                with col_pull:
                    if st.button(
                        f"Excavate Capture #{idx+1}",
                        key=f"excavate_{ts}_{idx}",
                        disabled=already_excavated
                    ):
                        with st.spinner(
                            "Fetching raw capture and extracting links..."
                        ):
                            success, html_text, err = (
                                archive_client.fetch_raw_capture(
                                    ts, cap["original_url"]
                                )
                            )

                            if success:
                                next_pid = f"P{len(store.pages) + 1}"

                                evidence = extract_page_evidence(
                                    html_content=html_text,
                                    original_url=cap["original_url"],
                                    page_id=next_pid,
                                    capture_timestamp=ts,
                                    archive_capture_url=cap["capture_url"]
                                )

                                store.add_page_evidence(evidence)

                                st.session_state.selected_page_id = next_pid
                                st.session_state.excavated_captures.add(
                                    capture_key
                                )

                                st.success(
                                    f"Excavation complete! Added {next_pid} "
                                    f"with {evidence['unique_links_recorded']} "
                                    f"verified hyperlinks."
                                )

                                st.rerun()

                            else:
                                st.error(f"Failed to fetch capture: {err}")

        elif st.session_state.live_cdx_status == "no_captures":
            st.warning(
                "No 200-OK captures were returned by the CDX API "
                "for this URL and year range."
            )

        elif st.session_state.live_cdx_status not in (
            None, "captures_found"
        ):
            st.error(
                f"Archive search failed: {st.session_state.live_cdx_status}"
            )


# ==============================================================================
# VIEW 3: FORENSIC PAGE INVESTIGATION
# ==============================================================================
elif "Forensic Investigation" in nav_view:
    st.markdown("## 🔬 Forensic Page Investigation")
    st.write(
        "Inspect the archaeological evidence for an individual historical webpage: "
        "verbatim metadata, SHA-256 fingerprint, content excerpt, and every verified outgoing hyperlink."
    )

    # Page Selector
    all_pages = store.get_all_pages()
    page_options = {p["page_id"]: f"[{p['page_id']}] {p.get('historical_figure', p['title'])} ({p['capture_timestamp'][:8]})" for p in all_pages}

    selected_pid = st.selectbox(
        "Select Webpage to Investigate",
        options=list(page_options.keys()),
        index=list(page_options.keys()).index(st.session_state.selected_page_id) if st.session_state.selected_page_id in page_options else 0,
        format_func=lambda x: page_options[x]
    )
    st.session_state.selected_page_id = selected_pid

    page = store.get_page(selected_pid)
    if not page:
        st.error("Page not found in evidence store.")
    else:
        # Page Metadata Dossier Card
        st.markdown(
            f"""
            <div class='seance-card'>
                <div style='display:flex; justify-content:space-between; align-items:center;'>
                    <h3 style='margin:0; color:#00ff88;'>[{page['page_id']}] {page['title']}</h3>
                    <span class='evidence-badge badge-verified'>VERIFIED ARCHIVAL RECORD</span>
                </div>
                <div style='margin-top:10px; display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 10px; font-size:0.88rem;'>
                    <div><b>Original URL:</b> <span class='mono-text'>{page['source_url']}</span></div>
                    <div><b>Capture Timestamp:</b> <span class='mono-text'>{page['capture_timestamp']}</span></div>
                    <div><b>Capture Date (UTC):</b> {page['capture_timestamp'][:4]}-{page['capture_timestamp'][4:6]}-{page['capture_timestamp'][6:8]}</div>
                    <div><b>Content SHA-256:</b> <span class='mono-text'>{page.get('content_sha256', 'N/A')[:20]}...</span></div>
                </div>
                <div style='margin-top:12px; font-size:0.9rem; color:#cbd5e1; background:#0c120f; padding:10px; border-radius:6px; border:1px solid #1a2520;'>
                    <b>Archaeological Excerpt:</b> <i>"{page.get('content_summary', 'No excerpt.')}"</i>
                </div>
                <div style='margin-top:10px;'>
                    <a href='{page['archive_capture_url']}' target='_blank' style='color:#38bdf8; font-size:0.85rem; text-decoration:none;'>
                        ↗ Historical Wayback Capture ({page['capture_timestamp'][:8]})
                    </a>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div class='disclaimer-banner'>
                <b>CRITICAL EVIDENCE SAFEGUARD:</b>
                Every outgoing hyperlink listed below was present in the verbatim archived HTML of this capture.
                <br>
                <i>Important:</i> An outgoing hyperlink does <b>NOT</b> prove that the site owners collaborated,
                knew each other, or shared identical philosophies. It proves only that an <code>&lt;a href&gt;</code>
                existed in the document.
            </div>
            """,
            unsafe_allow_html=True
        )

        # Links Filtering
        links = store.get_links_for_page(selected_pid)

        c_filter, c_search = st.columns([1, 2])
        with c_filter:
            scope_filter = st.selectbox("Link Scope Filter", ["All Links", "External Only (Outbound)", "Same-Site Only (Internal)"])
        with c_search:
            search_query = st.text_input("Filter by URL or Anchor Text", "")

        filtered_links = links
        if scope_filter == "External Only (Outbound)":
            filtered_links = [l for l in filtered_links if l.get("scope") == "external"]
        elif scope_filter == "Same-Site Only (Internal)":
            filtered_links = [l for l in filtered_links if l.get("scope") == "same_site"]

        if search_query:
            sq = search_query.lower()
            filtered_links = [
                l for l in filtered_links
                if sq in l.get("destination_url", "").lower() or sq in l.get("anchor_text", "").lower()
            ]

        st.markdown(f"### Extracted Outgoing Hyperlinks ({len(filtered_links)} of {len(links)})")

        if not filtered_links:
            st.info("No hyperlinks match the active filter criteria.")
        else:
            table_rows = []
            for l in filtered_links:
                scope = l.get("scope", "external")
                scope_badge = "EXTERNAL" if scope == "external" else "SAME-SITE"
                table_rows.append({
                    "Evidence ID": l["evidence_id"],
                    "Scope": scope_badge,
                    "Destination URL": l["destination_url"],
                    "Anchor Text": l.get("anchor_text", ""),
                    "AI Inferred": "No (Archival Fact)"
                })

            df = pd.DataFrame(table_rows)
            st.dataframe(df, use_container_width=True, hide_index=True)


# ==============================================================================
# VIEW 4: CONNECTION EXPLORER
# ==============================================================================
elif "Connection Explorer" in nav_view:
    st.markdown("## 🕸️ Connection Explorer")
    st.write(
        "Interactive topological map of verified outgoing hyperlinks extracted from historical web captures. "
        "Every connection represents an authenticated link trail backed by Evidence IDs."
    )

    st.markdown(
        """
        <div class='disclaimer-banner'>
            <b>ZERO SPECULATIVE CONNECTIONS:</b>
            This graph contains <i>only</i> verified hyperlinks extracted directly from archived HTML.
            No probabilistic link prediction, synthetic edges, or speculative social connections are displayed.
        </div>
        """,
        unsafe_allow_html=True
    )

    graph_data = store.get_connection_graph()

    # Render interactive D3 graph
    render_connection_graph(graph_data, height=520)

    st.markdown("### Verified Relationship Matrix")
    st.write(
        "Inspect each verified hyperlink trail, the source page, target domain, and the supporting Evidence IDs."
    )

    edge_rows = []
    for edge in graph_data["edges"]:
        source_label = edge["source"].replace("source:", "")
        target_label = edge["target"].replace("target:", "")
        edge_rows.append({
            "Source Page": source_label,
            "Target Domain": target_label,
            "Hyperlink Count": edge["link_count"],
            "Supporting Evidence IDs": ", ".join(edge["evidence_ids"]),
            "Sample Target URL": edge["sample_urls"][0] if edge.get("sample_urls") else ""
        })

    if edge_rows:
        df_edges = pd.DataFrame(edge_rows)
        st.dataframe(df_edges, use_container_width=True, hide_index=True)
    else:
        st.info("No outbound connections found in the evidence store.")


# ==============================================================================
# VIEW 5: ASK LOCAL AI HISTORIAN
# ==============================================================================
elif "Ask Local AI Historian" in nav_view:
    st.markdown("## 🧠 Ask the Local AI Historian")
    st.write(
        "Consult a locally hosted AI model running `gemma3:4b` via Ollama to interpret verified archival evidence. "
        "Strict prompt guardrails and automated citation audits ensure the model stays grounded in facts."
    )

    ai_status = historian.check_status()

    # Ollama status check
    if not ai_status["ollama_running"]:
        st.markdown(
            """
            <div class='seance-card' style='border-left: 4px solid #f87171;'>
                <h4 style='color:#f87171; margin-top:0;'>⚠️ Local AI Service Unavailable</h4>
                <p>Ollama is not currently running on <code>http://localhost:11434</code>.</p>
                <b>Beginner Setup Instructions:</b>
                <ol>
                    <li>Download and install Ollama from <a href='https://ollama.com' target='_blank' style='color:#38bdf8;'>ollama.com</a>.</li>
                    <li>Open PowerShell or Command Prompt and run: <code>ollama run gemma3:4b</code></li>
                    <li>Refresh this page once Ollama is responding.</li>
                </ol>
                <i>Note: Web Séance never fabricates or simulates AI responses when the local model is offline.</i>
            </div>
            """,
            unsafe_allow_html=True
        )
    elif not ai_status["model_available"]:
        st.markdown(
            f"""
            <div class='seance-card' style='border-left: 4px solid #f59e0b;'>
                <h4 style='color:#f59e0b; margin-top:0;'>⚠️ Target Model Not Downloaded</h4>
                <p>Ollama is online, but model <code>{config.DEFAULT_MODEL}</code> was not found.</p>
                <p>Available models: <code>{', '.join(ai_status['available_models']) or 'None'}</code></p>
                <b>To install the model, run in PowerShell:</b><br>
                <code>ollama pull {config.DEFAULT_MODEL}</code>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div class='seance-card' style='border-left: 3px solid #00ff88; padding: 0.8rem 1.2rem;'>
                <span class='evidence-badge badge-verified'>OLLAMA READY</span>
                <b>Gemma 3:4b</b> is active on <code>http://localhost:11434</code> with strict evidence grounding.
            </div>
            """,
            unsafe_allow_html=True
        )

        all_pages = store.get_all_pages()
        page_dict = {p["page_id"]: f"[{p['page_id']}] {p.get('historical_figure', p['title'])}" for p in all_pages}

        col_sel, col_preset = st.columns([1, 2])
        with col_sel:
            selected_pid = st.selectbox(
                "Archival Page Dossier",
                options=list(page_dict.keys()),
                index=list(page_dict.keys()).index(st.session_state.selected_page_id) if st.session_state.selected_page_id in page_dict else 0,
                format_func=lambda x: page_dict[x]
            )
            st.session_state.selected_page_id = selected_pid

        with col_preset:
            preset_questions = [
                "What was this website about, and what can we verify from its text?",
                "What other websites did it link to, and what domains appear in the HTML?",
                "What can we reasonably infer from these links without making unsupported leaps?",
                "What evidence supports this interpretation, and what evidence is missing?",
                "Did this website have any verified connection to other web pioneers?",
                "Custom query (type below)"
            ]
            chosen_preset = st.selectbox("Archaeological Query Prompt", preset_questions)

        if chosen_preset == "Custom query (type below)":
            user_question = st.text_input("Enter your forensic question:", "What was the purpose of this site?")
        else:
            user_question = chosen_preset

        page = store.get_page(selected_pid)
        links = store.get_links_for_page(selected_pid)

        # Show evidence dossier summary
        with st.expander(f"📁 Evidence Dossier Sent to Model ({len(links)} Verified Links)", expanded=False):
            st.text(historian.format_evidence_payload(page, links))

        if st.button("Consult AI Historian", type="primary"):
            with st.spinner("Local Gemma 3:4b is analyzing archival evidence..."):
                start_time = time.time()
                result = historian.consult(user_question, page, links)
                elapsed = time.time() - start_time
                result["elapsed_seconds"] = elapsed
                st.session_state.last_ai_result = result

        # Display AI Result if available
        if st.session_state.last_ai_result:
            res = st.session_state.last_ai_result
            if res.get("success"):
                st.markdown("### 📜 Historian Assessment")
                st.caption(f"Generated by local {res.get('model')} in {res.get('elapsed_seconds', 0):.1f}s")

                # Display the structured response
                st.markdown(
                    f"""
                    <div class='seance-card'>
                        <div style='line-height:1.6;'>
                            {res['response'].replace(chr(10), '<br>')}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # Citation & Guardrail Audit
                audit = res.get("audit", {})
                st.markdown("### 🛡️ Automated Evidence Audit")
                c_aud1, c_aud2, c_aud3 = st.columns(3)
                with c_aud1:
                    st.metric("Evidence IDs Cited", audit.get("total_citations", 0))
                with c_aud2:
                    if audit.get("cites_only_valid_ids"):
                        st.markdown("<span class='evidence-badge badge-verified'>✓ CITATIONS VALID</span>", unsafe_allow_html=True)
                        st.caption("All cited IDs exist in the dossier.")
                    else:
                        st.markdown("<span class='evidence-badge badge-ai'>⚠️ UNVERIFIED CITATION</span>", unsafe_allow_html=True)
                        st.caption(f"Invalid IDs: {audit.get('invalid_citations')}")
                with c_aud3:
                    if audit.get("acknowledged_limits"):
                        st.markdown("<span class='evidence-badge badge-verified'>✓ UNKNOWNS DECLARED</span>", unsafe_allow_html=True)
                        st.caption("Model identified missing evidence.")
                    else:
                        st.markdown("<span class='evidence-badge badge-samesite'>NOTE</span>", unsafe_allow_html=True)
                        st.caption("Review assertions for ungrounded claims.")

            else:
                st.error(f"Inference error: {res.get('message', 'Unknown failure')}")


# ==============================================================================
# VIEW 6: METHODOLOGY & INTEGRITY
# ==============================================================================
elif "Methodology & Integrity" in nav_view:
    st.markdown("## 🛡️ Evidence & Methodology")
    st.write(
        "Comprehensive documentation of archival provenance, extraction mechanics, "
        "evidence schemas, responsible AI guidelines, and epistemological limitations."
    )

    st.markdown(
        """
        ### 1. Data Provenance & The Internet Archive
        Web Séance sources all historical material directly from the **Internet Archive Wayback Machine**:
        - **CDX Server API**: Queries `https://web.archive.org/cdx/search/cdx` to locate exact capture timestamps
          with HTTP status `200` between 1996 and 2008.
        - **Verbatim Replay (`id_` syntax)**: Requests captures using the `id_` URL modifier
          (e.g., `https://web.archive.org/web/19981202075235id_/http://www.jwz.org:80/`). This instructs the Wayback
          Machine to return the raw, unadorned HTML without injecting the modern Wayback navigation banner, toolbar scripts,
          or tracking pixels.
        - **Polite Rate Throttling**: The client implements a mandatory 2.0-second pause between consecutive requests,
          adheres to timeouts, and halts immediately on HTTP 429 or 403 responses.

        ### 2. HTML Extraction & Sanitization
        Archival HTML is parsed deterministically using `BeautifulSoup4` with custom hygiene filters:
        - **Archive Link Stripping**: Any relative or absolute URLs matching `/web/`, `archive.org/web/`, or `wayback-toolbar`
          are discarded to prevent archive machinery from appearing as historical links.
        - **Scheme & Protocol Normalization**: Pseudo-protocols (`mailto:`, `javascript:`, `tel:`, `#anchor`) are excluded.
        - **Port Normalization**: Historical web captures frequently recorded default HTTP ports (`:80`). These are stripped
          to prevent false classification of same-site links as external domains.
        - **Scope Classification**:
          - `same_site`: Hostname matches the source domain (or is a subdomain).
          - `external`: Hostname points to a distinct external internet host.
        - **Cryptographic Fingerprinting**: Every page snapshot is hashed with SHA-256 to guarantee reproducible integrity.

        ### 3. Evidence Schema & Traceability
        Every verified hyperlink is tracked with an immutable record schema:
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

        ### 4. Responsible AI & Anti-Hallucination Guardrails
        - **Local Only**: All AI inference runs locally on the user's hardware via Ollama and `gemma3:4b`. No historical data
          is transmitted to third-party commercial APIs.
        - **Prompt Grounding**: The model is restricted exclusively to the provided Evidence Dossier and commanded to cite
          specific Evidence IDs (`[P#-L#]`).
        - **Three-Part Output**: The model must separate Confirmed Facts, Plausible Hypotheses, and Missing Information.
        - **The Insufficient Evidence Rule**: When a question exceeds the provided dossier, the model must declare
          *"Insufficient evidence"* rather than speculating.
        - **Automated Audit**: Web Séance parses the AI's response after generation, verifies that all cited Evidence IDs
          genuinely exist, and flags any hallucinated IDs.

        ### 5. Known Archaeological Limitations
        - **The Hyperlink Fallacy**: A hyperlink between site A and site B proves *only* that site A's HTML contained site B's URL.
          It does not prove friendship, ideological agreement, collaboration, or mutual awareness.
        - **Temporal Asymmetry**: Different pages were captured at different points in time. Comparing a 1996 capture of Jodi.org
          with a 2003 capture of Eric Raymond reflects different eras of the early web.
        - **Link Rot & Missing Assets**: Images, external scripts, and linked destinations may no longer be preserved in the archive.
        - **Survivorship Bias**: The Internet Archive crawled popular and connected pages more frequently than obscure personal sites.
        """
    )
