# -*- coding: utf-8 -*-
"""
Unit tests for WorldAuditor (02_TOOLS/world_auditor.py).
"""

import os
import sys
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TOOLS_DIR = os.path.join(ROOT_DIR, "02_TOOLS")
if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)

from world_auditor import WorldAuditor


class TestWorldAuditor(unittest.TestCase):

    def setUp(self):
        self.auditor = WorldAuditor()
        self.loaded = self.auditor.load_files()

    def test_load_state(self):
        self.assertTrue(self.loaded, "WorldAuditor must load world state and rules.")
        self.assertIsNotNone(self.auditor.world_state)
        self.assertIsNotNone(self.auditor.world_bugs)
        self.assertGreater(len(self.auditor.physical_laws_text), 0)

    def test_spatial_collision_check(self):
        self.auditor.check_spatial_collision()
        self.assertEqual(len(self.auditor.violations), 0, "No spatial collisions should exist.")

    def test_zone_boundary_confinement(self):
        self.auditor.check_zone_confinement()
        self.assertEqual(len(self.auditor.violations), 0, "All characters must be confined to car bounds.")

    def test_westinghouse_pneumatics(self):
        self.auditor.check_westinghouse_fail_safe()
        self.assertEqual(len(self.auditor.violations), 0, "Westinghouse fail-safe (0.0 bar) must be verified.")

    def test_bio_dehydration(self):
        self.auditor.check_respiratory_dehydration_balance()
        self.assertEqual(len(self.auditor.violations), 0, "Bio-dehydration balance must hold.")

    def test_full_audit_passes(self):
        exit_code = self.auditor.run_all()
        self.assertEqual(exit_code, 0, "WorldAuditor run_all() must return 0 (100% passed).")


if __name__ == "__main__":
    unittest.main()
