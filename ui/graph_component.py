"""
Network Graph Visualizer for Web Séance.
Renders an interactive force-directed SVG/D3 graph of verified outgoing hyperlink trails.
Every single edge represents an authenticated HTML hyperlink and displays supporting Evidence IDs.
"""

import json
from typing import Dict
import streamlit.components.v1 as components


def render_connection_graph(graph_data: Dict, height: int = 540):
    """
    Renders an interactive, dark-themed D3.js force graph of verified hyperlinks.
    """
    data_json = json.dumps(graph_data)

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                margin: 0;
                padding: 0;
                background-color: #0b0f0d;
                color: #e2e8f0;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace;
                overflow: hidden;
            }}
            #container {{
                width: 100%;
                height: {height}px;
                position: relative;
                border: 1px solid #1e2c24;
                border-radius: 8px;
                background: radial-gradient(circle at center, #121815 0%, #080c0a 100%);
            }}
            svg {{
                width: 100%;
                height: 100%;
            }}
            .node {{
                cursor: pointer;
                transition: filter 0.2s;
            }}
            .node:hover {{
                filter: brightness(1.3) drop-shadow(0 0 8px rgba(0,255,136,0.6));
            }}
            .link {{
                stroke: #2e4439;
                stroke-opacity: 0.7;
                stroke-width: 1.5px;
                transition: stroke 0.2s, stroke-width 0.2s;
            }}
            .link.highlighted {{
                stroke: #00ff88;
                stroke-opacity: 1;
                stroke-width: 2.5px;
            }}
            .label {{
                font-size: 11px;
                font-family: 'Courier New', Courier, monospace;
                fill: #cbd5e1;
                pointer-events: none;
                text-shadow: 0 1px 3px #000000;
            }}
            #tooltip {{
                position: absolute;
                display: none;
                background: #141b18;
                border: 1px solid #00ff88;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12px;
                line-height: 1.4;
                box-shadow: 0 4px 12px rgba(0,0,0,0.5);
                pointer-events: none;
                max-width: 320px;
                z-index: 100;
            }}
            .tt-title {{
                font-weight: bold;
                color: #00ff88;
                margin-bottom: 4px;
                font-family: monospace;
            }}
            .tt-meta {{
                color: #94a3b8;
                font-size: 11px;
            }}
            .tt-evidence {{
                margin-top: 4px;
                color: #38bdf8;
                font-family: monospace;
                font-size: 11px;
            }}
            #controls {{
                position: absolute;
                top: 10px;
                right: 10px;
                background: rgba(18, 24, 21, 0.85);
                border: 1px solid #1e2c24;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 11px;
                color: #94a3b8;
                font-family: monospace;
            }}
        </style>
        <script src="https://d3js.org/d3.v7.min.js"></script>
    </head>
    <body>
        <div id="container">
            <div id="controls">
                <span style="color:#00ff88">●</span> Source Page &nbsp;
                <span style="color:#38bdf8">●</span> Target Domain
            </div>
            <div id="tooltip"></div>
            <svg id="network"></svg>
        </div>

        <script>
            const data = {data_json};
            const container = document.getElementById('container');
            const tooltip = document.getElementById('tooltip');
            const width = container.clientWidth || 800;
            const height = {height};

            const svg = d3.select("#network")
                .attr("viewBox", [0, 0, width, height]);

            // Add arrow marker definitions
            svg.append("defs").append("marker")
                .attr("id", "arrow")
                .attr("viewBox", "0 -5 10 10")
                .attr("refX", 20)
                .attr("refY", 0)
                .attr("markerWidth", 6)
                .attr("markerHeight", 6)
                .attr("orient", "auto")
              .append("path")
                .attr("d", "M0,-4L8,0L0,4")
                .attr("fill", "#2e4439");

            svg.append("defs").append("marker")
                .attr("id", "arrow-active")
                .attr("viewBox", "0 -5 10 10")
                .attr("refX", 20)
                .attr("refY", 0)
                .attr("markerWidth", 6)
                .attr("markerHeight", 6)
                .attr("orient", "auto")
              .append("path")
                .attr("d", "M0,-4L8,0L0,4")
                .attr("fill", "#00ff88");

            const g = svg.append("g");

            // Setup zoom & pan
            svg.call(d3.zoom()
                .scaleExtent([0.4, 3])
                .on("zoom", (event) => g.attr("transform", event.transform))
            );

            // Setup force simulation
            const simulation = d3.forceSimulation(data.nodes)
                .force("link", d3.forceLink(data.edges).id(d => d.id).distance(120))
                .force("charge", d3.forceManyBody().strength(-280))
                .force("center", d3.forceCenter(width / 2, height / 2))
                .force("collision", d3.forceCollide().radius(35));

            // Draw links
            const link = g.append("g")
                .selectAll("line")
                .data(data.edges)
                .join("line")
                .attr("class", "link")
                .attr("marker-end", "url(#arrow)")
                .on("mouseover", (event, d) => {{
                    d3.select(event.currentTarget)
                        .classed("highlighted", true)
                        .attr("marker-end", "url(#arrow-active)");
                    tooltip.style.display = "block";
                    tooltip.innerHTML = `
                        <div class="tt-title">VERIFIED LINK TRAIL</div>
                        <div class="tt-meta">From: <b>${{d.source.label}}</b></div>
                        <div class="tt-meta">To: <b>${{d.target.label}}</b></div>
                        <div class="tt-meta">Total Hyperlinks: <b>${{d.link_count}}</b></div>
                        <div class="tt-evidence">Evidence IDs: ${{d.evidence_ids.join(', ')}}</div>
                    `;
                }})
                .on("mousemove", (event) => {{
                    tooltip.style.left = (event.pageX + 12) + "px";
                    tooltip.style.top = (event.pageY - 20) + "px";
                }})
                .on("mouseout", (event) => {{
                    d3.select(event.currentTarget)
                        .classed("highlighted", false)
                        .attr("marker-end", "url(#arrow)");
                    tooltip.style.display = "none";
                }});

            // Draw node groups
            const node = g.append("g")
                .selectAll("g")
                .data(data.nodes)
                .join("g")
                .attr("class", "node")
                .call(d3.drag()
                    .on("start", dragstarted)
                    .on("drag", dragged)
                    .on("end", dragended)
                )
                .on("mouseover", (event, d) => {{
                    tooltip.style.display = "block";
                    if (d.type === 'source_page') {{
                        tooltip.innerHTML = `
                            <div class="tt-title">[SOURCE PAGE] ${{d.id}}</div>
                            <div><b>${{d.full_title || d.label}}</b></div>
                            <div class="tt-meta">Capture: ${{d.capture_date || 'N/A'}}</div>
                            <div class="tt-meta">URL: ${{d.url}}</div>
                        `;
                    }} else {{
                        tooltip.innerHTML = `
                            <div class="tt-title">[EXTERNAL DESTINATION]</div>
                            <div>Domain: <b>${{d.label}}</b></div>
                            <div class="tt-meta">Verified target of archived hyperlinks</div>
                        `;
                    }}
                }})
                .on("mousemove", (event) => {{
                    tooltip.style.left = (event.pageX + 12) + "px";
                    tooltip.style.top = (event.pageY - 20) + "px";
                }})
                .on("mouseout", () => {{
                    tooltip.style.display = "none";
                }});

            // Node circles
            node.append("circle")
                .attr("r", d => d.type === 'source_page' ? 14 : 9)
                .attr("fill", d => d.color || "#00ff88")
                .attr("stroke", "#0b0f0d")
                .attr("stroke-width", 2);

            // Node labels
            node.append("text")
                .attr("class", "label")
                .attr("x", 16)
                .attr("y", 4)
                .text(d => d.label);

            simulation.on("tick", () => {{
                link
                    .attr("x1", d => d.source.x)
                    .attr("y1", d => d.source.y)
                    .attr("x2", d => d.target.x)
                    .attr("y2", d => d.target.y);

                node.attr("transform", d => `translate(${{d.x}},${{d.y}})`);
            }});

            function dragstarted(event) {{
                if (!event.active) simulation.alphaTarget(0.3).restart();
                event.subject.fx = event.subject.x;
                event.subject.fy = event.subject.y;
            }}

            function dragged(event) {{
                event.subject.fx = event.x;
                event.subject.fy = event.y;
            }}

            function dragended(event) {{
                if (!event.active) simulation.alphaTarget(0);
                event.subject.fx = null;
                event.subject.fy = null;
            }}
        </script>
    </body>
    </html>
    """

    components.html(html_code, height=height + 20)
