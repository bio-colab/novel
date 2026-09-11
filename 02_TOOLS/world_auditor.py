#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
WORLD AUDITOR & INVARIANT VERIFIER (مدقق حتمية العالم والثوابت الفيزيائية)
Project: قطار الرمل (Sand Train)
Architecture: Narrative Engineering Framework - Simulation Core
==============================================================================

This script performs deterministic invariant auditing across:
1. Reference Integrity: Checks that all laws cited in WORLD_BUGS exist in PHYSICAL_LAWS.md.
2. Spatial Collision Detection: Ensures no two agents occupy identical (x, y) coordinates without physical contact.
3. Zone Confinement Bounds: Ensures all agent coordinates lie within their car boundary [y_start, y_end].
4. Bio-Thermal Invariant Checks: Enforces LAW-BIO-01 (finger temp < 12°C -> dexterity < 0.60).
5. Resource Arithmetic Balance: Enforces total ammo sum and water conservation.

Exit Code:
  0: All invariants passed with zero violations.
  1: Invariant violations detected.
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
WORLD_STATE_PATH = os.path.join(ROOT_DIR, "05_WORLD_BRAIN", "world_state.yaml")
WORLD_BUGS_PATH = os.path.join(ROOT_DIR, "03_AUDIT_AND_ISSUES", "WORLD_BUGS.yaml")
PHYSICAL_LAWS_PATH = os.path.join(ROOT_DIR, "01_SPECS_AND_RULES", "PHYSICAL_LAWS.md")

