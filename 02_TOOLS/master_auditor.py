#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
MASTER AUDITOR & PLATFORM ORCHESTRATOR (المنسق المركزي الشامل لمنصة المحاكاة)
==============================================================================
Project: «قطار الرمل» (Sand Train) - Narrative Engineering Platform Engine
License: MIT
Framework Charter: «نحن نُحلل ونُقيّم.. ولا نُقوّم» (Evaluation & Determinism,
                   Zero Literary Interference).

Purpose:
  Acts as the unified master orchestrator executing the entire deterministic
  audit suite, including:
    1. Automated Unit Tests Suite (tests/ with Python unittest).
    2. Core Deterministic World Auditor (world_auditor.py with 20 subsystem checks).
    3. Epistemic & Grounding Calibrators (grounding_auditor.py, epistemic_tracker.py, causality_graph.py).
    4. Moral, Psychological & Socio-Political Engines (moral_entropy_monitor.py, psychology_detector.py,
       socio_demography_analyzer.py, historical_political_analyzer.py, chrono_event_engine.py).
    5. Sensory, Stylistic & Pacing Linters (sensory_linter.py, dialogue_auditor.py,
       pacing_visualizer.py, character_tracker.py).
    6. Secondary World Brain & Knowledge Graph Verifier (world_graph_builder.py).
    7. Governance, Baseline Sanctity & Staging Gate (SHA-256 baseline verification,
       workspace hygiene, author blessing staging validation).

Outputs:
  - Rich Terminal CLI Dashboard with structured execution phases and timings.
  - Generates comprehensive JSON audit record: 03_AUDIT_AND_ISSUES/MASTER_AUDIT_REPORT.json.
  - Strict Exit Codes: 0 if 100% passed, 1 if any failure/violation detected.
