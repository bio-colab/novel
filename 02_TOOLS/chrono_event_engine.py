#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
DISCRETE-EVENT SIMULATOR & PHYSICAL PROFILER (محاكي الأحداث والمنحنى الحتمي)
Project: قطار الرمل (Sand Train)
Architecture: Narrative Engineering Framework - Discrete-Event Simulator (DES)
==============================================================================

This tool computes deterministic physical decay curves across the discrete event
timeline of the novel (10.75 hours / 646 minutes):
1. Thermal Radiation Decay: Ambient temperature, wind chill, and car interior cooling.
2. Extremity & Motor Skill Degradation: Finger temperature and dexterity collapse.
3. Respiration Water Deficit: Cumulative liters lost to sub-zero arid exhalation.
4. Action Feasibility Validation: Compares required motor skills for physical actions
   against character biomechanical limits at that exact minute.

Exit Code:
  0: All physical curves calculated, feasible actions passed, and anomalies matched.
  1: Unhandled physical divergence or computational errors.
"""

import os
import sys
import math
import yaml
from typing import Dict, List, Tuple, Any

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Key Narrative Action Milestones to Evaluate
NARRATIVE_ACTIONS_TO_EVALUATE = [
    {
        "id": "ACT-01-INITIAL-INSPECTION",
        "minute": 15,
        "time": "19:15:00",
        "character": "أبو_علي",
        "action": "فحص صمام الديزل ومسح الكفين بالخرقة",
        "required_dexterity": 0.65,
        "requires_tools": False
    },
    {
        "id": "ACT-02-AMBUSH-ENGAGEMENT",
        "minute": 315,
        "time": "00:15:00",
        "character": "خالد",
        "action": "تلقيم البندقية وإطلاق النار في العتمة",
        "required_dexterity": 0.40,
        "requires_tools": False
    },
    {
        "id": "ACT-03-WIRE-TWISTING",
        "minute": 600,
        "time": "05:00:00",
        "character": "سردار",
        "action": "شد سلك معدني صلب (2 ملم) حول شق أنبوب الوقود بالأصابع",
        "required_dexterity": 0.60,
        "requires_tools": True,
        "associated_bug": "WORLD-BUG-005"
    },
    {
        "id": "ACT-04-PRIMER-PUMP-LEVER",
        "minute": 645,
        "time": "05:45:00",
        "character": "أبو_علي",
        "action": "سحب ذراع مضخة التحضير اليدوية للمحرك بكتلة الجذع والخرقة الملفوفة",
        "required_dexterity": 0.05,  # Gross motor skill (shoulder/torso pull with wrapped cloth)
        "requires_tools": False
    }
]

class ChronoEventEngine:
    def __init__(self):
        self.passes = []
        self.warnings = []
        self.violations = []
        self.flagged_anomalies = []

    def calculate_environment_at_minute(self, minute: int) -> Dict[str, float]:
        """Compute environmental thermodynamics at timeline minute [0..645]"""
        # Baseline at minute 0 (19:00:00): 0.0°C
        # Radiation cooling: ~1.8°C/hr down to pre-dawn minimum of -8.0°C at minute 570 (04:30)
        hours = minute / 60.0
        ambient_temp = max(-8.0, 0.0 - (1.8 * hours))
        
        # Wind chill effective temp (constant 38 km/h wind strikes right flank)
        wind_chill_c = ambient_temp - 5.4

        # Illumination: Starlight 0.8 Lux, dipping to 0.05 inside Car 03
        lux = 0.8 if minute < 600 else 2.5  # First signs of astronomical dawn at 05:22

        return {
            "ambient_temp_c": round(ambient_temp, 2),
            "wind_chill_c": round(wind_chill_c, 2),
            "lux": round(lux, 2)
        }

    def calculate_biometrics_at_minute(self, minute: int, initial_finger_temp: float = 22.0) -> Dict[str, float]:
        """Compute finger temp and motor dexterity decay over time"""
        env = self.calculate_environment_at_minute(minute)
        amb = env["ambient_temp_c"]
        hours = minute / 60.0

        # Thermal decay of extremities exposed to cold metal
        # Asymptotic approach towards ambient temperature
        finger_temp = max(amb, initial_finger_temp - (2.6 * hours))

        # Dexterity function: LAW-BIO-01
        # finger_temp < 12°C drops dexterity < 0.60; finger_temp < 2°C drops dexterity < 0.20
        if finger_temp >= 12.0:
            dexterity = max(0.60, 0.95 - (0.05 * hours))
        else:
            # Steep collapse below 12°C
            dexterity = max(0.08, 0.60 - (12.0 - finger_temp) * 0.05)

        # Respiration water loss for 14 souls
        # 40 ml/hr per person
        cumulative_water_loss_l = round(14 * 0.040 * hours, 2)

        return {
            "finger_temp_c": round(finger_temp, 2),
            "motor_dexterity": round(dexterity, 2),
            "cumulative_water_loss_liters": cumulative_water_loss_l
        }

    def evaluate_narrative_actions(self):
        """Audit physical feasibility of actions against biomechanical state curves"""
        for act in NARRATIVE_ACTIONS_TO_EVALUATE:
            act_id = act["id"]
            minute = act["minute"]
            time_str = act["time"]
            char = act["character"]
            action_desc = act["action"]
            req_dex = act["required_dexterity"]
            assoc_bug = act.get("associated_bug")

            env = self.calculate_environment_at_minute(minute)
            bio = self.calculate_biometrics_at_minute(minute)

            curr_dex = bio["motor_dexterity"]
            curr_fingers = bio["finger_temp_c"]

            if curr_dex >= req_dex:
                self.passes.append(
                    f"Action Feasible: '{char}' at {time_str} (min {minute}) executed '{action_desc}' (Req: {req_dex}, Available: {curr_dex}, Fingers: {curr_fingers}°C)."
                )
            else:
                msg = (
                    f"Biomechanic Collapse: '{char}' at {time_str} (min {minute}) attempted '{action_desc}'. "
                    f"Required dexterity: {req_dex}, but physical dexterity collapsed to {curr_dex} (Fingers: {curr_fingers}°C)."
                )
                if assoc_bug:
                    self.flagged_anomalies.append(f"[{assoc_bug} Confirmed] {msg}")
                else:
                    self.violations.append(f"[Unphysical Action Error] {msg}")

    def run_profiler(self) -> int:
        print("\n" + "=" * 75)
        print("  DISCRETE-EVENT SIMULATOR & PHYSICAL PROFILER (محاكي الأحداث والمنحنى الحتمي)")
        print("=" * 75)

        # Print physical profile at milestone intervals
        print("\n--- DETERMINISTIC TIMELINE DECAY CURVE (منحنى التدهور الزمني) ---")
        print(f"{'Time':<10} {'Min':<6} {'Ambient (°C)':<14} {'Wind Chill':<12} {'Fingers (°C)':<14} {'Dexterity':<12} {'Water Loss'}")
        print("-" * 75)
        for m in [0, 60, 180, 315, 450, 570, 645]:
            h = 19 + (m // 60)
            mins = m % 60
            time_label = f"{h%24:02d}:{mins:02d}:00"
            env = self.calculate_environment_at_minute(m)
            bio = self.calculate_biometrics_at_minute(m)
            print(
                f"{time_label:<10} {m:<6} {env['ambient_temp_c']:<14} {env['wind_chill_c']:<12} "
                f"{bio['finger_temp_c']:<14} {bio['motor_dexterity']:<12} {bio['cumulative_water_loss_liters']} L"
            )

        self.evaluate_narrative_actions()

        print("\n--- ACTION FEASIBILITY VERIFICATIONS ---")
        for p in self.passes:
            print(f"  ✅ {p}")

        if self.flagged_anomalies:
            print("\n--- CONFIRMED INVARIANT ANOMALIES & PLOT BREACHES ---")
            for a in self.flagged_anomalies:
                print(f"  🔍 {a}")

        if self.violations:
            print("\n--- CRITICAL BIOMECHANICAL VIOLATIONS ---")
            for v in self.violations:
                print(f"  ❌ {v}")
            print("\n" + "=" * 75)
            print(f"  PROFILER FAILED: {len(self.violations)} unphysical action(s) detected.")
            print("=" * 75 + "\n")
            return 1

        print("\n" + "=" * 75)
        print("  PROFILER PASSED: 100% Deterministic Event Physics Verified.")
        print("=" * 75 + "\n")
        return 0

if __name__ == "__main__":
    engine = ChronoEventEngine()
    sys.exit(engine.run_profiler())
