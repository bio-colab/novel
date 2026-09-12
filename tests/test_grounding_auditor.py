# -*- coding: utf-8 -*-
"""
Unit tests for GroundingAuditor (02_TOOLS/grounding_auditor.py).
"""

import os
import sys
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TOOLS_DIR = os.path.join(ROOT_DIR, "02_TOOLS")
if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)

from grounding_auditor import GroundingAuditor


class TestGroundingAuditor(unittest.TestCase):

    def setUp(self):
        self.auditor = GroundingAuditor()
        self.loaded = self.auditor.load_data()

    def test_load_data(self):
        self.assertTrue(self.loaded, "GroundingAuditor must successfully load baseline, bugs, and world state.")
        self.assertIsNotNone(self.auditor.parts)
        self.assertIsNotNone(self.auditor.line_map)
        self.assertIsNotNone(self.auditor.bugs_data)
        self.assertIsNotNone(self.auditor.world_state)

    def test_audit_chapter_indexing(self):
        self.auditor.audit_chapter_indexing()
        self.assertEqual(len(self.auditor.violations), 0, "Chapter indexing must pass with zero violations.")
        self.assertTrue(any("32 chapters" in p for p in self.auditor.passes))

    def test_audit_telemetry_grounding(self):
        self.auditor.audit_telemetry_grounding()
        self.assertEqual(len(self.auditor.violations), 0, "Telemetry grounding must pass with zero violations.")

    def test_audit_abbas_ammunition_truth(self):
        self.auditor.audit_abbas_ammunition_truth()
        self.assertEqual(len(self.auditor.violations), 0, "Abbas ammunition must confirm 3 rounds, not 30.")

    def test_audit_trapdoor_purge_and_exit_vector(self):
        self.auditor.audit_trapdoor_purge_and_exit_vector()
        self.assertEqual(len(self.auditor.violations), 0, "Trapdoor purge and sliding door exit must pass.")

    def test_audit_headcount_invariants_and_slip(self):
        self.auditor.audit_headcount_invariants_and_slip()
        self.assertEqual(len(self.auditor.violations), 0, "Headcount preservation and WORLD-BUG-007 slip audit must pass.")

    def test_audit_internal_time_vs_ephemeris(self):
        self.auditor.audit_internal_time_vs_ephemeris()
        self.assertEqual(len(self.auditor.violations), 0, "Internal time paradox audit (WORLD-BUG-008) must pass.")

    def test_full_run(self):
        success = self.auditor.run_all()
        self.assertTrue(success, "GroundingAuditor run_all() must return True.")


if __name__ == "__main__":
    unittest.main()
