#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
SIMULATION ENGINE UNIT TESTS (اختبارات الوحدة لمحرك المحاكاة والتوأم الرقمي)
Project: «قطار الرمل» (Sand Train) - Narrative Engineering Simulation Engine
Framework Charter: «نحن نُحلل ونُقيّم.. ولا نُقوّم»
==============================================================================
"""

import os
import sys
import unittest
from pydantic import ValidationError

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SIM_DIR = os.path.join(ROOT_DIR, "06_SIMULATION_ENGINE")
if SIM_DIR not in sys.path:
    sys.path.insert(0, SIM_DIR)

from schemas import (
    BiostateModel,
    AmmoPoolModel,
    WaterReserveModel,
    FuelLineModel,
    SimulationEvent,
    validate_law_compliance,
    assert_law_compliance,
    LawViolationError,
    EntityModel,
    EntityCategory
)
from components import (
    PositionComponent,
    BiomechanicalComponent,
    PsychologicalComponent
)
from registry import EntityRegistry
from systems.thermodynamics import ThermodynamicSystem
from systems.neurology import NeurologySystem
from systems.acoustics import AcousticsSystem
from systems.resources import ResourcesSystem
from systems.moral_entropy import MoralEntropySystem
from ticker import EventSourcedTicker
from constraints import NarrativeConstraintGenerator


class TestSimulationEngine(unittest.TestCase):
    """Test suite for Event-Sourced Chrono-Simulation Engine."""

    def test_01_biostate_schema_validation(self):
        """Validates Pydantic schema validation and physical impossibility rejection."""
        # Valid state
        bio = BiostateModel(
            character_name="خالد",
            core_temp_c=36.8,
            fingers_temp_c=22.0,
            motor_dexterity=0.90
        )
        self.assertEqual(bio.character_name, "خالد")
        self.assertTrue(bio.is_alive)

        # Invariant rejection: frozen fingers (<2°C) cannot have high fine motor dexterity (>0.35)
        with self.assertRaises(ValidationError):
            BiostateModel(
                character_name="خالد",
                core_temp_c=36.0,
                fingers_temp_c=0.0,
                motor_dexterity=0.85  # Violates LAW-BIO-01
            )

    def test_02_resources_schema_and_caliber_invariants(self):
        """Ensures strict caliber 7.62x39mm and ammunition conservation (LAW-AMMO-01)."""
        ammo = AmmoPoolModel(
            total_initial_rounds=118,
            rounds_fired=0,
            rounds_remaining=118,
            distribution={"عباس": 27, "خالد": 28, "حناطة": 28, "مخزن_طوارئ": 35}
        )
        self.assertEqual(ammo.caliber, "7.62x39mm")

        # Invalid caliber rejection
        with self.assertRaises(ValidationError):
            AmmoPoolModel(
                caliber="9mm",  # Invalid caliber
                total_initial_rounds=100,
                rounds_fired=0,
                rounds_remaining=100,
                distribution={}
            )

        # Ammunition balance non-conservation rejection
        with self.assertRaises(ValidationError):
            AmmoPoolModel(
                total_initial_rounds=118,
                rounds_fired=10,
                rounds_remaining=100,  # 10 + 100 != 118
                distribution={}
            )

    def test_03_law_compliance_gateway(self):
        """Verifies validate_law_compliance and assert_law_compliance."""
        water = WaterReserveModel(
            total_initial_liters=14.0,
            liters_consumed=0.0,
            liters_remaining=14.0,
            canonical_car="car_01"
        )
        is_ok, viols = validate_law_compliance(water)
        self.assertTrue(is_ok)
        self.assertEqual(len(viols), 0)

        # Violation test: corrupted water barrel in wrong car
        water_corrupted = WaterReserveModel(
            total_initial_liters=14.0,
            liters_consumed=0.0,
            liters_remaining=14.0,
            canonical_car="car_01"
        )
        # Manually alter attribute to test gateway
        water_corrupted.__dict__["canonical_car"] = "car_03"
        is_ok2, viols2 = validate_law_compliance(water_corrupted)
        self.assertFalse(is_ok2)
        self.assertTrue(any("WORLD-BUG-010" in v for v in viols2))

    def test_04_entity_registry_and_snapshot(self):
        """Verifies canonical entity registry initialization from world_state.yaml."""
        registry = EntityRegistry()
        registry.initialize_default_entities()

        self.assertEqual(len(registry.characters), 14)
        self.assertIn("خالد", registry.characters)
        self.assertIn("أبو_علي", registry.characters)
        self.assertIn("سردار", registry.characters)

        # Snapshot verification
        snap = registry.snapshot()
        self.assertEqual(snap["characters_count"], 14)
        self.assertIn("characters", snap)
        self.assertIn("خالد", snap["characters"])
        self.assertAlmostEqual(snap["environment"]["ambient_temp_c"], 0.0)

    def test_05_thermodynamics_and_cooling_curve(self):
        """Verifies radiation cooling formula hitting -8.0°C at minute 570."""
        registry = EntityRegistry()
        registry.initialize_default_entities()

        # Minute 0: 0.0°C
        env_0 = ThermodynamicSystem.update_environment(registry, 0)
        self.assertEqual(env_0["ambient_temp_c"], 0.0)

        # Minute 570 (04:30): -8.0°C floor
        env_570 = ThermodynamicSystem.update_environment(registry, 570)
        self.assertEqual(env_570["ambient_temp_c"], -8.0)

        # Minute 645 (05:45): maintains -8.0°C floor
        env_645 = ThermodynamicSystem.update_environment(registry, 645)
        self.assertEqual(env_645["ambient_temp_c"], -8.0)

    def test_06_neurology_and_motor_dexterity(self):
        """Verifies fine motor dexterity collapse and shivering transitions."""
        registry = EntityRegistry()
        registry.initialize_default_entities()

        # Update environment and characters at minute 570
        ThermodynamicSystem.update_environment(registry, 570)
        ThermodynamicSystem.update_characters(registry, -8.0, 570)
        NeurologySystem.update(registry, 570)

        khalid_bio = registry.characters["خالد"]["biomechanics"]
        self.assertLessEqual(khalid_bio.fingers_temp_c, 0.0)
        self.assertLessEqual(khalid_bio.motor_dexterity, 0.15)
        self.assertIn(khalid_bio.shivering_stage, ["shivering_exhaustion", "violent_shivering", "hypothermic_torpor"])

    def test_07_acoustics_intercar_isolation(self):
        """Verifies inter-car attenuation (>35 dB) per LAW-ACOUST-03."""
        # Inside same car: hearing is unobstructed
        can_hear_same, spl_same = AcousticsSystem.can_hear("car_01_guard", "car_01_guard", 120.0)
        self.assertTrue(can_hear_same)
        self.assertEqual(spl_same, 120.0)

        # Across adjacent car: 35 dB attenuation
        can_hear_adj, spl_adj = AcousticsSystem.can_hear("car_01_guard", "car_02_prisoners", 120.0)
        self.assertEqual(spl_adj, 85.0)

        # Across 3 cars: 105 dB attenuation; 80 dB speech becomes inaudible (<30 dB)
        can_hear_far, spl_far = AcousticsSystem.can_hear("locomotive", "car_03_hospital", 80.0)
        self.assertFalse(can_hear_far)
        self.assertLess(spl_far, 30.0)

    def test_08_ticker_and_narrative_constraints(self):
        """Verifies 645-minute simulation run and narrative constraint card generation."""
        registry = EntityRegistry()
        registry.initialize_default_entities()
        ticker = EventSourcedTicker(registry)

        ticker.run_simulation(total_minutes=645)
        self.assertEqual(ticker.current_minute, 645)
        self.assertGreaterEqual(len(ticker.state_history), 40)

        # Generate constraint cards
        cards = NarrativeConstraintGenerator.generate_constraint_cards(ticker)
        self.assertEqual(len(cards), 5)

        # Minute 15 card (Abu Ali initial inspection) must be feasible
        card_01 = next(c for c in cards if c["card_id"] == "CARD-01-STALL-COLD")
        self.assertTrue(card_01["action_evaluation"]["is_strictly_feasible"])

        # Minute 570 card (Sardar twisting wire under chassis at -8°C) must be unfeasible with bare hands
        card_04 = next(c for c in cards if c["card_id"] == "CARD-04-UNDER-CHASSIS-WIRE")
        self.assertFalse(card_04["action_evaluation"]["is_strictly_feasible"])
        self.assertIn("PR-005", card_04["action_evaluation"]["author_advisory_note"])

    def test_09_entity_taxonomy_and_id_uniqueness(self):
        """Validates canonical entity taxonomy, uniqueness and cross-index resolution."""
        registry = EntityRegistry()
        registry.initialize_default_entities()

        self.assertGreaterEqual(len(registry.entities), 39)
        self.assertEqual(len(registry.entities_by_category[EntityCategory.CHARACTER]), 14)
        self.assertEqual(len(registry.entities_by_category[EntityCategory.VEHICLE]), 5)
        self.assertEqual(len(registry.entities_by_category[EntityCategory.PROP]), 15)
        self.assertEqual(len(registry.entities_by_category[EntityCategory.LANDMARK]), 5)

        # ID Uniqueness
        all_ids = list(registry.entities.keys())
        self.assertEqual(len(all_ids), len(set(all_ids)))

        all_nums = list(registry.entities_by_numeric_id.keys())
        self.assertEqual(len(all_nums), len(set(all_nums)))

        # Cross-index lookups
        khalid_by_str = registry.get_entity("ENT-CHAR-1001")
        khalid_by_int = registry.get_entity(1001)
        khalid_by_name = registry.get_entity("خالد")
        self.assertIsNotNone(khalid_by_str)
        self.assertEqual(khalid_by_str, khalid_by_int)
        self.assertEqual(khalid_by_str, khalid_by_name)

    def test_10_entity_spatial_containment_and_props(self):
        """Verifies spatial containment and character prop possession queries."""
        registry = EntityRegistry()
        registry.initialize_default_entities()

        # Car 01 props
        car_01_props = registry.get_props_in_car("ENT-VEH-2002")
        self.assertGreaterEqual(len(car_01_props), 8)
        prop_ids = [p.entity_id for p in car_01_props]
        self.assertIn("ENT-PROP-3001", prop_ids)  # Blue water barrel
        self.assertIn("ENT-PROP-3005", prop_ids)  # Ammo crate

        # Items held by characters
        khalid_items = registry.get_items_held_by("ENT-CHAR-1001")
        self.assertEqual(len(khalid_items), 1)
        self.assertEqual(khalid_items[0].entity_id, "ENT-PROP-3002")  # Khalid's rifle

        abu_ali_items = registry.get_items_held_by("ENT-CHAR-1002")
        abu_ali_ids = [item.entity_id for item in abu_ali_items]
        self.assertIn("ENT-PROP-3008", abu_ali_ids)  # Wire cutter
        self.assertIn("ENT-PROP-3012", abu_ali_ids)  # Diesel rag

    def test_11_entity_schema_validation_rejection(self):
        """Ensures strict Pydantic rejection of invalid taxonomy IDs and malformed records."""
        # 1. Reject invalid prefix regex
        with self.assertRaises(ValidationError):
            EntityModel(
                entity_id="ENT-ALIEN-9999",
                numeric_id=9999,
                canonical_name="فضائي",
                category=EntityCategory.CHARACTER
            )

        # 2. Reject mismatch between string number and integer ID
        with self.assertRaises(ValidationError):
            EntityModel(
                entity_id="ENT-CHAR-1001",
                numeric_id=1002,  # Mismatch!
                canonical_name="خالد",
                category=EntityCategory.CHARACTER
            )

        # 3. Reject category range violation (e.g. VEHICLE given CHARACTER ID range)
        with self.assertRaises(ValidationError):
            EntityModel(
                entity_id="ENT-VEH-1001",  # VEHICLE must be in 2001..2099
                numeric_id=1001,
                canonical_name="عربة خطأ",
                category=EntityCategory.VEHICLE
            )

        # 4. Reject negative mass
        with self.assertRaises(ValidationError):
            EntityModel(
                entity_id="ENT-PROP-3001",
                numeric_id=3001,
                canonical_name="برميل سالب",
                category=EntityCategory.PROP,
                mass_kg=-5.0
            )


if __name__ == "__main__":
    unittest.main()
