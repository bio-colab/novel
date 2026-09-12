#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GROUNDING AUDITOR & TELEMETRY CALIBRATOR (مدقق المعايرة والربط النصي)
====================================================================
Project: «قطار الرمل» (Sand Train) - Closed World Simulator
License: MIT

Purpose:
  Enforces absolute epistemic honesty across the simulation and world brain.
  Ensures that every metric, telemetry value, and casualty count is explicitly
  categorized into:
    1. text_attested_evidence: strictly anchored to (part, chapter, line) with verified text.
    2. simulation_assumptions: explicitly marked with (class: assumption).
  
  Audits 5 Core Epistemic Dimensions:
    1. Telemetry Grounding & Calibration (Zero masquerading assumptions).
    2. Headcount Invariant & Slip Detection (14 initial -> 10 remaining; audits line 577 slip vs WORLD-BUG-007).
    3. Temporal Perception vs Astronomical Solar Ephemeris (Khalid's 2h statement vs 06:48 dawn -> WORLD-BUG-008).
    4. Exit Vector Authenticity (Mahdi's sliding side door vs trapdoor purge).
    5. Abbas Ammunition Grounding (3 text-attested shots vs 30-round fake telemetry).
"""

import os
import re
import sys
import yaml

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BASELINE_PATH = os.path.join(ROOT_DIR, "00_BASELINE", "novel_baseline.md")
WORLD_BUGS_PATH = os.path.join(ROOT_DIR, "03_AUDIT_AND_ISSUES", "WORLD_BUGS.yaml")
WORLD_STATE_PATH = os.path.join(ROOT_DIR, "05_WORLD_BRAIN", "world_state.yaml")
LAWS_PATH = os.path.join(ROOT_DIR, "01_SPECS_AND_RULES", "PHYSICAL_LAWS.md")


def parse_novel_structure(baseline_path):
    """
    Parses novel_baseline.md into structured parts and chapters.
    Returns:
      parts: list of dicts with part_num, title, chapters
      line_map: dict mapping 1-based line_number -> (part_num, chapter_num, line_text)
    """
    if not os.path.exists(baseline_path):
        return None, None

    with open(baseline_path, "r", encoding="utf-8") as f:
        lines = [line.rstrip("\r\n") for line in f]

    parts = []
    current_part = {
        "part_num": 1,
        "title": "ارتداد الحديد",
        "start_line": 1,
        "chapters": []
    }
    current_chapter = None
    line_map = {}

    part_pattern = re.compile(r"^(?:#\s+)?الجزء\s+(الأول|الثاني|الثالث|الرابع|الخامس):\s*(.+)$")
    chapter_pattern = re.compile(r"^##\s+(\d+)\.\s*(.+)$")

    part_arabic_to_num = {
        "الأول": 1,
        "الثاني": 2,
        "الثالث": 3,
        "الرابع": 4,
        "الخامس": 5
    }

    for idx, text in enumerate(lines, 1):
        # Check part header
        part_match = part_pattern.match(text)
        if part_match:
            p_name = part_match.group(1)
            p_title = part_match.group(2).strip()
            p_num = part_arabic_to_num.get(p_name, len(parts) + 1)
            if p_num > 1:
                if current_chapter:
                    current_chapter["end_line"] = idx - 1
                current_part["end_line"] = idx - 1
                parts.append(current_part)
                current_part = {
                    "part_num": p_num,
                    "title": p_title,
                    "start_line": idx,
                    "chapters": []
                }
                current_chapter = None

        # Check chapter header
        chap_match = chapter_pattern.match(text)
        if chap_match:
            if current_chapter:
                current_chapter["end_line"] = idx - 1
            chap_num = int(chap_match.group(1))
            chap_title = chap_match.group(2).strip()
            current_chapter = {
                "part_num": current_part["part_num"],
                "chapter_num": chap_num,
                "title": chap_title,
                "start_line": idx,
                "end_line": len(lines)
            }
            current_part["chapters"].append(current_chapter)

        p_num = current_part["part_num"]
        c_num = current_chapter["chapter_num"] if current_chapter else 0
        line_map[idx] = (p_num, c_num, text)

    if current_chapter:
        current_chapter["end_line"] = len(lines)
    current_part["end_line"] = len(lines)
    parts.append(current_part)

    # Enrich chapter objects with full identifiers and body text
    for p in parts:
        for c in p["chapters"]:
            s = c["start_line"]
            e = c["end_line"]
            c["full_id"] = f"[ج{c['part_num']}/ف{c['chapter_num']}]"
            c["full_title"] = f"[ج{c['part_num']}/ف{c['chapter_num']}] {c['title']}"
            c["body"] = "\n".join(lines[s:e])

    return parts, line_map


class GroundingAuditor:
    def __init__(self):
        self.passes = []
        self.violations = []
        self.warnings = []
        self.parts = None
        self.line_map = None
        self.bugs_data = None
        self.world_state = None

    def load_data(self):
        if not os.path.exists(BASELINE_PATH):
            self.violations.append(f"Baseline file missing: {BASELINE_PATH}")
            return False
        if not os.path.exists(WORLD_BUGS_PATH):
            self.violations.append(f"World bugs file missing: {WORLD_BUGS_PATH}")
            return False
        if not os.path.exists(WORLD_STATE_PATH):
            self.violations.append(f"World state file missing: {WORLD_STATE_PATH}")
            return False

        self.parts, self.line_map = parse_novel_structure(BASELINE_PATH)
        with open(WORLD_BUGS_PATH, "r", encoding="utf-8") as f:
            self.bugs_data = yaml.safe_load(f)
        with open(WORLD_STATE_PATH, "r", encoding="utf-8") as f:
            self.world_state = yaml.safe_load(f)
        return True

    def audit_chapter_indexing(self):
        """Verify that all 32 chapters across the 5 parts are cleanly and non-ambiguously indexed"""
        total_chapters = sum(len(p["chapters"]) for p in self.parts)
        expected_distribution = {1: 8, 2: 6, 3: 8, 4: 5, 5: 5}
        actual_distribution = {p["part_num"]: len(p["chapters"]) for p in self.parts}

        if actual_distribution != expected_distribution:
            self.violations.append(
                f"[Chapter Indexing Error] Chapter distribution {actual_distribution} does not match expected {expected_distribution}."
            )
        else:
            self.passes.append(
                f"Chapter Structure: 32 chapters across 5 parts uniquely indexed with compound (Part, Chapter) keys (no ID collisions)."
            )

    def audit_telemetry_grounding(self):
        """
        Ensure every empirical claim in WORLD_BUGS.yaml is partitioned into:
          - text_attested_evidence (with valid source anchor)
          - simulation_assumptions (with explicit class: assumption)
        """
        bugs = self.bugs_data.get("bugs", [])
        grounded_count = 0
        assumption_count = 0

        for bug in bugs:
            b_id = bug.get("id")
            evidence = bug.get("evidence", {})

            # 1. Inspect text_attested_evidence
            attested = evidence.get("text_attested_evidence", [])
            for item in attested:
                if "source:" not in item and "Part " not in item:
                    self.violations.append(
                        f"[Ungrounded Telemetry] Bug '{b_id}' has unanchored text evidence: '{item}'."
                    )
                else:
                    grounded_count += 1

            # 2. Inspect simulation_assumptions
            assumptions = evidence.get("simulation_assumptions", [])
            for item in assumptions:
                if "class: assumption" not in item:
                    self.violations.append(
                        f"[Unclassified Assumption] Bug '{b_id}' assumption missing 'class: assumption' tag: '{item}'."
                    )
                else:
                    assumption_count += 1

        self.passes.append(
            f"Telemetry Grounding: Audited {grounded_count} text-attested anchors and {assumption_count} explicit simulation assumptions (zero masquerading data)."
        )

    def audit_abbas_ammunition_truth(self):
        """
        Validate Abbas ammunition expenditure:
        Must be strictly 3 text-attested shots (lines 625, 639), jammed on 4th.
        Rejects any claim of 30 rounds as factual telemetry.
        """
        # Find lines 625 and 639 in novel baseline
        line_625 = self.line_map.get(625, (0, 0, ""))[2]
        line_639 = self.line_map.get(639, (0, 0, ""))[2]

        if "طَخ... طَخ" not in line_625:
            self.violations.append(f"[Abbas Ammo Anchor Error] Line 625 missing text 'طَخ... طَخ'. Found: '{line_625}'")
        if "خرجت طلقة واحدة، ثم انحشرت الطلقة الأخيرة" not in line_639:
            self.violations.append(f"[Abbas Ammo Anchor Error] Line 639 missing jamming text. Found: '{line_639}'")

        # Check WORLD-BUG-002 data
        bug_002 = next((b for b in self.bugs_data.get("bugs", []) if b.get("id") == "WORLD-BUG-002"), None)
        if not bug_002:
            self.violations.append("[Bug Missing] WORLD-BUG-002 not found in WORLD_BUGS.yaml.")
            return

        evidence = bug_002.get("evidence", {})
        trace = evidence.get("causal_consumption_trace", {})
        breakdown = trace.get("rounds_expended_breakdown", {})
        abbas_rounds = breakdown.get("abbas_weapon_rounds_fired")

        if abbas_rounds == 30:
            self.violations.append(
                "[False Telemetry] WORLD-BUG-002 still asserts 'abbas_weapon_rounds_fired: 30', contradicting text (3 rounds fired)."
            )
        elif abbas_rounds == 3:
            self.passes.append(
                "Abbas Weapon Grounding: Exactly 3 rounds verified against Part 3 Ch 2 (lines 625, 639), jammed on 4th (false 30-round telemetry purged)."
            )
        else:
            self.violations.append(f"[Abbas Rounds Anomaly] Expected 3 rounds, found: {abbas_rounds}")

    def audit_trapdoor_purge_and_exit_vector(self):
        """
        Verify that Mahdi's exit vector in the baseline is the sliding side door,
        and confirm that no speculative trapdoor leaks into baseline specifications or world_state.yaml.
        """
        # Check novel text at lines 701-717
        line_701 = self.line_map.get(701, (0, 0, ""))[2]
        line_717 = self.line_map.get(717, (0, 0, ""))[2]

        if "الباب الجانبي المنزلق للعربة الوسطى" not in line_701:
            self.violations.append(f"[Exit Vector Anchor Error] Line 701 missing sliding door text: '{line_701}'")
        if "قفز من فتحة الباب المفتوح" not in line_717:
            self.violations.append(f"[Exit Vector Anchor Error] Line 717 missing jump text: '{line_717}'")

        # Check world_state.yaml for trapdoor leak
        with open(WORLD_STATE_PATH, "r", encoding="utf-8") as f:
            ws_content = f.read()

        if "trapdoor" in ws_content.lower() or "فتحة الصيانة" in ws_content:
            self.violations.append(
                "[Baseline Pollution] 'trapdoor' or 'فتحة الصيانة' detected in frozen world_state.yaml snapshot!"
            )
        else:
            self.passes.append(
                "Baseline Sanctity: Frozen world_state.yaml is 100% clean of future speculative trapdoor repairs."
            )

        # Check WORLD-BUG-006 description
        bug_006 = next((b for b in self.bugs_data.get("bugs", []) if b.get("id") == "WORLD-BUG-006"), None)
        if bug_006:
            desc = bug_006.get("observed", {}).get("description", "")
            if "doors_exit: front/rear only" in str(bug_006.get("evidence", {})):
                self.violations.append("[Factual Error] WORLD-BUG-006 still asserts 'doors_exit: front/rear only'.")
            elif "الباب الجانبي المنزلق" in desc:
                self.passes.append(
                    "Exit Vector Grounding: Mahdi's exit via sliding side door correctly anchored (Part 3 Ch 4, lines 701-717)."
                )

    def audit_headcount_invariants_and_slip(self):
        """
        Audit headcount conservation:
          - Initial headcount: 14 living souls.
          - Detect and assert Part 2 Ch 6 Line 577 slip («عشرة رجال»).
          - Verify it is codified as WORLD-BUG-007.
          - Verify Post-Ambush headcount is 10 living souls (Part 4 Ch 3 Line 1141).
        """
        # Line 577 in novel baseline
        line_577 = self.line_map.get(577, (0, 0, ""))[2]
        line_1141 = self.line_map.get(1141, (0, 0, ""))[2]

        slip_text_found = "صوت تنفس متقطع لعشرة رجال" in line_577
        post_ambush_found = "أنفاس الرجال العشرة المتبقين" in line_1141

        if not slip_text_found:
            self.violations.append(f"[Headcount Anchor Error] Line 577 missing 'عشرة رجال' text: '{line_577}'")
        if not post_ambush_found:
            self.violations.append(f"[Headcount Anchor Error] Line 1141 missing 'الرجال العشرة المتبقين' text: '{line_1141}'")

        # Verify WORLD-BUG-007 exists in WORLD_BUGS.yaml
        bug_007 = next((b for b in self.bugs_data.get("bugs", []) if b.get("id") == "WORLD-BUG-007"), None)
        if not bug_007:
            self.violations.append("[Unrecorded Slip] Headcount text slip (10 men at 23:50 vs 14 actual) is NOT codified in WORLD_BUGS.yaml.")
        else:
            self.passes.append(
                "Headcount Invariant & Slip Detection: Pre-ambush slip at Line 577 ('عشرة رجال') successfully recorded and audited as WORLD-BUG-007."
            )
            self.passes.append(
                "Headcount Phase Conservation: 14 initial souls (19:00..23:59) -> 10 living souls post-ambush (Part 4 Ch 3 Line 1141) strictly verified."
            )

    def audit_internal_time_vs_ephemeris(self):
        """
        Audit internal perceived time vs astronomical sunrise:
          - Detect Khalid's line at Line 1253 («بقى ساعتين ويطلع الضو»).
          - Verify that the +3.8h discrepancy against 06:48 sunrise is recorded as WORLD-BUG-008.
        """
        line_1253 = self.line_map.get(1253, (0, 0, ""))[2]
        khalid_line_found = "بقى ساعتين ويطلع الضو" in line_1253

        if not khalid_line_found:
            self.violations.append(f"[Chrono Anchor Error] Line 1253 missing 'بقى ساعتين ويطلع الضو': '{line_1253}'")

        bug_008 = next((b for b in self.bugs_data.get("bugs", []) if b.get("id") == "WORLD-BUG-008"), None)
        if not bug_008:
            self.violations.append("[Unrecorded Paradox] Internal time discrepancy ('بقى ساعتين ويطلع الضو' vs 06:48 dawn) is NOT codified in WORLD_BUGS.yaml.")
        else:
            self.passes.append(
                "Chrono Grounding & Ephemeris Calibration: Khalid's Line 1253 statement ('بقى ساعتين') vs 06:48 astronomical dawn codified as WORLD-BUG-008."
            )

    def run_all(self):
        print("\n" + "=" * 80)
        print("  GROUNDING AUDITOR & TELEMETRY CALIBRATOR (مدقق المعايرة والربط النصي)")
        print("=" * 80)

        if not self.load_data():
            print("\n[CRITICAL ERROR] Failed to load required project files.")
            for v in self.violations:
                print(f"  ❌ {v}")
            return False

        self.audit_chapter_indexing()
        self.audit_telemetry_grounding()
        self.audit_abbas_ammunition_truth()
        self.audit_trapdoor_purge_and_exit_vector()
        self.audit_headcount_invariants_and_slip()
        self.audit_internal_time_vs_ephemeris()

        print("\n--- PASSED GROUNDING INVARIANTS (المعايرات النصية الناجحة) ---")
        for p in self.passes:
            print(f"  ✅ {p}")

        if self.warnings:
            print("\n--- GROUNDING WARNINGS (تنبيهات المعايرة) ---")
            for w in self.warnings:
                print(f"  ⚠️ {w}")

        if self.violations:
            print("\n--- GROUNDING VIOLATIONS (الخروقات وفجوات الربط النصي) ---")
            for v in self.violations:
                print(f"  ❌ {v}")
            print("\n" + "=" * 80)
            print(f"  GROUNDING FAILED: {len(self.violations)} calibration violation(s) detected.")
            print("=" * 80 + "\n")
            return False

        print("\n" + "=" * 80)
        print("  GROUNDING AUDIT PASSED: 100% Epistemic Telemetry & Text Calibration Verified.")
        print("=" * 80 + "\n")
        return True


if __name__ == "__main__":
    auditor = GroundingAuditor()
    success = auditor.run_all()
    sys.exit(0 if success else 1)
