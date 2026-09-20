#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
TEST WORLD SCHEMA & SPECIFICATION CONTRACT
Project: «قطار الرمل» (Sand Train) - Narrative Engineering Core
Milestone: MILESTONE-NARRATIVE-OS-v1.0 (Phase 1)
==============================================================================
"""

import copy
import pytest
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "02_TOOLS"))

from schema_validator import WorldSchemaValidator, SCHEMAS_DIR


@pytest.fixture
def validator():
    return WorldSchemaValidator()


@pytest.fixture
def manifest_path():
    return PROJECT_ROOT / "05_WORLD_BRAIN" / "world_manifest.yaml"


@pytest.fixture
def rules_path():
    return PROJECT_ROOT / "01_SPECS_AND_RULES" / "rules_manifest.yaml"


@pytest.fixture
def entities_path():
    return PROJECT_ROOT / "05_WORLD_BRAIN" / "entities_catalog.yaml"


def test_manifest_schema_compliance(validator, manifest_path):
    """World manifest conforms 100% to world_manifest.schema.json."""
    is_valid, errors = validator.validate_manifest(manifest_path)
    assert is_valid, f"Manifest validation failed: {errors}"


def test_rules_schema_compliance(validator, rules_path):
    """Declarative rules manifest conforms 100% to rule.schema.json."""
    is_valid, errors = validator.validate_rules(rules_path)
    assert is_valid, f"Rules validation failed: {errors}"


def test_entities_schema_compliance(validator, entities_path):
    """Entities catalog conforms 100% to entity.schema.json."""
    is_valid, errors = validator.validate_entities(entities_path)
    assert is_valid, f"Entities validation failed: {errors}"


def test_world_contract_holistic_audit(validator, manifest_path):
    """Holistic cross-reference verification passes with zero errors."""
    report = validator.validate_world_contract(manifest_path)
    assert report["manifest_valid"] is True
    assert report["rules_valid"] is True
    assert report["entities_valid"] is True
    assert report["cross_references_valid"] is True
    assert report["overall_success"] is True
    assert len(report["errors"]) == 0
    assert report["stats"]["characters_count"] == 14
    assert report["stats"]["rules_count"] >= 16


def test_manifest_negative_mutation_missing_field(validator, manifest_path):
    """Validator must reject a manifest missing a required field (e.g. chronotope)."""
    raw = validator.load_yaml(manifest_path)
    del raw["chronotope"]
    schema = validator.load_json(validator.manifest_schema_path)
    is_valid, errors = validator.validate_against_schema(raw, schema)
    assert not is_valid
    assert any("chronotope" in e for e in errors)


def test_manifest_negative_mutation_invalid_temperature_bounds(validator, manifest_path):
    """Validator must reject a manifest with missing temperature min/max requirements."""
    raw = validator.load_yaml(manifest_path)
    del raw["environment"]["temperature_celsius"]["min"]
    schema = validator.load_json(validator.manifest_schema_path)
    is_valid, errors = validator.validate_against_schema(raw, schema)
    assert not is_valid
    assert any("min" in e for e in errors)


def test_rules_negative_mutation_invalid_law_id(validator, rules_path):
    """Validator must reject a rule whose ID does not match LAW-[A-Z]+-[0-9]{2}."""
    raw = validator.load_yaml(rules_path)
    raw["rules"][0]["id"] = "INVALID_RULE_TAG_999"
    schema = validator.load_json(validator.rule_schema_path)
    is_valid, errors = validator.validate_against_schema(raw, schema)
    assert not is_valid
    assert any("INVALID_RULE_TAG_999" in e or "pattern" in e for e in errors)


def test_rules_negative_mutation_invalid_domain(validator, rules_path):
    """Validator must reject a rule with a non-existent scientific domain."""
    raw = validator.load_yaml(rules_path)
    raw["rules"][0]["domain"] = "astrology_magic"
    schema = validator.load_json(validator.rule_schema_path)
    is_valid, errors = validator.validate_against_schema(raw, schema)
    assert not is_valid
    assert any("astrology_magic" in e or "enum" in e for e in errors)


def test_entities_negative_mutation_missing_affordance(validator, entities_path):
    """Validator must reject a character entity missing an affordance anchor."""
    raw = validator.load_yaml(entities_path)
    del raw["characters"][0]["properties"]["affordance_anchor"]
    schema = validator.load_json(validator.entity_schema_path)
    is_valid, errors = validator.validate_against_schema(raw, schema)
    assert not is_valid
    assert any("affordance_anchor" in e for e in errors)