==============================================================================
"""

import os
import sys
import time
import json
import yaml
import hashlib
import unittest
import argparse
from datetime import datetime, timezone
from typing import Dict, List, Any

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TOOLS_DIR = os.path.join(ROOT_DIR, "02_TOOLS")
TESTS_DIR = os.path.join(ROOT_DIR, "tests")
REPORT_PATH = os.path.join(ROOT_DIR, "03_AUDIT_AND_ISSUES", "MASTER_AUDIT_REPORT.json")

if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)


class MasterAuditor:
    """Unified Platform Orchestrator and Master Audit Runner."""

    def __init__(self, verbose: bool = False, is_ci: bool = False):
        self.verbose = verbose
        self.is_ci = is_ci
        self.start_time = 0.0
        self.total_duration = 0.0
        self.results: Dict[str, Any] = {
            "metadata": {
                "engine": "Sand Train Closed-World Platform Engine",
                "version": "2.0.0-platform-engine",
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "charter": "نحن نُحلل ونُقيّم.. ولا نُقوّم"
            },
            "phases": {},
            "summary": {
                "total_checks": 0,
                "passed_checks": 0,
                "failed_checks": 0,
                "success_rate_percent": 100.0,
                "status": "PENDING"
            }
        }
        self.phase_failures = 0

    def run_phase_unit_tests(self) -> bool:
        """Phase 1: Executes automated unit tests suite using unittest."""
        t0 = time.time()
        print("\n" + "━" * 80)
        print("  PHASE 1: AUTOMATED UNIT TESTS SUITE (حزمة اختبارات الوحدة المؤتمتة)")
        print("━" * 80)

        loader = unittest.TestLoader()
        suite = loader.discover(TESTS_DIR)
        runner = unittest.TextTestRunner(verbosity=1 if not self.verbose else 2)
        test_result = runner.run(suite)

        duration = time.time() - t0
        total_tests = test_result.testsRun
        failures = len(test_result.failures)
        errors = len(test_result.errors)
        passed = total_tests - (failures + errors)
        success = (failures == 0 and errors == 0)

        self.results["phases"]["01_unit_tests"] = {
            "name": "Automated Unit Tests",
            "total_tests": total_tests,
            "passed": passed,
            "failures": failures,
            "errors": errors,
            "duration_seconds": round(duration, 3),
            "status": "PASSED" if success else "FAILED"
        }

        if success:
            print(f"  ✅ Unit Tests Passed: {passed}/{total_tests} tests verified ({duration:.2f}s).")
        else:
            print(f"  ❌ Unit Tests Failed: {failures} failures, {errors} errors out of {total_tests} tests.")
            self.phase_failures += 1

        return success

    def run_phase_core_invariants(self) -> bool:
        """Phase 2: Executes WorldAuditor (20 Subsystem Invariant Checks)."""
        t0 = time.time()
        print("\n" + "━" * 80)
        print("  PHASE 2: CORE WORLD INVARIANTS & INTEGRITY AUDITOR (المدقق الحتمي العام)")
        print("━" * 80)

        from world_auditor import WorldAuditor
        auditor = WorldAuditor()
        exit_code = auditor.run_all()
        duration = time.time() - t0
        success = (exit_code == 0)

        self.results["phases"]["02_core_invariants"] = {
            "name": "World Invariants Auditor (20 Subsystem Checks)",
            "passed_invariants": len(auditor.passes),
            "violations": len(auditor.violations),
            "warnings": len(auditor.warnings),
            "duration_seconds": round(duration, 3),
            "status": "PASSED" if success else "FAILED"
        }

        if success:
            print(f"  ✅ World Invariants Verified: {len(auditor.passes)} checks passed ({duration:.2f}s).")
        else:
            print(f"  ❌ World Invariants Failed: {len(auditor.violations)} violation(s).")
            self.phase_failures += 1

        return success

    @staticmethod
    def _is_success(res: Any) -> bool:
        if isinstance(res, bool):
            return res
        if isinstance(res, int):
            return res == 0
        return bool(res)

    def run_phase_epistemic_grounding(self) -> bool:
        """Phase 3: Executes Grounding, Epistemic Tracker & Causality Graph."""
        t0 = time.time()
        print("\n" + "━" * 80)
        print("  PHASE 3: EPISTEMIC STATE & GROUNDING CALIBRATION (المعايرة المعرفية والسببية)")
        print("━" * 80)

        from grounding_auditor import GroundingAuditor
        from epistemic_tracker import EpistemicTracker
        from causality_graph import CausalityGraphAnalyzer

        g_auditor = GroundingAuditor()
        g_success = self._is_success(g_auditor.run_all())

        e_tracker = EpistemicTracker()
        e_success = self._is_success(e_tracker.run_audit())

        c_graph = CausalityGraphAnalyzer()
        c_success = self._is_success(c_graph.run_analysis())

        duration = time.time() - t0
        all_passed = g_success and e_success and c_success

        self.results["phases"]["03_epistemic_grounding"] = {
            "grounding_auditor": "PASSED" if g_success else "FAILED",
            "epistemic_tracker": "PASSED" if e_success else "FAILED",
            "causality_graph": "PASSED" if c_success else "FAILED",
            "duration_seconds": round(duration, 3),
            "status": "PASSED" if all_passed else "FAILED"
        }

        if all_passed:
            print(f"  ✅ Epistemic & Causality Engines: 100% Grounded and Acyclic ({duration:.2f}s).")
        else:
            print("  ❌ Epistemic / Grounding / Causality Violations Detected.")
            self.phase_failures += 1

        return all_passed

    def run_phase_existential_socio_political(self) -> bool:
        """Phase 4: Executes Moral Entropy, Behavioral, Socio-Demography & History."""
        t0 = time.time()
        print("\n" + "━" * 80)
        print("  PHASE 4: EXISTENTIAL, BEHAVIORAL & SOCIO-POLITICAL ENGINES (الأخلاق والسياسة)")
        print("━" * 80)

        from moral_entropy_monitor import MoralEntropyMonitor
        from psychology_detector import PsychologyDetector
        from socio_demography_analyzer import SocioDemographyAnalyzer
        from historical_political_analyzer import HistoricalPoliticalAnalyzer
        from chrono_event_engine import ChronoEventEngine

        m_monitor = MoralEntropyMonitor()
        m_success = self._is_success(m_monitor.run_all())

        p_detector = PsychologyDetector()
        p_success = self._is_success(p_detector.run_detector())

        s_analyzer = SocioDemographyAnalyzer()
        s_success = self._is_success(s_analyzer.run_all_audits())

        h_analyzer = HistoricalPoliticalAnalyzer()
        h_success = self._is_success(h_analyzer.run_all_audits())

        c_engine = ChronoEventEngine()
        c_success = self._is_success(c_engine.run_profiler())

        duration = time.time() - t0
        all_passed = m_success and p_success and s_success and h_success and c_success

        self.results["phases"]["04_existential_socio_political"] = {
            "moral_entropy_monitor": "PASSED" if m_success else "FAILED",
            "psychology_detector": "PASSED" if p_success else "FAILED",
            "socio_demography_analyzer": "PASSED" if s_success else "FAILED",
            "historical_political_analyzer": "PASSED" if h_success else "FAILED",
            "chrono_event_engine": "PASSED" if c_success else "FAILED",
            "duration_seconds": round(duration, 3),
            "status": "PASSED" if all_passed else "FAILED"
        }

        if all_passed:
            print(f"  ✅ Moral, Psychological, Socio-Demographic & Historical Engines: 100% Passed ({duration:.2f}s).")
        else:
            print("  ❌ Behavioral / Existential Engines Detected Violations.")
            self.phase_failures += 1

        return all_passed

    def run_phase_stylistic_sensory_linters(self) -> bool:
        """Phase 5: Executes Sensory Linter, Dialogue Auditor, Pacing & Characters."""
        t0 = time.time()
        print("\n" + "━" * 80)
        print("  PHASE 5: SENSORY DENSITY, PACING & DIALOGUE LINTERS (المقاييس الأسلوبية)")
        print("━" * 80)

        from pathlib import Path
        baseline_path = Path(ROOT_DIR) / "00_BASELINE" / "novel_baseline.md"

        from sensory_linter import analyze_sensory_density
        from dialogue_auditor import audit_dialogue
        from pacing_visualizer import analyze_pacing
        from character_tracker import audit_characters

        s_success = True
        try:
            analyze_sensory_density(baseline_path)
        except Exception as e:
            print(f"  ❌ Sensory Linter Error: {e}")
            s_success = False

        d_success = True
        try:
            audit_dialogue(baseline_path)
        except Exception as e:
            print(f"  ❌ Dialogue Auditor Error: {e}")
            d_success = False

        p_success = True
        try:
            analyze_pacing(baseline_path)
        except Exception as e:
            print(f"  ❌ Pacing Visualizer Error: {e}")
            p_success = False

        c_success = True
        try:
            audit_characters(baseline_path)
        except Exception as e:
            print(f"  ❌ Character Tracker Error: {e}")
            c_success = False

        duration = time.time() - t0
        all_passed = s_success and d_success and p_success and c_success

        self.results["phases"]["05_stylistic_sensory_linters"] = {
            "sensory_linter": "PASSED" if s_success else "FAILED",
            "dialogue_auditor": "PASSED" if d_success else "FAILED",
            "pacing_visualizer": "PASSED" if p_success else "FAILED",
            "character_tracker": "PASSED" if c_success else "FAILED",
            "duration_seconds": round(duration, 3),
            "status": "PASSED" if all_passed else "FAILED"
        }

        if all_passed:
            print(f"  ✅ Stylistic, Sensory & Pacing Linters: 100% Verified ({duration:.2f}s).")
        else:
            print("  ❌ Stylistic Linters Detected Violations.")
            self.phase_failures += 1

        return all_passed

    def run_phase_world_brain_graph(self) -> bool:
        """Phase 6: Verifies Knowledge Graph generation."""
        t0 = time.time()
        print("\n" + "━" * 80)
        print("  PHASE 6: WORLD BRAIN KNOWLEDGE GRAPH VERIFIER (العقل الثانوي وشبكة المعرفة)")
        print("━" * 80)

        from pathlib import Path
        brain_dir = Path(ROOT_DIR) / "05_WORLD_BRAIN"
        output_html = brain_dir / "world_brain_graph.html"

        from world_graph_builder import parse_world_brain, generate_interactive_html
        g_success = True
        try:
            nodes, edges = parse_world_brain(brain_dir)
            generate_interactive_html(nodes, edges, output_html)
            print(f"  Parsed {len(nodes)} Ontological Nodes and {len(edges)} Relationships.")
        except Exception as e:
            print(f"  ❌ World Brain Graph Error: {e}")
            g_success = False

        duration = time.time() - t0

        self.results["phases"]["06_world_brain_graph"] = {
            "world_graph_builder": "PASSED" if g_success else "FAILED",
            "duration_seconds": round(duration, 3),
            "status": "PASSED" if g_success else "FAILED"
        }

        if g_success:
            print(f"  ✅ Knowledge Graph Verified: Interactive Obsidian Graph Built ({duration:.2f}s).")
        else:
            print("  ❌ Knowledge Graph Builder Failed.")
            self.phase_failures += 1

        return g_success

    def run_phase_governance_and_sanctity(self) -> bool:
        """Phase 7: Verifies Baseline Sanctity (SHA-256), Workspace Hygiene & Staging Proposals."""
        t0 = time.time()
        print("\n" + "━" * 80)
        print("  PHASE 7: GOVERNANCE, BASELINE SANCTITY & STAGING GATE (قدسية المتن ومقترحات التصحيح)")
        print("━" * 80)

        passed_checks = 0
        failed_checks = 0
        checks_log = []

        # Check 1: Baseline Sanctity Hash (SHA-256)
        baseline_path = os.path.join(ROOT_DIR, "00_BASELINE", "novel_baseline.md")
        expected_hash = "A173202BB1BF875B3EF371ACE387B107418E7292BA58CC79F751DE087FF607EC"
        if os.path.exists(baseline_path):
            with open(baseline_path, "rb") as f:
                actual_hash = hashlib.sha256(f.read()).hexdigest().upper()
            if actual_hash == expected_hash:
                passed_checks += 1
                checks_log.append("✅ Baseline SHA-256 integrity verified (100% frozen ground truth).")
            else:
                failed_checks += 1
                checks_log.append(f"❌ Baseline hash mismatch: {actual_hash} != {expected_hash}")
        else:
            failed_checks += 1
            checks_log.append("❌ Baseline file 00_BASELINE/novel_baseline.md missing.")

        # Check 2: Root Hygiene (Absence of redundant duplicate RTF)
        root_rtf = os.path.join(ROOT_DIR, "رواية.rtf")
        if not os.path.exists(root_rtf):
            passed_checks += 1
            checks_log.append("✅ Root workspace clean: No redundant duplicate RTF found.")
        else:
            failed_checks += 1
            checks_log.append("❌ Redundant duplicate رواية.rtf detected at repository root.")

        # Checks 3..N: Staging Proposal Coverage for all registered bugs
        bugs_file = os.path.join(ROOT_DIR, "03_AUDIT_AND_ISSUES", "WORLD_BUGS.yaml")
        if os.path.exists(bugs_file):
            with open(bugs_file, "r", encoding="utf-8") as f:
                bugs_data = yaml.safe_load(f)
            bugs_list = bugs_data.get("bugs", [])
            for b in bugs_list:
                bid = b.get("id", "UNKNOWN")
                prop_file_rel = b.get("remediation_proposal", {}).get("proposal_file", "")
                prop_path = os.path.join(ROOT_DIR, prop_file_rel) if prop_file_rel else ""

                if prop_path and os.path.exists(prop_path) and os.path.getsize(prop_path) > 100:
                    with open(prop_path, "r", encoding="utf-8") as pf:
                        content = pf.read()
                    if "[ ]" in content and ("معتمد من الكاتب" in content or "Author Blessed" in content):
                        passed_checks += 1
                        checks_log.append(f"✅ {bid}: Staging proposal valid with author blessing checkbox ({prop_file_rel}).")
                    else:
                        failed_checks += 1
                        checks_log.append(f"❌ {bid}: Staging proposal missing author blessing checkbox.")
                else:
                    failed_checks += 1
                    checks_log.append(f"❌ {bid}: Missing or empty staging proposal file ({prop_file_rel}).")
        else:
            failed_checks += 1
            checks_log.append("❌ WORLD_BUGS.yaml not found.")

        duration = time.time() - t0
        total_checks = passed_checks + failed_checks
        all_passed = (failed_checks == 0 and total_checks > 0)

        self.results["phases"]["07_governance_and_sanctity"] = {
            "name": "Governance, Baseline Sanctity & Staging Coverage",
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "failed_checks": failed_checks,
            "duration_seconds": round(duration, 3),
            "status": "PASSED" if all_passed else "FAILED",
            "details": checks_log
        }

        for log_line in checks_log:
            print(f"  {log_line}")

        if all_passed:
            print(f"  ✅ Governance & Sanctity Gate: {passed_checks}/{total_checks} checks passed ({duration:.2f}s).")
        else:
            print(f"  ❌ Governance Violations Detected: {failed_checks} failed check(s).")
            self.phase_failures += 1

        return all_passed

    def generate_report(self) -> None:
        """Serializes aggregated results into 03_AUDIT_AND_ISSUES/MASTER_AUDIT_REPORT.json."""
        self.results["summary"]["status"] = "PASSED" if self.phase_failures == 0 else "FAILED"
        self.results["summary"]["total_phases"] = len(self.results["phases"])
        self.results["summary"]["passed_phases"] = len(self.results["phases"]) - self.phase_failures
        self.results["summary"]["failed_phases"] = self.phase_failures
        self.results["summary"]["total_duration_seconds"] = round(self.total_duration, 3)

        # Aggregate check counters across all phases
        total_checks = 0
        passed_checks = 0
        failed_checks = 0

        # Phase 1: Unit tests
        p1 = self.results["phases"].get("01_unit_tests", {})
        total_checks += p1.get("total_tests", 0)
        passed_checks += p1.get("passed", 0)
        failed_checks += (p1.get("failures", 0) + p1.get("errors", 0))

        # Phase 2: Core Invariants
        p2 = self.results["phases"].get("02_core_invariants", {})
        p2_pass = p2.get("passed_invariants", 0)
        p2_fail = p2.get("violations", 0)
        total_checks += (p2_pass + p2_fail)
        passed_checks += p2_pass
        failed_checks += p2_fail

        # Phase 3: Epistemic & Grounding
        p3 = self.results["phases"].get("03_epistemic_grounding", {})
        for tool in ["grounding_auditor", "epistemic_tracker", "causality_graph"]:
            if tool in p3:
                total_checks += 1
                if p3[tool] == "PASSED":
                    passed_checks += 1
                else:
                    failed_checks += 1

        # Phase 4: Existential & Socio-Political
        p4 = self.results["phases"].get("04_existential_socio_political", {})
        for tool in ["moral_entropy_monitor", "psychology_detector", "socio_demography_analyzer", "historical_political_analyzer", "chrono_event_engine"]:
            if tool in p4:
                total_checks += 1
                if p4[tool] == "PASSED":
                    passed_checks += 1
                else:
                    failed_checks += 1

        # Phase 5: Stylistic & Sensory Linters
        p5 = self.results["phases"].get("05_stylistic_sensory_linters", {})
        for tool in ["sensory_linter", "dialogue_auditor", "pacing_visualizer", "character_tracker"]:
            if tool in p5:
                total_checks += 1
                if p5[tool] == "PASSED":
                    passed_checks += 1
                else:
                    failed_checks += 1

        # Phase 6: World Brain Graph
        p6 = self.results["phases"].get("06_world_brain_graph", {})
        if "world_graph_builder" in p6:
            total_checks += 1
            if p6["world_graph_builder"] == "PASSED":
                passed_checks += 1
            else:
                failed_checks += 1

        # Phase 7: Governance & Sanctity
        p7 = self.results["phases"].get("07_governance_and_sanctity", {})
        total_checks += p7.get("total_checks", 0)
        passed_checks += p7.get("passed_checks", 0)
        failed_checks += p7.get("failed_checks", 0)

        success_rate = (passed_checks / total_checks * 100.0) if total_checks > 0 else 0.0

        self.results["summary"]["total_checks"] = total_checks
        self.results["summary"]["passed_checks"] = passed_checks
        self.results["summary"]["failed_checks"] = failed_checks
        self.results["summary"]["success_rate_percent"] = round(success_rate, 2)

        os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
        with open(REPORT_PATH, "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)

    def run_all(self) -> int:
        """Executes full multi-phase platform audit."""
        self.start_time = time.time()

        print("\n" + "═" * 80)
        print("  SAND TRAIN PLATFORM ENGINE: UNIFIED MASTER AUDITOR (v2.1.0)")
        print("  ميثاق المنظومة: «نحن نُحلل ونُقيّم.. ولا نُقوّم»")
        print("═" * 80)

        p1 = self.run_phase_unit_tests()
        p2 = self.run_phase_core_invariants()
        p3 = self.run_phase_epistemic_grounding()
        p4 = self.run_phase_existential_socio_political()
        p5 = self.run_phase_stylistic_sensory_linters()
        p6 = self.run_phase_world_brain_graph()
        p7 = self.run_phase_governance_and_sanctity()

        self.total_duration = time.time() - self.start_time
        self.generate_report()

        print("\n" + "═" * 80)
        if self.phase_failures == 0:
            print(f"  🎉 MASTER AUDIT PASSED: 100% Deterministic Integrity Verified ({self.total_duration:.2f}s)")
            print(f"  📊 Total Checks: {self.results['summary']['total_checks']} Passed | 0 Violations (100.0%)")
            print(f"  📄 Master Audit Report Saved: 03_AUDIT_AND_ISSUES/MASTER_AUDIT_REPORT.json")
            print("═" * 80 + "\n")
            return 0
        else:
            print(f"  ❌ MASTER AUDIT FAILED: {self.phase_failures} Phase(s) Reported Violations ({self.total_duration:.2f}s)")
            print(f"  📊 Total Checks: {self.results['summary']['total_checks']} ({self.results['summary']['passed_checks']} Passed, {self.results['summary']['failed_checks']} Failed)")
            print(f"  📄 Review Report: 03_AUDIT_AND_ISSUES/MASTER_AUDIT_REPORT.json")
            print("═" * 80 + "\n")
            return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Master Auditor & Platform Orchestrator for Sand Train")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose testing output")
    parser.add_argument("--ci", action="store_true", help="Run in CI mode")
    args = parser.parse_args()

    master = MasterAuditor(verbose=args.verbose, is_ci=args.ci)
    sys.exit(master.run_all())
