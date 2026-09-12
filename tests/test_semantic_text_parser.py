# -*- coding: utf-8 -*-
"""
Unit tests for SemanticNovelParser (02_TOOLS/semantic_text_parser.py).
"""

import os
import sys
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TOOLS_DIR = os.path.join(ROOT_DIR, "02_TOOLS")
if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)

from semantic_text_parser import SemanticNovelParser


class TestSemanticNovelParser(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.parser = SemanticNovelParser()

    def test_parser_loaded(self):
        self.assertTrue(self.parser.is_loaded, "SemanticNovelParser should load baseline without error.")
        self.assertGreater(len(self.parser.lines), 1000, "Novel should have over 1000 lines.")

    def test_parts_structure(self):
        self.assertEqual(self.parser.total_parts(), 5, "Novel must have exactly 5 parts.")
        expected_titles = [
            "ارتداد الحديد",
            "قاع الليل",
            "انصهار الرصاص والجليد",
            "شجن الحديد",
            "سكة إلى سجن آخر"
        ]
        for idx, title in enumerate(expected_titles, start=1):
            part = self.parser.get_part(idx)
            self.assertIsNotNone(part, f"Part {idx} must exist.")
            self.assertEqual(part["part_num"], idx)
            self.assertEqual(part["title"], title)

    def test_total_chapters(self):
        self.assertEqual(self.parser.total_chapters(), 32, "Novel must have exactly 32 chapters.")

    def test_exact_anchor_resolution(self):
        # Khalid's line at 1253
        loc = self.parser.locate_anchor("بقى ساعتين ويطلع الضو", expected_line=1253)
        self.assertTrue(loc["found"])
        self.assertEqual(loc["line_no"], 1253)
        self.assertEqual(loc["part_num"], 4)
        self.assertEqual(loc["chapter_num"], 5)
        self.assertEqual(loc["drift"], 0)

    def test_chapter_scoped_anchor_resolution(self):
        # Sliding door in Part 3 Chapter 4
        loc = self.parser.locate_anchor("الباب الجانبي المنزلق للعربة الوسطى", part_num=3, chapter_num=4)
        self.assertTrue(loc["found"])
        self.assertEqual(loc["part_num"], 3)
        self.assertEqual(loc["chapter_num"], 4)

    def test_anchor_not_found(self):
        loc = self.parser.locate_anchor("عبارة خيالية يستحيل وجودها في النص نهائياً")
        self.assertFalse(loc["found"])
        self.assertIsNone(loc["line_no"])


if __name__ == "__main__":
    unittest.main()