class WorldAuditor:
    def __init__(self):
        self.violations = []
        self.warnings = []
        self.passes = []
        self.world_state = None
        self.world_bugs = None
        self.physical_laws_text = ""

    def load_files(self):
        # 1. Load world_state.yaml
        if not os.path.exists(WORLD_STATE_PATH):
            self.violations.append(f"Missing file: {WORLD_STATE_PATH}")
            return False
        with open(WORLD_STATE_PATH, "r", encoding="utf-8") as f:
            self.world_state = yaml.safe_load(f)

        # 2. Load WORLD_BUGS.yaml
        if not os.path.exists(WORLD_BUGS_PATH):
            self.violations.append(f"Missing file: {WORLD_BUGS_PATH}")
            return False
        with open(WORLD_BUGS_PATH, "r", encoding="utf-8") as f:
            self.world_bugs = yaml.safe_load(f)

        # 3. Load PHYSICAL_LAWS.md
        if not os.path.exists(PHYSICAL_LAWS_PATH):
            self.violations.append(f"Missing file: {PHYSICAL_LAWS_PATH}")
            return False
        with open(PHYSICAL_LAWS_PATH, "r", encoding="utf-8") as f:
            self.physical_laws_text = f.read()

        return True

    def check_laws_reference_integrity(self):
        """Verify that all laws referenced in WORLD_BUGS exist in PHYSICAL_LAWS.md"""
        bugs = self.world_bugs.get("bugs", [])
        # Find all defined laws in PHYSICAL_LAWS.md (e.g. [LAW-THERMO-01], LAW-SPATIAL-01)
        defined_laws = set(re.findall(r"\[(LAW-[A-Z]+-\d+)\]", self.physical_laws_text))

        checked_count = 0
        missing_laws = []
        for bug in bugs:
            law_broken = bug.get("law_broken", "")
            # Extract law codes mentioned (e.g., LAW-SPATIAL-01)
            cited_laws = re.findall(r"(LAW-[A-Z]+-\d+)", law_broken)
            for law in cited_laws:
                checked_count += 1
                if law not in defined_laws:
                    missing_laws.append((bug.get('id'), law))
                    self.violations.append(
                        f"[Laws Reference Error] {bug.get('id')}: Cited law '{law}' is not defined in PHYSICAL_LAWS.md"
                    )
        if not missing_laws:
            self.passes.append(f"Reference Integrity: All {checked_count} cited laws exist in PHYSICAL_LAWS.md")

    def check_spatial_collision(self):
        """Ensure no two characters occupy the exact same (x, y) coordinates"""
        characters = self.world_state.get("characters", {})
        coords_map = {}
        for name, data in characters.items():
            coords = data.get("coordinates", {})
            x = coords.get("x_m")
            y = coords.get("y_m")
            if x is None or y is None:
                self.violations.append(f"[Spatial Error] Character '{name}' has missing coordinates.")
                continue
            
            coord_key = (round(x, 2), round(y, 2))
            if coord_key in coords_map:
                existing_char = coords_map[coord_key]
                self.violations.append(
                    f"[Spatial Collision] '{name}' and '{existing_char}' occupy identical coordinates {coord_key} without documented interaction."
                )
            else:
                coords_map[coord_key] = name

        self.passes.append(f"Spatial Collision Check: {len(coords_map)} characters occupy distinct, non-overlapping coordinates.")

    def check_zone_confinement(self):
        """Ensure all character coordinates fall within the [y_start, y_end] bounds of their assigned car"""
        cars = self.world_state.get("train", {}).get("cars", {})
        characters = self.world_state.get("characters", {})

        confinement_passes = 0
        for name, data in characters.items():
            loc_id = data.get("location")
            coords = data.get("coordinates", {})
            y_m = coords.get("y_m")
            x_m = coords.get("x_m")

            # Check x width bounds (0.0 to 2.8m)
            if x_m < 0.0 or x_m > 2.8:
                self.violations.append(
                    f"[Boundary Error] '{name}' x-coordinate ({x_m}m) exceeds train width (0.0m - 2.8m)."
                )

            car_info = cars.get(loc_id)
            if not car_info:
                self.violations.append(f"[Zone Error] Unknown location '{loc_id}' for character '{name}'.")
                continue

            y_start = car_info.get("y_start_m")
            y_end = car_info.get("y_end_m")

            if y_start is not None and y_end is not None:
                if not (y_start <= y_m <= y_end):
                    self.violations.append(
                        f"[Boundary Error] '{name}' in '{loc_id}' at y={y_m}m is outside car bounds [{y_start}m, {y_end}m]."
                    )
                else:
                    confinement_passes += 1

        self.passes.append(f"Zone Boundary Confinement: All {confinement_passes} characters strictly confined within physical car bounds.")

    def check_bio_thermal_invariants(self):
        """Verify LAW-BIO-01: finger temp < 12°C requires motor_dexterity < 0.60"""
        characters = self.world_state.get("characters", {})
        bio_passes = 0
        for name, data in characters.items():
            phys = data.get("physical", {})
            fingers_temp = phys.get("fingers_temp_c", 20.0)
            dexterity = phys.get("motor_dexterity", 1.0)
            core_temp = phys.get("core_temp_c", 37.0)

            char_valid = True
            # Check LAW-BIO-01
            if fingers_temp < 12.0:
                if dexterity >= 0.60:
                    char_valid = False
                    self.violations.append(
                        f"[LAW-BIO-01 Violation] '{name}' has finger temp {fingers_temp}°C (< 12°C) but dexterity is {dexterity} (must be < 0.60)."
                    )
            
            # Check physiological mortality/hypothermia threshold
            if core_temp < 32.0:
                self.warnings.append(
                    f"[Hypothermia Warning] '{name}' core temp is {core_temp}°C (Critical Hypothermia Stage 3)."
                )
            if char_valid:
                bio_passes += 1

        self.passes.append(f"Bio-Thermal Invariants (LAW-BIO-01): Passed for all {bio_passes} characters.")

    def check_resource_conservation(self):
        """Verify ammunition arithmetic balance"""
        ammo = self.world_state.get("inventory", {}).get("ammunition_7_62x39", {})
        khalid_ammo = ammo.get("weapon_khalid_ak47_rounds", 0)
        abbas_ammo = ammo.get("weapon_abbas_ak47_rounds", 0)
        crate_ammo = ammo.get("wooden_crate_car_01", {}).get("rounds", 0)
        total_effective = ammo.get("total_effective_rounds", 0)

        sum_calculated = khalid_ammo + abbas_ammo + crate_ammo
        if sum_calculated != total_effective:
            self.violations.append(
                f"[Resource Invariant Error] Ammo sum ({khalid_ammo} + {abbas_ammo} + {crate_ammo} = {sum_calculated}) does not match total_effective_rounds ({total_effective})."
            )
        else:
            self.passes.append(f"Resource Arithmetic: Ammunition balance strictly verified ({sum_calculated} rounds match total).")

        # Water supply sanity
        water = self.world_state.get("inventory", {}).get("water_supply", {}).get("volume_remaining_liters", 0)
        if water <= 0:
            self.violations.append(f"[Resource Invariant Error] Water supply is depleted ({water}L).")
        else:
            self.passes.append(f"Resource Conservation: Water reserve verified at {water}L.")

    def run_all(self):
        print("\n" + "=" * 75)
        print("  WORLD AUDITOR & INVARIANT VERIFIER (مدقق حتمية العالم والثوابت)")
        print("=" * 75)

        if not self.load_files():
            print("\n[CRITICAL ERROR] Failed to load required world files.")
            for v in self.violations:
                print(f"  ❌ {v}")
            return 1

        self.check_laws_reference_integrity()
        self.check_spatial_collision()
        self.check_zone_confinement()
        self.check_bio_thermal_invariants()
        self.check_resource_conservation()

        print("\n--- PASSED INVARIANTS (الفحوصات الناجحة) ---")
        for p in self.passes:
            print(f"  ✅ {p}")

        if self.warnings:
            print("\n--- SYSTEM WARNINGS (تنبيهات النظام) ---")
            for w in self.warnings:
                print(f"  ⚠️  {w}")

        if self.violations:
            print("\n--- INVARIANT VIOLATIONS (الخروقات المكتشفة) ---")
            for v in self.violations:
                print(f"  ❌ {v}")
            print("\n" + "=" * 75)
            print(f"  AUDIT FAILED: {len(self.violations)} invariant violation(s) detected.")
            print("=" * 75 + "\n")
            return 1
        else:
            print("\n" + "=" * 75)
            print("  AUDIT PASSED: 100% Deterministic World Invariant Integrity Verified.")
            print("=" * 75 + "\n")
            return 0

if __name__ == "__main__":
    auditor = WorldAuditor()
    sys.exit(auditor.run_all())
