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
import io
import unittest
import unittest.mock
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
    validate_law_compliance,
    SimulationEvent
)
from registry import EntityRegistry
from ticker import EventSourcedTicker
from replayer import EventReplayer
from world_auditor import WorldAuditor
from moral_entropy_monitor import MoralEntropyMonitor
from master_auditor import MasterAuditor
from causality_graph import CausalityGraphAnalyzer
from epistemic_tracker import EpistemicTracker
from chrono_event_engine import ChronoEventEngine, NARRATIVE_ACTIONS_TO_EVALUATE


class TestNegativeMutations(unittest.TestCase):
    """Falsifiability & Violation Detection Suite (True E2E Mutation Tests)."""

    def test_mutation_01_spatial_collision_detected(self):
        """Mutation E2E: Place two characters at identical (X, Y) coordinates and assert WorldAuditor catches it."""
        auditor = WorldAuditor()
        auditor.load_files()
        
        # Inject artificial collision: assign Bassam the exact coordinates of Khalid
        self.assertIn("خالد", auditor.world_state["characters"])
        self.assertIn("بسام", auditor.world_state["characters"])
        
        khalid_coords = auditor.world_state["characters"]["خالد"]["coordinates"]
        auditor.world_state["characters"]["بسام"]["coordinates"] = dict(khalid_coords)
        
        # Run the real WorldAuditor spatial collision pipeline
        auditor.check_spatial_collision()
        
        # Assert WorldAuditor actively catches and records the violation
        self.assertTrue(
            any("[Spatial Collision]" in v and "بسام" in v and "خالد" in v for v in auditor.violations),
            f"WorldAuditor must detect spatial collision in violations: {auditor.violations}"
        )

    def test_mutation_02_zone_boundary_escape_detected(self):
        """Mutation E2E: Teleport character outside designated car physical boundaries and assert WorldAuditor catches it."""
        auditor = WorldAuditor()
        auditor.load_files()
        
        # Khalid is assigned to car_01_guard (y: 17.0m -> 29.0m). Mutate Y coordinate to 45.0m (Car 3 zone)
        auditor.world_state["characters"]["خالد"]["coordinates"]["y_m"] = 45.0
        
        # Run the real WorldAuditor zone confinement pipeline
        auditor.check_zone_confinement()
        
        # Assert WorldAuditor actively catches and records the boundary escape
        self.assertTrue(
            any("[Boundary Error]" in v and "خالد" in v and "outside car bounds" in v for v in auditor.violations),
            f"WorldAuditor must detect boundary escape in violations: {auditor.violations}"
        )

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
        """Mutation E2E: Cite a non-existent law in WORLD_BUGS and assert WorldAuditor pipeline flags it."""
        auditor = WorldAuditor()
        auditor.load_files()
        
        # Inject fictitious law into the auditor's active bugs data
        fictitious_citation = "LAW-FICTION-99"
        auditor.world_bugs["bugs"].append({
            "id": "WORLD-BUG-MUTATION-TEST",
            "title": "Fictitious law test bug",
            "law_broken": f"Violation of {fictitious_citation}"
        })
        
        # Run the real WorldAuditor reference integrity check
        auditor.check_laws_reference_integrity()
        
        # Assert WorldAuditor actively records the unresolved citation
        self.assertTrue(
            any("[Laws Reference Error]" in v and fictitious_citation in v for v in auditor.violations),
            f"WorldAuditor must flag unresolved fictitious law in violations: {auditor.violations}"
        )

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
        """Mutation E2E: Drop a character from the 14 occupants matrix and assert MoralEntropyMonitor detects it."""
        monitor = MoralEntropyMonitor()
        monitor.load_data()
        
        # Mutate by removing Mahdi from moral typology quadrants (14 -> 13)
        monitor.MORAL_QUADRANTS = {
            k: {
                "name_ar": v["name_ar"],
                "description": v["description"],
                "characters": [c for c in v["characters"] if c != "مهدي"],
                "governing_law": v["governing_law"]
            }
            for k, v in monitor.MORAL_QUADRANTS.items()
        }
        
        # Run the real MoralEntropyMonitor typology and census audit
        result = monitor.audit_moral_typology_quadrants()
        
        # Assert MoralEntropyMonitor actively catches the headcount deviation
        self.assertFalse(result["passed"], "Moral audit must fail when headcount is 13!")
        self.assertEqual(result["total_census"], 13)
        self.assertTrue(
            any("[Moral Census]" in v and "13" in v and "expected exactly 14" in v for v in monitor.violations),
            f"MoralEntropyMonitor must flag census violation: {monitor.violations}"
        )

    def test_mutation_09_baseline_sanctity_tamper_caught(self):
        """Mutation E2E: Tamper with baseline manuscript and assert MasterAuditor governance gate rejects it."""
        baseline_path = os.path.join(ROOT_DIR, "00_BASELINE", "novel_baseline.md")
        with open(baseline_path, "rb") as f:
            valid_bytes = f.read().replace(b"\r\n", b"\n")
            
        canonical_hash = "75AC9D6A1D2B71B677D3119B2E6D6A922AFD4A1B3DC046B5D2841B3C198316B0"
        self.assertEqual(hashlib.sha256(valid_bytes).hexdigest().upper(), canonical_hash)

        # Mathematical inequality assertion
        tampered_bytes = valid_bytes + b" "
        self.assertNotEqual(hashlib.sha256(tampered_bytes).hexdigest().upper(), canonical_hash)

        # End-to-End Governance Gate Assertion in MasterAuditor
        auditor = MasterAuditor()
        orig_open = open

        def mocked_open(path, *args, **kwargs):
            if "novel_baseline.md" in str(path):
                return io.BytesIO(b"Tampered Baseline Content by Mutation Test")
            return orig_open(path, *args, **kwargs)

        with unittest.mock.patch("builtins.open", side_effect=mocked_open):
            gate_passed = auditor.run_phase_governance_and_sanctity()
            self.assertFalse(gate_passed, "MasterAuditor governance gate must strictly reject tampered baseline content!")

        phase_summary = auditor.results["phases"]["07_governance_and_sanctity"]
        self.assertEqual(phase_summary["status"], "FAILED")
        self.assertGreater(phase_summary["failed_checks"], 0)
        self.assertTrue(any("Baseline hash mismatch" in line for line in phase_summary["details"]))

    def test_mutation_10_causal_dag_cycle_detected(self):
        """Mutation E2E: Inject circular causal loop into narrative DAG and assert CausalityGraphAnalyzer catches it."""
        analyzer = CausalityGraphAnalyzer()
        analyzer.build_graph()
        self.assertTrue(analyzer.verify_dag_acyclicity(), "Baseline DAG must be strictly acyclic")

        # Inject circular causal cycle: Engine restart (EVT-016) causes Sabotage (EVT-001)
        analyzer.adj["EVT-016-ENGINE_RESTART"].append("EVT-001-SABOTAGE")
        analyzer.in_degree["EVT-001-SABOTAGE"] += 1
        analyzer.violations.clear()

        # Run real CausalityGraphAnalyzer acyclicity check
        is_dag_mutated = analyzer.verify_dag_acyclicity()
        self.assertFalse(is_dag_mutated, "Causality graph must reject circular causality loops!")
        self.assertTrue(
            any("[Causal Loop Detected]" in v for v in analyzer.violations),
            f"Analyzer must detect causal loop violation: {analyzer.violations}"
        )

    def test_mutation_11_illegal_omniscience_leak_detected(self):
        """Mutation E2E: Grant Khalid in Car 1 illegal knowledge of Mahdi's jump plan and assert EpistemicTracker catches leak."""
        tracker = EpistemicTracker()
        tracker.load_world_state()

        # Leak localized secret of Mahdi (Car 2) to Khalid (Car 1) without physical transmission vector
        secret_fact = "اللحظة_القادمة_هي_لحظة_القفز"
        tracker.world_state["characters"]["خالد"]["epistemic_bubble"]["known_truths"].append(secret_fact)

        # Run real EpistemicTracker inter-car omniscience leak audit
        tracker.check_inter_car_omniscience_leaks()
        self.assertTrue(
            any("[Omniscience Leak]" in v and "خالد" in v and secret_fact in v for v in tracker.violations),
            f"EpistemicTracker must flag illegal omniscience leak: {tracker.violations}"
        )

    def test_mutation_12_epistemic_contradiction_detected(self):
        """Mutation E2E: Place identical fact in known_truths and blind_spots and assert EpistemicTracker flags contradiction."""
        tracker = EpistemicTracker()
        tracker.load_world_state()

        # Inject contradiction in Abu Ali's bubble: both knowing and being blind to broken diesel line
        contradictory_fact = "أنبوب_الديزل_منكسر"
        tracker.world_state["characters"]["أبو_علي"]["epistemic_bubble"]["blind_spots"].append(contradictory_fact)

        # Run real EpistemicTracker integrity audit
        tracker.check_epistemic_bubbles_integrity()
        self.assertTrue(
            any("[Epistemic Contradiction]" in v and "أبو_علي" in v for v in tracker.violations),
            f"EpistemicTracker must detect epistemic contradiction: {tracker.violations}"
        )

    def test_mutation_13_impossible_task_duration_and_dexterity_rejected(self):
        """Mutation E2E: Inject high dexterity task at peak frost without tools and assert ChronoEventEngine catches collapse."""
        engine = ChronoEventEngine()

        # Inject an impossible action: Bassam performing delicate surgery at minute 500 (03:00) requiring dexterity 0.90
        # (while physical dexterity collapsed to 0.08 due to sub-zero temperatures)
        original_actions = list(NARRATIVE_ACTIONS_TO_EVALUATE)
        NARRATIVE_ACTIONS_TO_EVALUATE.append({
            "id": "ACT-MUTATION-IMPOSSIBLE-SURGERY",
            "minute": 500,
            "time": "03:00:00",
            "character": "بسام",
            "action": "خياطة شريان دقيق بأصابع عارية متجمدة في الصقيع",
            "required_dexterity": 0.90,
            "requires_tools": False
        })
        try:
            engine.evaluate_narrative_actions()
            self.assertTrue(
                any("[Unphysical Action Error]" in v and "بسام" in v for v in engine.violations),
                f"ChronoEventEngine must catch unphysical action exceeding biomechanical limits: {engine.violations}"
            )
        finally:
            NARRATIVE_ACTIONS_TO_EVALUATE.clear()
            NARRATIVE_ACTIONS_TO_EVALUATE.extend(original_actions)

    def test_mutation_14_temporal_event_ordering_regression_caught(self):
        """Mutation E2E: Feed out-of-order temporal events (t2 < t1) and assert EventReplayer rejects timeline regression."""
        evt1 = SimulationEvent(
            event_id="EVT-TEST-01",
            minute=100,
            time_clock="20:40:00",
            event_type="ENVIRONMENT_UPDATE",
            payload={"ambient_temp_c": -1.0}
        )
        # Mutated: Event 2 has minute 50 (temporal inversion / time travel backward)
        evt2 = SimulationEvent(
            event_id="EVT-TEST-02",
            minute=50,
            time_clock="19:50:00",
            event_type="ENVIRONMENT_UPDATE",
            payload={"ambient_temp_c": 0.0}
        )

        # Run real EventReplayer.replay and assert strict temporal ordering enforcement
        with self.assertRaises(ValueError) as ctx:
            EventReplayer.replay([evt1, evt2])

        self.assertIn("Temporal Ordering Violation", str(ctx.exception))
        self.assertIn("EVT-TEST-02", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
