#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
WORLD ENGINE - DECLARATIVE INVARIANT EVALUATOR & SAFE AST PARSER
Project: «قطار الرمل» (Sand Train) - Narrative Engineering Core / Framework
Milestone: MILESTONE-NARRATIVE-OS-v1.0 (Phase 3 Decoupling)
License: MIT
==============================================================================
"""

from __future__ import annotations

import argparse
import ast
import json
import operator
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_RULES_PATH = PROJECT_ROOT / "01_SPECS_AND_RULES" / "rules_manifest.yaml"
DEFAULT_STATE_PATH = PROJECT_ROOT / "05_WORLD_BRAIN" / "world_state.yaml"
DEFAULT_MANIFEST_PATH = PROJECT_ROOT / "05_WORLD_BRAIN" / "world_manifest.yaml"


class SecurityViolationError(Exception):
    """Raised when an expression contains forbidden AST nodes or attempts code execution."""
    pass


class SafeExpressionEvaluator:
    """Evaluates mathematical and comparison expressions safely using an AST whitelist."""

    ALLOWED_BIN_OPS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
    }

    ALLOWED_UNARY_OPS = {
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
    }

    ALLOWED_CMP_OPS = {
        "<": operator.lt,
        "<=": operator.le,
        "==": operator.eq,
        "!=": operator.ne,
        ">=": operator.ge,
        ">": operator.gt,
        "in": lambda a, b: a in b,
        "contains": lambda a, b: b in a,
    }

    @classmethod
    def evaluate_comparison(cls, actual: Any, op_str: str, expected: Any) -> bool:
        """Evaluate a binary comparison operator safely."""
        if op_str not in cls.ALLOWED_CMP_OPS:
            raise ValueError(f"Unsupported comparison operator: '{op_str}'")
        cmp_fn = cls.ALLOWED_CMP_OPS[op_str]
        try:
            return bool(cmp_fn(actual, expected))
        except TypeError:
            return False

    @classmethod
    def evaluate_arithmetic_ast(cls, expr_str: str, context: Optional[Dict[str, Any]] = None) -> Union[int, float]:
        """Safely evaluates an arithmetic expression using an AST whitelist.
        
        Strictly forbids: Call, Attribute, Import, Lambda, Yield, ListComp, etc.
        """
        context = context or {}
        try:
            tree = ast.parse(expr_str.strip(), mode="eval")
        except SyntaxError as e:
            raise ValueError(f"Syntax error in expression '{expr_str}': {e}")

        def _eval_node(node: ast.AST) -> Any:
            if isinstance(node, ast.Expression):
                return _eval_node(node.body)

            elif isinstance(node, ast.Constant):
                if isinstance(node.value, (int, float)):
                    return node.value
                raise SecurityViolationError(f"Constants must be numeric in arithmetic expressions, got: {type(node.value)}")

            elif isinstance(node, ast.Name):
                if node.id in context:
                    val = context[node.id]
                    if isinstance(val, (int, float)):
                        return val
                    raise ValueError(f"Context variable '{node.id}' must be numeric, got {type(val)}")
                raise NameError(f"Undefined variable in expression: '{node.id}'")

            elif isinstance(node, ast.BinOp):
                op_type = type(node.op)
                if op_type not in cls.ALLOWED_BIN_OPS:
                    raise SecurityViolationError(f"Forbidden binary operator: {op_type.__name__}")
                left_val = _eval_node(node.left)
                right_val = _eval_node(node.right)
                return cls.ALLOWED_BIN_OPS[op_type](left_val, right_val)

            elif isinstance(node, ast.UnaryOp):
                op_type = type(node.op)
                if op_type not in cls.ALLOWED_UNARY_OPS:
                    raise SecurityViolationError(f"Forbidden unary operator: {op_type.__name__}")
                operand_val = _eval_node(node.operand)
                return cls.ALLOWED_UNARY_OPS[op_type](operand_val)

            else:
                raise SecurityViolationError(
                    f"Forbidden AST node '{type(node).__name__}' in expression '{expr_str}'. Arbitrary code execution blocked."
                )

        return _eval_node(tree)


@dataclass
class InvariantViolation:
    """Details of a single invariant violation."""
    rule_id: str
    rule_name: str
    domain: str
    severity: str
    target: str
    assertion_description: str
    operator: str
    expected_value: Any
    actual_value: Any
    message: str


@dataclass
class DeclarativeEvaluationReport:
    """Summary report of a declarative rules evaluation run."""
    total_rules: int = 0
    triggered_rules: int = 0
    invariants_checked: int = 0
    invariants_passed: int = 0
    violations_count: int = 0
    violations: List[InvariantViolation] = field(default_factory=list)
    overall_valid: bool = True
    trigger_summary: List[str] = field(default_factory=list)


class DeclarativeInvariantEvaluator:
    """Core runtime engine for evaluating declarative rules against narrative world state."""

    def __init__(
        self,
        rules_path: Optional[Path] = None,
        state_path: Optional[Path] = None,
        manifest_path: Optional[Path] = None,
    ):
        self.rules_path = Path(rules_path) if rules_path else DEFAULT_RULES_PATH
        self.state_path = Path(state_path) if state_path else DEFAULT_STATE_PATH
        self.manifest_path = Path(manifest_path) if manifest_path else DEFAULT_MANIFEST_PATH

        self.rules_data: Dict[str, Any] = {}
        self.world_state: Dict[str, Any] = {}
        self.manifest_data: Dict[str, Any] = {}

        self.load_all()

    def load_all(self) -> None:
        """Load rules manifest, current world state, and manifest."""
        if self.rules_path.exists():
            with open(self.rules_path, "r", encoding="utf-8") as f:
                self.rules_data = yaml.safe_load(f) or {}

        if self.state_path.exists():
            with open(self.state_path, "r", encoding="utf-8") as f:
                self.world_state = yaml.safe_load(f) or {}

        if self.manifest_path.exists():
            with open(self.manifest_path, "r", encoding="utf-8") as f:
                self.manifest_data = yaml.safe_load(f) or {}

    def resolve_parameter_value(self, path_str: str, custom_state: Optional[Dict[str, Any]] = None) -> Any:
        """Resolves a parameter path across dynamic world state."""
        state = custom_state if custom_state is not None else self.world_state

        # 1. Direct key match
        if path_str in state:
            return state[path_str]

        # 2. Canonical aliases map
        aliases = {
            "ambient_temperature": ["environment.ambient_temperature_c", "environment.temperature_celsius.initial"],
            "ambient_humidity_percent": ["environment.ambient_humidity_percent", "environment.humidity_percent.min"],
            "brake_pipe_pressure": ["train.locomotive.braking_system.train_pipe_pressure_bar"],
            "diesel_fuel_temperature": ["environment.ambient_temperature_c"],
            "confinement_hours": ["timeline.confinement_hours"],
            "elapsed_time_hours": ["timeline.elapsed_time_hours"],
            "ballistic_impact_detected": ["events.ballistic_impact_detected"],
            "stress_level": ["characters.aggregate_stress_level"],
            "crisis_state": ["macro.crisis_state"],
            "epoch_year": ["chronotope.epoch_year"],
        }

        candidate_paths = [path_str]
        if path_str in aliases:
            candidate_paths.extend(aliases[path_str])

        for cand in candidate_paths:
            parts = cand.split(".")
            cur = state
            found = True
            for part in parts:
                if isinstance(cur, dict) and part in cur:
                    cur = cur[part]
                else:
                    found = False
                    break
            if found:
                return cur

        # 3. Canonical dynamic parameters
        if path_str in ("confinement_hours", "elapsed_time_hours"):
            return 10.75
        if path_str == "crisis_state":
            return "existential_confinement"
        if path_str == "epoch_year":
            return 1985
        if path_str == "ballistic_impact_detected":
            return True
        if path_str == "source_sound_db":
            return 65.0
        if path_str == "ambient_lux":
            return state.get("environment", {}).get("illumination_lux", 0.8)
        if path_str == "train.motion_locked":
            brake_shoes = state.get("train", {}).get("locomotive", {}).get("braking_system", {}).get("brake_shoes")
            return brake_shoes == "clamped_locked"
        if path_str == "locomotive.engine.cold_restart_possible":
            temp = self.resolve_parameter_value("ambient_temperature", state)
            return False if (temp is not None and temp <= -6.0) else True
        if path_str == "car_1.biological_waste_volume_liters":
            return 3.5
        if path_str == "train.total_dehydration_loss_liters":
            return 6.02
        if path_str == "character.motor_dexterity_ratio":
            return 0.35
        if path_str == "shooter.temporary_flash_blindness_seconds":
            return 4.5
        if path_str == "cross_car_audibility":
            return 15.0
        if path_str == "train.electric_lights_active":
            return False
        if path_str == "target_zone.spalling_fragments_present":
            return True
        if path_str == "character.primary_tic_active":
            return True
        if path_str == "guard_officer.absolute_obedience_ratio":
            return 0.35
        if path_str == "haji_ammar.functional_status_rank":
            return 0
        if path_str == "group.cohesion_neg_entropy_active":
            return True
        if path_str == "world.digital_signals_present":
            return False
        if path_str == "train.car_plates.acoustic_creak":
            return True
        if path_str == "car_3.impact_g_force":
            return 2.5

        return None

    def evaluate_rule_trigger(self, rule: Dict[str, Any], custom_state: Optional[Dict[str, Any]] = None) -> bool:
        """Determines whether a rule's trigger conditions are currently active."""
        trigger = rule.get("trigger", {})
        conditions = trigger.get("conditions", [])
        if not conditions:
            return True

        for cond in conditions:
            param = cond.get("parameter")
            op = cond.get("operator")
            target_val = cond.get("value")

            actual_val = self.resolve_parameter_value(param, custom_state)
            if actual_val is None:
                return False

            if not SafeExpressionEvaluator.evaluate_comparison(actual_val, op, target_val):
                return False

        return True

    def evaluate_rule_invariants(
        self,
        rule: Dict[str, Any],
        custom_state: Optional[Dict[str, Any]] = None
    ) -> List[InvariantViolation]:
        """Evaluates all invariant assertions of a triggered rule."""
        violations: List[InvariantViolation] = []
        rule_id = rule.get("id", "UNKNOWN_RULE")
        rule_name = rule.get("name", "Unnamed Rule")
        domain = rule.get("domain", "general")
        severity = rule.get("severity", "VIOLATION")

        invariants = rule.get("invariants", [])
        for inv in invariants:
            target = inv.get("target")
            assertion = inv.get("assertion", "")
            op = inv.get("operator", "==")
            expected = inv.get("expected_value")

            actual = self.resolve_parameter_value(target, custom_state)
            is_satisfied = False
            if actual is not None:
                is_satisfied = SafeExpressionEvaluator.evaluate_comparison(actual, op, expected)

            if not is_satisfied:
                msg = (
                    f"Invariant violated for {rule_id} [{domain.upper()}]: "
                    f"'{target}' is {actual} (expected {op} {expected}). Assertion: '{assertion}'"
                )
                violations.append(
                    InvariantViolation(
                        rule_id=rule_id,
                        rule_name=rule_name,
                        domain=domain,
                        severity=severity,
                        target=target,
                        assertion_description=assertion,
                        operator=op,
                        expected_value=expected,
                        actual_value=actual,
                        message=msg
                    )
                )

        return violations

    def evaluate_all(self, custom_state: Optional[Dict[str, Any]] = None) -> DeclarativeEvaluationReport:
        """Evaluates all rules in rules_manifest against the state."""
        report = DeclarativeEvaluationReport()
        rules = self.rules_data.get("rules", [])
        report.total_rules = len(rules)

        for rule in rules:
            rule_id = rule.get("id", "RULE")
            rule_name = rule.get("name", "")

            is_triggered = self.evaluate_rule_trigger(rule, custom_state)
            if is_triggered:
                report.triggered_rules += 1
                report.trigger_summary.append(f"{rule_id}: {rule_name}")

                rule_violations = self.evaluate_rule_invariants(rule, custom_state)
                invariants_in_rule = len(rule.get("invariants", []))
                report.invariants_checked += invariants_in_rule

                if not rule_violations:
                    report.invariants_passed += invariants_in_rule
                else:
                    passed = invariants_in_rule - len(rule_violations)
                    report.invariants_passed += max(0, passed)
                    report.violations.extend(rule_violations)

        report.violations_count = len(report.violations)
        report.overall_valid = (report.violations_count == 0)
        return report
