#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
WORLD ENGINE - UNIFIED COMMAND-LINE INTERFACE (CLI)
Project: «قطار الرمل» (Sand Train) - Narrative Engineering Core / Framework
Milestone: MILESTONE-NARRATIVE-OS-v1.0 (Phase 3 Decoupling)
License: MIT
==============================================================================
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from world_engine.evaluator import DeclarativeInvariantEvaluator
from world_engine.validator import WorldSchemaValidator
from world_engine.dag import CausalityDAGVerifier

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = PROJECT_ROOT / "novel_template"
DEFAULT_MANIFEST_PATH = PROJECT_ROOT / "05_WORLD_BRAIN" / "world_manifest.yaml"


def audit_world(manifest_path: Path) -> Dict[str, Any]:
    """Execute holistic schema validation, DAG verification, and invariant evaluation on a world manifest."""
    manifest_path = Path(manifest_path).resolve()
    result: Dict[str, Any] = {
        "manifest_path": str(manifest_path),
        "is_valid": True,
        "manifest_valid": False,
        "rules_valid": False,
        "entities_valid": False,
        "cross_references_valid": False,
        "schema_errors": [],
        "cross_ref_errors": [],
        "dag_valid": False,
        "events_count": 0,
        "rules_evaluated": 0,
        "triggered_rules": 0,
        "invariants_passed": 0,
        "invariants_checked": 0,
        "invariant_violations": [],
    }

    if not manifest_path.exists():
        result["is_valid"] = False
        result["schema_errors"].append(f"Manifest file not found: {manifest_path}")
        return result

    # 1. Schema & Contract Validation
    validator = WorldSchemaValidator()
    report = validator.validate_world_contract(manifest_path)
    result["manifest_valid"] = report["manifest_valid"]
    result["rules_valid"] = report["rules_valid"]
    result["entities_valid"] = report["entities_valid"]
    result["cross_references_valid"] = report["cross_references_valid"]
    result["schema_errors"] = report["errors"]

    if report["errors"]:
        result["is_valid"] = False
        return result

    # 2. Causality Graph Acyclicity Check
    world_dir = manifest_path.parent
    workspace_root = manifest_path.parent.parent
    manifest = validator.load_yaml(manifest_path)
    causality_ref = manifest.get("causality_graph_ref")
    if causality_ref:
        cand1 = world_dir / causality_ref
        cand2 = workspace_root / causality_ref
        c_path = cand1 if cand1.exists() else cand2
        if c_path.exists():
            dag_verifier = CausalityDAGVerifier.from_yaml_file(c_path)
            is_acyclic, order = dag_verifier.verify_dag_acyclicity()
            result["dag_valid"] = is_acyclic
            result["events_count"] = len(dag_verifier.nodes)
            if not is_acyclic:
                result["is_valid"] = False

    # 3. Declarative Invariant Evaluation
    rules_ref = manifest.get("rules_manifest_ref")
    rules_path = None
    if rules_ref:
        cand1 = world_dir / rules_ref
        cand2 = workspace_root / rules_ref
        rules_path = cand1 if cand1.exists() else cand2

    state_path = world_dir / "world_state.yaml"
    evaluator = DeclarativeInvariantEvaluator(
        rules_path=rules_path,
        state_path=state_path if state_path.exists() else None,
        manifest_path=manifest_path
    )
    eval_report = evaluator.evaluate_all()
    result["rules_evaluated"] = eval_report.total_rules
    result["triggered_rules"] = eval_report.triggered_rules
    result["invariants_passed"] = eval_report.invariants_passed
    result["invariants_checked"] = eval_report.invariants_checked
    result["invariant_violations"] = eval_report.violations

    if eval_report.violations:
        result["is_valid"] = False

    return result


