"""
World Engine Obsidian Vault Generator.
======================================
Automated generator of rich, connected Obsidian vaults from world manifests,
entities, causality graphs, rules, and physical state representations.

Features:
- Complete .obsidian configuration (Graph View color groups, app preferences).
- Wikilink-rich notes for Characters, Locations, Laws, Events, and Props.
- Frontmatter metadata for Obsidian Dataview and semantic queries.
- Standalone Markdown fallback tables for instant rendering without plugins.
- Bi-directional linking across characters, locations, events, and physical laws.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import yaml

logger = logging.getLogger("world_engine.vault_generator")


def _sanitize_filename(name: str) -> str:
    """Sanitize note filename for OS and Obsidian link compatibility."""
    cleaned = re.sub(r'[\\/*?:"<>|]', "", name).strip()
    return cleaned.replace(" ", "_") if cleaned else "ملاحظة"


class ObsidianVaultGenerator:
    """Generates a complete Obsidian Vault from a World Engine instance or data dictionary."""

    def __init__(
        self,
        instance_dir: Optional[str | Path] = None,
        world_data: Optional[Dict[str, Any]] = None,
    ):
        self.instance_dir = Path(instance_dir) if instance_dir else None
        self.data: Dict[str, Any] = world_data or {}

        if self.instance_dir and not self.data:
            self._load_from_instance(self.instance_dir)

    def _load_from_instance(self, path: Path) -> None:
        """Load manifest, entities, rules, causality, and state from an instance directory."""
        manifest_file = path / "world_manifest.yaml"
        if manifest_file.exists():
            with open(manifest_file, "r", encoding="utf-8") as f:
                self.data["manifest"] = yaml.safe_load(f) or {}

        entities_file = path / "entities_catalog.yaml"
        if entities_file.exists():
            with open(entities_file, "r", encoding="utf-8") as f:
                self.data["entities"] = yaml.safe_load(f) or {}

        rules_file = path / "rules_manifest.yaml"
        if rules_file.exists():
            with open(rules_file, "r", encoding="utf-8") as f:
                self.data["rules"] = yaml.safe_load(f) or {}

        causality_file = path / "causality_graph.yaml"
        if causality_file.exists():
            with open(causality_file, "r", encoding="utf-8") as f:
                self.data["causality"] = yaml.safe_load(f) or {}

        state_file = path / "world_state.yaml"
        if state_file.exists():
            with open(state_file, "r", encoding="utf-8") as f:
                self.data["state"] = yaml.safe_load(f) or {}

    def export(self, output_dir: str | Path) -> Dict[str, Any]:
        """Export the vault to the specified directory.

        Returns summary statistics of created notes.
        """
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        stats = {
            "characters": 0,
            "locations": 0,
            "laws": 0,
            "events": 0,
            "props": 0,
            "total_notes": 0,
        }

        # 1. Setup .obsidian config
        self._write_obsidian_config(out_path)

        # 2. Setup folder hierarchy
        dirs = {
            "characters": out_path / "Characters",
            "locations": out_path / "Locations",
            "laws": out_path / "Laws",
            "events": out_path / "Events",
            "props": out_path / "Props",
        }
        for d in dirs.values():
            d.mkdir(parents=True, exist_ok=True)

        # 3. Generate individual notes
        char_notes = self._generate_character_notes(dirs["characters"])
        stats["characters"] = len(char_notes)

        loc_notes = self._generate_location_notes(dirs["locations"])
        stats["locations"] = len(loc_notes)

        law_notes = self._generate_law_notes(dirs["laws"])
        stats["laws"] = len(law_notes)

        evt_notes = self._generate_event_notes(dirs["events"])
        stats["events"] = len(evt_notes)

        prop_notes = self._generate_prop_notes(dirs["props"])
        stats["props"] = len(prop_notes)

        # 4. Generate Master Dashboard
        self._generate_dashboard(out_path, stats)
        stats["total_notes"] = sum(stats.values()) + 1  # include dashboard

        return stats

    def _write_obsidian_config(self, out_path: Path) -> None:
        """Write .obsidian settings, graph view colors, and app configurations."""
        obsidian_dir = out_path / ".obsidian"
        obsidian_dir.mkdir(parents=True, exist_ok=True)

        app_config = {
            "useMarkdownLinks": False,
            "showLineNumber": True,
            "livePreview": True,
            "defaultViewMode": "preview",
        }
        with open(obsidian_dir / "app.json", "w", encoding="utf-8") as f:
            json.dump(app_config, f, indent=2)

        # Graph color groups: green for characters, blue for locations, red for laws, purple for events, yellow for props
        graph_config = {
            "collapse-filter": False,
            "search": "",
            "colorGroups": [
                {"query": 'tag:#character or path:"Characters"', "color": {"a": 1, "rgb": 4905322}},     # Emerald Green
                {"query": 'tag:#location or path:"Locations"', "color": {"a": 1, "rgb": 3647214}},       # Cyan/Blue
                {"query": 'tag:#law or path:"Laws"', "color": {"a": 1, "rgb": 15024467}},                # Crimson/Orange
                {"query": 'tag:#event or path:"Events"', "color": {"a": 1, "rgb": 10565860}},             # Purple
                {"query": 'tag:#prop or path:"Props"', "color": {"a": 1, "rgb": 15588373}},               # Gold/Amber
            ],
            "lineSizeMultiplier": 1.2,
            "nodeSizeMultiplier": 1.1,
            "forces": {
                "textFadeMultiplier": 0,
                "nodeStrength": -30,
                "linkDistance": 45,
                "linkStrength": 1,
                "centerStrength": 0.5,
            },
        }
        with open(obsidian_dir / "graph.json", "w", encoding="utf-8") as f:
            json.dump(graph_config, f, indent=2)

    def _generate_character_notes(self, char_dir: Path) -> List[str]:
        """Generate markdown notes for each character."""
        created = []
        entities = self.data.get("entities", {})
        chars = entities.get("characters", [])
        state_chars = self.data.get("state", {}).get("characters", {})

        # If characters is a dict, convert to list
        if isinstance(chars, dict):
            chars_list = []
            for cid, cval in chars.items():
                if isinstance(cval, dict):
                    cval["id"] = cid
                    chars_list.append(cval)
                else:
                    chars_list.append({"id": cid, "name": str(cval)})
            chars = chars_list

        for char in chars:
            props_data = char.get("properties", {}) if isinstance(char, dict) else {}
            cid = char.get("entity_id") or char.get("id") or char.get("canonical_name") or char.get("name", "unknown")
            name = char.get("canonical_name") or char.get("name") or cid
            filename = _sanitize_filename(name) + ".md"

            # Merge with state info if present
            s_char = state_chars.get(cid, {}) if isinstance(state_chars, dict) else {}
            tier = char.get("tier") or props_data.get("tier") or s_char.get("agency_type", "primary_agent")
            loc_id = s_char.get("current_location") or char.get("location_id") or char.get("location") or "العربة_الأولى"
            loc_link = f"[[{_sanitize_filename(loc_id)}]]"

            tic = char.get("tic") or props_data.get("tic") or s_char.get("behavioral_tic", "غير محدد")
            role = char.get("role") or props_data.get("role", "شخصية سردية")
            status = s_char.get("status", "حي")
            known_truths = s_char.get("known_truths", [])
            blind_spots = s_char.get("blind_spots", [])
            affordance = s_char.get("occupied_affordance_slot") or char.get("slot", "حيز حر")

            # Frontmatter
            lines = [
                "---",
                f'id: "{cid}"',
                f'name: "{name}"',
                'type: "character"',
                f'tier: "{tier}"',
                f'location: "{loc_link}"',
                f'role: "{role}"',
                f'tic: "{tic}"',
                f'status: "{status}"',
                "tags:",
                "  - character",
                f"  - character/{tier}",
                "---",
                "",
                f"# {name}",
                "",
                f"> **الدور والمهنة:** {role}  ",
                f"> **الموقع الراهن:** {loc_link} (`{affordance}`)  ",
                f"> **الحالة الحيوية:** {status}  ",
                f"> **اللازمة السلوكية القهرية (Tic):** {tic}  ",
                "",
                "## 1. السمات والمتاحيات الظاهراتية (Phenomenological Traits)",
                f"- **المستوى السردي:** `{tier}`",
                f"- **الحيز المشغول:** `{affordance}`",
                f"- **اللازمة القهرية:** `{tic}`",
                "",
                "## 2. الحقل الإبستيمي والمعرفي (Epistemic Matrix)",
                "### ما يعلمه الفاعل يقيناً (Known Truths):",
            ]

            if known_truths:
                for kt in known_truths:
                    lines.append(f"- ✅ `{kt}`")
            else:
                lines.append("- *(محدود بحدود الرؤية والسمع المباشرة في حيزه)*")

            lines.extend([
                "",
                "### البقع العمياء والمحجوبات (Blind Spots):",
            ])
            if blind_spots:
                for bs in blind_spots:
                    lines.append(f"- ❌ `{bs}`")
            else:
                lines.append("- *(لا توجد بقع عمياء مفصولة حرجة مسجلة)*")

            lines.extend([
                "",
                "## 3. الشبكة السيميائية والروابط",
                f"- **الموقع الفيزيائي:** {loc_link}",
                "- **القوانين الحاكمة لحالته:** [[LAW-BIO-01]], [[LAW-PSYCH-01]]",
                "",
                "---",
                f"*وثيقة مستخرجة آلياً بواسطة World Engine - {name}*",
            ])

            with open(char_dir / filename, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            created.append(filename)

        return created

    def _generate_location_notes(self, loc_dir: Path) -> List[str]:
        """Generate markdown notes for each location/zone."""
        created = []
        manifest = self.data.get("manifest", {})
        topo = manifest.get("spatial_topology", {})
        zones = topo.get("zones", [])

        # Fallback zones if none defined in manifest
        if not zones:
            zones = [
                {"id": "locomotive_cab", "name": "كابينة القاطرة", "type": "cab", "length_m": 8.0},
                {"id": "car_01", "name": "العربة الأولى", "type": "passenger_guards", "length_m": 16.5},
                {"id": "car_02", "name": "العربة الثانية (الوسطى)", "type": "passenger_cohort", "length_m": 16.5},
                {"id": "car_03", "name": "العربة الثالثة (الأخيرة)", "type": "caboose_rear", "length_m": 16.4},
            ]

        for i, zone in enumerate(zones):
            zid = zone.get("id", f"zone_{i}")
            name = zone.get("name") or zid
            filename = _sanitize_filename(name) + ".md"

            ztype = zone.get("type", "interior_compartment")
            length = zone.get("length_m", 15.0)

            # Link adjacent zones
            prev_link = f"[[{_sanitize_filename(zones[i-1]['name'])}]]" if i > 0 else "*(نهاية المغلف)*"
            next_link = f"[[{_sanitize_filename(zones[i+1]['name'])}]]" if i < len(zones) - 1 else "*(نهاية المغلف)*"

            lines = [
                "---",
                f'id: "{zid}"',
                f'name: "{name}"',
                'type: "location"',
                f'zone_type: "{ztype}"',
                f'length_m: {length}',
                "tags:",
                "  - location",
                f"  - location/{ztype}",
                "---",
                "",
                f"# {name}",
                "",
                f"> **المعرف الفضائي:** `{zid}`  ",
                f"> **النوع الطوبولوجي:** `{ztype}`  ",
                f"> **الطول المتري:** `{length} m`  ",
                "",
                "## 1. الطوبولوجيا والجوار المكاني",
                f"- **المحطة السابقة / جهة الأمام:** {prev_link}",
                f"- **المحطة التالية / جهة الخلف:** {next_link}",
                "- **التوهين الصوتي عبر الحواجز:** `~20 dB` لكل فاصل فولاذي مقفل.",
                "",
                "## 2. الثوابت الفيزيائية والمناخية للغلاف",
                "- **درجة الحرارة الأساسية:** `-8.0°C`",
                "- **الإضاءة:** `0.0 Lux` (عتمة صقيعية دامسة)",
                "- **القوانين الحاكمة:** [[LAW-ACOUST-03]], [[LAW-ACOUST-04]], [[LAW-THERMO-01]], [[LAW-BIO-06]]",
                "",
                "## 3. الشاغلون والمتاحيات الإدراكية (Occupants & Affordances)",
                "- *يتم تتبع تواجد الفاعلين داخل هذه المنطقة استناداً لسجل الحالة الفيزيائية الحية.*",
                "",
                "---",
                f"*سجل الحيز المكاني - {name}*",
            ]

            with open(loc_dir / filename, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            created.append(filename)

        return created

    def _generate_law_notes(self, law_dir: Path) -> List[str]:
        """Generate markdown notes for each physical and systemic law."""
        created = []
        rules = self.data.get("rules", {}).get("rules", [])

        # If rules is empty, provide baseline physical laws
        if not rules:
            rules = [
                {"id": "LAW-THERMO-01", "name": "الانكماش الحراري والتجمد", "domain": "thermodynamics", "severity": "critical", "description": "انخفاض الحرارة لما دون -8C يؤدي لتجمد السوائل وانكماش المعادن."},
                {"id": "LAW-ACOUST-03", "name": "العزل الصوتي بين العربات", "domain": "acoustics", "severity": "major", "description": "الحواجز الفولاذية تخمد الصوت بأكثر من 35 dB مانعة انتقال الهمس والحديث."},
                {"id": "LAW-ACOUST-04", "name": "التوصيل الصوتي الهيكلي الميكانيكي", "domain": "acoustics", "severity": "major", "description": "الصدمات الميكانيكية المباشرة على الفولاذ تنتقل عبر كامل طول القطار بسرعة 5000 m/s."},
                {"id": "LAW-BIO-01", "name": "التجمد ونقص التروية البيولوجية", "domain": "biology", "severity": "critical", "description": "التعرض المستمر لدرجات الصفر المطلق يسبب اصطكاك الأسنان وتصلب الأصابع والهلع."},
                {"id": "LAW-BIO-06", "name": "ديناميكا الهواء الحبيس وتراكم CO2", "domain": "biology", "severity": "major", "description": "التنفس المستمر لـ 14 فرداً في حيز مغلق يرفع تركيز CO2 ويسبب تبلد الإدراك."},
                {"id": "LAW-PSYCH-01", "name": "تفتت الحوار تحت الهلع", "domain": "psychology", "severity": "medium", "description": "تفكك البنية النحوية للجمل وتحولها إلى شظايا لغوية عند تصاعد الخطر الحتمي."},
            ]

        for rule in rules:
            rid = rule.get("id", "LAW-GENERIC")
            name = rule.get("name") or rid
            filename = _sanitize_filename(rid) + ".md"

            domain = rule.get("domain", "physics")
            severity = rule.get("severity", "critical")
            desc = rule.get("description", "قانون حاكم للعالم.")
            invariant = rule.get("invariant") or rule.get("condition") or "حتمي وغير قابل للمخالفة"

            lines = [
                "---",
                f'id: "{rid}"',
                f'name: "{name}"',
                'type: "law"',
                f'domain: "{domain}"',
                f'severity: "{severity}"',
                "tags:",
                "  - law",
                f"  - law/{domain}",
                f"  - severity/{severity}",
                "---",
                "",
                f"# {rid}: {name}",
                "",
                f"> **المجال العلمي:** `{domain}`  ",
                f"> **مستوى الصرامة:** `{severity}`  ",
                "",
                "## 1. الصياغة المنظومية (Systemic Definition)",
                desc,
                "",
                "## 2. الثابت الرياضي / الحتمي (Mathematical Invariant)",
                "```yaml",
                f"invariant_check: \"{invariant}\"",
                "```",
                "",
                "## 3. الأثر على السرد والفضاء الإبداعي",
                "- **التوافق مع ميثاق الحياد الإبداعي:** هذا القانون أداة فحص لاتساق العالم الموضوعي ولا يفرض أسلوباً لغوياً على الكاتب.",
                f"- **الكيانات الخاضعة له:** كافة الشخصيات [[Characters]] والمواقع المتأثرة بمجال `{domain}`.",
                "",
                "---",
                f"*دستور القوانين الحتمية - World Engine*",
            ]

            with open(law_dir / filename, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            created.append(filename)

        return created

    def _generate_event_notes(self, evt_dir: Path) -> List[str]:
        """Generate markdown notes for each causal event in the DAG."""
        created = []
        causality = self.data.get("causality", {})
        events = causality.get("events", [])

        # If causality events is a dict, convert to list
        if isinstance(events, dict):
            ev_list = []
            for eid, evalue in events.items():
                if isinstance(evalue, dict):
                    evalue["id"] = eid
                    ev_list.append(evalue)
                else:
                    ev_list.append({"id": eid, "description": str(evalue)})
            events = ev_list

        for ev in events:
            eid = ev.get("id", "EVT-00")
            desc = ev.get("description") or ev.get("name") or eid
            filename = _sanitize_filename(eid) + ".md"

            minute = ev.get("minute", 0)
            actor = ev.get("actor", "فاعل عام")
            actor_link = f"[[{_sanitize_filename(actor)}]]"
            causes = ev.get("causes", [])
            caused_by = ev.get("caused_by") or ev.get("dependencies", [])

            lines = [
                "---",
                f'id: "{eid}"',
                f'minute: {minute}',
                f'actor: "{actor_link}"',
                'type: "event"',
                "tags:",
                "  - event",
                "  - causality/dag",
                "---",
                "",
                f"# {eid}: {desc}",
                "",
                f"> **التوقيت النسبي:** الدقيقة `{minute}`  ",
                f"> **الفاعل الرئيسي:** {actor_link}  ",
                "",
                "## 1. التوصيف السردي للحدث",
                desc,
                "",
                "## 2. المسار السببي في شبكة DAG",
                "### الأسباب السابقة (Caused By / Dependencies):",
            ]

            if caused_by:
                for c in caused_by:
                    c_link = f"[[{_sanitize_filename(str(c))}]]"
                    lines.append(f"- ⬅️ سبب ناتج عن: {c_link}")
            else:
                lines.append("- *(حدث أولي / جذر سببي Initial Root)*")

            lines.extend([
                "",
                "### النتائج اللاحقة (Leads To / Causes):",
            ])

            if causes:
                for target in causes:
                    t_link = f"[[{_sanitize_filename(str(target))}]]"
                    lines.append(f"- ➡️ يؤدي بحتمية إلى: {t_link}")
            else:
                lines.append("- *(نقطة توازن نهائية / طرف سببي Leaf Node)*")

            lines.extend([
                "",
                "---",
                f"*سجل شبكة السببية - {eid}*",
            ])

            with open(evt_dir / filename, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            created.append(filename)

        return created

    def _generate_prop_notes(self, prop_dir: Path) -> List[str]:
        """Generate markdown notes for props and critical equipment."""
        created = []
        entities = self.data.get("entities", {})
        props = entities.get("props", [])

        # If props is a dict, convert
        if isinstance(props, dict):
            plist = []
            for pid, pval in props.items():
                if isinstance(pval, dict):
                    pval["id"] = pid
                    plist.append(pval)
                else:
                    plist.append({"id": pid, "name": str(pval)})
            props = plist

        for p in props:
            props_data = p.get("properties", {}) if isinstance(p, dict) else {}
            pid = p.get("entity_id") or p.get("id") or p.get("canonical_name") or p.get("name", "prop")
            name = p.get("canonical_name") or p.get("name") or pid
            filename = _sanitize_filename(name) + ".md"

            owner = p.get("owner") or props_data.get("holder") or props_data.get("owner") or "غير معين"
            owner_link = f"[[{_sanitize_filename(owner)}]]" if owner != "غير معين" else "*(متاح في البيئة)*"
            ptype = p.get("category") or p.get("type", "أداة / عتاد")

            lines = [
                "---",
                f'id: "{pid}"',
                f'name: "{name}"',
                'type: "prop"',
                f'owner: "{owner_link}"',
                "tags:",
                "  - prop",
                "---",
                "",
                f"# {name}",
                "",
                f"> **النوع:** `{ptype}`  ",
                f"> **الحائز / المالك:** {owner_link}  ",
                "",
                "## 1. التوصيف المادي والسيميائي",
                f"أداة مادية مرتبطة بحركة الشخصيات وسياق العالم الحتمي.",
                "",
                "## 2. الثوابت الفيزيائية والمادية",
                "- تخضع لقوانين انحدار كفاءة المواد في الصقيع [[LAW-MAT-01]].",
                "",
                "---",
                f"*سجل العتاد والمقتنيات - {name}*",
            ]

            with open(prop_dir / filename, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            created.append(filename)

        return created

    def _generate_dashboard(self, out_path: Path, stats: Dict[str, int]) -> None:
        """Generate the main entry dashboard (00_World_Dashboard.md)."""
        manifest = self.data.get("manifest", {})
        title = manifest.get("title", "عالم سردي مؤرض")
        genre = manifest.get("genre", "نوفيلا تراجيدية وجودية")
        chrono = manifest.get("chronotope", {})
        time_setting = chrono.get("temporal_bounds") or chrono.get("time_range") or "ليلة شتوية قارسة"
        spatial_setting = chrono.get("spatial_scope") or "مغلف قطار مغلق في البادية"

        lines = [
            "---",
            f'title: "{title}"',
            'type: "dashboard"',
            "tags:",
            "  - dashboard",
            "  - world_engine",
            "---",
            "",
            f"# 🌐 لوحة تحكم العالم السردي: «{title}»",
            "",
            "> [!NOTE] ميثاق الحياد الإبداعي",
            "> **«نحن نُحلل ونُقيّم.. ولا نُقوّم»** — هذا المستودع تم توليده آلياً بواسطة **نظام تشغيل العوالم السردية (World Engine)** لرصد اتساق القوانين الفيزيائية والشبكة السببية ومصفوفة المتاحيات دون أي تدخل في الصياغة الأدبية للكاتب.",
            "",
            "## 📊 إحصاءات الكينونة والمعمار",
            "",
            "| المكون المعرفي | العدد الكلي | المسار في المستودع |",
            "| :--- | :---: | :--- |",
            f"| 👥 **الشخصيات والفاعلون** | `{stats['characters']}` | `Characters/` |",
            f"| 📍 **المواقع والفضاءات** | `{stats['locations']}` | `Locations/` |",
            f"| ⚖️ **القوانين الفيزيائية الحاكمة** | `{stats['laws']}` | `Laws/` |",
            f"| ⛓️ **أحداث شبكة السببية (DAG)** | `{stats['events']}` | `Events/` |",
            f"| 🗝️ **المقتنيات والعتاد المادي** | `{stats['props']}` | `Props/` |",
            "",
            "---",
            "",
            "## 🧭 الإطار الزمكاني الحتمي (Chronotope)",
            f"- **النوع الأدبي:** `{genre}`",
            f"- **الإطار الزمني:** `{time_setting}`",
            f"- **الفضاء المكاني:** `{spatial_setting}`",
            "- **درجة الحرارة الأساسية:** `-8.0°C` | **الإضاءة:** `0.0 Lux`",
            "",
            "---",
            "",
            "## 🗺️ روابط الدخول السريع (Navigation)",
            "- 🔍 **عرض الغراف التفاعلي:** اضغط `Ctrl + G` داخل Obsidian لتشاهد الشبكة الملونة الحية.",
            "- 👥 **استكشاف الشخصيات:** افتح مجلد `Characters/` لتصفح متاحيات كل بطل وحقله الإبستيمي.",
            "- ⚖️ **دستور القوانين:** تصفح `Laws/` لمعرفة الشروط الفيزيائية الصارمة لبيئة الرواية.",
            "- ⛓️ **شبكة السببية:** تصفح `Events/` لمراجعة تسلسل الأسباب والنتائج دون أي تكرار أو دورات ممتنعة.",
            "",
            "```dataview",
            "TABLE role, location, status, tic",
            'FROM "Characters"',
            "SORT file.name ASC",
            "```",
            "",
            "---",
            f"*تم التصدير بنجاح بواسطة World Engine v2.5.0*",
        ]

        with open(out_path / "00_لوحة_تحكم_العالم.md", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
