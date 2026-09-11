"""
World Graph Builder & Interactive Graph Engine (محرك الرسم البياني للعقل الثانوي)
Parses all Markdown notes in 05_WORLD_BRAIN, extracts [[Wikilinks]] and frontmatter,
and compiles an interactive standalone HTML visualization (Canvas / Vis-like graph).
"""
import os
import re
import sys
import json
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

CATEGORY_CONFIG = {
    '01_CHARACTERS': {'label': 'الشخصيات', 'color': '#3b82f6', 'radius': 14},
    '02_SEMIOTICS_AND_SYMBOLS': {'label': 'السيميائيات والرموز', 'color': '#f59e0b', 'radius': 12},
    '03_PHYSICS_AND_LAWS': {'label': 'الفيزياء وقوانين المادة', 'color': '#8b5cf6', 'radius': 12},
    '04_SOCIOLOGY_AND_POWER': {'label': 'علم الاجتماع وبنية السلطة', 'color': '#10b981', 'radius': 12},
    '05_DRAMATURGY_AND_GRAPH': {'label': 'الدراما والحبكة', 'color': '#ef4444', 'radius': 12},
    'ROOT': {'label': 'البوابة المركزية', 'color': '#ec4899', 'radius': 16}
}

def parse_world_brain(brain_dir: Path):
    nodes = {}
    edges = []
    
    # 1. Collect all nodes
    for md_file in brain_dir.rglob("*.md"):
        rel_dir = md_file.parent.name
        cat_key = rel_dir if rel_dir in CATEGORY_CONFIG else 'ROOT'
        node_id = md_file.stem
        
        with open(md_file, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
            
        # Parse frontmatter if present
        title = node_id.replace('_', ' ')
        frontmatter = {}
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                fm_text = parts[1]
                for line in fm_text.splitlines():
                    if ':' in line:
                        k, v = line.split(':', 1)
                        frontmatter[k.strip()] = v.strip()
                if 'title' in frontmatter:
                    title = frontmatter['title']
                    
        # Extract first quote or paragraph as snippet
        quotes = re.findall(r'>\s*«?([^»\n]+)»?', content)
        snippet = quotes[0] if quotes else ""
        if not snippet:
            # First non-header paragraph
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip() and not p.startswith('#') and not p.startswith('---')]
            snippet = paragraphs[0][:150] + "..." if paragraphs else ""
            
        nodes[node_id] = {
            'id': node_id,
            'title': title,
            'category': cat_key,
            'categoryLabel': CATEGORY_CONFIG[cat_key]['label'],
            'color': CATEGORY_CONFIG[cat_key]['color'],
            'radius': CATEGORY_CONFIG[cat_key]['radius'],
            'snippet': snippet,
            'filePath': str(md_file.relative_to(brain_dir.parent)).replace('\\', '/')
        }

    # 2. Extract [[Wikilinks]]
    edge_set = set()
    for md_file in brain_dir.rglob("*.md"):
        source_id = md_file.stem
        with open(md_file, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
            
        links = re.findall(r'\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]', content)
        for target in links:
            target_id = target.strip().replace(' ', '_')
            # Clean possible path elements
            target_id = Path(target_id).stem
            
            if target_id in nodes and source_id != target_id:
                edge_pair = tuple(sorted([source_id, target_id]))
                if edge_pair not in edge_set:
                    edge_set.add(edge_pair)
                    edges.append({
                        'source': source_id,
                        'target': target_id
                    })

    return list(nodes.values()), edges

def generate_interactive_html(nodes, edges, output_file: Path):
    nodes_json = json.dumps(nodes, ensure_ascii=False)
    edges_json = json.dumps(edges, ensure_ascii=False)
    categories_json = json.dumps(CATEGORY_CONFIG, ensure_ascii=False)
    
    html_template = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>العقل الثانوي: عالم رواية قطار الرمل</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Cairo", sans-serif; }}
        body {{ background: #0f172a; color: #f8fafc; overflow: hidden; height: 100vh; display: flex; }}
        #graph-container {{ flex: 1; position: relative; height: 100%; }}
        canvas {{ display: block; width: 100%; height: 100%; }}
        
        /* Top Navigation Overlay */
        .toolbar {{
            position: absolute; top: 16px; right: 16px; z-index: 10;
            background: rgba(30, 41, 59, 0.85); backdrop-filter: blur(8px);
            padding: 12px 18px; border-radius: 12px; border: 1px solid #334155;
            box-shadow: 0 8px 24px rgba(0,0,0,0.4); display: flex; gap: 12px; align-items: center;
        }}
        .toolbar h1 {{ font-size: 15px; font-weight: 700; color: #38bdf8; margin-left: 12px; }}
        .search-box {{
            background: #0f172a; border: 1px solid #475569; color: #fff;
            padding: 6px 12px; border-radius: 6px; font-size: 13px; width: 180px; outline: none;
        }}
        .search-box:focus {{ border-color: #38bdf8; }}
        .btn {{
            background: #334155; color: #f1f5f9; border: 1px solid #475569;
            padding: 6px 12px; border-radius: 6px; font-size: 12px; cursor: pointer; transition: all 0.2s;
        }}
        .btn:hover {{ background: #475569; color: #fff; }}
        
        /* Categories Legend */
        .legend {{
            position: absolute; bottom: 16px; right: 16px; z-index: 10;
            background: rgba(30, 41, 59, 0.85); backdrop-filter: blur(8px);
            padding: 12px 16px; border-radius: 10px; border: 1px solid #334155;
            font-size: 12px; display: flex; flex-direction: column; gap: 6px;
        }}
        .legend-item {{ display: flex; align-items: center; gap: 8px; cursor: pointer; }}
        .legend-color {{ width: 12px; height: 12px; border-radius: 50%; }}

        /* Node Inspector Sidebar */
        #inspector {{
            width: 340px; height: 100%; background: #1e293b; border-left: 1px solid #334155;
            padding: 24px; overflow-y: auto; display: none; z-index: 20;
            box-shadow: -4px 0 20px rgba(0,0,0,0.5);
        }}
        #inspector h2 {{ font-size: 20px; color: #f8fafc; margin-bottom: 6px; }}
        #inspector .badge {{
            display: inline-block; padding: 3px 10px; border-radius: 20px;
            font-size: 11px; font-weight: 600; margin-bottom: 16px;
        }}
        #inspector .section-title {{ font-size: 13px; font-weight: 700; color: #94a3b8; margin: 16px 0 8px; text-transform: uppercase; }}
        #inspector p {{ font-size: 13px; line-height: 1.6; color: #cbd5e1; }}
        #inspector .connections-list {{ list-style: none; display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }}
        #inspector .connection-tag {{
            background: #0f172a; border: 1px solid #475569; padding: 4px 10px;
            border-radius: 6px; font-size: 12px; color: #38bdf8; cursor: pointer; text-decoration: none;
        }}
        #inspector .connection-tag:hover {{ border-color: #38bdf8; background: #1e293b; }}
        #inspector .close-btn {{ float: left; cursor: pointer; color: #94a3b8; font-size: 18px; }}
        #inspector .close-btn:hover {{ color: #fff; }}
    </style>
</head>
<body>
    <div id="graph-container">
        <div class="toolbar">
            <h1>العقل الثانوي: قطار الرمل</h1>
            <input type="text" id="search" class="search-box" placeholder="ابحث عن عقدة أو شخصية...">
            <button class="btn" id="reset-zoom">إعادة ضبط المشهد</button>
        </div>

        <div class="legend" id="legend"></div>
        <canvas id="canvas"></canvas>
    </div>

    <div id="inspector">
        <span class="close-btn" id="close-inspector">&times;</span>
        <h2 id="ins-title">عنوان العقدة</h2>
        <span class="badge" id="ins-badge">الفئة</span>
        <div class="section-title">المقتطف السيميائي / التوصيف</div>
        <p id="ins-snippet">...</p>
        <div class="section-title">العلاقات والروابط المتصلة (<span id="ins-conn-count">0</span>)</div>
        <ul class="connections-list" id="ins-connections"></ul>
        <div class="section-title" style="margin-top: 24px;">مسار الملف المعرفي</div>
        <code style="font-size: 11px; color: #64748b;" id="ins-path"></code>
    </div>

    <script>
        const rawNodes = {nodes_json};
        const rawEdges = {edges_json};
        const categories = {categories_json};

        // Populate Legend
        const legendContainer = document.getElementById('legend');
        Object.entries(categories).forEach(([k, v]) => {{
            const item = document.createElement('div');
            item.className = 'legend-item';
            item.innerHTML = `<span class="legend-color" style="background: ${{v.color}}"></span><span>${{v.label}}</span>`;
            legendContainer.appendChild(item);
        }});

        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        let width = canvas.width = window.innerWidth;
        let height = canvas.height = window.innerHeight;

        window.addEventListener('resize', () => {{
            width = canvas.width = window.innerWidth;
            height = canvas.height = window.innerHeight;
        }});

        // Build Graph Data Structures
        const nodes = rawNodes.map((n, i) => ({{
            ...n,
            x: width / 2 + (Math.random() - 0.5) * 400,
            y: height / 2 + (Math.random() - 0.5) * 400,
            vx: 0, vy: 0,
            connectedNodes: new Set()
        }}));

        const nodeMap = Object.fromEntries(nodes.map(n => [n.id, n]));

        const edges = rawEdges.map(e => {{
            const source = nodeMap[e.source];
            const target = nodeMap[e.target];
            if (source && target) {{
                source.connectedNodes.add(target);
                target.connectedNodes.add(source);
                return {{ source, target }};
            }}
            return null;
        }}).filter(Boolean);

        // Transform / Zoom
        let transform = {{ x: 0, y: 0, k: 1 }};
        let isDragging = false;
        let dragNode = null;
        let startX, startY;
        let selectedNode = null;
        let hoveredNode = null;
        let searchQuery = "";

        // Simple Force Simulation
        function stepSimulation() {{
            const repulsion = 1200;
            const springLen = 90;
            const springK = 0.04;
            const centerK = 0.005;

            // Repulsion between nodes
            for (let i = 0; i < nodes.length; i++) {{
                for (let j = i + 1; j < nodes.length; j++) {{
                    const a = nodes[i], b = nodes[j];
                    const dx = b.x - a.x;
                    const dy = b.y - a.y;
                    const distSq = dx * dx + dy * dy || 1;
                    const dist = Math.sqrt(distSq);
                    if (dist < 450) {{
                        const f = repulsion / distSq;
                        const fx = (dx / dist) * f;
                        const fy = (dy / dist) * f;
                        a.vx -= fx; a.vy -= fy;
                        b.vx += fx; b.vy += fy;
                    }}
                }}
            }}

            // Spring attraction
            edges.forEach(e => {{
                const dx = e.target.x - e.source.x;
                const dy = e.target.y - e.source.y;
                const dist = Math.sqrt(dx * dx + dy * dy) || 1;
                const f = (dist - springLen) * springK;
                const fx = (dx / dist) * f;
                const fy = (dy / dist) * f;
                e.source.vx += fx; e.source.vy += fy;
                e.target.vx -= fx; e.target.vy -= fy;
            }});

            // Gravity towards center
            nodes.forEach(n => {{
                if (n === dragNode) return;
                n.vx += (width / 2 - n.x) * centerK;
                n.vy += (height / 2 - n.y) * centerK;
                n.vx *= 0.85; // damping
                n.vy *= 0.85;
                n.x += n.vx;
                n.y += n.vy;
            }});
        }}

        function draw() {{
            ctx.clearRect(0, 0, width, height);
            ctx.save();
            ctx.translate(transform.x, transform.y);
            ctx.scale(transform.k, transform.k);

            // Draw Edges
            edges.forEach(e => {{
                const isHighlight = selectedNode && (selectedNode === e.source || selectedNode === e.target);
                ctx.strokeStyle = isHighlight ? '#38bdf8' : '#334155';
                ctx.lineWidth = isHighlight ? 2 : 1;
                ctx.beginPath();
                ctx.moveTo(e.source.x, e.source.y);
                ctx.lineTo(e.target.x, e.target.y);
                ctx.stroke();
            }});

            // Draw Nodes
            nodes.forEach(n => {{
                const isMatch = searchQuery && n.title.includes(searchQuery);
                const isSelected = n === selectedNode;
                const isHovered = n === hoveredNode;
                const isConnected = selectedNode && selectedNode.connectedNodes.has(n);

                let radius = n.radius;
                if (isSelected || isHovered) radius += 4;

                ctx.beginPath();
                ctx.arc(n.x, n.y, radius, 0, Math.PI * 2);
                ctx.fillStyle = isMatch ? '#f43f5e' : n.color;
                ctx.fill();

                if (isSelected || isConnected || isHovered) {{
                    ctx.strokeStyle = '#fff';
                    ctx.lineWidth = 2.5;
                    ctx.stroke();
                }}

                // Label
                ctx.fillStyle = (isSelected || isHovered || isMatch) ? '#fff' : '#94a3b8';
                ctx.font = `${{isSelected ? 'bold 13px' : '11px'}} Cairo, sans-serif`;
                ctx.textAlign = 'center';
                ctx.fillText(n.title, n.x, n.y + radius + 14);
            }});

            ctx.restore();
        }}

        function animate() {{
            stepSimulation();
            draw();
            requestAnimationFrame(animate);
        }}
        animate();

        // Mouse Interactions
        function getMousePos(e) {{
            return {{
                x: (e.clientX - transform.x) / transform.k,
                y: (e.clientY - transform.y) / transform.k
            }};
        }}

        canvas.addEventListener('mousedown', e => {{
            const pos = getMousePos(e);
            const hit = nodes.find(n => {{
                const dx = n.x - pos.x, dy = n.y - pos.y;
                return Math.sqrt(dx * dx + dy * dy) <= n.radius + 4;
            }});

            if (hit) {{
                dragNode = hit;
                selectNode(hit);
            }} else {{
                isDragging = true;
                startX = e.clientX - transform.x;
                startY = e.clientY - transform.y;
            }}
        }});

        window.addEventListener('mousemove', e => {{
            if (dragNode) {{
                const pos = getMousePos(e);
                dragNode.x = pos.x;
                dragNode.y = pos.y;
                dragNode.vx = dragNode.vy = 0;
            }} else if (isDragging) {{
                transform.x = e.clientX - startX;
                transform.y = e.clientY - startY;
            }} else {{
                const pos = getMousePos(e);
                hoveredNode = nodes.find(n => {{
                    const dx = n.x - pos.x, dy = n.y - pos.y;
                    return Math.sqrt(dx * dx + dy * dy) <= n.radius + 4;
                }}) || null;
            }}
        }});

        window.addEventListener('mouseup', () => {{
            dragNode = null;
            isDragging = false;
        }});

        canvas.addEventListener('wheel', e => {{
            e.preventDefault();
            const factor = e.deltaY < 0 ? 1.1 : 0.9;
            transform.k = Math.max(0.2, Math.min(3, transform.k * factor));
        }});

        // Inspector View
        const inspector = document.getElementById('inspector');
        function selectNode(node) {{
            selectedNode = node;
            inspector.style.display = 'block';
            document.getElementById('ins-title').innerText = node.title;
            const badge = document.getElementById('ins-badge');
            badge.innerText = node.categoryLabel;
            badge.style.background = node.color + '25';
            badge.style.color = node.color;
            document.getElementById('ins-snippet').innerText = node.snippet || "عقدة أنطولوجية معرفية.";
            document.getElementById('ins-path').innerText = node.filePath;

            const connList = document.getElementById('ins-connections');
            connList.innerHTML = '';
            document.getElementById('ins-conn-count').innerText = node.connectedNodes.size;
            node.connectedNodes.forEach(c => {{
                const li = document.createElement('li');
                li.innerHTML = `<span class="connection-tag">${{c.title}}</span>`;
                li.addEventListener('click', () => selectNode(c));
                connList.appendChild(li);
            }});
        }}

        document.getElementById('close-inspector').addEventListener('click', () => {{
            inspector.style.display = 'none';
            selectedNode = null;
        }});

        document.getElementById('search').addEventListener('input', e => {{
            searchQuery = e.target.value.trim();
        }});

        document.getElementById('reset-zoom').addEventListener('click', () => {{
            transform = {{ x: 0, y: 0, k: 1 }};
        }});
    </script>
</body>
</html>
"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_template)
    print(f"Successfully generated interactive world graph HTML: {output_file} ({os.path.getsize(output_file)} bytes)")

if __name__ == '__main__':
    base_dir = Path(__file__).resolve().parent.parent
    brain_dir = base_dir / "05_WORLD_BRAIN"
    output_html = brain_dir / "world_brain_graph.html"
    
    nodes, edges = parse_world_brain(brain_dir)
    print(f"Parsed {len(nodes)} Ontological Nodes and {len(edges)} Relationships.")
    generate_interactive_html(nodes, edges, output_html)
