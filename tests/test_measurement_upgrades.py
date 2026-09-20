#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UNIT TESTS: MEASUREMENT SUITE CALIBRATION & ANTI-PARADOX UPGRADES
Project: «قطار الرمل» (Sand Train) - World Auditing Hardening
License: MIT
"""

import sys
import unittest
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent.parent / "02_TOOLS"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from epistemic_tracker import EpistemicTracker
from moral_entropy_monitor import MoralEntropyMonitor
from chrono_event_engine import ChronoEventEngine


class TestMeasurementUpgrades(unittest.TestCase):
    """Tests verifying the calibration and paradox-resolution upgrades in measurement tools."""

    def test_epistemic_metaphor_vs_omniscience_filtering(self):
        """Verify that EpistemicTracker distinguishes between poetic intuition and true omniscience leaks."""
        tracker = EpistemicTracker()
        
        # 1. Poetic Intuition (Must NOT be flagged as an illegal leak)
        metaphor = "أشعر أن الموت يحوم فوق رؤوسنا وأن الليل سيبتلع أحدنا في العربات الخلفية"
        res_metaphor = tracker.audit_metaphor_vs_omniscience(
            character="خالد",
            statement=metaphor,
            localized_truth="مقتل عباس على الحصى"
        )
        self.assertFalse(res_metaphor["is_leak"], "Poetic intuition must not be flagged as an illegal omniscience leak.")
        self.assertEqual(res_metaphor["classification"], "metaphoric_intuition")

        # 2. Fact Leak (MUST be flagged as an illegal omniscience leak)
        factual_leak = "عباس مقتول خارج العربة بثلاث طلقات في صدره وجثته على الحصى ممسكة بحجر الصوان"
        res_leak = tracker.audit_metaphor_vs_omniscience(
            character="خالد",
            statement=factual_leak,
            localized_truth="مقتل عباس على الحصى"
        )
        self.assertTrue(res_leak["is_leak"], "Explicit factual knowledge from outside car must be flagged as leak.")
        self.assertEqual(res_leak["classification"], "illegal_omniscience_leak")

    def test_moral_entropy_material_grounding(self):
        """Verify that MoralEntropyMonitor anchors all S_moral transitions to concrete physical transactions."""
        monitor = MoralEntropyMonitor()
        loaded = monitor.load_data()
        self.assertTrue(loaded, "MoralEntropyMonitor must load data cleanly.")

        res = monitor.audit_material_grounding_of_moral_entropy()
        self.assertTrue(res["passed"], "All S_moral steps must possess verified material grounding.")
        self.assertEqual(res["grounded_milestones"], 5, "Exactly 5 milestones must be physically grounded.")

    def test_caloric_depletion_curve(self):
        """Verify that ChronoEventEngine computes continuous caloric deficit enforcing LAW-BIO-04."""
        engine = ChronoEventEngine()
        engine.audit_caloric_depletion_and_torpor()
        self.assertEqual(len(engine.violations), 0, "Caloric accounting must pass with zero violations.")
        self.assertTrue(any("Continuous Caloric Depletion" in p for p in engine.passes))

    def test_diesel_paraffin_gelling_invariant(self):
        """Verify that diesel fuel cloud point and gelling (LAW-CHEM-01) is verified."""
        from world_auditor import WorldAuditor
        auditor = WorldAuditor()
        loaded = auditor.load_files()
        self.assertTrue(loaded, "WorldAuditor must load files cleanly.")
        auditor.check_diesel_paraffin_gelling_invariant()
        self.assertEqual(len(auditor.violations), 0, "Diesel paraffin gelling check must pass without violations.")
        self.assertTrue(any("Diesel Chemistry & Gelling (LAW-CHEM-01)" in p for p in auditor.passes))

    def test_excretion_and_atmosphere_invariant(self):
        """Verify that excretion and enclosed atmosphere (LAW-BIO-05) is verified."""
        from world_auditor import WorldAuditor
        auditor = WorldAuditor()
        loaded = auditor.load_files()
        self.assertTrue(loaded, "WorldAuditor must load files cleanly.")
        auditor.check_excretion_and_atmosphere_invariant()
        self.assertEqual(len(auditor.violations), 0, "Excretion check must pass without violations.")
        self.assertTrue(any("Excretion & Enclosed Atmosphere (LAW-BIO-05)" in p for p in auditor.passes))

    def test_sociology_physics_bridge(self):
        """Verify that guard power erosion is causally anchored in cold biology."""
        from socio_demography_analyzer import SocioDemographyAnalyzer
        analyzer = SocioDemographyAnalyzer()
        res = analyzer.audit_sociology_physics_bridge()
        self.assertTrue(res["passed"], "Sociology-physics bridge must pass with verified physical markers.")
        self.assertTrue(res["motor_stiffness_present"])
        self.assertTrue(res["vocal_tremor_present"])
        self.assertTrue(res["khalid_power_decline"])


if __name__ == "__main__":
    unittest.main()
