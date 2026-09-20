#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
WORLD SPECIFICATION & CONTRACT SCHEMA VALIDATOR
Project: «قطار الرمل» (Sand Train) - Narrative Engineering Core / Framework
Milestone: MILESTONE-NARRATIVE-OS-v1.0 (Phase 1)
License: MIT
==============================================================================

Role & Purpose:
  Validates narrative world manifest, declarative rules, and entities catalog
  against standard JSON/YAML schemas. Enforces structural invariants, prevents
  corrupted world states, and verifies cross-references before runtime compilation.
==============================================================================
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCHEMAS_DIR = PROJECT_ROOT / "01_SPECS_AND_RULES" / "schemas"

DEFAULT_MANIFEST_SCHEMA = SCHEMAS_DIR / "world_manifest.schema.json"
DEFAULT_RULE_SCHEMA = SCHEMAS_DIR / "rule.schema.json"
DEFAULT_ENTITY_SCHEMA = SCHEMAS_DIR / "entity.schema.json"


class WorldSchemaValidator:
    """Validates world configurations against formal narrative OS schemas."""

    def __init__(self, schemas_dir: Optional[Path] = None):
        self.schemas_dir = schemas_dir or SCHEMAS_DIR
        self.manifest_schema_path = self.schemas_dir / "world_manifest.schema.json"
        self.rule_schema_path = self.schemas_dir / "rule.schema.json"
        self.entity_schema_path = self.schemas_dir / "entity.schema.json"

    def load_json(self, path: Path) -> Dict[str, Any]:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_yaml(self, path: Path) -> Dict[str, Any]:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def validate_against_schema(self, data: Dict[str, Any], schema: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate data dict against loaded JSON schema."""
        errors: List[str] = []
        if not HAS_JSONSCHEMA:
            errors.append("jsonschema library is not installed.")
            return False, errors

        validator = jsonschema.Draft202012Validator(schema)
        for error in validator.iter_errors(data):
            path_str = " -> ".join(str(p) for p in error.absolute_path) or "root"
            errors.append(f"[{path_str}]: {error.message}")

        return len(errors) == 0, errors

    def validate_file(self, data_path: Path, schema_path: Path) -> Tuple[bool, List[str]]:
        """Validate a YAML or JSON file against a schema file."""
        if not data_path.exists():
            return False, [f"File not found: {data_path}"]
        if not schema_path.exists():
            return False, [f"Schema not found: {schema_path}"]

        try:
            if data_path.suffix in [".yaml", ".yml"]:
                data = self.load_yaml(data_path)
            else:
                data = self.load_json(data_path)
        except Exception as e:
            return False, [f"Failed to parse {data_path.name}: {e}"]

        try:
            schema = self.load_json(schema_path)
        except Exception as e:
            return False, [f"Failed to parse schema {schema_path.name}: {e}"]

        return self.validate_against_schema(data, schema)

    def validate_manifest(self, manifest_path: Path) -> Tuple[bool, List[str]]:
        """Validate a world manifest file."""
        return self.validate_file(manifest_path, self.manifest_schema_path)

    def validate_rules(self, rules_path: Path) -> Tuple[bool, List[str]]:
        """Validate a rules manifest file."""
        return self.validate_file(rules_path, self.rule_schema_path)

    def validate_entities(self, entities_path: Path) -> Tuple[bool, List[str]]:
        """Validate an entities catalog file."""
        return self.validate_file(entities_path, self.entity_schema_path)

    def validate_world_contract(self, manifest_path: Path) -> Dict[str, Any]:
        """Perform holistic validation on a complete world specification."""
        report: Dict[str, Any] = {
            "manifest_path": str(manifest_path),
            "manifest_valid": False,
            "rules_valid": False,
            "entities_valid": False,
            "cross_references_valid": False,
            "errors": [],
            "warnings": [],
            "stats": {}
        }

        if not manifest_path.exists():
            report["errors"].append(f"Manifest not found: {manifest_path}")
            return report

        # 1. Validate Manifest schema
        is_manifest_valid, m_errors = self.validate_manifest(manifest_path)
        report["manifest_valid"] = is_manifest_valid
        report["errors"].extend([f"Manifest: {e}" for e in m_errors])
        if not is_manifest_valid:
            return report

        manifest = self.load_yaml(manifest_path)
        base_dir = manifest_path.parent.parent  # Workspace root

        # 2. Check and validate rules ref
        rules_ref = manifest.get("rules_manifest_ref")
        if rules_ref:
            rules_path = base_dir / rules_ref
            is_rules_valid, r_errors = self.validate_rules(rules_path)
            report["rules_valid"] = is_rules_valid
            report["errors"].extend([f"Rules: {e}" for e in r_errors])
            if is_rules_valid:
                rules_data = self.load_yaml(rules_path)
                report["stats"]["rules_count"] = len(rules_data.get("rules", []))
        else:
            report["warnings"].append("No rules_manifest_ref declared in manifest.")

        # 3. Check and validate entities ref
        entities_ref = manifest.get("entities_catalog_ref")
        entities_data = None
        if entities_ref:
            entities_path = base_dir / entities_ref
            is_entities_valid, e_errors = self.validate_entities(entities_path)
            report["entities_valid"] = is_entities_valid
            report["errors"].extend([f"Entities: {e}" for e in e_errors])
            if is_entities_valid:
                entities_data = self.load_yaml(entities_path)
                characters = entities_data.get("characters", [])
                report["stats"]["characters_count"] = len(characters)
        else:
            report["warnings"].append("No entities_catalog_ref declared in manifest.")

        # 4. Cross-Reference Consistency
        cross_errors = []
        zones = {z["id"] for z in manifest.get("spatial_topology", {}).get("zones", [])}
        inventories = manifest.get("resource_ledger", {}).get("initial_inventories", [])
        for inv in inventories:
            loc = inv.get("location_zone_id")
            if loc and loc not in zones:
                cross_errors.append(f"Resource {inv.get('resource_id')} placed in non-existent zone '{loc}'")

        headcount_spec = manifest.get("headcount_target", {})
        if headcount_spec and entities_data:
            target_souls = headcount_spec.get("initial_total")
            actual_souls = len(entities_data.get("characters", []))
            if target_souls != actual_souls:
                cross_errors.append(
                    f"Headcount mismatch: manifest targets {target_souls} souls, but entities catalog has {actual_souls}"
                )

        causality_ref = manifest.get("causality_graph_ref")
        if causality_ref:
            causality_path = base_dir / causality_ref
            if not causality_path.exists():
                cross_errors.append(f"Referenced causality graph does not exist: {causality_path}")

        report["cross_references_valid"] = len(cross_errors) == 0
        report["errors"].extend([f"Cross-Reference: {e}" for e in cross_errors])

        overall_ok = (
            report["manifest_valid"]
            and report.get("rules_valid", True)
            and report.get("entities_valid", True)
            and report["cross_references_valid"]
        )
        report["overall_success"] = overall_ok
        return report


def main():
    parser = argparse.ArgumentParser(description="Narrative World OS Schema Validator")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=PROJECT_ROOT / "05_WORLD_BRAIN" / "world_manifest.yaml",
        help="Path to world manifest YAML file"
    )
    args = parser.parse_args()

    validator = WorldSchemaValidator()
    print("===========================================================================")
    print("  WORLD SPECIFICATION & CONTRACT VALIDATOR (مدقق عقود ومخططات العالم)")
    print("===========================================================================")
    print(f"Auditing manifest: {args.manifest}")

    report = validator.validate_world_contract(args.manifest)

    print("\n--- SCHEMA VALIDATION RESULTS ---")
    print(f"  • World Manifest Schema:  {'✅ VALID' if report['manifest_valid'] else '❌ INVALID'}")
    print(f"  • Rules Manifest Schema:   {'✅ VALID' if report['rules_valid'] else '❌ INVALID'}")
    print(f"  • Entities Catalog Schema: {'✅ VALID' if report['entities_valid'] else '❌ INVALID'}")
    print(f"  • Cross-References Check:  {'✅ VALID' if report['cross_references_valid'] else '❌ INVALID'}")

    if report["stats"]:
        print(f"\n--- WORLD STATS ---")
        for k, v in report["stats"].items():
            print(f"  • {k}: {v}")

    if report["warnings"]:
        print("\n--- WARNINGS ---")
        for w in report["warnings"]:
            print(f"  ⚠️  {w}")

    if report["errors"]:
        print("\n--- ERRORS ---")
        for e in report["errors"]:
            print(f"  ❌ {e}")
        print("\n===========================================================================")
        print("  VALIDATION FAILED: World specification does not meet contract standards.")
        print("===========================================================================")
        sys.exit(1)

    print("\n===========================================================================")
    print("  VALIDATION PASSED: 100% Contract Compliance Verified.")
    print("===========================================================================")
    sys.exit(0)


if __name__ == "__main__":
    main()
