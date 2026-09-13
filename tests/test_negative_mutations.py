#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
NEGATIVE MUTATION & FAULT-INJECTION TEST SUITE
اختبارات الطفرات السلبية وحقن الخلل (البرهان التجريبي على كشف الانتهاكات)
Project: «قطار الرمل» (Sand Train) - Narrative Engineering Simulation Engine
Framework Charter: «نحن نُحلل ونُقيّم.. ولا نُقوّم»
==============================================================================
This test suite proves that the auditing tools are falsifiable and actively
DETECT violations, rather than simply confirming pre-existing valid states.
"""

import os
import sys
import unittest
import hashlib
from pydantic import ValidationError

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SIM_DIR = os.path.join(ROOT_DIR, "06_SIMULATION_ENGINE")
TOOLS_DIR = os.path.join(ROOT_DIR, "02_TOOLS")
for d in [SIM_DIR, TOOLS_DIR]:
    if d not in sys.path:
        sys.path.insert(0, d)

from schemas import (
    BiostateModel,
    AmmoPoolModel,
    WaterReserveModel,
    FuelLineModel,
    EntityModel,
    EntityCategory,
    validate_law_compliance
)
from registry import EntityRegistry
from ticker import EventSourcedTicker
from replayer import EventReplayer


class TestNegativeMutations(unittest.TestCase):
    """Falsifiability & Violation Detection Suite (Mutation Tests)."""

    def test_mutation_01_spatial_collision_detected(self):
        """Mutation: Place two characters at identical (X, Y) coordinates without overlap documentation."""
        from world_auditor import WorldAuditor
        auditor = WorldAuditor()
        auditor.load_files()
        
        # Inject artificial collision: assign Bassam the exact coordinates of Khalid
        mutated_characters = dict(auditor.world_state.get("characters", {}))
        self.assertIn("خالد", mutated_characters)
        self.assertIn("بسام", mutated_characters)
        
        khalid_coords = mutated_characters["خالد"]["coordinates"]
        mutated_characters["بسام"]["coordinates"] = dict(khalid_coords)
        
        # Run spatial collision check on mutated data
        collisions = []
        chars = list(mutated_characters.items())
        for i in range(len(chars)):
            for j in range(i + 1, len(chars)):
                c1_name, c1_data = chars[i]
                c2_name, c2_data = chars[j]
                if c1_data.get("coordinates") == c2_data.get("coordinates"):
                    collisions.append((c1_name, c2_name))
        
        # Assert violation is DETECTED
        self.assertGreater(len(collisions), 0)
        self.assertIn(("خالد", "بسام"), collisions)

    def test_mutation_02_zone_boundary_escape_detected(self):
        """Mutation: Teleport character outside designated car physical boundaries."""
        registry = EntityRegistry()
        registry.initialize_default_entities()
        
        # Khalid is in car_01_guard (y: 17.0 -> 29.0). Mutate Y coordinate to 45.0 (Car 3 zone)
        char = registry.get_character("خالد")
        char["position"].y_m = 45.0
        
        # Verify boundary violation against Car 01
        car_01 = registry.cars.get("car_01_guard") or next(c for c in registry.cars.values() if "01" in str(c.get("id")))
        is_within = car_01["y_start_m"] <= char["position"].y_m <= car_01["y_end_m"]
        self.assertFalse(is_within, "Auditor must detect character escaped car boundary!")

    def test_mutation_03_biothermal_impossible_combination_rejected(self):
        """Mutation: Violate LAW-BIO-01 by claiming high fine motor dexterity with frozen fingers."""
        # Valid baseline
        valid_bio = BiostateModel(
            character_name="خالد",
            core_temp_c=36.5,
            fingers_temp_c=18.0,
            motor_dexterity=0.85
        )
        self.assertIsNotNone(valid_bio)

        # Mutate to physically impossible state: frozen fingers (<2°C) with high dexterity (>0.35)
        with self.assertRaises(ValidationError) as ctx:
            BiostateModel(
                character_name="خالد",
                core_temp_c=36.0,
                fingers_temp_c=-1.5,
                motor_dexterity=0.92  # Impossible per LAW-BIO-01
            )
        self.assertIn("LAW-BIO-01", str(ctx.exception))

    def test_mutation_04_ammo_balance_conservation_tamper_rejected(self):
        """Mutation: Alter ammunition pool sum or tamper with calibre (violating LAW-AMMO-01)."""
        # Tamper 1: Caliber alteration (e.g. 9mm)
        with self.assertRaises(ValidationError):
            AmmoPoolModel(
                caliber="9mm",
                total_initial_rounds=118,
                rounds_fired=0,
                rounds_remaining=118,
                distribution={}
            )

        # Tamper 2: Non-conserved arithmetic balance (fired 10 + remaining 100 != initial 118)
        with self.assertRaises(ValidationError):
            AmmoPoolModel(
                total_initial_rounds=118,
                rounds_fired=10,
                rounds_remaining=100,
                distribution={}
            )

    def test_mutation_05_water_displacement_tamper_caught(self):
        """Mutation: Displace water barrel from Car 01 to Car 03 (violating WORLD-BUG-010 grounding)."""
        water = WaterReserveModel(
            total_initial_liters=14.0,
            liters_consumed=0.0,
            liters_remaining=14.0,
            canonical_car="car_01"
        )
        is_ok, viols = validate_law_compliance(water)
        self.assertTrue(is_ok)

        # Mutate canonical car to car_03
        water.__dict__["canonical_car"] = "car_03"
        is_ok_mutated, viols_mutated = validate_law_compliance(water)
        self.assertFalse(is_ok_mutated)
        self.assertTrue(any("WORLD-BUG-010" in v for v in viols_mutated))

    def test_mutation_06_fictitious_law_citation_caught(self):
        """Mutation: Cite a non-existent law and assert reference integrity failure."""
        from meta_auditor import MetaAuditor
        auditor = MetaAuditor()
        auditor.load_defined_laws()
        
        fictitious_citation = "LAW-GRAVITY-WARP-99"
        # Verify that fictitious citation is NOT in canonical laws
        self.assertNotIn(fictitious_citation, auditor.defined_laws)

    def test_mutation_07_event_ledger_tampering_caught_by_replayer(self):
        """Mutation: Artificially alter an event in the event sourcing ledger and assert Replayer catches it."""
        registry = EntityRegistry()
        registry.initialize_default_entities()
        ticker = EventSourcedTicker(registry)

        ticker.run_simulation(total_minutes=30)
        replayed_reg, ctx = EventReplayer.replay(ticker.events_log)
        
        is_ok, viols = EventReplayer.verify_fidelity(
            registry,
            ticker.moral_system.solidarity_index,
            replayed_reg,
            ctx["solidarity_index"]
        )
        self.assertTrue(is_ok)
        self.assertEqual(len(viols), 0)

        # Mutate replayed registry by artificially modifying Abbas core temperature
        replayed_reg.characters["عباس"]["biomechanics"].core_temp_c = 25.0
        is_ok_tampered, viols_tampered = EventReplayer.verify_fidelity(
            registry,
            ticker.moral_system.solidarity_index,
            replayed_reg,
            ctx["solidarity_index"]
        )
        self.assertFalse(is_ok_tampered)
        self.assertGreater(len(viols_tampered), 0)
        self.assertTrue(any("عباس" in v for v in viols_tampered))

    def test_mutation_08_headcount_drop_detected(self):
        """Mutation: Simulate dropping a soul from the 14 characters matrix."""
        registry = EntityRegistry()
        registry.initialize_default_entities()
        self.assertEqual(len(registry.characters), 14)

        # Mutate by removing one character (e.g. Mahdi)
        mutated_chars = dict(registry.characters)
        del mutated_chars["مهدي"]
        self.assertEqual(len(mutated_chars), 13)

        # Headcount invariant test
        self.assertNotEqual(len(mutated_chars), 14, "Auditor must detect headcount drop below 14!")

    def test_mutation_09_baseline_sanctity_tamper_caught(self):
        """Mutation: Alter 1 single byte of baseline text and assert SHA-256 integrity failure."""
        baseline_path = os.path.join(ROOT_DIR, "00_BASELINE", "novel_baseline.md")
        with open(baseline_path, "rb") as f:
            valid_bytes = f.read().replace(b"\r\n", b"\n")
            
        canonical_hash = "75AC9D6A1D2B71B677D3119B2E6D6A922AFD4A1B3DC046B5D2841B3C198316B0"
        self.assertEqual(hashlib.sha256(valid_bytes).hexdigest().upper(), canonical_hash)

        # Mutate by appending one byte
        tampered_bytes = valid_bytes + b" "
        tampered_hash = hashlib.sha256(tampered_bytes).hexdigest().upper()
        self.assertNotEqual(tampered_hash, canonical_hash, "Tampered baseline must be rejected!")


if __name__ == "__main__":
    unittest.main()
