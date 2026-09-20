#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
SCHEMA VALIDATOR SHIM (BACKWARD COMPATIBILITY LAYER)
Redirects to world_engine.validator while preserving 100% legacy API compatibility.
==============================================================================
"""

import sys
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from world_engine.validator import (
    WorldSchemaValidator,
    SCHEMAS_DIR,
)

DEFAULT_MANIFEST_SCHEMA = SCHEMAS_DIR / "world_manifest.schema.json"
DEFAULT_RULE_SCHEMA = SCHEMAS_DIR / "rule.schema.json"
DEFAULT_ENTITY_SCHEMA = SCHEMAS_DIR / "entity.schema.json"


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
