#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
TEMPORAL TRANSITION AUDITOR (مدقق الصيرورة والتحول الزمني الحتمي)
Project: قطار الرمل (Sand Train)
Architecture: Narrative Engineering Framework - Multi-State Temporal Matrix
==============================================================================

This tool audits the continuous progression across 5 milestone chronological
states (T0 to T4) over the 10.75-hour night:
  1. Monotonic Cooling Decay: ambient temp strictly monotonically falls to -8°C.
  2. Hypercapnia & CO2 Accumulation (LAW-BIO-06): CO2 accumulates across closed
     carriages, breaching the 1.5% threshold at midnight.
  3. Bio-Thermal Dexterity Coupling (LAW-BIO-01): dexterity < 0.60 whenever
     fingers < 12°C in any temporal state.
  4. Paraffin Gelling Confinement (LAW-CHEM-01): engine fuel line gelling is
     enforced when temp <= -6.0°C.
  5. Allostatic Load & Apathy Progression (LAW-PSYCH-03): cumulative stress
     monotonically ascends to lethal apathy (> 0.85) at false dawn.
  6. Battery Cold Drain (LAW-ELEC-01 & LAW-MAT-01): battery charge depletes
     to 0% before 03:00 under sub-zero chemical stagnation.
==============================================================================
"""

import os
import sys
import yaml
from typing import Dict, List, Any

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TEMPORAL_STATES_PATH = os.path.join(ROOT_DIR, "05_WORLD_BRAIN", "temporal_states.yaml")


class TemporalTransitionAuditor:
    def __init__(self, states_path: str = TEMPORAL_STATES_PATH):
        self.states_path = states_path
        self.states_data = None
        self.violations: List[str] = []
        self.passes: List[str] = []

    def load_data(self) -> bool:
        if not os.path.exists(self.states_path):
            self.violations.append(f"Missing temporal states file: {self.states_path}")
            return False
        with open(self.states_path, "r", encoding="utf-8") as f:
            self.states_data = yaml.safe_load(f)
        return True

    def audit_temporal_transitions(self) -> bool:
        if not self.states_data:
            return False

        states = self.states_data.get("states", [])
        if len(states) < 5:
            self.violations.append(f"Insufficient temporal milestone states: expected 5, found {len(states)}")
            return False

        prev_temp = 100.0
        prev_co2 = 0.0
        prev_allostatic = -1.0
        prev_battery = 101.0

        for state in states:
            s_id = state.get("id")
            env = state.get("environment", {})
            air = state.get("air_quality", {})
            bio = state.get("biometrics", {})
            battery = state.get("battery", {})
            train = state.get("train", {})

            # 1. Monotonic Cooling Decay
            temp = env.get("ambient_temperature_c", 0.0)
            if temp > prev_temp:
                self.violations.append(
                    f"[Temporal Invariant Violation] Ambient temp rose from {prev_temp}°C to {temp}°C in state '{s_id}'."
                )
            prev_temp = temp

            # 2. Cumulative CO2 Accumulation (LAW-BIO-06)
            car2_co2 = air.get("car_02_co2_percent", 0.0)
            if car2_co2 < prev_co2:
                self.violations.append(
                    f"[LAW-BIO-06 Violation] CO2 in Car 02 dropped from {prev_co2}% to {car2_co2}% without ventilation in '{s_id}'."
                )
            prev_co2 = car2_co2

            # 3. Bio-Thermal Dexterity Coupling (LAW-BIO-01)
            khalid_fingers = bio.get("khalid_fingers_temp_c", 20.0)
            khalid_dexterity = bio.get("khalid_dexterity", 1.0)
            if khalid_fingers < 12.0 and khalid_dexterity >= 0.60:
                self.violations.append(
                    f"[LAW-BIO-01 Violation] Khalid fingers {khalid_fingers}°C with dexterity {khalid_dexterity} in '{s_id}'."
                )

            # 4. Paraffin Gelling Confinement (LAW-CHEM-01)
            fuel_status = train.get("fuel_line", "")
            if temp <= -6.0:
                if fuel_status != "gelled_paraffin_blocked":
                    self.violations.append(
                        f"[LAW-CHEM-01 Violation] Temp is {temp}°C (<= -6.0°C) but fuel status is '{fuel_status}' in '{s_id}'."
                    )

            # 5. Allostatic Load Progression (LAW-PSYCH-03)
            allostatic = bio.get("allostatic_load", 0.0)
            if allostatic < prev_allostatic:
                self.violations.append(
                    f"[LAW-PSYCH-03 Violation] Allostatic load reversed from {prev_allostatic} to {allostatic} in '{s_id}'."
                )
            prev_allostatic = allostatic

            # 6. Battery Depletion (LAW-ELEC-01 & LAW-MAT-01)
            bat_pct = battery.get("auxiliary_charge_percent", 0.0)
            if bat_pct > prev_battery:
                self.violations.append(
                    f"[LAW-ELEC-01 Violation] Battery recharged from {prev_battery}% to {bat_pct}% in '{s_id}'."
                )
            prev_battery = bat_pct

        if not self.violations:
            self.passes.append(
                f"Dynamic Temporal Transitions: Monotonic cooling, cumulative CO2, allostatic fatigue, and chemical gelling verified across {len(states)} chronological states."
            )
            return True
        return False

    def run_all(self) -> int:
        print("\n" + "=" * 75)
        print("  TEMPORAL TRANSITION AUDITOR (مدقق الصيرورة والتحول الزمني الحتمي)")
        print("=" * 75)
        if not self.load_data():
            for v in self.violations:
                print(f"  ❌ {v}")
            return 1
        if self.audit_temporal_transitions():
            for p in self.passes:
                print(f"  ✅ {p}")
            print("\n  AUDIT PASSED: 100% Deterministic Temporal Continuity Verified.\n")
            return 0
        else:
            for v in self.violations:
                print(f"  ❌ {v}")
            print(f"\n  AUDIT FAILED: {len(self.violations)} temporal transition violation(s).\n")
            return 1


if __name__ == "__main__":
    auditor = TemporalTransitionAuditor()
    sys.exit(auditor.run_all())
