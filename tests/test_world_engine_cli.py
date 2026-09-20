#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
TEST WORLD ENGINE CLI & PACKAGE ARCHITECTURE
Project: «قطار الرمل» (Sand Train) - Narrative Engineering Core
Milestone: MILESTONE-NARRATIVE-OS-v1.0 (Phase 3 Decoupling)
==============================================================================
"""

import argparse
import sys
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "02_TOOLS"))

import world_engine
from world_engine.cli import cmd_audit, cmd_init
from world_engine.evaluator import DeclarativeInvariantEvaluator, SafeExpressionEvaluator
from world_engine.validator import WorldSchemaValidator
from world_engine.dag import CausalityDAGVerifier


def test_world_engine_package_exports():
    """world_engine package exports all primary narrative engine primitives."""
    assert hasattr(world_engine, "DeclarativeInvariantEvaluator")
    assert hasattr(world_engine, "SafeExpressionEvaluator")
    assert hasattr(world_engine, "WorldSchemaValidator")
    assert hasattr(world_engine, "CausalityDAGVerifier")
    assert world_engine.__version__ == "1.0.0"


def test_cli_audit_sand_train():
    """world_engine CLI audit succeeds on Sand Train baseline manifest."""
    args = argparse.Namespace(
        manifest=PROJECT_ROOT / "05_WORLD_BRAIN" / "world_manifest.yaml"
    )
    exit_code = cmd_audit(args)
    assert exit_code == 0


def test_cli_init_and_audit_new_world(tmp_path):
    """world_engine init creates a valid, compilable world instance passing audit."""
    target_dir = tmp_path / "SubmarineWorld"
    init_args = argparse.Namespace(
        name="Submarine World",
        output=target_dir,
        genre="deep_sea_survival_thriller",
        force=False
    )
    init_code = cmd_init(init_args)
    assert init_code == 0
    assert (target_dir / "world_manifest.yaml").exists()
    assert (target_dir / "rules_manifest.yaml").exists()
    assert (target_dir / "entities_catalog.yaml").exists()
    assert (target_dir / "causality_graph.yaml").exists()
    assert (target_dir / "world_state.yaml").exists()
    assert (target_dir / "README.md").exists()

    # Now audit the scaffolded world
    audit_args = argparse.Namespace(
        manifest=target_dir / "world_manifest.yaml"
    )
    audit_code = cmd_audit(audit_args)
    assert audit_code == 0


def test_cli_audit_catches_invalid_manifest(tmp_path):
    """world_engine CLI audit returns non-zero on non-existent manifest."""
    fake_manifest = tmp_path / "does_not_exist.yaml"
    args = argparse.Namespace(manifest=fake_manifest)
    exit_code = cmd_audit(args)
    assert exit_code != 0


def test_backward_compatibility_shims():
    """Legacy 02_TOOLS import paths remain 100% operational without regression."""
    from declarative_evaluator import DeclarativeInvariantEvaluator as LegacyEvaluator
    from schema_validator import WorldSchemaValidator as LegacyValidator

    evaluator = LegacyEvaluator()
    assert evaluator.rules_path.exists()

    validator = LegacyValidator()
    assert validator.schemas_dir.exists()