def cmd_audit(args: argparse.Namespace) -> int:
    """Execute holistic schema validation and invariant evaluation on a world."""
    manifest_path = Path(args.manifest) if args.manifest else DEFAULT_MANIFEST_PATH

    print("===========================================================================")
    print("  WORLD ENGINE CLI: UNIFIED AUDIT (مدقق نظام تشغيل العوالم الموحد)")
    print("===========================================================================")
    print(f"Auditing world manifest: {manifest_path}")

    report = audit_world(manifest_path)

    print("\n--- 1. SCHEMA & CONTRACT VALIDATION ---")
    print(f"  • World Manifest Schema:  {'✅ VALID' if report['manifest_valid'] else '❌ INVALID'}")
    print(f"  • Rules Manifest Schema:   {'✅ VALID' if report['rules_valid'] else '❌ INVALID'}")
    print(f"  • Entities Catalog Schema: {'✅ VALID' if report['entities_valid'] else '❌ INVALID'}")
    print(f"  • Cross-References Check:  {'✅ VALID' if report['cross_references_valid'] else '❌ INVALID'}")

    if report["schema_errors"]:
        print("\n--- SCHEMA ERRORS ---")
        for e in report["schema_errors"]:
            print(f"  ❌ {e}")
        return 1

    print("\n--- 2. CAUSALITY DAG CHECK ---")
    print(f"  • Event Chain Acyclicity: {'✅ ACYCLIC (100% Causal)' if report['dag_valid'] else '❌ CYCLIC'}")
    print(f"  • Verified Events Count:  {report['events_count']}")

    print("\n--- 3. DECLARATIVE INVARIANT EVALUATION ---")
    print(f"  • Rules Evaluated:       {report['rules_evaluated']}")
    print(f"  • Active Triggered Laws: {report['triggered_rules']}")
    print(f"  • Invariants Passed:     {report['invariants_passed']} / {report['invariants_checked']}")
    print(f"  • Invariant Violations:  {len(report['invariant_violations'])}")

    if report["invariant_violations"]:
        print("\n--- INVARIANT VIOLATIONS ---")
        for v in report["invariant_violations"]:
            print(f"  ❌ [{v.severity}] {v.rule_id}: {v.message}")
        return 1

    print("\n===========================================================================")
    print("  AUDIT SUCCESS: World passes all schema, causal, and invariant contracts.")
    print("===========================================================================")
    return 0


def cmd_init(args: argparse.Namespace) -> int:
    """Initialize a new narrative world instance from boilerplate template."""
    world_name = args.name
    output_dir = Path(args.output).resolve()
    genre = args.genre or "existential_survival_tragedy"

    print("===========================================================================")
    print("  WORLD ENGINE CLI: SCAFFOLD NEW WORLD (بناء عالم روائي جديد)")
    print("===========================================================================")
    print(f"World Name: {world_name}")
    print(f"Target Directory: {output_dir}")

    if output_dir.exists() and any(output_dir.iterdir()):
        if not args.force:
            print(f"❌ Error: Output directory '{output_dir}' already exists and is not empty. Use --force to overwrite.")
            return 1

    output_dir.mkdir(parents=True, exist_ok=True)

    if not TEMPLATE_DIR.exists():
        print(f"❌ Error: Template directory not found at '{TEMPLATE_DIR}'")
        return 1

    # Copy and customize templates
    replacements = {
        "{{WORLD_ID}}": world_name.lower().replace(" ", "_"),
        "{{WORLD_TITLE}}": world_name,
        "{{GENRE}}": genre,
    }

    files_created = []
    for template_file in TEMPLATE_DIR.glob("*.template.yaml"):
        dest_filename = template_file.name.replace(".template.yaml", ".yaml")
        dest_path = output_dir / dest_filename
        
        content = template_file.read_text(encoding="utf-8")
        for placeholder, val in replacements.items():
            content = content.replace(placeholder, val)
        
        dest_path.write_text(content, encoding="utf-8")
        files_created.append(dest_filename)

    # Copy README if present
    readme_template = TEMPLATE_DIR / "README.md"
    if readme_template.exists():
        shutil.copy(readme_template, output_dir / "README.md")
        files_created.append("README.md")

    print("\n--- SCAFFOLDING COMPLETE ---")
    for f in files_created:
        print(f"  📄 Created: {f}")

    # Automatically validate the newly generated world!
    new_manifest_path = output_dir / "world_manifest.yaml"
    if new_manifest_path.exists():
        validator = WorldSchemaValidator()
        report = validator.validate_world_contract(new_manifest_path)
        print("\n--- AUTOMATIC INITIAL VALIDATION ---")
        print(f"  • Template Contract Valid: {'✅ PASS' if report['overall_success'] else '❌ FAIL'}")

    print("\n===========================================================================")
    print(f"  NEW WORLD READY: cd {output_dir} and start authoring.")
    print("===========================================================================")
    return 0


def main():
    parser = argparse.ArgumentParser(
        prog="world_engine",
        description="Narrative World OS - Core CLI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Subcommand: audit
    audit_parser = subparsers.add_parser("audit", help="Audit a narrative world against schemas and invariants")
    audit_parser.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help="Path to world_manifest.yaml (defaults to Sand Train manifest)"
    )

    # Subcommand: init
    init_parser = subparsers.add_parser("init", help="Initialize a new narrative world instance from template")
    init_parser.add_argument("--name", type=str, required=True, help="Title of the new narrative world")
    init_parser.add_argument("--output", type=Path, required=True, help="Target directory for the new world")
    init_parser.add_argument("--genre", type=str, default="existential_survival_tragedy", help="Narrative genre")
    init_parser.add_argument("--force", action="store_true", help="Force overwrite existing directory")

    args = parser.parse_args()

    if args.command == "audit":
        sys.exit(cmd_audit(args))
    elif args.command == "init":
        sys.exit(cmd_init(args))
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
