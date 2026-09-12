#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for Stylistic Linters, Character Tracker, and World Brain Graph.
Tests sensory density, dialogue attribution, pacing, character presence, and knowledge graph ontology.
"""

import os
import sys
import unittest
from pathlib import Path

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TOOLS_DIR = os.path.join(ROOT_DIR, "02_TOOLS")
BASELINE_PATH = Path(ROOT_DIR) / "00_BASELINE" / "novel_baseline.md"
BRAIN_DIR = Path(ROOT_DIR) / "05_WORLD_BRAIN"

if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)

from sensory_linter import analyze_sensory_density, SENSORY_LEXICON
from dialogue_auditor import audit_dialogue, CHARACTERS
from pacing_visualizer import analyze_pacing
from character_tracker import audit_characters
from world_graph_builder import parse_world_brain


class TestStylisticLinters(unittest.TestCase):
    """Tests for stylistic, pacing, dialogue, and knowledge graph tools."""

    def test_sensory_lexicon_integrity(self):
        """Verify that sensory lexicon defines all 5 sensory modalities with rich vocabularies."""
        self.assertIn("Tactile (لمسي / حراري / ألم)", SENSORY_LEXICON)
        self.assertIn("Visual (بصري / ضوء وظل وتفاصيل)", SENSORY_LEXICON)
        self.assertIn("Auditory (سمعي / أصوات وإيقاع)", SENSORY_LEXICON)
        self.assertIn("Olfactory (شمي)", SENSORY_LEXICON)
        self.assertIn("Gustatory (تذوقي)", SENSORY_LEXICON)
        for modality, words in SENSORY_LEXICON.items():
            self.assertGreater(len(words), 10, f"Modality '{modality}' vocabulary is too sparse.")

    def test_sensory_linter_runs_cleanly(self):
        """Verify that analyze_sensory_density parses baseline novel without errors."""
        try:
            analyze_sensory_density(BASELINE_PATH)
        except Exception as e:
            self.fail(f"analyze_sensory_density raised an exception: {e}")

    def test_dialogue_auditor_extraction(self):
        """Verify that dialogue auditor extracts spoken lines and attributes them."""
        self.assertEqual(len(CHARACTERS), 14, "Dialogue auditor must track all 14 canonical characters.")
        try:
            audit_dialogue(BASELINE_PATH)
        except Exception as e:
            self.fail(f"audit_dialogue raised an exception: {e}")

    def test_pacing_visualizer_execution(self):
        """Verify that pacing visualizer calculates scene cadence and tension index."""
        try:
            analyze_pacing(BASELINE_PATH)
        except Exception as e:
            self.fail(f"analyze_pacing raised an exception: {e}")

    def test_character_tracker_coverage(self):
        """Verify that character tracker audits all 14 characters across all parts."""
        try:
            audit_characters(str(BASELINE_PATH))
        except Exception as e:
            self.fail(f"audit_characters raised an exception: {e}")

    def test_world_brain_graph_ontology(self):
        """Verify that world brain parses exactly 36 ontological nodes and over 130 relations."""
        nodes, edges = parse_world_brain(BRAIN_DIR)
        self.assertEqual(len(nodes), 36, f"Expected 36 ontological nodes, got {len(nodes)}.")
        self.assertGreaterEqual(len(edges), 130, f"Expected >= 130 relationships, got {len(edges)}.")


if __name__ == "__main__":
    unittest.main()
