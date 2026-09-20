#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
META-AUDITOR: CODEBASE INVARIANT & LAW REFERENCE VERIFIER
(المدقق الفوقي لسلامة استشهادات القوانين المرجعية عبر المستودع)
===============================================================================
Project: «قطار الرمل» (Sand Train)
Engine: Closed World Deterministic Evaluator - Meta-Auditing Module

Purpose:
  Scans all Python tools, documentation (README, MEMORY), and issue registries
  (WORLD_BUGS.yaml) to ensure that EVERY cited law (LAW-*-*) is officially
  defined in PHYSICAL_LAWS.md. Guarantees 0 orphan or unresolved law citations.

Guarantees:
  - 100% Read-Only self-reflective scan.
  - Zero tolerance for phantom or uncodified law citations.
  - Generates cross-reference matrix of law coverage.
===============================================================================
"""

import os
import sys
import re
from typing import Dict, List, Set, Any

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PHYSICAL_LAWS_PATH = os.path.join(ROOT_DIR, "01_SPECS_AND_RULES", "PHYSICAL_LAWS.md")
TOOLS_DIR = os.path.join(ROOT_DIR, "02_TOOLS")


class MetaAuditor:
    """Automated meta-auditor verifying repository self-consistency."""

    def __init__(self, root_dir: str = ROOT_DIR):
        self.root_dir = root_dir
        self.laws_path = os.path.join(root_dir, "01_SPECS_AND_RULES", "PHYSICAL_LAWS.md")
        self.defined_laws: Set[str] = set()
        self.citations: Dict[str, List[str]] = {}
        self.violations: List[str] = []
        self.passes: List[str] = []

    def load_defined_laws(self) -> bool:
        if not os.path.exists(self.laws_path):
            self.violations.append(f"PHYSICAL_LAWS.md missing at: {self.laws_path}")
            return False

        with open(self.laws_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract [LAW-CATEGORY-NUMBER]
        self.defined_laws = set(re.findall(r"\[(LAW-[A-Z]+-[0-9]+)\]", content))
        return len(self.defined_laws) > 0

    def scan_codebase_for_citations(self) -> Dict[str, List[str]]:
        scan_paths = []

        # 1. All python tools (excluding phase evaluation drivers)
        if os.path.exists(TOOLS_DIR):
            for fname in os.listdir(TOOLS_DIR):
                if fname.endswith(".py") and not fname.startswith("run_jev_"):
                    scan_paths.append(os.path.join(TOOLS_DIR, fname))

        # 2. Key markdown and yaml documents
        additional_docs = [
            os.path.join(self.root_dir, "README.md"),
            os.path.join(self.root_dir, "MEMORY.md"),
            os.path.join(self.root_dir, "03_AUDIT_AND_ISSUES", "WORLD_BUGS.yaml"),
            os.path.join(self.root_dir, "01_SPECS_AND_RULES", "CHARACTER_DOSSIERS.md"),
            os.path.join(self.root_dir, "01_SPECS_AND_RULES", "CHRONO_SPATIAL_SYSTEM.md"),
            os.path.join(self.root_dir, "01_SPECS_AND_RULES", "NARRATIVE_STANDARDS.md")
        ]

        for doc_path in additional_docs:
            if os.path.exists(doc_path):
                scan_paths.append(doc_path)

        citations: Dict[str, List[str]] = {}
        for path in scan_paths:
            rel_path = os.path.relpath(path, self.root_dir)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                matches = set(re.findall(r"(LAW-[A-Z]+-[0-9]+)", content))
                for m in matches:
                    citations.setdefault(m, []).append(rel_path)

        self.citations = citations
        return citations

    def audit_reference_integrity(self) -> bool:
        if not self.load_defined_laws():
            return False

        self.scan_codebase_for_citations()

        # Check 1: Any cited law must be officially defined
        undefined_cited = set(self.citations.keys()) - self.defined_laws
        if undefined_cited:
            for unc in sorted(undefined_cited):
                referencing = ", ".join(self.citations[unc])
                self.violations.append(
                    f"[Unresolved Law Citation] '{unc}' is cited in [{referencing}] but NOT defined in PHYSICAL_LAWS.md"
                )
        else:
            self.passes.append(
                f"Reference Completeness: All {len(self.citations)} distinct laws cited across the codebase are officially defined in PHYSICAL_LAWS.md."
            )

        # Check 2: Total defined laws count
        self.passes.append(
            f"Statutory Corpus: {len(self.defined_laws)} canonical laws codified in PHYSICAL_LAWS.md."
        )

        return len(self.violations) == 0

    def run_all(self) -> int:
        print("\n" + "=" * 80)
        print("  META-AUDITOR: STATUTORY REFERENCE INTEGRITY (مدقق المرجعية القانونية الفوقي)")
        print("=" * 80)

        success = self.audit_reference_integrity()

        print("\n--- PASSED META-INVARIANTS ---")
        for p in self.passes:
            print(f"  ✅ {p}")

        if self.citations:
            print("\n--- STATUTORY CITATION MAP (خارطة الاستشهادات بالقوانين) ---")
            for law in sorted(self.citations.keys()):
                files = ", ".join([os.path.basename(f) for f in self.citations[law]])
                print(f"  • {law:<16} ──> [{files}]")

        uncited = sorted(self.defined_laws - set(self.citations.keys()))
        if uncited:
            print(f"\n--- CODIFIED DORMANT LAWS ({len(uncited)} laws available for future narrative events) ---")
            print(f"  {', '.join(uncited)}")

        if self.violations:
            print("\n--- META-INVARIANT VIOLATIONS ---")
            for v in self.violations:
                print(f"  ❌ {v}")
            print("\n" + "=" * 80)
            print(f"  META-AUDIT FAILED: {len(self.violations)} reference violation(s) detected.")
            print("=" * 80 + "\n")
            return 1

        print("\n" + "=" * 80)
        print("  META-AUDIT PASSED: 100% Statutory Reference Integrity Verified.")
        print("=" * 80 + "\n")
        return 0


if __name__ == "__main__":
    auditor = MetaAuditor()
    sys.exit(auditor.run_all())
