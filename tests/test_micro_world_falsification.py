#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
TEST SUITE: Micro-World Falsification & Multi-World Universality Test
Project: «قطار الرمل» (Sand Train) / Narrative Engine Core
Phase: Phase 4 of MILESTONE-NARRATIVE-OS-v1.0
==============================================================================

Role & Purpose:
  Validates that world_engine operates as a truly universal Narrative World OS
  capable of compiling, validating, and auditing an entirely separate narrative world
  (Orbital Station Aurora-9: Airlock Failure) with ZERO custom code, and proving
  falsification rigor through negative mutation tests.
==============================================================================
"""

import copy
from pathlib import Path
import pytest
import yaml

from world_engine.validator import WorldSchemaValidator
from world_engine.dag import CausalityDAGValidator, CausalCycleError
from world_engine.evaluator import DeclarativeInvariantEvaluator
from world_engine.cli import audit_world

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SAND_TRAIN_MANIFEST = PROJECT_ROOT / "05_WORLD_BRAIN" / "world_manifest.yaml"
ORBITAL_MANIFEST = PROJECT_ROOT / "instances" / "orbital_station" / "world_manifest.yaml"


@pytest.fixture
def orbital_station_data():
    """Loads all Orbital Station YAML manifests into memory."""
    with open(ORBITAL_MANIFEST, "r", encoding="utf-8") as f:
        manifest = yaml.safe_load(f)
    base_dir = ORBITAL_MANIFEST.parent
    with open(base_dir / manifest["rules_manifest_ref"], "r", encoding="utf-8") as f:
        rules = yaml.safe_load(f)
    with open(base_dir / manifest["entities_catalog_ref"], "r", encoding="utf-8") as f:
        entities = yaml.safe_load(f)
    with open(base_dir / manifest["causality_graph_ref"], "r", encoding="utf-8") as f:
        causality = yaml.safe_load(f)
    with open(base_dir / "world_state.yaml", "r", encoding="utf-8") as f:
        state = yaml.safe_load(f)

    return {
        "manifest": manifest,
        "rules": rules,
        "entities": entities,
        "causality": causality,
        "state": state,
    }


def test_orbital_station_baseline_audit_clean():
    """Test 1: Clean baseline of Orbital Station must pass audit with zero violations."""
    report = audit_world(ORBITAL_MANIFEST)
    assert report["is_valid"] is True
    assert len(report["schema_errors"]) == 0
    assert len(report["cross_ref_errors"]) == 0
    assert report["dag_valid"] is True
    assert report["events_count"] == 5
    assert len(report["invariant_violations"]) == 0


def test_falsification_spacesuit_double_occupancy(orbital_station_data):
    """Test 2: Falsification - Two persons attempting to occupy single EVA suit triggers FATAL violation."""
    rules = orbital_station_data["rules"]
    mutated_state = copy.deepcopy(orbital_station_data["state"])

    # Mutate state: 2 persons stuffed into single spacesuit
    mutated_state["suit_occupants_count"] = 2
    mutated_state["suit_eva_01"]["occupant_count"] = 2

    evaluator = DeclarativeInvariantEvaluator()
    evaluator.load_rules(rules["rules"])
    results = evaluator.evaluate_all(mutated_state)

    # Invariant suit_eva_01.occupant_count <= 1 must fail
    violations = [v for v in results.violations if v.rule_id == "LAW-BIO-01"]
    assert len(violations) == 1
    assert violations[0].severity == "FATAL"
    assert "suit_eva_01.occupant_count" in violations[0].target


def test_falsification_hypoxia_decompression_breach(orbital_station_data):
    """Test 3: Falsification - Unsealed occupant remaining conscious at 38 kPa triggers FATAL violation."""
    rules = orbital_station_data["rules"]
    mutated_state = copy.deepcopy(orbital_station_data["state"])

    # Mutate state: decompression below 50 kPa, but character miraculously awake
    mutated_state["airlock_pressure_kpa"] = 38.0
    mutated_state["unsealed_occupant"]["unconscious"] = False

    evaluator = DeclarativeInvariantEvaluator()
    evaluator.load_rules(rules["rules"])
    results = evaluator.evaluate_all(mutated_state)

    violations = [v for v in results.violations if v.rule_id == "LAW-PNEUM-01"]
    assert len(violations) == 1
    assert violations[0].severity == "FATAL"
    assert "unsealed_occupant.unconscious" in violations[0].target


def test_falsification_zero_g_kinetics_drift_violation(orbital_station_data):
    """Test 4: Falsification - Untethered push without resulting drift violates momentum conservation."""
    rules = orbital_station_data["rules"]
    mutated_state = copy.deepcopy(orbital_station_data["state"])

    # Mutate state: untethered push but 0 drift velocity
    mutated_state["tether_engaged"] = False
    mutated_state["drift_velocity_mps"] = 0.0

    evaluator = DeclarativeInvariantEvaluator()
    evaluator.load_rules(rules["rules"])
    results = evaluator.evaluate_all(mutated_state)

    violations = [v for v in results.violations if v.rule_id == "LAW-KIN-01"]
    assert len(violations) == 1
    assert violations[0].severity == "VIOLATION"


def test_falsification_differential_pressure_lock(orbital_station_data):
    """Test 5: Falsification - Hatch unlocked while chamber pressure is high triggers FATAL violation."""
    rules = orbital_station_data["rules"]
    mutated_state = copy.deepcopy(orbital_station_data["state"])

    # Mutate state: high pressure differential but outer hatch unlocked
    mutated_state["chamber_pressure_kpa"] = 90.0
    mutated_state["outer_hatch"]["mechanical_lock"] = False

    evaluator = DeclarativeInvariantEvaluator()
    evaluator.load_rules(rules["rules"])
    results = evaluator.evaluate_all(mutated_state)

    violations = [v for v in results.violations if v.rule_id == "LAW-ELECTRO-01"]
    assert len(violations) == 1
    assert violations[0].severity == "FATAL"


def test_falsification_causal_cycle_detected(orbital_station_data):
    """Test 6: Falsification - Inserting a causal loop into orbital events triggers CausalCycleError."""
    causality = copy.deepcopy(orbital_station_data["causality"])

    # Inject circular dependency: EVT-ORB-005 causes EVT-ORB-002
    for evt in causality["events"]:
        if evt["id"] == "EVT-ORB-005":
            evt["causes"] = ["EVT-ORB-002"]

    validator = CausalityDAGValidator()
    with pytest.raises(CausalCycleError) as exc_info:
        validator.verify_acyclicity(causality["events"])

    assert "Causal cycle detected" in str(exc_info.value)


def test_falsification_orphan_spatial_affordance_zone(orbital_station_data):
    """Test 7: Falsification - Assigning character to unmapped zone triggers cross-reference validation error."""
    manifest = orbital_station_data["manifest"]
    entities = copy.deepcopy(orbital_station_data["entities"])

    # Move astronaut to an unmapped fictitious zone
    entities["characters"][0]["location_id"] = "zone_phantom_black_hole"

    validator = WorldSchemaValidator()
    errors = validator.validate_cross_references(manifest, entities)

    assert len(errors) > 0
    assert any("zone_phantom_black_hole" in err for err in errors)


def test_multi_world_universality_concurrent():
    """Test 8: Concurrent Multi-World OS Validation.
    Proves that world_engine audits Sand Train AND Orbital Station in the same session
    without state pollution or cross-contamination.
    """
    report_sand = audit_world(SAND_TRAIN_MANIFEST)
    report_orbital = audit_world(ORBITAL_MANIFEST)

    # Both worlds must be 100% valid
    assert report_sand["is_valid"] is True
    assert report_orbital["is_valid"] is True

    # Sand Train specific assertions
    assert report_sand["events_count"] == 16
    assert len(report_sand["schema_errors"]) == 0

    # Orbital Station specific assertions
    assert report_orbital["events_count"] == 5
    assert len(report_orbital["schema_errors"]) == 0
