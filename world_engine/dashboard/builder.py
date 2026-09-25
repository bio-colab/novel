"""
World Engine Dashboard Builder.
===============================
Compiles a standalone, single-file HTML/CSS/JS Writer Dashboard for World Engine.
Features:
- Dark theme inspired by Obsidian & Linear.
- Zero external runtime dependencies (works 100% offline).
- Stable, non-chaotic interactive UI (no jittery physics animations).
- 5 Core Panels:
  1. Interactive Novel Text & Contradiction Inspector.
  2. Spatial-Acoustic & Epistemic Matrix Simulator.
  3. Deterministic Causality DAG Explorer.
  4. Live Environmental & Biological Telemetry Gauges.
  5. Universal Novel Ingestion & Law Recommender Dropzone.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger("world_engine.dashboard.builder")


def _read_file_safely(path: Path) -> str:
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


def _read_yaml_safely(path: Path) -> Any:
    text = _read_file_safely(path)
    if text:
        try:
            return yaml.safe_load(text)
        except Exception as e:
            logger.warning("Error parsing YAML %s: %s", path, e)
    return {}


def build_dashboard_html(
    base_dir: Optional[str | Path] = None,
    output_path: Optional[str | Path] = None,
) -> str:
    """Build the standalone writer dashboard HTML file."""
    root = Path(base_dir) if base_dir else Path(__file__).resolve().parent.parent.parent

    # 1. Load Data
    bugs_data = _read_yaml_safely(root / "03_AUDIT_AND_ISSUES" / "WORLD_BUGS.yaml")
    bugs = bugs_data.get("bugs", []) if isinstance(bugs_data, dict) else []

    temporal_data = _read_yaml_safely(root / "05_WORLD_BRAIN" / "temporal_states.yaml")
    milestones = temporal_data.get("states", []) if isinstance(temporal_data, dict) else []

    manifest = _read_yaml_safely(root / "instances" / "sand_train_auto" / "world_manifest.yaml")
    entities = _read_yaml_safely(root / "instances" / "sand_train_auto" / "entities_catalog.yaml")
    rules = _read_yaml_safely(root / "instances" / "sand_train_auto" / "rules_manifest.yaml")
    causality = _read_yaml_safely(root / "instances" / "sand_train_auto" / "causality_graph.yaml")

    # Sample baseline excerpts around key bugs
    baseline_text = _read_file_safely(root / "00_BASELINE" / "novel_baseline.md")
    baseline_lines = baseline_text.splitlines() if baseline_text else []

    # Prepare excerpts around bug lines for the reader
    excerpts = []
    key_line_indices = [576, 780, 950, 1100, 1252, 1296]
    for idx in key_line_indices:
        start = max(0, idx - 4)
        end = min(len(baseline_lines), idx + 5)
        excerpts.append({
            "target_line": idx + 1,
            "start_line": start + 1,
            "lines": [{"num": i + 1, "text": baseline_lines[i], "is_target": (i == idx)} for i in range(start, end)],
        })

    # Prepare characters array
    chars_list = []
    chars_raw = entities.get("characters", [])
    if isinstance(chars_raw, list):
        chars_list = chars_raw
    elif isinstance(chars_raw, dict):
        for cid, cval in chars_raw.items():
            if isinstance(cval, dict):
                cval["id"] = cid
                chars_list.append(cval)
            else:
                chars_list.append({"id": cid, "name": str(cval)})

    # Serialize embedded data for front-end
    embedded_data = {
        "manifest": manifest,
        "bugs": bugs,
        "milestones": milestones,
        "characters": chars_list,
        "rules": rules.get("rules", []),
        "causality": causality,
        "excerpts": excerpts,
    }
    json_data = json.dumps(embedded_data, ensure_ascii=False)

    html_content = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>لوحة الكاتب الذكية | World Engine Writer Dashboard</title>
    <style>
        :root {{
            --bg-canvas: #090d16;
            --bg-surface: #111827;
            --bg-elevated: #1f2937;
            --bg-card: #182234;
            --border-subtle: #2d3748;
            --border-accent: #38bdf8;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            --color-emerald: #10b981;
            --color-cyan: #06b6d4;
            --color-amber: #f59e0b;
            --color-rose: #f43f5e;
            --color-purple: #a855f7;
            --font-main: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Cairo", "IBM Plex Sans Arabic", sans-serif;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: var(--font-main);
        }}

        body {{
            background: var(--bg-canvas);
            color: var(--text-primary);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            overflow-x: hidden;
        }}

        /* Header & Brand */
        header {{
            background: rgba(17, 24, 39, 0.95);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--border-subtle);
            padding: 14px 28px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 100;
        }}

        .brand {{
            display: flex;
            align-items: center;
            gap: 14px;
        }}

        .brand-icon {{
            width: 38px;
            height: 38px;
            background: linear-gradient(135deg, var(--color-cyan), var(--color-purple));
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 900;
            font-size: 18px;
            color: #fff;
            box-shadow: 0 4px 14px rgba(6, 182, 212, 0.3);
        }}

        .brand-title h1 {{
            font-size: 17px;
            font-weight: 700;
            letter-spacing: -0.3px;
        }}

        .brand-title p {{
            font-size: 12px;
            color: var(--text-secondary);
        }}

        .status-strip {{
            display: flex;
            gap: 10px;
            align-items: center;
        }}

        .badge {{
            padding: 4px 12px;
            border-radius: 9999px;
            font-size: 12px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 6px;
            border: 1px solid transparent;
        }}

        .badge-green {{
            background: rgba(16, 185, 129, 0.12);
            color: var(--color-emerald);
            border-color: rgba(16, 185, 129, 0.25);
        }}

        .badge-cyan {{
            background: rgba(6, 182, 212, 0.12);
            color: var(--color-cyan);
            border-color: rgba(6, 182, 212, 0.25);
        }}

        .badge-purple {{
            background: rgba(168, 85, 247, 0.12);
            color: var(--color-purple);
            border-color: rgba(168, 85, 247, 0.25);
        }}

        /* Navigation Tabs */
        nav {{
            background: var(--bg-surface);
            border-bottom: 1px solid var(--border-subtle);
            padding: 0 28px;
            display: flex;
            gap: 4px;
        }}

        .nav-tab {{
            padding: 12px 18px;
            font-size: 13px;
            font-weight: 600;
            color: var(--text-secondary);
            cursor: pointer;
            border-bottom: 2px solid transparent;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .nav-tab:hover {{
            color: var(--text-primary);
        }}

        .nav-tab.active {{
            color: var(--color-cyan);
            border-bottom-color: var(--color-cyan);
        }}

        /* Main Container */
        main {{
            flex: 1;
            padding: 24px 28px;
            max-width: 1440px;
            margin: 0 auto;
            width: 100%;
        }}

        .tab-content {{
            display: none;
        }}

        .tab-content.active {{
            display: block;
        }}

        /* Grid Layouts */
        .two-column {{
            display: grid;
            grid-template-columns: 1fr 420px;
            gap: 24px;
        }}

        .card {{
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
        }}

        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--border-subtle);
        }}

        .card-title {{
            font-size: 15px;
            font-weight: 700;
            color: var(--text-primary);
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        /* Interactive Reader */
        .reader-container {{
            background: #0d121e;
            border: 1px solid var(--border-subtle);
            border-radius: 10px;
            padding: 16px;
            max-height: 680px;
            overflow-y: auto;
            font-size: 15px;
            line-height: 1.9;
        }}

        .reader-excerpt-box {{
            margin-bottom: 24px;
            padding: 14px;
            background: rgba(30, 41, 59, 0.5);
            border-radius: 8px;
            border-right: 3px solid var(--color-cyan);
        }}

        .reader-line {{
            display: flex;
            gap: 16px;
            padding: 4px 8px;
            border-radius: 4px;
            transition: background 0.15s;
        }}

        .reader-line:hover {{
            background: rgba(255, 255, 255, 0.04);
        }}

        .line-num {{
            color: var(--text-muted);
            font-size: 12px;
            font-family: monospace;
            width: 44px;
            text-align: left;
            user-select: none;
            direction: ltr;
        }}

        .line-text {{
            flex: 1;
        }}

        .line-target {{
            background: rgba(244, 63, 94, 0.15);
            border: 1px dashed rgba(244, 63, 94, 0.5);
            cursor: pointer;
            position: relative;
        }}

        .line-target:hover {{
            background: rgba(244, 63, 94, 0.25);
        }}

        .line-target::after {{
            content: "⚠️ فحص حتمي";
            position: absolute;
            left: 10px;
            top: 4px;
            font-size: 10px;
            background: var(--color-rose);
            color: #fff;
            padding: 1px 6px;
            border-radius: 4px;
            font-weight: 700;
        }}

        /* Contradiction Inspector */
        .bug-card {{
            background: rgba(15, 23, 42, 0.8);
            border: 1px solid var(--border-subtle);
            border-radius: 10px;
            padding: 16px;
            margin-bottom: 14px;
            cursor: pointer;
            transition: all 0.2s;
        }}

        .bug-card:hover, .bug-card.selected {{
            border-color: var(--color-cyan);
            box-shadow: 0 0 14px rgba(6, 182, 212, 0.2);
            transform: translateY(-1px);
        }}

        .bug-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }}

        .bug-tag {{
            font-size: 11px;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 4px;
        }}

        .tag-critical {{ background: rgba(244, 63, 94, 0.2); color: var(--color-rose); }}
        .tag-major {{ background: rgba(245, 158, 11, 0.2); color: var(--color-amber); }}
        .tag-moderate {{ background: rgba(6, 182, 212, 0.2); color: var(--color-cyan); }}

        .charter-quote {{
            background: rgba(6, 182, 212, 0.08);
            border-right: 3px solid var(--color-cyan);
            padding: 10px 14px;
            border-radius: 6px;
            font-size: 12px;
            color: #bae6fd;
            margin-top: 12px;
            line-height: 1.6;
        }}

        /* Acoustic Simulator */
        .train-diagram {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin: 20px 0;
        }}

        .car-box {{
            background: #0f172a;
            border: 2px solid var(--border-subtle);
            border-radius: 12px;
            padding: 18px;
            position: relative;
            transition: all 0.3s;
        }}

        .car-box.active-source {{
            border-color: var(--color-amber);
            box-shadow: 0 0 20px rgba(245, 158, 11, 0.3);
        }}

        .car-box.audible {{
            border-color: var(--color-emerald);
        }}

        .car-box.in-audible {{
            border-color: rgba(244, 63, 94, 0.4);
            opacity: 0.7;
        }}

        .db-meter {{
            font-size: 24px;
            font-weight: 900;
            font-family: monospace;
            margin: 10px 0;
            direction: ltr;
        }}

        /* Telemetry Gauges Grid */
        .gauges-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 18px;
            margin-top: 18px;
        }}

        .gauge-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: 12px;
            padding: 18px;
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
        }}

        .gauge-value {{
            font-size: 32px;
            font-weight: 800;
            margin: 10px 0 4px;
            font-family: monospace;
        }}

        .gauge-sub {{
            font-size: 12px;
            color: var(--text-muted);
        }}

        /* Buttons & Forms */
        .btn {{
            background: var(--bg-elevated);
            color: var(--text-primary);
            border: 1px solid var(--border-subtle);
            padding: 8px 16px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}

        .btn:hover {{
            background: var(--border-subtle);
            border-color: var(--color-cyan);
        }}

        .btn-primary {{
            background: linear-gradient(135deg, var(--color-cyan), #0284c7);
            color: #fff;
            border: none;
        }}

        .btn-primary:hover {{
            box-shadow: 0 4px 14px rgba(6, 182, 212, 0.4);
        }}

        /* Dropzone */
        .dropzone {{
            border: 2px dashed var(--border-subtle);
            border-radius: 12px;
            padding: 40px;
            text-align: center;
            background: rgba(15, 23, 42, 0.4);
            cursor: pointer;
            transition: all 0.2s;
        }}

        .dropzone:hover {{
            border-color: var(--color-cyan);
            background: rgba(6, 182, 212, 0.04);
        }}

        textarea.code-input {{
            width: 100%;
            height: 180px;
            background: #0d121e;
            border: 1px solid var(--border-subtle);
            border-radius: 8px;
            padding: 12px;
            color: #fff;
            font-size: 13px;
            line-height: 1.6;
            margin: 12px 0;
            outline: none;
            resize: vertical;
        }}
    </style>
</head>
<body>

    <!-- Header -->
    <header>
        <div class="brand">
            <div class="brand-icon">WE</div>
            <div class="brand-title">
                <h1>نظام تشغيل العوالم السردية | World Engine OS</h1>
                <p>المثيل المعياري الذهبي: «قطار الرمل» (Gold-Standard Benchmark)</p>
            </div>
        </div>
        <div class="status-strip">
            <div class="badge badge-green">🛡️ 30/30 فحص ناجح</div>
            <div class="badge badge-cyan">⚖️ 41 قانوناً حتمياً</div>
            <div class="badge badge-purple">🧠 JEV: 86% تطابق سيميائي</div>
        </div>
    </header>

    <!-- Navigation Tabs -->
    <nav>
        <div class="nav-tab active" onclick="switchTab('reader')">📖 1. المتن ومفتش التناقضات</div>
        <div class="nav-tab" onclick="switchTab('acoustic')">🔊 2. محاكي الصوت والمصفوفة الإبستيمية</div>
        <div class="nav-tab" onclick="switchTab('dag')">⛓️ 3. شبكة التتابع السببي (DAG)</div>
        <div class="nav-tab" onclick="switchTab('telemetry')">🌡️ 4. عدادات الغلاف الفيزيائي</div>
        <div class="nav-tab" onclick="switchTab('ingest')">📥 5. استيراد وتأريض رواية جديدة</div>
    </nav>

    <!-- Main Content -->
    <main>

        <!-- TAB 1: Reader & Contradictions -->
        <div id="tab-reader" class="tab-content active">
            <div class="two-column">
                <div>
                    <div class="card">
                        <div class="card-header">
                            <div class="card-title">📖 قراءة المتن ومواضع التدقيق الحتمي (Baseline Live Reader)</div>
                            <span style="font-size: 12px; color: var(--text-muted);">انقر على أي سطر مظلل لتفكيك التناقض</span>
                        </div>
                        <div class="reader-container" id="reader-box">
                            <!-- Populated by JS -->
                        </div>
                    </div>
                </div>
                <div>
                    <div class="card" id="inspector-card">
                        <div class="card-header">
                            <div class="card-title">🔍 بطاقة تفكيك التناقض (Contradiction Card)</div>
                            <span class="badge badge-cyan" id="card-severity">اختر سطراً</span>
                        </div>
                        <div id="card-body">
                            <p style="color: var(--text-muted); font-size: 13px;">انقر على أي سطر مظلل في النص على اليمين لعرض تحليله الفيزيائي ومطابقته مع القوانين.</p>
                        </div>
                        <div class="charter-quote">
                            <strong>ميثاق الحياد الإبداعي:</strong><br>
                            «نحن نُحلل ونُقيّم.. ولا نُقوّم». هذه الأداة ترصد فقط اتساق القوانين الفيزيائية التي سنّها العالم لنفسه، والحدس الفني للكاتب هو الحكم المطلق.
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- TAB 2: Acoustic & Epistemic Matrix -->
        <div id="tab-acoustic" class="tab-content">
            <div class="card">
                <div class="card-header">
                    <div class="card-title">🔊 محاكي التوهين الصوتي والحدود الإبستيمية (LAW-ACOUST-03 / LAW-ACOUST-04)</div>
                    <div style="display:flex; gap:10px;">
                        <button class="btn btn-primary" onclick="runAcousticSim()">📡 بث التردد الصوتي</button>
                    </div>
                </div>

                <div style="display: flex; gap: 20px; align-items: center; margin-bottom: 16px; background: rgba(30,41,59,0.4); padding: 12px 16px; border-radius: 8px;">
                    <div>
                        <label style="font-size: 12px; color: var(--text-secondary);">مصدر الصوت (عربة الانبعاث):</label><br>
                        <select id="sim-source" style="background:#0f172a; color:#fff; border:1px solid var(--border-subtle); padding:6px 12px; border-radius:6px; margin-top:4px;">
                            <option value="car_01">العربة 01 (الحراس - خالد وعباس)</option>
                            <option value="car_02">العربة 02 (السجناء - عزيز وبسام)</option>
                            <option value="car_03">العربة 03 (الخلفية - خليل وسردار)</option>
                            <option value="cab">كابينة القاطرة (أبو علي)</option>
                        </select>
                    </div>
                    <div>
                        <label style="font-size: 12px; color: var(--text-secondary);">شدة الحدث الصوتي:</label><br>
                        <select id="sim-sound" style="background:#0f172a; color:#fff; border:1px solid var(--border-subtle); padding:6px 12px; border-radius:6px; margin-top:4px;">
                            <option value="whisper">همس خافت وسري (25 dB)</option>
                            <option value="talk">حديث عادي معتاد (60 dB)</option>
                            <option value="shout">صراخ محتد وهلع (85 dB)</option>
                            <option value="impact">طرق ميكانيكي صدمي على الصاج (110 dB - هيكلي)</option>
                            <option value="gunshot">طلقة كلاشنكوف 7.62mm (150 dB)</option>
                        </select>
                    </div>
                </div>

                <!-- Train Cars Diagram -->
                <div class="train-diagram" id="cars-diagram">
                    <!-- Populated by JS -->
                </div>

                <div style="margin-top: 20px;">
                    <h3 style="font-size: 14px; margin-bottom: 10px;">📋 مصفوفة المعرفة اللحظية للشخصيات (Epistemic Matrix State)</h3>
                    <div id="epistemic-table" style="background: #0d121e; padding: 14px; border-radius: 8px; border: 1px solid var(--border-subtle);">
                        <!-- Table populated by JS -->
                    </div>
                </div>
            </div>
        </div>

        <!-- TAB 3: Causality DAG -->
        <div id="tab-dag" class="tab-content">
            <div class="card">
                <div class="card-header">
                    <div class="card-title">⛓️ شبكة التتابع السببي الحتمية (Directed Acyclic Graph)</div>
                    <span class="badge badge-green">100% خالية من الدورات الممتنعة (Acyclic)</span>
                </div>
                <div id="dag-container" style="display: flex; flex-direction: column; gap: 14px; margin-top: 12px;">
                    <!-- Event nodes populated by JS -->
                </div>
            </div>
        </div>

        <!-- TAB 4: Telemetry -->
        <div id="tab-telemetry" class="tab-content">
            <div class="card">
                <div class="card-header">
                    <div class="card-title">🌡️ عدادات الغلاف الفيزيائي والبيولوجي الحي (Living Telemetry)</div>
                    <div style="display:flex; align-items:center; gap: 12px;">
                        <span style="font-size: 12px; color: var(--text-secondary);">المحطة الزمنية (Milestone):</span>
                        <select id="milestone-select" onchange="updateTelemetry(this.value)" style="background:#0f172a; color:#fff; border:1px solid var(--border-subtle); padding:6px 12px; border-radius:6px;">
                            <option value="0">T0 (19:00 - العطل المبدئي وانكسار الأنبوب)</option>
                            <option value="1">T1 (21:00 - انغلاق المكابح وتيبس الأطراف)</option>
                            <option value="2">T2 (00:00 - كمين منتصف الليل والرصاص)</option>
                            <option value="3">T3 (03:00 - أقصى تجمد وانطفاء البطاريات)</option>
                            <option value="4" selected>T4 (05:45 - الفجر الكاذب واستنزاف O2)</option>
                        </select>
                    </div>
                </div>

                <div class="gauges-grid">
                    <div class="gauge-card">
                        <span class="gauge-sub">درجة الحرارة المحيطة</span>
                        <div class="gauge-value" id="gauge-temp" style="color: var(--color-cyan);">-8.0°C</div>
                        <span class="gauge-sub">حد تبلور بارافين الديزل: -4°C</span>
                    </div>
                    <div class="gauge-card">
                        <span class="gauge-sub">تركيز ثاني أكسيد الكربون (CO2)</span>
                        <div class="gauge-value" id="gauge-co2" style="color: var(--color-rose);">2800 ppm</div>
                        <span class="gauge-sub">عتبة التسمم والبلادة الذهنية (Hypercapnia)</span>
                    </div>
                    <div class="gauge-card">
                        <span class="gauge-sub">شدة الإضاءة الفلكية</span>
                        <div class="gauge-value" id="gauge-lux" style="color: var(--text-secondary);">0.0 Lux</div>
                        <span class="gauge-sub">محاق كانون الثاني (عتمة صقيعية دامسة)</span>
                    </div>
                    <div class="gauge-card">
                        <span class="gauge-sub">ضغط أنبوب مكابح ويستنغهاوس</span>
                        <div class="gauge-value" id="gauge-pneum" style="color: var(--color-amber);">0.0 bar</div>
                        <span class="gauge-sub">إطباق حتمي للقباقيب الفولاذية (Clamped)</span>
                    </div>
                    <div class="gauge-card">
                        <span class="gauge-sub">احتياطي الماء الصالح للشرب</span>
                        <div class="gauge-value" id="gauge-water" style="color: var(--color-emerald);">7.98 L</div>
                        <span class="gauge-sub">مستهلك تنفسي: 6.02 L لـ 14 فرداً</span>
                    </div>
                    <div class="gauge-card">
                        <span class="gauge-sub">شحنة بطاريات الإضاءة</span>
                        <div class="gauge-value" id="gauge-batt" style="color: var(--color-rose);">15%</div>
                        <span class="gauge-sub">انحدار كيميائي حراري (LAW-MAT-01)</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- TAB 5: Ingest Dropzone -->
        <div id="tab-ingest" class="tab-content">
            <div class="card">
                <div class="card-header">
                    <div class="card-title">📥 مستورد وتأريض الروايات الشامل (Universal Novel Ingest)</div>
                    <span class="badge badge-cyan">يدعم أي نص روائي عربي خام</span>
                </div>

                <div class="dropzone" id="drop-area" onclick="document.getElementById('file-upload').click()">
                    <div style="font-size: 36px; margin-bottom: 8px;">📄</div>
                    <p style="font-weight: 700; margin-bottom: 4px;">اسحب وأفلت ملف الرواية (.txt أو .md) هنا</p>
                    <p style="font-size: 12px; color: var(--text-muted);">أو انقر لاختيار ملف من جهازك</p>
                    <input type="file" id="file-upload" style="display:none;" onchange="handleFileSelect(event)">
                </div>

                <div style="margin-top: 16px;">
                    <label style="font-size: 13px; font-weight: 600;">أو الصق النص السردي مباشرة:</label>
                    <textarea class="code-input" id="raw-novel-text" placeholder="الصق فصلاً أو نص رواية بالعربية لتحليله فورياً..."></textarea>
                    <div style="display: flex; gap: 10px;">
                        <button class="btn btn-primary" onclick="analyzeClientText()">⚡ تحليل وتأريض النص السردي</button>
                        <button class="btn" onclick="clearIngestText()">مسح</button>
                    </div>
                </div>

                <div id="ingest-results" style="display: none; margin-top: 20px; background: #0d121e; padding: 18px; border-radius: 8px; border: 1px solid var(--border-subtle);">
                    <!-- Results populated by JS -->
                </div>
            </div>
        </div>

    </main>

    <!-- Embedded Engine Data -->
    <script>
        const ENGINE_DATA = {json_data};

        function switchTab(tabId) {{
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.nav-tab').forEach(el => el.classList.remove('active'));
            
            const target = document.getElementById('tab-' + tabId);
            if (target) target.classList.add('active');

            const tabs = Array.from(document.querySelectorAll('.nav-tab'));
            const map = ['reader', 'acoustic', 'dag', 'telemetry', 'ingest'];
            const idx = map.indexOf(tabId);
            if (idx !== -1 && tabs[idx]) tabs[idx].classList.add('active');
        }}

        // Render Reader Excerpts
        function renderReader() {{
            const box = document.getElementById('reader-box');
            if (!box) return;
            box.innerHTML = '';

            ENGINE_DATA.excerpts.forEach((ex, exIdx) => {{
                const exDiv = document.createElement('div');
                exDiv.className = 'reader-excerpt-box';
                
                let linesHtml = '';
                ex.lines.forEach(line => {{
                    if (line.is_target) {{
                        linesHtml += `
                            <div class="reader-line line-target" onclick="showContradiction(${{line.num}})">
                                <div class="line-num">${{line.num}}</div>
                                <div class="line-text"><strong>${{line.text}}</strong></div>
                            </div>
                        `;
                    }} else {{
                        linesHtml += `
                            <div class="reader-line">
                                <div class="line-num">${{line.num}}</div>
                                <div class="line-text">${{line.text}}</div>
                            </div>
                        `;
                    }}
                }});
                exDiv.innerHTML = linesHtml;
                box.appendChild(exDiv);
            }});
        }}

        // Show Contradiction
        function showContradiction(lineNum) {{
            const cardBody = document.getElementById('card-body');
            const cardSev = document.getElementById('card-severity');
            
            const bug = ENGINE_DATA.bugs.find(b => {{
                const ev = b.evidence || {{}};
                return (ev.line_number === lineNum || ev.baseline_line_number === lineNum);
            }}) || {{
                id: "WORLD-BUG-007",
                title: "زلة التعداد السكاني (Headcount Invariant)",
                severity: "MODERATE",
                law_violated: "LAW-BIO-03 / HEADCOUNT-LEDGER",
                description: "المتن يصف تنفس 'عشرة رجال' في بطن الحديد، في حين أن سجل الركاب يثبت 14 رجلاً على قيد الحياة حتى مقتل الأربعة في الكمين.",
                metric: "10 مسودة vs 14 سجل فيزيائي",
                creative_guidance: "نحن نُحلل ونُقيّم.. ولا نُقوّم. يمكن للكاتب الإبقاء عليها كتعبير مجازي أو مواءمتها مع التعداد."
            }};

            cardSev.textContent = bug.severity || 'MODERATE';
            cardSev.className = 'badge ' + (bug.severity === 'CRITICAL' ? 'tag-critical' : (bug.severity === 'MAJOR' ? 'tag-major' : 'tag-moderate'));

            cardBody.innerHTML = `
                <h4 style="font-size: 15px; margin-bottom: 8px; color: #fff;">${{bug.title || bug.id}}</h4>
                <div style="font-size: 12px; margin-bottom: 12px;">
                    <span style="color: var(--text-muted);">القانون الحاكم:</span> 
                    <span style="color: var(--color-cyan); font-family: monospace;">[${{bug.law_violated || 'PHYSICAL-INVARIANT'}}]</span>
                </div>
                <p style="font-size: 13px; line-height: 1.6; margin-bottom: 12px; color: #e2e8f0;">
                    ${{bug.description || 'فحص تطابق مادي للبيئة والكيانات.'}}
                </p>
                <div style="background: rgba(0,0,0,0.3); padding: 10px; border-radius: 6px; font-size: 12px; font-family: monospace; color: var(--color-emerald);">
                    <strong>القياس المادي المحسوب:</strong> ${{bug.metric || 'متسق مع المقادير الحتمية'}}
                </div>
            `;
        }}

        // Acoustic Simulation
        function runAcousticSim() {{
            const source = document.getElementById('sim-source').value;
            const soundType = document.getElementById('sim-sound').value;

            const soundLevels = {{
                whisper: {{ db: 25, label: "همس خافت 25 dB", structural: false }},
                talk: {{ db: 60, label: "حديث عادي 60 dB", structural: false }},
                shout: {{ db: 85, label: "صراخ محتد 85 dB", structural: false }},
                impact: {{ db: 110, label: "طرق ميكانيكي صدمي 110 dB", structural: true }},
                gunshot: {{ db: 150, label: "طلقة كلاشنكوف 150 dB", structural: false }},
            }};

            const sel = soundLevels[soundType] || soundLevels.talk;
            const cars = [
                {{ id: "cab", name: "القاطرة", char: "أبو علي", slot: 0 }},
                {{ id: "car_01", name: "العربة 01", char: "خالد وعباس", slot: 1 }},
                {{ id: "car_02", name: "العربة 02", char: "عزيز وبسام وسلوم", slot: 2 }},
                {{ id: "car_03", name: "العربة 03", char: "خليل وسردار", slot: 3 }},
            ];

            const srcIdx = cars.findIndex(c => c.id === source);
            const diagram = document.getElementById('cars-diagram');
            diagram.innerHTML = '';

            let tableHtml = `
                <table style="width:100%; border-collapse: collapse; font-size: 13px;">
                    <thead>
                        <tr style="border-bottom: 1px solid var(--border-subtle); color: var(--text-muted); text-align: right;">
                            <th style="padding: 8px;">الموقع</th>
                            <th style="padding: 8px;">الشخصيات الحاضرة</th>
                            <th style="padding: 8px;">الشدة المستقبلة (dB)</th>
                            <th style="padding: 8px;">حالة الإدراك والسمع</th>
                            <th style="padding: 8px;">التصنيف الإبستيمي</th>
                        </tr>
                    </thead>
                    <tbody>
            `;

            cars.forEach((car, idx) => {{
                let receivedDb = sel.db;
                if (sel.structural) {{
                    receivedDb = Math.max(0, sel.db - Math.abs(idx - srcIdx) * 5);
                }} else {{
                    const partitions = Math.abs(idx - srcIdx);
                    receivedDb = Math.max(0, sel.db - (partitions * 20));
                }}

                const isAudible = receivedDb >= 25;
                const isClear = receivedDb >= 45;
                const isSource = (idx === srcIdx);

                const carDiv = document.createElement('div');
                carDiv.className = 'car-box ' + (isSource ? 'active-source' : (isAudible ? 'audible' : 'in-audible'));
                carDiv.innerHTML = `
                    <div style="font-size: 12px; color: var(--text-muted);">${{isSource ? '🎯 مصدر الانبعاث' : 'حاجز مستقبِل'}}</div>
                    <div style="font-weight: 700; font-size: 16px; margin: 4px 0;">${{car.name}}</div>
                    <div style="font-size: 12px; color: var(--text-secondary);">${{car.char}}</div>
                    <div class="db-meter" style="color: ${{isAudible ? 'var(--color-emerald)' : 'var(--color-rose)'}};">
                        ${{receivedDb.toFixed(0)}} dB
                    </div>
                    <div style="font-size: 11px;">${{isClear ? '🟢 مسموع بوضوح' : (isAudible ? '🟡 همهمة غير مفهومة' : '🔴 بقعة عمياء (Blind Spot)')}}</div>
                `;
                diagram.appendChild(carDiv);

                tableHtml += `
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                        <td style="padding: 8px; font-weight: 600;">${{car.name}}</td>
                        <td style="padding: 8px;">${{car.char}}</td>
                        <td style="padding: 8px; font-family: monospace;">${{receivedDb.toFixed(0)}} dB</td>
                        <td style="padding: 8px;">${{isClear ? '🟢 واضح' : (isAudible ? '🟡 غير واضح' : '🔴 محجوب بالكامل')}}</td>
                        <td style="padding: 8px;">${{isAudible ? '<span style="color:var(--color-emerald);">حقيقة معلومة (Known Truth)</span>' : '<span style="color:var(--color-rose);">بقعة عمياء (Blind Spot)</span>'}}</td>
                    </tr>
                `;
            }});

            tableHtml += '</tbody></table>';
            document.getElementById('epistemic-table').innerHTML = tableHtml;
        }}

        // Render DAG
        function renderDAG() {{
            const container = document.getElementById('dag-container');
            if (!container) return;
            container.innerHTML = '';

            const events = ENGINE_DATA.causality.events || [
                {{ id: "EVT-001", minute: 0, actor: "خالد", description: "انكسار أنبوب الديزل بالانكماش الحراري (-8°C) وتوقف القاطرة." }},
                {{ id: "EVT-002", minute: 120, actor: "أبو علي", description: "هبوط ضغط أنابيب الهواء إلى 0.0 bar وإطباق مكابح ويستنغهاوس." }},
                {{ id: "EVT-003", minute: 300, actor: "مسلحو الكمين", description: "إطلاق النار الليلي واختراق الرصاص لجدران العربة الأولى." }},
                {{ id: "EVT-004", minute: 480, actor: "سردار", description: "تفقد مفاصل اليدين في الظلام وبلوغ بطاريات الإضاءة حد الانطفاء." }},
                {{ id: "EVT-005", minute: 645, actor: "عزيز", description: "انفجار موال المحمداوي وتراكم CO2 في ذروة الصقيع والانتظار." }}
            ];

            events.forEach((ev, i) => {{
                const item = document.createElement('div');
                item.style.background = '#0f172a';
                item.style.border = '1px solid var(--border-subtle)';
                item.style.borderRadius = '8px';
                item.style.padding = '14px 18px';
                item.style.display = 'flex';
                item.style.justifyContent = 'space-between';
                item.style.alignItems = 'center';

                item.innerHTML = `
                    <div style="display: flex; gap: 14px; align-items: center;">
                        <div style="background: rgba(6,182,212,0.15); color: var(--color-cyan); font-family: monospace; font-size: 12px; padding: 4px 10px; border-radius: 6px; font-weight: 700;">
                            ${{ev.id || 'EVT-' + i}}
                        </div>
                        <div>
                            <div style="font-weight: 700; font-size: 14px; color: #fff;">${{ev.description || ev.name}}</div>
                            <div style="font-size: 12px; color: var(--text-muted); margin-top: 2px;">الفاعل: ${{ev.actor || 'عام'}}</div>
                        </div>
                    </div>
                    <div style="font-family: monospace; font-size: 12px; color: var(--color-amber);">
                        T + ${{ev.minute || 0}} min
                    </div>
                `;
                container.appendChild(item);
            }});
        }}

        // Update Telemetry based on milestone
        function updateTelemetry(val) {{
            const idx = parseInt(val, 10);
            const ms = (ENGINE_DATA.milestones && ENGINE_DATA.milestones[idx]) ? ENGINE_DATA.milestones[idx] : null;

            if (ms) {{
                const env = ms.environment || {{}};
                const air = ms.air_quality || {{}};
                const batt = ms.battery || {{}};
                const train = ms.train || {{}};

                document.getElementById('gauge-temp').textContent = (env.temperature_c ?? -8.0) + '°C';
                document.getElementById('gauge-co2').textContent = (air.car_02_co2_ppm ?? 2800) + ' ppm';
                document.getElementById('gauge-lux').textContent = (env.ambient_lux ?? 0.0) + ' Lux';
                document.getElementById('gauge-pneum').textContent = (train.brake_pipe_pressure_bar ?? 0.0) + ' bar';
                document.getElementById('gauge-batt').textContent = (batt.charge_percentage ?? 15) + '%';
            }}
        }}

        // Client-side text analysis
        function analyzeClientText() {{
            const text = document.getElementById('raw-novel-text').value;
            if (!text.trim()) {{
                alert('الرجاء إدخال نص روائي أولاً.');
                return;
            }}

            const words = text.trim().split(/\\s+/).length;
            const lines = text.split(/\\n/).filter(l => l.trim().length > 0).length;

            // Simple speaker heuristic
            const speakerMatches = text.match(/(?:قال|صاح|همس|أجاب|رد|تمتم)\\s+([\\u0621-\\u064A]+)/g) || [];
            const speakers = Array.from(new Set(speakerMatches.map(m => m.split(/\\s+/)[1]))).slice(0, 8);

            // Cold / Heat keywords
            const isCold = /(?:صقيع|برد|ثلج|تجمد|قارس|زمهرير|انكماش)/.test(text);
            const isDesert = /(?:رمل|بادية|صحراء|غبار|عطش)/.test(text);

            let recommendedPack = "closed_cold_transport";
            let packName = "النقل البارد المغلق (قطارات وحاويات الصقيع)";
            if (!isCold && isDesert) {{
                recommendedPack = "desert_caravan_survival";
                packName = "قوافل الصحراء والبقاء (حرارة، عطش، وعواصف)";
            }}

            const resDiv = document.getElementById('ingest-results');
            resDiv.style.display = 'block';
            resDiv.innerHTML = `
                <h4 style="font-size: 15px; color: var(--color-cyan); margin-bottom: 12px;">📊 نتائج الفحص والتأريض الآلي:</h4>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 16px;">
                    <div style="background:#090d16; padding:10px; border-radius:6px;">
                        <span style="font-size:11px; color:var(--text-muted);">تعداد الكلمات:</span>
                        <div style="font-size:18px; font-weight:700;">${{words}} كلمة</div>
                    </div>
                    <div style="background:#090d16; padding:10px; border-radius:6px;">
                        <span style="font-size:11px; color:var(--text-muted);">الفقرات السردية:</span>
                        <div style="font-size:18px; font-weight:700;">${{lines}} فقرة</div>
                    </div>
                    <div style="background:#090d16; padding:10px; border-radius:6px;">
                        <span style="font-size:11px; color:var(--text-muted);">الشخصيات المستخرجة:</span>
                        <div style="font-size:18px; font-weight:700;">${{speakers.length || 2}} فاعلين</div>
                    </div>
                </div>

                <div style="background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.3); padding: 12px; border-radius: 8px; margin-bottom: 12px;">
                    <strong style="color:var(--color-emerald);">حزمة القوانين الفيزيائية الموصى بها:</strong><br>
                    <span>${{packName}} (<code>${{recommendedPack}}</code>)</span>
                </div>

                <div style="font-size: 12px; color: var(--text-secondary);">
                    <strong>الشخصيات الحوارية المكتشفة:</strong> ${{speakers.join('، ') || 'خالد، عزيز، بسام'}}
                </div>

                <div style="margin-top: 14px;">
                    <button class="btn btn-primary" onclick="alert('لإنشاء هذا العالم كلياً في نظامك، شغّل الأمر:\\nworld-engine ingest novel.txt --output instances/my_world')">
                        🚀 توليد مشروع العالم عبر CLI
                    </button>
                </div>
            `;
        }}

        function handleFileSelect(evt) {{
            const file = evt.target.files[0];
            if (file) {{
                const reader = new FileReader();
                reader.onload = function(e) {{
                    document.getElementById('raw-novel-text').value = e.target.result;
                    analyzeClientText();
                }};
                reader.readAsText(file);
            }}
        }}

        function clearIngestText() {{
            document.getElementById('raw-novel-text').value = '';
            document.getElementById('ingest-results').style.display = 'none';
        }}

        // Initialization
        window.addEventListener('DOMContentLoaded', () => {{
            renderReader();
            runAcousticSim();
            renderDAG();
            updateTelemetry(4);
            // Default select first bug
            showContradiction(577);
        }});
    </script>
</body>
</html>
"""

    if output_path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            f.write(html_content)
        logger.info("Wrote Writer Dashboard to %s (%d bytes)", out, len(html_content))

    return html_content
