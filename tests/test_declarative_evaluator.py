#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
TEST DECLARATIVE INVARIANT EVALUATOR & AST SAFETY
Project: «قطار الرمل» (Sand Train) - Narrative Engineering Core
Milestone: MILESTONE-NARRATIVE-OS-v1.0 (Phase 2)
==============================================================================
"""

import copy
import pytest
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "02_TOOLS"))

from declarative_evaluator import (
    DeclarativeInvariantEvaluator,
    SafeExpressionEvaluator,
    SecurityViolationError,
    DEFAULT_RULES_PATH,
    DEFAULT_STATE_PATH
)


@pytest.fixture
def evaluator():
    return DeclarativeInvariantEvaluator()


# =============================================================================
# 1. AST SECURITY & ZERO-EVAL TESTS (توجيه JEV الصارم)
# =============================================================================

def test_safe_ast_arithmetic_success():
    """Valid arithmetic expressions compute accurately without eval()."""
    res1 = SafeExpressionEvaluator.evaluate_arithmetic_ast("10 + 25 * 2")
    assert res1 == 60

    res2 = SafeExpressionEvaluator.evaluate_arithmetic_ast("(100 - 40) / 3")
    assert res2 == 20.0

    res3 = SafeExpressionEvaluator.evaluate_arithmetic_ast("2 ** 8")
    assert res3 == 256

    res4 = SafeExpressionEvaluator.evaluate_arithmetic_ast("base_temp + delta", {"base_temp": -8.0, "delta": 2.5})
    assert res4 == -5.5


def test_safe_ast_blocks_function_calls():
    """SafeExpressionEvaluator must raise SecurityViolationError on function calls."""
    with pytest.raises(SecurityViolationError):
        SafeExpressionEvaluator.evaluate_arithmetic_ast("__import__('os').system('dir')")

    with pytest.raises(SecurityViolationError):
        SafeExpressionEvaluator.evaluate_arithmetic_ast("print('exploit')")


def test_safe_ast_blocks_attribute_access():
    """SafeExpressionEvaluator must raise SecurityViolationError on attribute access."""
    with pytest.raises(SecurityViolationError):
        SafeExpressionEvaluator.evaluate_arithmetic_ast("(1).__class__")


def test_safe_ast_blocks_string_literals_in_arithmetic():
    """Non-numeric constants in arithmetic trees must be rejected."""
    with pytest.raises(SecurityViolationError):
        SafeExpressionEvaluator.evaluate_arithmetic_ast("'hello' + 'world'")


def test_safe_comparison_operators():
    """Safe comparison evaluates correctly across supported operators."""
    assert SafeExpressionEvaluator.evaluate_comparison(5, "<=", 10) is True
    assert SafeExpressionEvaluator.evaluate_comparison(15, "<=", 10) is False
    assert SafeExpressionEvaluator.evaluate_comparison(-8.0, "==", -8.0) is True
    assert SafeExpressionEvaluator.evaluate_comparison("clamped_locked", "==", "clamped_locked") is True
    assert SafeExpressionEvaluator.evaluate_comparison("clamped_locked", "!=", "released") is True
    assert SafeExpressionEvaluator.evaluate_comparison("car_1", "in", ["car_0", "car_1", "car_2"]) is True


# =============================================================================
# 2. CANONICAL DECLARATIVE INVARIANTS (تقييم قطار الرمل الكانوني)
# =============================================================================

def test_baseline_declarative_rules_compliance(evaluator):
    """Current world state satisfies 100% of declarative rules with zero violations."""
    report = evaluator.evaluate_all()
    assert report.total_rules >= 16
    assert report.triggered_rules >= 10
    assert report.violations_count == 0
    assert report.overall_valid is True
    assert report.invariants_passed == report.invariants_checked


def test_diesel_gelling_rule_trigger_and_invariant(evaluator):
    """LAW-CHEM-01 is inactive at 0.0C (baseline t0) but triggers below -6.0C to enforce cold_restart_possible == False."""
    rule = next(r for r in evaluator.rules_data["rules"] if r["id"] == "LAW-CHEM-01")
    
    # 1. At baseline t0 (0.0C), temperature is not below -6.0C, so trigger is False
    assert evaluator.evaluate_rule_trigger(rule) is False

    # 2. When subzero temperature hits -8.0C during the night, trigger activates
    subzero_state = copy.deepcopy(evaluator.world_state)
    subzero_state["environment"]["ambient_temperature_c"] = -8.0
    assert evaluator.evaluate_rule_trigger(rule, subzero_state) is True

    # Invariant must hold under subzero state
    violations = evaluator.evaluate_rule_invariants(rule, subzero_state)
    assert len(violations) == 0



def test_pneumatic_brake_rule_trigger_and_invariant(evaluator):
    """LAW-PNEUM-01 triggers below 0.5 bar and enforces motion_locked == True."""
    rule = next(r for r in evaluator.rules_data["rules"] if r["id"] == "LAW-PNEUM-01")
    assert evaluator.evaluate_rule_trigger(rule) is True
    violations = evaluator.evaluate_rule_invariants(rule)
    assert len(violations) == 0


# =============================================================================
# 3. NEGATIVE MUTATION INJECTIONS (فحوصات الطفرات السلبية وكشف الخروقات)
# =============================================================================

def test_negative_mutation_unearned_diesel_restart(evaluator):
    """Injecting cold_restart_possible=True at -8C must trigger a FATAL invariant violation."""
    corrupted_state = copy.deepcopy(evaluator.world_state)
    corrupted_state["locomotive.engine.cold_restart_possible"] = True

    rule = next(r for r in evaluator.rules_data["rules"] if r["id"] == "LAW-CHEM-01")
    violations = evaluator.evaluate_rule_invariants(rule, corrupted_state)

    assert len(violations) == 1
    v = violations[0]
    assert v.rule_id == "LAW-CHEM-01"
    assert v.severity == "FATAL"
    assert v.actual_value is True
    assert v.expected_value is False


def test_negative_mutation_unearned_brake_release(evaluator):
    """Injecting motion_locked=False with zero pipe pressure must trigger a FATAL violation."""
    corrupted_state = copy.deepcopy(evaluator.world_state)
    corrupted_state["train.motion_locked"] = False

    rule = next(r for r in evaluator.rules_data["rules"] if r["id"] == "LAW-PNEUM-01")
    violations = evaluator.evaluate_rule_invariants(rule, corrupted_state)

    assert len(violations) == 1
    v = violations[0]
    assert v.rule_id == "LAW-PNEUM-01"
    assert v.severity == "FATAL"
    assert v.actual_value is False
    assert v.expected_value is True


def test_negative_mutation_defying_excretion_confinement(evaluator):
    """Injecting zero biological waste after 10.75h confinement must trigger FATAL violation."""
    corrupted_state = copy.deepcopy(evaluator.world_state)
    corrupted_state["car_1.biological_waste_volume_liters"] = 0.5

    rule = next(r for r in evaluator.rules_data["rules"] if r["id"] == "LAW-BIO-05")
    violations = evaluator.evaluate_rule_invariants(rule, corrupted_state)

    assert len(violations) == 1
    v = violations[0]
    assert v.rule_id == "LAW-BIO-05"
    assert v.severity == "FATAL"
    assert v.actual_value == 0.5
    assert v.expected_value == 3.0


def test_negative_mutation_hollywood_acrobatic_dexterity(evaluator):
    """Injecting fine motor dexterity of 0.95 after 45m subzero must trigger FATAL violation."""
    corrupted_state = copy.deepcopy(evaluator.world_state)
    corrupted_state["character.motor_dexterity_ratio"] = 0.95

    rule = next(r for r in evaluator.rules_data["rules"] if r["id"] == "LAW-BIO-01")
    violations = evaluator.evaluate_rule_invariants(rule, corrupted_state)

    assert len(violations) == 1
    v = violations[0]
    assert v.rule_id == "LAW-BIO-01"
    assert v.severity == "FATAL"
    assert v.actual_value == 0.95
    assert v.expected_value == 0.40
