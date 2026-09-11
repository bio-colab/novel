#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
HISTORICAL & POLITICAL ANALYZER (محلل الكرونوتوب التاريخي والواقع السياسي)
===============================================================================
Novel: «قطار الرمل» (Sand Train)
Engine: Closed World Deterministic Evaluator - History & Politics Module

Purpose:
  Audits the historical chronotope (analog isolation, zero modern anachronisms)
  and political semiotics (state disintegration, prison-to-prison fatalistic trajectory)
  enforcing LAW-POL-01, LAW-POL-02, and LAW-POL-03.

Guarantees:
  - 100% Read-Only inspection of baseline novel (00_BASELINE/novel_baseline.md).
  - Deterministic evaluation of linguistic, material, and geopolitical invariants.
  - Zero tolerance for anachronistic bleed (digital phones, GPS, internet).
===============================================================================
"""

import os
import sys
import re
from typing import Dict, List, Any

# Fix Windows UTF-8 stdout encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

BASELINE_PATH = os.path.join(os.path.dirname(__file__), "..", "00_BASELINE", "novel_baseline.md")
LAWS_PATH = os.path.join(os.path.dirname(__file__), "..", "01_SPECS_AND_RULES", "PHYSICAL_LAWS.md")

# ==============================================================================
# TAXONOMY & AUDIT REGISTRY
# ==============================================================================
DIGITAL_ANACHRONISMS = [
    r"موبايل",
    r"هاتف\s*ذكي",
    r"شاشة\s*لمس",
    r"إنترنت",
    r"حاسوب",
    r"كمبيوتر",
    r"رقمي",
    r"ستالايت",
    r"جي\s*بي\s*إس",
    r"إلكتروني",
    r"واي\s*فاي",
    r"رسالة\s*نصية",
    r"كاميرا\s*مراقبة"
]

ANALOG_ERA_ARTIFACTS = {
    "ديزل": 1,
    "كلاشنكوف|بندقية": 5,
    "مفتاح": 2,
    "ساعة": 3,
    "ورقة": 5,
    "دنانير": 1,
    "صاج": 10,
    "سلك": 3
}

STATE_SEMIOTIC_TOKENS = [
    r"حراسة", r"مفرزة", r"وزارة", r"مدير", r"لوائح", r"أوامر",
    r"محضر", r"خاكي", r"حراس", r"سجان", r"حكومية", r"رسمي"
]

VOID_AND_THREAT_TOKENS = [
    r"صحراء", r"صوان", r"رمل", r"صقيع", r"برد", r"ليل",
    r"سواد", r"رصاص", r"تلال", r"مسلحين", r"ريح", r"عتمة"
]

GEOPOLITICAL_TERMINALS = {
    "origin_prison": r"بادوش",
    "destination_prison": r"البير",
    "hostile_corridor": r"الحماد|الجزيرة|السماوة"
}


class HistoricalPoliticalAnalyzer:
    """Deterministic Historical Chronotope and Political Invariant Evaluator."""

    def __init__(self, baseline_path: str = BASELINE_PATH):
        self.baseline_path = baseline_path
        self.raw_text = self._load_baseline()

    def _load_baseline(self) -> str:
        if not os.path.exists(self.baseline_path):
            raise FileNotFoundError(f"Baseline file missing at: {self.baseline_path}")
        with open(self.baseline_path, "r", encoding="utf-8") as f:
            return f.read()

    def audit_anachronism_isolation(self) -> Dict[str, Any]:
        """
        Validates LAW-POL-01:
        Confirms absolute ZERO occurrences of digital or post-analog modern technology.
        """
        violations = {}
        for pattern in DIGITAL_ANACHRONISMS:
            matches = len(re.findall(pattern, self.raw_text))
            if matches > 0:
                violations[pattern] = matches

        passed = len(violations) == 0
        return {
            "passed": passed,
            "anachronisms_detected": len(violations),
            "violations": violations
        }

    def audit_analog_material_artifacts(self) -> Dict[str, Any]:
        """
        Validates LAW-POL-01 (Positive Attestation):
        Confirms robust presence of mechanical and analog embargo-era artifacts.
        """
        counts = {}
        missing = []
        for pattern, min_expected in ANALOG_ERA_ARTIFACTS.items():
            count = len(re.findall(pattern, self.raw_text))
            counts[pattern] = count
            if count < min_expected:
                missing.append(pattern)

        passed = len(missing) == 0
        return {
            "passed": passed,
            "counts": counts,
            "missing_artifacts": missing
        }

    def audit_state_erosion_vs_void(self) -> Dict[str, Any]:
        """
        Validates LAW-POL-02:
        Measures the ratio of Central State Semiotic Tokens vs Hostile Desert Void Tokens.
        In the periphery, the State is overwhelmed by the Void (Ratio < 0.35).
        """
        state_count = sum(len(re.findall(t, self.raw_text)) for t in STATE_SEMIOTIC_TOKENS)
        void_count = sum(len(re.findall(t, self.raw_text)) for t in VOID_AND_THREAT_TOKENS)

        ratio = state_count / void_count if void_count > 0 else 1.0
        # In an eviscerated state context, the void vastly outnumbers state tokens
        passed = ratio <= 0.35 and state_count >= 10 and void_count >= 50

        return {
            "passed": passed,
            "state_token_count": state_count,
            "void_token_count": void_count,
            "state_to_void_ratio": round(ratio, 3)
        }

    def audit_geopolitical_prison_trajectory(self) -> Dict[str, Any]:
        """
        Validates LAW-POL-03:
        Verifies the prison-to-prison trajectory (Badush -> Al-Beer) with zero civilian escape exits.
        """
        origin_count = len(re.findall(GEOPOLITICAL_TERMINALS["origin_prison"], self.raw_text))
        dest_count = len(re.findall(GEOPOLITICAL_TERMINALS["destination_prison"], self.raw_text))
        corridor_count = len(re.findall(GEOPOLITICAL_TERMINALS["hostile_corridor"], self.raw_text))

        # Check that there are no civilian station exits
        civilian_station_escapes = len(re.findall(r"محطة\s*ركاب|قطار\s*مدني|تذكرة\s*سفر", self.raw_text))

        passed = (
            origin_count >= 1
            and dest_count >= 1
            and corridor_count >= 1
            and civilian_station_escapes == 0
        )

        return {
            "passed": passed,
            "origin_badush_mentions": origin_count,
            "destination_albeer_mentions": dest_count,
            "desert_corridor_mentions": corridor_count,
            "civilian_escapes": civilian_station_escapes
        }

    def run_all_audits(self) -> bool:
        """Executes full diagnostic suite and returns True if 100% compliant."""
        print("\n" + "=" * 80)
        print("  HISTORICAL & POLITICAL ANALYZER (محلل الكرونوتوب التاريخي والواقع السياسي)")
        print("=" * 80)

        anachronism_res = self.audit_anachronism_isolation()
        print("\n--- ANALOG CHRONOTOPE & ZERO ANACHRONISMS (LAW-POL-01) ---")
        print(f"  Anachronisms Detected: {anachronism_res['anachronisms_detected']}")
        if anachronism_res["passed"]:
            print("  ✅ LAW-POL-01 Invariant Verified: Zero modern digital technology bleeds detected.")
        else:
            print(f"  ❌ Anachronisms Violated: {anachronism_res['violations']}")

        artifact_res = self.audit_analog_material_artifacts()
        print("\n--- POSITIVE ANALOG ARTIFACT ATTESTATION ---")
        for art, count in artifact_res["counts"].items():
            print(f"  - {art:<25}: {count} occurrences")
        if artifact_res["passed"]:
            print("  ✅ Analog Materiality Verified: Key historical mechanical artifacts robustly attested.")
        else:
            print(f"  ❌ Missing Artifacts: {artifact_res['missing_artifacts']}")

        erosion_res = self.audit_state_erosion_vs_void()
        print("\n--- STATE EROSION VS HOSTILE VOID (LAW-POL-02) ---")
        print(f"  State Institutional Presence : {erosion_res['state_token_count']} tokens")
        print(f"  Hostile Desert & Threat Void : {erosion_res['void_token_count']} tokens")
        print(f"  State-to-Void Ratio          : {erosion_res['state_to_void_ratio']} (Expected <= 0.35)")
        if erosion_res["passed"]:
            print("  ✅ LAW-POL-02 Invariant Verified: Peripheral void overwhelmingly dominates crumbling state presence.")
        else:
            print("  ❌ State Erosion Ratio Violated.")

        geo_res = self.audit_geopolitical_prison_trajectory()
        print("\n--- GEOPOLITICAL PRISON-TO-PRISON TRAJECTORY (LAW-POL-03) ---")
        print(f"  Origin Prison (Badush)       : {geo_res['origin_badush_mentions']} mentions")
        print(f"  Destination Prison (Al-Beer) : {geo_res['destination_albeer_mentions']} mentions")
        print(f"  Hostile Corridor (Al-Hammad) : {geo_res['desert_corridor_mentions']} mentions")
        print(f"  Civilian Escape Outlets      : {geo_res['civilian_escapes']} mentions")
        if geo_res["passed"]:
            print("  ✅ LAW-POL-03 Invariant Verified: Fatalistic closed loop prison trajectory confirmed.")
        else:
            print("  ❌ Geopolitical Trajectory Violated.")

        overall_passed = (
            anachronism_res["passed"]
            and artifact_res["passed"]
            and erosion_res["passed"]
            and geo_res["passed"]
        )

        print("\n" + "=" * 80)
        if overall_passed:
            print("  HISTORICAL & POLITICAL AUDIT PASSED: 100% Invariant Compliance Verified.")
        else:
            print("  HISTORICAL & POLITICAL AUDIT FAILED: Invariants Violated.")
        print("=" * 80 + "\n")

        return overall_passed


if __name__ == "__main__":
    analyzer = HistoricalPoliticalAnalyzer()
    success = analyzer.run_all_audits()
    sys.exit(0 if success else 1)
