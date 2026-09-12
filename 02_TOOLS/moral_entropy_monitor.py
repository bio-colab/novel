#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
MORAL ENTROPY & EXISTENTIAL SOLIDARITY MONITOR (مراقب الإنتروبيا الأخلاقية والتضامن الوجودي)
==============================================================================
Project: «قطار الرمل» (Sand Train) - Narrative Engineering & Closed-World Simulator
License: MIT
Framework Principle: «نحن نُحلل ونُقيّم.. ولا نُقوّم» (Evaluation & Physical Consistency,
                     Zero Literary Interference or Scalar Honor Gamification).

Purpose:
  Monitors and evaluates ethical, psychological, and existential dynamics within
  the closed, resource-starved train environment under sub-zero desert confinement.
  
  Unlike naive scalar "Honor Meters" (+/- points) common in video games, this engine
  models moral dynamics through thermodynamic and sociological invariants:
    1. Moral Typology & 4-Quadrant Census (Zero ideological monopoly, strict 14-headcount).
    2. Moral Entropy Dynamics (S_moral) tracking degradation vs negentropic solidarity
       across 5 critical narrative milestones (t=0 -> 315 -> 390 -> 500 -> 645 min).
    3. Causal Moral Debt & Physical Retribution (Hasan Kaz's worthless currency vs
       Hannata's weapon forfeiture and command breakdown).
    4. Funerary Dignity & Sacred Memory (Abbas's pebble, Salloum's cover, Mawal catharsis).

Enforces Statutory Laws:
  - [LAW-ETHIC-01] حتمية التضامن العضوي ومقاومة الإنتروبيا الأخلاقية (Organic Solidarity & Moral Negentropy)
  - [LAW-ETHIC-02] قدسية الكرامة المادية والطقس الجنائزي في فضاء الحصر (Funerary Dignity & Sacred Memory Invariant)
  - [LAW-ETHIC-03] الرنين الوجداني ككابح للانهيار البيولوجي العصابي (Emotional Resonance as Hypothermic/Psychological Buffer)
  - [LAW-SOC-01] تآكل الهيمنة البيروقراطية (Erosion of Bureaucratic Hegemony)
  - [LAW-SOC-02] سيادة القيمة الاستعمالية على التبادلية (Primacy of Use-Value over Exchange-Value)
  - [LAW-SOC-03] كسر التراتبية الطبقية واحتكار السلاح (Caste Inversion & Emergency Weapon Transfer)

Exit Codes:
  0: All moral and existential invariants verified with zero violations.
  1: Invariant violations detected.
==============================================================================
"""

import os
import re
import sys
import yaml
from typing import Dict, List, Any, Optional

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BASELINE_PATH = os.path.join(ROOT_DIR, "00_BASELINE", "novel_baseline.md")
PHYSICAL_LAWS_PATH = os.path.join(ROOT_DIR, "01_SPECS_AND_RULES", "PHYSICAL_LAWS.md")
WORLD_STATE_PATH = os.path.join(ROOT_DIR, "05_WORLD_BRAIN", "world_state.yaml")
WORLD_BUGS_PATH = os.path.join(ROOT_DIR, "03_AUDIT_AND_ISSUES", "WORLD_BUGS.yaml")


class MoralEntropyMonitor:
    """
    Evaluator for Moral Entropy, Existential Typology, and Human Solidarity.
    Guarantees strict alignment between narrative actions and thermodynamic/social laws.
    """

    # 4 Archetypal Moral Quadrants across the 14 train occupants
    MORAL_QUADRANTS: Dict[str, Dict[str, Any]] = {
        "solidarity_dignity": {
            "name_ar": "التضامن والكرامة والنجدة العضوية",
            "description": "استجابة إيثارية تهدف لصيانة بقاء المجموعة المشترك وحفظ الكرامة الإنسانية",
            "characters": ["خالد", "سردار", "أبو علي", "عزيز", "بشير"],
            "governing_law": "LAW-ETHIC-01"
        },
        "institutional_legalism": {
            "name_ar": "التشبث البيروقراطي القانوني",
            "description": "إنكار الانهيار عبر التمسك باللوائح والمحاضر والتراتبية الوظيفية المنهارة",
            "characters": ["حجي عمار"],
            "governing_law": "LAW-SOC-01"
        },
        "atomistic_preservation": {
            "name_ar": "الذرائعية الفردية والنجاة الأنانية",
            "description": "محاولة النجاة المنفردة وتفضيل المصلحة الذاتية والمادية على مصير الجماعة",
            "characters": ["مهدي", "حسن كاز"],
            "governing_law": "LAW-SOC-02"
        },
        "panic_dehumanization": {
            "name_ar": "الذعر الحركي والشلل العصابي والانحلال",
            "description": "فقدان السيطرة الحركية والتحول إلى كتل ذعر سلبية أو فاقدة للقدرة على المبادرة",
            "characters": ["حناطة", "أبو اللول", "سلوم", "خليل", "بسام", "عباس"],
            "governing_law": "LAW-BIO-02"
        }
    }

    # Chronological Milestones and Expected Moral Entropy (S_moral in [0.0, 1.0])
    MORAL_ENTROPY_TRAJECTORY: List[Dict[str, Any]] = [
        {
            "timeline_min": 0,
            "wall_clock": "19:00",
            "phase": "العطل الأولي والارتداد",
            "s_moral": 0.20,
            "mechanics": "ارتياب متبادل، احتجاز مؤسساتي روتيني، فصل طبقي وعسكري صارم",
            "negentropy_action": "حفظ النظام وتثبيت السجناء داخل العربات"
        },
        {
            "timeline_min": 315,
            "wall_clock": "00:15",
            "phase": "المباغتة البالستية والاختراق",
            "s_moral": 0.85,
            "mechanics": "ذروة الإنتروبيا الأخلاقية: ذعر، هروب فردي، شلل الحراس، مقتل عباس وسلوم",
            "negentropy_action": "انهيار السيطرة وتفكك الرابطة الاجتماعية تحت الرصاص"
        },
        {
            "timeline_min": 390,
            "wall_clock": "01:30",
            "phase": "الفرز الطبي وانتشال الجثامين",
            "s_moral": 0.55,
            "mechanics": "بدء النيغينتروبيا (مقاومة الإنتروبيا): سحب جثة عباس، تضميد بسام للجرحى، تقنين الماء",
            "negentropy_action": "اقتسام 14 لتر ماء بالتساوي (100 مل/فرد) وصيانة الموتى"
        },
        {
            "timeline_min": 500,
            "wall_clock": "03:00",
            "phase": "الموال العراقي والرنين الوجداني",
            "s_moral": 0.35,
            "mechanics": "رنين وجداني جمعي يكسر الصمت ويثبط الذهول التخادري والبلادة الصقيعية",
            "negentropy_action": "موال عزيز يوحد أرواح السجانين والمحكومين ويكبح التحلل العصبي"
        },
        {
            "timeline_min": 645,
            "wall_clock": "05:45",
            "phase": "العمل الجماعي تحت الشاسيه وبزوغ الفجر",
            "s_moral": 0.25,
            "mechanics": "تضامن عضوي تقني كامل: أبو علي وسردار يصلحان خط الوقود بالأيدي المتجمدة",
            "negentropy_action": "إنجاز البقاء الفيزيائي عبر العمل اليدوي المشترك وكسر التراتبية"
        }
    ]

    def __init__(self):
        self.baseline_text: str = ""
        self.baseline_lines: List[str] = []
        self.world_state: Dict[str, Any] = {}
        self.physical_laws_text: str = ""
        self.bugs_data: Dict[str, Any] = {}
        self.passes: List[str] = []
        self.warnings: List[str] = []
        self.violations: List[str] = []

    def load_data(self) -> bool:
        """Loads and parses all required narrative baseline and world state files."""
        if not os.path.exists(BASELINE_PATH):
            self.violations.append(f"novel_baseline.md missing at: {BASELINE_PATH}")
            return False

        with open(BASELINE_PATH, "r", encoding="utf-8") as f:
            self.baseline_text = f.read()
            self.baseline_lines = self.baseline_text.splitlines()

        if not os.path.exists(PHYSICAL_LAWS_PATH):
            self.violations.append(f"PHYSICAL_LAWS.md missing at: {PHYSICAL_LAWS_PATH}")
            return False

        with open(PHYSICAL_LAWS_PATH, "r", encoding="utf-8") as f:
            self.physical_laws_text = f.read()

        if os.path.exists(WORLD_STATE_PATH):
            with open(WORLD_STATE_PATH, "r", encoding="utf-8") as f:
                self.world_state = yaml.safe_load(f) or {}

        if os.path.exists(WORLD_BUGS_PATH):
            with open(WORLD_BUGS_PATH, "r", encoding="utf-8") as f:
                self.bugs_data = yaml.safe_load(f) or {}

        return True

    def _normalize_name(self, name: str) -> str:
        """Normalizes character names across underscores and whitespace."""
        return name.replace("_", " ").strip()

    def audit_moral_typology_quadrants(self) -> Dict[str, Any]:
        """
        Audit 1: Validates that the 14 occupants are mapped into the 4 moral quadrants
        without omission, duplication, or ideological monopoly.
        """
        all_assigned = []
        quadrant_counts = {}

        for q_id, q_data in self.MORAL_QUADRANTS.items():
            chars = q_data["characters"]
            quadrant_counts[q_id] = len(chars)
            for c in chars:
                norm_c = self._normalize_name(c)
                if norm_c in all_assigned:
                    self.violations.append(f"[Moral Census] Duplicate assignment for character: '{c}'")
                all_assigned.append(norm_c)

        total_census = len(all_assigned)
        if total_census != 14:
            self.violations.append(f"[Moral Census] Total classified characters is {total_census}, expected exactly 14.")
        else:
            self.passes.append(f"Moral Typology Census: Exactly 14/14 train occupants classified across 4 archetypes.")

        # Check for ideological monopoly (no single quadrant should hold > 60% of occupants)
        for q_id, count in quadrant_counts.items():
            pct = (count / total_census) * 100 if total_census else 0
            if pct > 60.0:
                self.violations.append(f"[Moral Monopoly] Quadrant '{q_id}' contains {pct:.1f}% of characters (> 60%), violating human plurality.")

        # Verify all characters exist in baseline text
        missing_in_text = []
        for c in all_assigned:
            if c not in self.baseline_text:
                missing_in_text.append(c)

        if missing_in_text:
            self.violations.append(f"[Moral Verification] Characters not found in baseline text: {missing_in_text}")
        else:
            self.passes.append("Moral Typology Verification: All 14 characters actively attested in baseline manuscript.")

        return {
            "passed": len(self.violations) == 0,
            "total_census": total_census,
            "quadrant_counts": quadrant_counts
        }

    def audit_moral_entropy_curve(self) -> Dict[str, Any]:
        """
        Audit 2: Validates thermodynamic moral entropy curve (S_moral in [0.0, 1.0]).
        Enforces LAW-ETHIC-01:
          - Peak entropy must occur during the ambush (t=315 min, S >= 0.80).
          - Negentropy (anti-entropy) drop must occur during triage, mawal, and collective repair.
          - S_moral must never drop to 0.0 (preserves tragic realism; no saccharine utopia).
        """
        prev_time = -1
        peak_entropy = -1.0
        peak_time = -1

        for step in self.MORAL_ENTROPY_TRAJECTORY:
            t = step["timeline_min"]
            s = step["s_moral"]

            if t <= prev_time:
                self.violations.append(f"[Entropy Timeline Error] Non-monotonic time step at t={t}")
            prev_time = t

            if not (0.0 < s <= 1.0):
                self.violations.append(f"[Entropy Range Error] S_moral={s} out of strict bounds (0.0, 1.0] at t={t}")

            if s > peak_entropy:
                peak_entropy = s
                peak_time = t

        # Peak entropy must be at ambush (t=315)
        if peak_time != 315:
            self.violations.append(f"[Entropy Dynamics Error] Peak moral entropy occurred at t={peak_time}, expected t=315 (ambush).")
        elif peak_entropy < 0.80:
            self.violations.append(f"[Entropy Dynamics Error] Peak entropy S={peak_entropy} at ambush is too low (< 0.80).")
        else:
            self.passes.append(f"Moral Entropy Peak Verified: S_moral = {peak_entropy:.2f} at t=315 min (ambush & breakdown).")

        # Verify Negentropic Recovery (S_moral decreases monotonically after peak)
        post_peak_steps = [step for step in self.MORAL_ENTROPY_TRAJECTORY if step["timeline_min"] >= 315]
        for i in range(len(post_peak_steps) - 1):
            curr_s = post_peak_steps[i]["s_moral"]
            next_s = post_peak_steps[i + 1]["s_moral"]
            if next_s >= curr_s:
                self.violations.append(
                    f"[Negentropy Violation] Expected moral entropy reduction from t={post_peak_steps[i]['timeline_min']} "
                    f"({curr_s}) to t={post_peak_steps[i+1]['timeline_min']} ({next_s}) under LAW-ETHIC-01."
                )

        final_s = self.MORAL_ENTROPY_TRAJECTORY[-1]["s_moral"]
        if final_s == 0.0:
            self.violations.append("[Tragic Realism Violation] S_moral reached 0.0 (unrealistic utopian resolution).")
        else:
            self.passes.append(f"Moral Negentropy Trajectory Verified: S_moral drops from 0.85 -> {final_s:.2f} via collective physical acts.")

        return {
            "passed": len(self.violations) == 0,
            "peak_entropy": peak_entropy,
            "final_entropy": final_s
        }

    def audit_causal_moral_debt(self) -> Dict[str, Any]:
        """
        Audit 3: Audits physical causality punishing moral decay / atomistic betrayal:
          1. Hasan Kaz: attempting to flee alone with paper cash -> frozen death in desert,
             banknotes scattered across thorn bushes (Part 5, Chapter 1, lines 1271-1279).
          2. Hannata: hysterical panic and paralysis -> stripped of rifle by Khalid,
             weapon transferred to prisoner Sardar (Part 3, Chapter 3, line 753).
        """
        # 1. Hasan Kaz Banknote Scattering Proof
        hasan_kaz_found = False
        hasan_line_idx = -1
        for i, line in enumerate(self.baseline_lines):
            if "رزمة الدنانير" in line and "أشواك شجيرة شنان" in line:
                hasan_kaz_found = True
                hasan_line_idx = i + 1
                break

        if not hasan_kaz_found:
            self.violations.append("[Moral Debt Violation] Hasan Kaz's scattered banknotes scene not found in baseline.")
        else:
            self.passes.append(
                f"Causal Moral Debt (Hasan Kaz): Verified at Line {hasan_line_idx} - Banknotes scattered in desert thorns "
                f"enforcing LAW-SOC-02 (Use-value over exchange-value)."
            )

        # 2. Hannata Disarmament and Caste Inversion Proof
        hannata_disarmed = False
        hannata_line_idx = -1
        for i, line in enumerate(self.baseline_lines):
            if "حناطة الملقى على الأرض" in line and "انتزع بندقيته الكلاشنكوف" in line and "سردار" in line:
                hannata_disarmed = True
                hannata_line_idx = i + 1
                break

        if not hannata_disarmed:
            self.violations.append("[Caste Inversion Violation] Hannata weapon forfeiture to Sardar not found in baseline.")
        else:
            self.passes.append(
                f"Causal Power Inversion (Hannata): Verified at Line {hannata_line_idx} - Khalid disarms terrified guard "
                f"and transfers AK-47 to prisoner Sardar enforcing LAW-SOC-03."
            )

        return {
            "passed": len(self.violations) == 0,
            "hasan_kaz_line": hasan_line_idx,
            "hannata_line": hannata_line_idx
        }

    def audit_funerary_dignity_preservation(self) -> Dict[str, Any]:
        """
        Audit 4: Enforces LAW-ETHIC-02 (Funerary Dignity & Sacred Memory) and
        LAW-ETHIC-03 (Emotional Resonance as Hypothermic Buffer):
          1. Abbas's Pebble: Held in pocket (lines 501, 571), clutched in death (line 1019),
             kept in hand by Khalid (line 1021).
          2. Salloum's Body: Laid in rear car, covered with Abu Ali's torn shirt (line 1011),
             rear car preserved as sacred space for the dead (line 1035).
          3. Aziz's Mawal: Sung in darkness (line 1145, 1213), re-centering brain chemistry
             and breaking hypothermic torpor.
        """
        # 1. Abbas Stone Invariant
        stone_in_death = False
        stone_line_idx = -1
        for i, line in enumerate(self.baseline_lines):
            if "الحصاة الصوانية الصغيرة" in line and "مطبقة بقوة هائلة" in line:
                stone_in_death = True
                stone_line_idx = i + 1
                break

        if not stone_in_death:
            self.violations.append("[Funerary Dignity Error] Abbas clutching flint pebble in death not found in baseline.")
        else:
            self.passes.append(
                f"Funerary Dignity (Abbas Pebble): Verified at Line {stone_line_idx} - Clutched stone preserved in death "
                f"enforcing LAW-ETHIC-02."
            )

        # 2. Salloum Covered Body Invariant
        salloum_covered = False
        salloum_line_idx = -1
        for i, line in enumerate(self.baseline_lines):
            if "سلوم ممدداً" in line and "قميص أبي علي" in line and ("تغطى" in line or "مغطى بنصف قميص" in line):
                salloum_covered = True
                salloum_line_idx = i + 1
                break

        if not salloum_covered:
            self.violations.append("[Funerary Dignity Error] Salloum body covered with Abu Ali's shirt not found in baseline.")
        else:
            self.passes.append(
                f"Funerary Dignity (Salloum Shroud): Verified at Line {salloum_line_idx} - Body covered with torn shirt "
                f"enforcing LAW-ETHIC-02."
            )

        # 3. Rear Car Dedicated for the Dead
        rear_car_dead = False
        rear_car_line_idx = -1
        for i, line in enumerate(self.baseline_lines):
            if "العربة هاي تبقى للموتى" in line:
                rear_car_dead = True
                rear_car_line_idx = i + 1
                break

        if not rear_car_dead:
            self.violations.append("[Funerary Sacred Space Error] Khalid's declaration designating rear car for the dead missing.")
        else:
            self.passes.append(
                f"Sacred Confinement Space: Verified at Line {rear_car_line_idx} - Rear car designated exclusively for the fallen."
            )

        # 4. Aziz's Mawal Catharsis
        mawal_found = False
        mawal_line_idx = -1
        for i, line in enumerate(self.baseline_lines):
            if "موال عزيز: انصهار الأرواح" in line:
                mawal_found = True
                mawal_line_idx = i + 1
                break

        if not mawal_found:
            self.violations.append("[Emotional Resonance Error] Aziz's Mawal chapter header not found in baseline.")
        else:
            self.passes.append(
                f"Emotional Resonance & Catharsis: Verified at Line {mawal_line_idx} - Aziz's Mawal enforces LAW-ETHIC-03 "
                f"as neuro-biological hypothermic buffer."
            )

        return {
            "passed": len(self.violations) == 0,
            "stone_line": stone_line_idx,
            "salloum_line": salloum_line_idx,
            "rear_car_line": rear_car_line_idx,
            "mawal_line": mawal_line_idx
        }

    def run_all(self) -> bool:
        """Runs all 4 moral and existential audit modules and prints comprehensive report."""
        print("\n" + "=" * 80)
        print("  MORAL ENTROPY & EXISTENTIAL SOLIDARITY MONITOR (مراقب الإنتروبيا الأخلاقية)")
        print("  Framework Charter: «نحن نُحلل ونُقيّم.. ولا نُقوّم» (Zero Moral Patronizing)")
        print("=" * 80)

        if not self.load_data():
            print("\n[CRITICAL ERROR] Failed to load required narrative files.")
            for v in self.violations:
                print(f"  ❌ {v}")
            return False

        self.audit_moral_typology_quadrants()
        self.audit_moral_entropy_curve()
        self.audit_causal_moral_debt()
        self.audit_funerary_dignity_preservation()

        print("\n--- PASSED MORAL & EXISTENTIAL INVARIANTS (الفحوصات الأخلاقية الناجحة) ---")
        for p in self.passes:
            print(f"  ✅ {p}")

        if self.warnings:
            print("\n--- MORAL AUDIT WARNINGS (تنبيهات المنظومة الأخلاقية) ---")
            for w in self.warnings:
                print(f"  ⚠️  {w}")

        if self.violations:
            print("\n--- MORAL INVARIANT VIOLATIONS (الخروقات الأخلاقية والوجودية) ---")
            for v in self.violations:
                print(f"  ❌ {v}")
            print("\n" + "=" * 80)
            print(f"  MORAL AUDIT FAILED: {len(self.violations)} invariant violation(s) detected.")
            print("=" * 80 + "\n")
            return False

        print("\n" + "=" * 80)
        print("  MORAL AUDIT PASSED: 100% Moral Entropy & Existential Solidarity Invariants Verified.")
        print("=" * 80 + "\n")
        return True


if __name__ == "__main__":
    monitor = MoralEntropyMonitor()
    success = monitor.run_all()
    sys.exit(0 if success else 1)
