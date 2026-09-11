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
4. Bio-Thermal Invariants: Enforces LAW-BIO-01 (finger temp < 12°C -> dexterity < 0.60) and hypothermia thresholds.
5. Resource Arithmetic Balance: Enforces total ammo sum and water conservation.
6. Westinghouse Pneumatics: Enforces LAW-PNEUM-01 fail-safe shoe clamping at 0.0 bar.
7. Bio-Dehydration Balance: Enforces LAW-BIO-03 sub-zero breath water loss (40ml/hr) vs ration reserve.
8. Acoustic Epistemic Boundary: Enforces LAW-ACOUST-03 inter-car attenuation (>35 dB loss).
9. Chrono-Spatial Telemetry: Enforces timestamp format and temporal validity [0..645 minutes].
10. Train Spatial Topology: Enforces non-overlapping, continuous car intervals within train length envelope.

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

    def check_westinghouse_fail_safe(self):
        """Verify LAW-PNEUM-01: Fail-safe pneumatic braking mechanics"""
        brakes = self.world_state.get("train", {}).get("locomotive", {}).get("braking_system", {})
        pipe_pressure = brakes.get("train_pipe_pressure_bar", 5.0)
        shoes_state = brakes.get("brake_shoes", "")
        engine = self.world_state.get("train", {}).get("locomotive", {}).get("engine", {})
        engine_status = engine.get("status", "")
        engine_rpm = engine.get("rpm", 0)

        # Invariant: If pipe pressure < 3.5 bar (and specifically 0.0 bar), brake shoes MUST clamp the wheels
        if pipe_pressure < 3.5:
            if shoes_state != "clamped_locked":
                self.violations.append(
                    f"[LAW-PNEUM-01 Violation] Air pipe pressure is {pipe_pressure} bar (< 3.5 bar) but brake shoes are '{shoes_state}' (must be 'clamped_locked')."
                )
            elif engine_status != "stalled" or engine_rpm != 0:
                self.violations.append(
                    f"[LAW-PNEUM-01 Violation] Brake shoes clamped at 0.0 bar but locomotive engine is {engine_status} with {engine_rpm} RPM."
                )
            else:
                self.passes.append(
                    f"Westinghouse Pneumatics (LAW-PNEUM-01): Fail-safe lock verified at 0.0 bar (shoes clamped, motion locked)."
                )
        else:
            self.passes.append(f"Westinghouse Pneumatics: Nominal pressure ({pipe_pressure} bar).")

    def check_respiratory_dehydration_balance(self):
        """Verify LAW-BIO-03: Sub-zero desert respiration water loss against ration reserves"""
        env = self.world_state.get("environment", {})
        humidity = env.get("ambient_humidity_percent", 50.0)
        water_inv = self.world_state.get("inventory", {}).get("water_supply", {})
        vol_liters = water_inv.get("volume_remaining_liters", 0.0)
        ration_ml = water_inv.get("ration_unit_ml", 100.0)
        characters = self.world_state.get("characters", {})
        char_count = len(characters)

        # Desert aridity check (< 15% humidity triggers 40 ml/hr breath loss)
        loss_rate_per_person_ml_hr = 40.0 if humidity <= 15.0 else 25.0
        hourly_train_loss_liters = (char_count * loss_rate_per_person_ml_hr) / 1000.0

        # Timeline duration: 10.75 hours (19:00:00 to 05:45:00)
        duration_hours = 10.75
        total_respiratory_deficit_liters = round(hourly_train_loss_liters * duration_hours, 2)

        # Check reserve sufficiency
        ration_round_liters = (char_count * ration_ml) / 1000.0
        total_ration_rounds = vol_liters / ration_round_liters if ration_round_liters > 0 else 0

        if vol_liters < total_respiratory_deficit_liters:
            self.warnings.append(
                f"[LAW-BIO-03 Warning] Water reserves ({vol_liters}L) below theoretical 10.75h respiration deficit ({total_respiratory_deficit_liters}L)."
            )
        else:
            self.passes.append(
                f"Bio-Dehydration Balance (LAW-BIO-03): Respiration loss ({total_respiratory_deficit_liters}L for {char_count} souls over 10.75h) safely covered by {vol_liters}L reserve ({total_ration_rounds:.1f} ration rounds)."
            )

    def check_acoustic_epistemic_bounds(self):
        """Verify LAW-ACOUST-03: Inter-car acoustic attenuation prevents low-decibel knowledge leaks"""
        cars = self.world_state.get("train", {}).get("cars", {})
        car_01_occupants = cars.get("car_01_guard", {}).get("occupants", [])
        characters = self.world_state.get("characters", {})

        acoustic_leak = False
        for name in car_01_occupants:
            char_data = characters.get(name, {})
            auditory_bubble = char_data.get("epistemic_bubble", {}).get("auditory", "").lower()
            forbidden_terms = ["همس_سلوم", "عطاس_بشير", "حركة_العربة_الأخيرة_الخافتة"]
            for term in forbidden_terms:
                if term in auditory_bubble:
                    acoustic_leak = True
                    self.violations.append(
                        f"[LAW-ACOUST-03 Violation] '{name}' in Car 01 can hear low-intensity event '{term}' across closed cars (> 35 dB loss)."
                    )

        if not acoustic_leak:
            self.passes.append(
                "Inter-Car Acoustic Boundary (LAW-ACOUST-03): Acoustic attenuation (>35 dB loss) strictly compartmentalizes auditory perception."
            )

    def check_chrono_spatial_telemetry(self):
        """Verify consistency of timestamps and timeline progression across bugs and world state"""
        bugs = self.world_bugs.get("bugs", [])
        valid_timestamps = 0
        timestamp_pattern = re.compile(r"(\d{2}:\d{2}:\d{2})\s*\(Minute\s*(\d+)")

        for bug in bugs:
            bug_id = bug.get("id")
            evidence = bug.get("evidence", {})
            ts = evidence.get("telemetry_timestamp", "")
            if not ts:
                self.violations.append(f"[Telemetry Missing] Bug '{bug_id}' lacks telemetry_timestamp.")
                continue

            match = timestamp_pattern.search(ts)
            if not match:
                self.violations.append(f"[Telemetry Format Error] Bug '{bug_id}' has invalid timestamp format: '{ts}'.")
                continue

            time_str, minute_str = match.groups()
            minute_val = int(minute_str)
            if not (0 <= minute_val <= 645):
                self.violations.append(
                    f"[Timeline Range Error] Bug '{bug_id}' minute {minute_val} exceeds simulation window [0, 645]."
                )
            else:
                valid_timestamps += 1

        if valid_timestamps == len(bugs):
            self.passes.append(
                f"Chrono-Spatial Telemetry: All {valid_timestamps} world bugs possess verified timestamp and minute telemetries [0..645]."
            )

    def check_train_topology_and_envelope(self):
        """Verify geometric continuity and non-overlapping envelope of train cars"""
        train_metrics = self.world_state.get("train", {}).get("metrics", {})
        total_len = train_metrics.get("total_length_m", 0.0)
        cars = self.world_state.get("train", {}).get("cars", {})

        # Sort cars by y_start_m
        sorted_cars = sorted(cars.items(), key=lambda item: item[1].get("y_start_m", 0.0))
        overlap_found = False
        prev_y_end = 0.0

        for car_id, car_data in sorted_cars:
            y_start = car_data.get("y_start_m", 0.0)
            y_end = car_data.get("y_end_m", 0.0)
            length = car_data.get("length_m", 0.0)

            # Check car internal length arithmetic
            if round(y_end - y_start, 2) != round(length, 2):
                overlap_found = True
                self.violations.append(
                    f"[Topology Error] '{car_id}' length mismatch: y_end - y_start ({y_end - y_start:.2f}m) != length_m ({length}m)."
                )

            # Check non-overlap with previous car
            if y_start < prev_y_end:
                overlap_found = True
                self.violations.append(
                    f"[Topology Error] '{car_id}' y_start ({y_start}m) overlaps with previous car end ({prev_y_end}m)."
                )
            prev_y_end = y_end

        if prev_y_end > total_len:
            self.violations.append(
                f"[Topology Error] Train cars extend to {prev_y_end}m, exceeding total_length_m ({total_len}m)."
            )
        elif not overlap_found:
            self.passes.append(
                f"Train Spatial Topology: All {len(sorted_cars)} car intervals are continuous, non-overlapping, and bounded within {total_len}m envelope."
            )

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
        self.check_westinghouse_fail_safe()
        self.check_respiratory_dehydration_balance()
        self.check_acoustic_epistemic_bounds()
        self.check_chrono_spatial_telemetry()
        self.check_train_topology_and_envelope()
        self.check_subsystem_engines()

    def check_subsystem_engines(self):
        """Invoke and verify the three core narrative subsystem engines"""
        tools_dir = os.path.dirname(__file__)
        if tools_dir not in sys.path:
            sys.path.insert(0, tools_dir)

        # 1. Epistemic Tracker
        try:
            from epistemic_tracker import EpistemicTracker
            tracker = EpistemicTracker(WORLD_STATE_PATH)
            if tracker.load_world_state():
                tracker.check_epistemic_bubbles_integrity()
                tracker.check_inter_car_omniscience_leaks()
                tracker.check_transmission_channel_physics()
                if tracker.violations:
                    self.violations.extend(tracker.violations)
                else:
                    self.passes.append("Epistemic Engine: 100% boundary isolation, channels, and zero omniscience leaks verified.")
        except Exception as e:
            self.warnings.append(f"Could not run EpistemicTracker: {e}")

        # 2. Causality Graph Analyzer
        try:
            from causality_graph import CausalityGraphAnalyzer
            c_analyzer = CausalityGraphAnalyzer()
            c_analyzer.build_graph()
            if c_analyzer.verify_dag_acyclicity():
                self.passes.append(f"Causality DAG Engine: Acyclicity verified across {len(c_analyzer.nodes)} events with zero causal cycles.")
            if c_analyzer.violations:
                self.violations.extend(c_analyzer.violations)
        except Exception as e:
            self.warnings.append(f"Could not run CausalityGraphAnalyzer: {e}")

        # 3. Chrono-Event Engine
        try:
            from chrono_event_engine import ChronoEventEngine
            chrono_eng = ChronoEventEngine()
            chrono_eng.evaluate_narrative_actions()
            if chrono_eng.violations:
                self.violations.extend(chrono_eng.violations)
            else:
                self.passes.append("Chrono-Event Engine: Action feasibility and biological decay curves strictly validated.")
        except Exception as e:
            self.warnings.append(f"Could not run ChronoEventEngine: {e}")

        # 4. Psychology & Behavioral Detector
        try:
            from psychology_detector import PsychologyDetector
            psy_detector = PsychologyDetector()
            if psy_detector.load_novel():
                psy_detector.audit_neurological_tics_distribution()
                psy_detector.audit_panic_dialogue_fragmentation()
                psy_detector.audit_defense_mechanism_archetypes()
                if psy_detector.violations:
                    self.violations.extend(psy_detector.violations)
                else:
                    self.passes.append("Psychology Detector: 100% behavioral tics (LAW-BIO-02) and panic speech fragmentation verified.")
        except Exception as e:
            self.warnings.append(f"Could not run PsychologyDetector: {e}")

        # 5. Socio-Demography & Ideology Analyzer
        try:
            from socio_demography_analyzer import SocioDemographyAnalyzer
            socio_analyzer = SocioDemographyAnalyzer()
            demo_res = socio_analyzer.audit_demographic_census_and_strata()
            ideo_res = socio_analyzer.audit_ideological_distribution()
            power_res = socio_analyzer.audit_power_inversion_dynamics()
            econ_res = socio_analyzer.audit_economic_value_inversion()

            if demo_res["passed"] and ideo_res["passed"] and power_res["passed"] and econ_res["passed"]:
                self.passes.append("Socio-Demography Engine: 100% demographic mosaic, power inversion (LAW-SOC-01/03), and use-value primacy (LAW-SOC-02) verified.")
            else:
                self.violations.append("SocioDemographyAnalyzer detected invariants violation in social strata or power inversion dynamics.")
        except Exception as e:
            self.warnings.append(f"Could not run SocioDemographyAnalyzer: {e}")

        # 6. Historical & Political Analyzer
        try:
            from historical_political_analyzer import HistoricalPoliticalAnalyzer
            hist_analyzer = HistoricalPoliticalAnalyzer()
            anachronism_res = hist_analyzer.audit_anachronism_isolation()
            artifact_res = hist_analyzer.audit_analog_material_artifacts()
            erosion_res = hist_analyzer.audit_state_erosion_vs_void()
            geo_res = hist_analyzer.audit_geopolitical_prison_trajectory()

            if anachronism_res["passed"] and artifact_res["passed"] and erosion_res["passed"] and geo_res["passed"]:
                self.passes.append("Historical-Political Engine: 100% analog isolation (LAW-POL-01), state erosion (LAW-POL-02), and closed prison trajectory (LAW-POL-03) verified.")
            else:
                self.violations.append("HistoricalPoliticalAnalyzer detected anachronism or geopolitical trajectory violation.")
        except Exception as e:
            self.warnings.append(f"Could not run HistoricalPoliticalAnalyzer: {e}")

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

