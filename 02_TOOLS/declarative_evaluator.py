#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
DECLARATIVE EVALUATOR SHIM (BACKWARD COMPATIBILITY LAYER)
Redirects to world_engine while preserving 100% legacy API compatibility.
==============================================================================
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from world_engine.evaluator import (
    DeclarativeInvariantEvaluator,
    SafeExpressionEvaluator,
    SecurityViolationError,
    InvariantViolation,
    DeclarativeEvaluationReport,
    DEFAULT_RULES_PATH,
    DEFAULT_STATE_PATH,
    DEFAULT_MANIFEST_PATH,
)


def main():
    from world_engine.cli import main as cli_main
    cli_main()


__all__ = [
    "DeclarativeInvariantEvaluator",
    "SafeExpressionEvaluator",
    "SecurityViolationError",
    "InvariantViolation",
    "DeclarativeEvaluationReport",
    "DEFAULT_RULES_PATH",
    "DEFAULT_STATE_PATH",
    "DEFAULT_MANIFEST_PATH",
    "main",
]

if __name__ == "__main__":
    main()
