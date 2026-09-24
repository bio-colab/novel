# -*- coding: utf-8 -*-
"""
Unit tests for MetaAuditor (02_TOOLS/meta_auditor.py).
"""

import os
import sys
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TOOLS_DIR = os.path.join(ROOT_DIR, "02_TOOLS")
if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)

from meta_auditor import MetaAuditor


class TestMetaAuditor(unittest.TestCase):

    def setUp(self):
        self.auditor = MetaAuditor()
        self.loaded = self.auditor.load_defined_laws()

    def test_load_defined_laws(self):
        self.assertTrue(self.loaded, "MetaAuditor must load defined laws from PHYSICAL_LAWS.md.")
        self.assertEqual(len(self.auditor.defined_laws), 41, "There must be exactly 41 codified laws in PHYSICAL_LAWS.md.")
        self.assertIn("LAW-ELEC-01", self.auditor.defined_laws, "LAW-ELEC-01 must be codified in PHYSICAL_LAWS.md.")
        self.assertIn("LAW-BIO-05", self.auditor.defined_laws, "LAW-BIO-05 must be codified in PHYSICAL_LAWS.md.")
        self.assertIn("LAW-CHEM-01", self.auditor.defined_laws, "LAW-CHEM-01 must be codified in PHYSICAL_LAWS.md.")
        self.assertIn("LAW-BIO-06", self.auditor.defined_laws, "LAW-BIO-06 must be codified in PHYSICAL_LAWS.md.")
        self.assertIn("LAW-THERMO-03", self.auditor.defined_laws, "LAW-THERMO-03 must be codified in PHYSICAL_LAWS.md.")
        self.assertIn("LAW-ACOUST-04", self.auditor.defined_laws, "LAW-ACOUST-04 must be codified in PHYSICAL_LAWS.md.")
        self.assertIn("LAW-MAT-01", self.auditor.defined_laws, "LAW-MAT-01 must be codified in PHYSICAL_LAWS.md.")
        self.assertIn("LAW-PSYCH-03", self.auditor.defined_laws, "LAW-PSYCH-03 must be codified in PHYSICAL_LAWS.md.")

    def test_ethical_laws_present(self):
        ethical_laws = {"LAW-ETHIC-01", "LAW-ETHIC-02", "LAW-ETHIC-03"}
        self.assertTrue(ethical_laws.issubset(self.auditor.defined_laws), "All 3 ethical laws must be codified.")

    def test_scan_codebase_citations(self):
        citations = self.auditor.scan_codebase_for_citations()
        self.assertGreater(len(citations), 15, "Codebase should cite at least 15 distinct laws.")

    def test_no_orphan_citations(self):
        success = self.auditor.audit_reference_integrity()
        self.assertTrue(success, "All cited laws across codebase must be defined in PHYSICAL_LAWS.md.")
        self.assertEqual(len(self.auditor.violations), 0, "Zero orphan law citations allowed.")


if __name__ == "__main__":
    unittest.main()
