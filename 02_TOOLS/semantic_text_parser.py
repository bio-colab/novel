#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
SEMANTIC NOVEL PARSER & HIERARCHICAL LOCATOR (محرك التحليل الدلالي والتأصيل الهرمي)
==============================================================================
Project: «قطار الرمل» (Sand Train) - Closed-World Platform Engine
License: MIT
Framework Principle: «نحن نُحلل ونُقيّم.. ولا نُقوّم» (Evaluation & Physical Consistency,
                     Zero Literary Interference).

Purpose:
  Provides a robust, resilient parser for the Arabic novel text that supersedes
  fragile, absolute raw line numbers.
  
  Structural Anchors:
    - Hierarchical Hierarchy: Part (الجزء 1..5) -> Chapter (الفصل 1..N) -> Paragraph/Line.
    - Compound Indexing: (Part, Chapter) ensures unambiguous addressing across the 32 chapters.
    - Dynamic Anchor Resolution: Locates text citations semantically and dynamically
      resolves their actual line numbers with configurable drift tolerance.
    - Zero Brittle Numbers: Decouples physical telemetry and evidence validation
      from cosmetic markdown spacing drifts.
==============================================================================
"""

import os
import re
import sys
from typing import Dict, List, Any, Optional, Tuple

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_BASELINE_PATH = os.path.join(ROOT_DIR, "00_BASELINE", "novel_baseline.md")


class SemanticNovelParser:
    """
    Robust Arabic Novel Parser providing structural navigation and dynamic
    semantic anchor resolution across Parts, Chapters, and Lines.
    """

    PART_ARABIC_TO_NUM: Dict[str, int] = {
        "الأول": 1,
        "الثاني": 2,
        "الثالث": 3,
        "الرابع": 4,
        "الخامس": 5
    }

    def __init__(self, baseline_path: str = DEFAULT_BASELINE_PATH):
        self.baseline_path = baseline_path
        self.lines: List[str] = []
        self.parts: List[Dict[str, Any]] = []
        self.chapters_by_compound: Dict[Tuple[int, int], Dict[str, Any]] = {}
        self.line_map: Dict[int, Dict[str, Any]] = {}
        self.is_loaded: bool = False

        if os.path.exists(self.baseline_path):
            self.load_and_parse()

    def load_and_parse(self) -> bool:
        """Loads and parses the baseline file into a structured hierarchical tree."""
        if not os.path.exists(self.baseline_path):
            return False

        with open(self.baseline_path, "r", encoding="utf-8") as f:
            self.lines = [line.rstrip("\r\n") for line in f]

        self.parts = []
        self.chapters_by_compound = {}
        self.line_map = {}

        part_pattern = re.compile(r"^(?:#\s+)?الجزء\s+(الأول|الثاني|الثالث|الرابع|الخامس):\s*(.+)$")
        chapter_pattern = re.compile(r"^##\s+(\d+)\.\s*(.+)$")

        current_part: Dict[str, Any] = {
            "part_num": 1,
            "title": "ارتداد الحديد",
            "start_line": 1,
            "chapters": []
        }
        current_chapter: Optional[Dict[str, Any]] = None

        for idx, line in enumerate(self.lines, start=1):
            p_match = part_pattern.match(line)
            c_match = chapter_pattern.match(line)

            if p_match:
                p_name = p_match.group(1)
                p_title = p_match.group(2).strip()
                p_num = self.PART_ARABIC_TO_NUM.get(p_name, len(self.parts) + 1)

                if idx > 1:
                    if current_chapter:
                        current_chapter["end_line"] = idx - 1
                    current_part["end_line"] = idx - 1
                    self.parts.append(current_part)

                    current_part = {
                        "part_num": p_num,
                        "title": p_title,
                        "start_line": idx,
                        "chapters": []
                    }
                    current_chapter = None
                else:
                    current_part["part_num"] = p_num
                    current_part["title"] = p_title

            elif c_match:
                c_num = int(c_match.group(1))
                c_title = c_match.group(2).strip()

                if current_chapter:
                    current_chapter["end_line"] = idx - 1

                current_chapter = {
                    "part_num": current_part["part_num"],
                    "chapter_num": c_num,
                    "title": c_title,
                    "start_line": idx,
                    "end_line": len(self.lines),
                    "lines": []
                }
                current_part["chapters"].append(current_chapter)
                self.chapters_by_compound[(current_part["part_num"], c_num)] = current_chapter

            p_num_curr = current_part["part_num"]
            c_num_curr = current_chapter["chapter_num"] if current_chapter else 0

            self.line_map[idx] = {
                "part_num": p_num_curr,
                "chapter_num": c_num_curr,
                "text": line
            }

            if current_chapter:
                current_chapter["lines"].append((idx, line))

        if current_chapter:
            current_chapter["end_line"] = len(self.lines)
        current_part["end_line"] = len(self.lines)
        self.parts.append(current_part)

        self.is_loaded = True
        return True

    def total_parts(self) -> int:
        return len(self.parts)

    def total_chapters(self) -> int:
        return len(self.chapters_by_compound)

    def get_part(self, part_num: int) -> Optional[Dict[str, Any]]:
        for p in self.parts:
            if p["part_num"] == part_num:
                return p
        return None

    def get_chapter(self, part_num: int, chapter_num: int) -> Optional[Dict[str, Any]]:
        return self.chapters_by_compound.get((part_num, chapter_num))

    def locate_anchor(
        self,
        snippet: str,
        part_num: Optional[int] = None,
        chapter_num: Optional[int] = None,
        expected_line: Optional[int] = None,
        drift_tolerance: int = 25
    ) -> Dict[str, Any]:
        """
        Resiliently locates a text snippet semantically:
          1. If part_num and chapter_num are provided, restricts search to that chapter.
          2. If expected_line is provided, first checks the exact line and immediate neighborhood.
          3. Returns full provenance: resolved line number, compound chapter key, drift delta.
        """
        if not self.is_loaded:
            self.load_and_parse()

        # Step 1: Check expected line directly if provided
        if expected_line is not None and 1 <= expected_line <= len(self.lines):
            exact_text = self.lines[expected_line - 1]
            if snippet in exact_text:
                meta = self.line_map.get(expected_line, {})
                return {
                    "found": True,
                    "match_type": "exact_line",
                    "line_no": expected_line,
                    "part_num": meta.get("part_num", 0),
                    "chapter_num": meta.get("chapter_num", 0),
                    "line_text": exact_text,
                    "drift": 0
                }

            # Search within drift_tolerance window around expected_line
            w_start = max(1, expected_line - drift_tolerance)
            w_end = min(len(self.lines), expected_line + drift_tolerance)
            for l_idx in range(w_start, w_end + 1):
                cur_text = self.lines[l_idx - 1]
                if snippet in cur_text:
                    meta = self.line_map.get(l_idx, {})
                    return {
                        "found": True,
                        "match_type": "window_drift",
                        "line_no": l_idx,
                        "part_num": meta.get("part_num", 0),
                        "chapter_num": meta.get("chapter_num", 0),
                        "line_text": cur_text,
                        "drift": l_idx - expected_line
                    }

        # Step 2: Search within specified Chapter
        if part_num is not None and chapter_num is not None:
            chap = self.get_chapter(part_num, chapter_num)
            if chap:
                for l_idx, l_text in chap["lines"]:
                    if snippet in l_text:
                        drift = (l_idx - expected_line) if expected_line else 0
                        return {
                            "found": True,
                            "match_type": "chapter_scoped",
                            "line_no": l_idx,
                            "part_num": part_num,
                            "chapter_num": chapter_num,
                            "line_text": l_text,
                            "drift": drift
                        }

        # Step 3: Search within specified Part
        elif part_num is not None:
            part = self.get_part(part_num)
            if part:
                for l_idx in range(part["start_line"], part["end_line"] + 1):
                    l_text = self.lines[l_idx - 1]
                    if snippet in l_text:
                        meta = self.line_map.get(l_idx, {})
                        drift = (l_idx - expected_line) if expected_line else 0
                        return {
                            "found": True,
                            "match_type": "part_scoped",
                            "line_no": l_idx,
                            "part_num": part_num,
                            "chapter_num": meta.get("chapter_num", 0),
                            "line_text": l_text,
                            "drift": drift
                        }

        # Step 4: Global Search across entire novel
        for l_idx, l_text in enumerate(self.lines, start=1):
            if snippet in l_text:
                meta = self.line_map.get(l_idx, {})
                drift = (l_idx - expected_line) if expected_line else 0
                return {
                    "found": True,
                    "match_type": "global_fallback",
                    "line_no": l_idx,
                    "part_num": meta.get("part_num", 0),
                    "chapter_num": meta.get("chapter_num", 0),
                    "line_text": l_text,
                    "drift": drift
                }

        return {
            "found": False,
            "match_type": "not_found",
            "line_no": None,
            "part_num": None,
            "chapter_num": None,
            "line_text": None,
            "drift": None
        }


if __name__ == "__main__":
    parser = SemanticNovelParser()
    print("Semantic Novel Parser Initialized:")
    print(f"  • Total Lines: {len(parser.lines)}")
    print(f"  • Total Parts: {parser.total_parts()}")
    print(f"  • Total Chapters: {parser.total_chapters()}")
    
    # Test Anchor Resolution
    test_snippet = "بقى ساعتين ويطلع الضو"
    loc = parser.locate_anchor(test_snippet, expected_line=1253)
    print(f"\nTest Anchor '{test_snippet}':")
    print(f"  Found: {loc['found']} at Line {loc['line_no']} (Part {loc['part_num']}, Chapter {loc['chapter_num']})")
    print(f"  Match Type: {loc['match_type']}, Drift: {loc['drift']}")
