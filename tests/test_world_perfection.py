#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
TEST SUITE: WORLD PERFECTION & ADVANCED INVARIANTS
(حزمة اختبارات اكتمال العالم وتكامل الثوابت المتقدمة)
==============================================================================
Tests:
  1. Affordance slot exclusivity and collision detection.
  2. Car affordance boundary confinement and unknown slot detection.
  3. Dynamic temporal state transition monotonicity (cooling & CO2).
  4. Negative mutation on temporal states: artificial heating rejected.
  5. Negative mutation on temporal states: CO2 ventilation leak rejected.
  6. Negative mutation on temporal states: reverse allostatic load rejected.
  7. Verification of the 5 new codified laws in PHYSICAL_LAWS.md.
==============================================================================
"""

import os
import sys
import unittest
import copy

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TOOLS_DIR = os.path.join(ROOT_DIR, "02_TOOLS")
if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)

from world_auditor import WorldAuditor
from temporal_transition_auditor import TemporalTransitionAuditor


class TestWorldPerfection(unittest.TestCase):
    """Exhaustive tests for phenomenological affordances and temporal matrix."""

    def setUp(self):
        self.auditor = WorldAuditor()
        self.auditor.load_files()

    def test_affordance_slots_clean_baseline(self):
        """Baseline check: all 14 characters occupy valid, distinct affordance slots."""
        self.auditor.check_spatial_collision()
        self.auditor.check_zone_confinement()
        self.assertEqual(len(self.auditor.violations), 0, f"Baseline should have 0 violations: {self.auditor.violations}")

    def test_mutation_affordance_exclusive_collision_detected(self):
        """Mutation: Two characters assigned the same exclusive affordance slot must trigger violation."""
        # Assign Abu Ali to Khalid's exclusive ammunition crate slot
        khalid_slot = self.auditor.world_state["characters"]["خالد"]["affordance_slot"]
        self.auditor.world_state["characters"]["أبو_علي"]["affordance_slot"] = khalid_slot

        self.auditor.check_spatial_collision()
        self.assertTrue(
            any("[Spatial Collision]" in v and "أبو_علي" in v and "خالد" in v for v in self.auditor.violations),
            f"Expected exclusive affordance collision, got: {self.auditor.violations}"
        )

    def test_mutation_unknown_affordance_slot_rejected(self):
        """Mutation: Character assigned an affordance slot not defined in the car must trigger boundary error."""
        self.auditor.world_state["characters"]["خالد"]["affordance_slot"] = "سرير_طائر_غير_موجود"
        self.auditor.check_zone_confinement()
        self.assertTrue(
            any("[Boundary Error]" in v and "سرير_طائر_غير_موجود" in v for v in self.auditor.violations),
            f"Expected invalid affordance slot error, got: {self.auditor.violations}"
        )

    def test_temporal_transition_clean_baseline(self):
        """Baseline check: all 5 temporal states satisfy physical continuity and monotonicity."""
        temp_auditor = TemporalTransitionAuditor()
        self.assertTrue(temp_auditor.load_data())
        self.assertTrue(temp_auditor.audit_temporal_transitions())
        self.assertEqual(len(temp_auditor.violations), 0)

    def test_mutation_temporal_heating_rejected(self):
        """Mutation: An unphysical temperature rise at midnight must be caught by TemporalTransitionAuditor."""
        temp_auditor = TemporalTransitionAuditor()
        self.assertTrue(temp_auditor.load_data())
        # Inject artificial warming in state T2 (00:00)
        temp_auditor.states_data["states"][2]["environment"]["ambient_temperature_c"] = +5.0
        self.assertFalse(temp_auditor.audit_temporal_transitions())
        self.assertTrue(
            any("Ambient temp rose" in v for v in temp_auditor.violations),
            f"Expected ambient temperature rise violation, got: {temp_auditor.violations}"
        )

    def test_mutation_temporal_co2_drop_rejected(self):
        """Mutation: CO2 dropping in an unventilated car at midnight must be caught."""
        temp_auditor = TemporalTransitionAuditor()
        self.assertTrue(temp_auditor.load_data())
        # Drop CO2 in Car 02 at midnight without ventilation
        temp_auditor.states_data["states"][2]["air_quality"]["car_02_co2_percent"] = 0.10
        self.assertFalse(temp_auditor.audit_temporal_transitions())
        self.assertTrue(
            any("CO2 in Car 02 dropped" in v for v in temp_auditor.violations),
            f"Expected CO2 drop violation, got: {temp_auditor.violations}"
        )

    def test_mutation_temporal_allostatic_reversal_rejected(self):
        """Mutation: Stress fatigue miraculously resetting to zero at 03:00 must be caught."""
        temp_auditor = TemporalTransitionAuditor()
        self.assertTrue(temp_auditor.load_data())
        temp_auditor.states_data["states"][3]["biometrics"]["allostatic_load"] = 0.05
        self.assertFalse(temp_auditor.audit_temporal_transitions())
        self.assertTrue(
            any("Allostatic load reversed" in v for v in temp_auditor.violations),
            f"Expected allostatic reversal violation, got: {temp_auditor.violations}"
        )

    def test_codification_of_five_new_statutory_laws(self):
        """Verify that all five newly formulated statutory laws exist in PHYSICAL_LAWS.md."""
        laws = ["LAW-BIO-06", "LAW-THERMO-03", "LAW-ACOUST-04", "LAW-MAT-01", "LAW-PSYCH-03"]
        for law in laws:
            self.assertIn(
                law, self.auditor.physical_laws_text,
                f"Statutory law {law} must be canonically codified in PHYSICAL_LAWS.md"
            )


if __name__ == "__main__":
    unittest.main()
