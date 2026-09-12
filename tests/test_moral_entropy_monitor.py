# -*- coding: utf-8 -*-
"""
Unit tests for MoralEntropyMonitor (02_TOOLS/moral_entropy_monitor.py).
"""

import os
import sys
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TOOLS_DIR = os.path.join(ROOT_DIR, "02_TOOLS")
if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)

from moral_entropy_monitor import MoralEntropyMonitor


class TestMoralEntropyMonitor(unittest.TestCase):

    def setUp(self):
        self.monitor = MoralEntropyMonitor()
        self.loaded = self.monitor.load_data()

    def test_load_data(self):
        self.assertTrue(self.loaded, "MoralEntropyMonitor must load baseline and rules.")
        self.assertGreater(len(self.monitor.baseline_lines), 0)

    def test_audit_moral_typology_quadrants(self):
        res = self.monitor.audit_moral_typology_quadrants()
        self.assertTrue(res["passed"], "Moral typology quadrants audit must pass.")
        self.assertEqual(res["total_census"], 14, "Total classified souls must equal 14.")
        # Verify non-monopoly: each quadrant <= 60% of 14 (i.e. <= 8)
        for q_id, count in res["quadrant_counts"].items():
            self.assertLessEqual(count, 8, f"Quadrant '{q_id}' has {count} members, exceeding 60% threshold.")

    def test_audit_moral_entropy_curve(self):
        res = self.monitor.audit_moral_entropy_curve()
        self.assertTrue(res["passed"], "Moral entropy curve audit must pass.")
        self.assertEqual(res["peak_entropy"], 0.85, "Peak entropy must be 0.85 at ambush.")
        self.assertGreater(res["final_entropy"], 0.0, "Entropy must remain > 0 to preserve tragic realism.")
        self.assertLess(res["final_entropy"], res["peak_entropy"], "Final entropy must be lower than peak.")

    def test_audit_causal_moral_debt(self):
        res = self.monitor.audit_causal_moral_debt()
        self.assertTrue(res["passed"], "Causal moral debt audit must pass.")
        self.assertIsNotNone(res["hasan_kaz_line"])
        self.assertIsNotNone(res["hannata_line"])

    def test_audit_funerary_dignity_preservation(self):
        res = self.monitor.audit_funerary_dignity_preservation()
        self.assertTrue(res["passed"], "Funerary dignity preservation audit must pass.")
        self.assertIsNotNone(res["stone_line"])
        self.assertIsNotNone(res["salloum_line"])
        self.assertIsNotNone(res["rear_car_line"])
        self.assertIsNotNone(res["mawal_line"])

    def test_full_run(self):
        success = self.monitor.run_all()
        self.assertTrue(success, "MoralEntropyMonitor run_all() must return True.")


if __name__ == "__main__":
    unittest.main()
