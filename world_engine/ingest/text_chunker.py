#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
NARRATIVE TEXT CHUNKER & HIERARCHICAL SEGMENTER (محلل الهيكل السردي وتجزئة المتن)
Project: Narrative World OS / Framework
License: MIT
==============================================================================
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class ParagraphChunk:
    index: int
    start_line: int
    end_line: int
    text: str
    word_count: int


@dataclass
class ChapterChunk:
    chapter_index: int
    title: str
    start_line: int
    end_line: int
    paragraphs: List[ParagraphChunk] = field(default_factory=list)
    word_count: int = 0


@dataclass
class PartChunk:
    part_index: int
    title: str
    start_line: int
    end_line: int
    chapters: List[ChapterChunk] = field(default_factory=list)
    word_count: int = 0


@dataclass
class ChunkedDocument:
    source_path: Optional[str]
    raw_text: str
    total_lines: int
    total_words: int
    parts: List[PartChunk] = field(default_factory=list)
    chapters: List[ChapterChunk] = field(default_factory=list)
    paragraphs: List[ParagraphChunk] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_path": self.source_path,
            "total_lines": self.total_lines,
            "total_words": self.total_words,
            "parts_count": len(self.parts),
            "chapters_count": len(self.chapters),
            "paragraphs_count": len(self.paragraphs),
        }


class NarrativeTextChunker:
    """Parses raw Arabic or multilingual narrative texts into hierarchical chunks."""

    ARABIC_NUMERALS: Dict[str, int] = {
        "الأول": 1, "الأولى": 1, "واحد": 1,
        "الثاني": 2, "الثانية": 2, "اثنين": 2,
        "الثالث": 3, "الثالثة": 3, "ثلاثة": 3,
        "الرابع": 4, "الرابعة": 4, "أربعة": 4,
        "الخامس": 5, "الخامسة": 5, "خمسة": 5,
        "السادس": 6, "السادسة": 6, "ستة": 6,
        "السابع": 7, "السابعة": 7, "سبعة": 7,
        "الثامن": 8, "الثامنة": 8, "ثمانية": 8,
        "التاسع": 9, "التاسعة": 9, "تسعة": 9,
        "العاشر": 10, "العاشرة": 10, "عشرة": 10,
    }

    PART_REGEX = re.compile(
        r"^(?:#+\s+)?(?:الجزء|القسم|الباب|Part)\s+([\u0621-\u064A0-9a-zA-Z]+)(?:\s*[:\-]\s*(.*))?$",
        re.IGNORECASE
    )

    CHAPTER_REGEX = re.compile(
        r"^(?:##+\s+)?(?:(?:الفصل|الإصحاح|Chapter)\s+([\u0621-\u064A0-9a-zA-Z]+)|(\d+)\.?)(?:\s*[:\-]?\s*(.*))?$",
        re.IGNORECASE
    )

    def __init__(self):
        pass

    def parse_file(self, file_path: str | Path) -> ChunkedDocument:
        path = Path(file_path).resolve()
        if not path.exists():
            raise FileNotFoundError(f"Source narrative file not found: {path}")

        raw_text = path.read_text(encoding="utf-8", errors="replace")
        return self.parse_text(raw_text, source_path=str(path))

    def parse_text(self, text: str, source_path: Optional[str] = None) -> ChunkedDocument:
        lines = [line.rstrip("\r\n") for line in text.splitlines()]
        total_lines = len(lines)
        total_words = sum(len(line.split()) for line in lines)

        doc = ChunkedDocument(
            source_path=source_path,
            raw_text=text,
            total_lines=total_lines,
            total_words=total_words,
            parts=[],
            chapters=[],
            paragraphs=[],
        )

        current_part: Optional[PartChunk] = None
        current_chapter: Optional[ChapterChunk] = None
        current_para_lines: List[Tuple[int, str]] = []
        para_idx = 1

        def commit_paragraph():
            nonlocal para_idx, current_para_lines
            if not current_para_lines:
                return
            start_l = current_para_lines[0][0]
            end_l = current_para_lines[-1][0]
            para_text = " ".join(line_str.strip() for _, line_str in current_para_lines)
            w_count = len(para_text.split())
            if w_count > 0:
                p_chunk = ParagraphChunk(
                    index=para_idx,
                    start_line=start_l,
                    end_line=end_l,
                    text=para_text,
                    word_count=w_count,
                )
                doc.paragraphs.append(p_chunk)
                if current_chapter:
                    current_chapter.paragraphs.append(p_chunk)
                    current_chapter.word_count += w_count
                para_idx += 1
            current_para_lines = []

        part_idx_counter = 1
        chap_idx_counter = 1

        for line_no, line in enumerate(lines, start=1):
            stripped = line.strip()

            # Check if Part Header
            part_match = self.PART_REGEX.match(stripped)
            if part_match:
                commit_paragraph()
                part_raw = part_match.group(1).strip()
                part_title = (part_match.group(2) or "").strip()
                p_num = self.ARABIC_NUMERALS.get(part_raw, part_idx_counter)
                if current_part:
                    current_part.end_line = line_no - 1
                current_part = PartChunk(
                    part_index=p_num,
                    title=part_title or f"Part {p_num}",
                    start_line=line_no,
                    end_line=total_lines,
                    chapters=[],
                    word_count=0,
                )
                doc.parts.append(current_part)
                part_idx_counter += 1
                continue

            # Check if Chapter Header
            chap_match = self.CHAPTER_REGEX.match(stripped)
            if chap_match:
                commit_paragraph()
                chap_id_str = (chap_match.group(1) or chap_match.group(2) or "").strip()
                chap_title = (chap_match.group(3) or "").strip()
                c_num = self.ARABIC_NUMERALS.get(chap_id_str, chap_idx_counter)
                if chap_id_str.isdigit():
                    c_num = int(chap_id_str)

                if current_chapter:
                    current_chapter.end_line = line_no - 1
                current_chapter = ChapterChunk(
                    chapter_index=c_num,
                    title=chap_title or f"Chapter {c_num}",
                    start_line=line_no,
                    end_line=total_lines,
                    paragraphs=[],
                    word_count=0,
                )
                doc.chapters.append(current_chapter)
                if current_part:
                    current_part.chapters.append(current_chapter)
                chap_idx_counter += 1
                continue

            # Blank lines separate paragraphs
            if not stripped:
                commit_paragraph()
            else:
                current_para_lines.append((line_no, line))

        commit_paragraph()

        # If no explicit chapters were found, synthesize a single root chapter
        if not doc.chapters and doc.paragraphs:
            root_chapter = ChapterChunk(
                chapter_index=1,
                title="المتن السردي العام",
                start_line=1,
                end_line=total_lines,
                paragraphs=doc.paragraphs.copy(),
                word_count=sum(p.word_count for p in doc.paragraphs),
            )
            doc.chapters.append(root_chapter)

        # If no parts were found, synthesize a single root part
        if not doc.parts and doc.chapters:
            root_part = PartChunk(
                part_index=1,
                title="الرواية الكاملة",
                start_line=1,
                end_line=total_lines,
                chapters=doc.chapters.copy(),
                word_count=sum(c.word_count for c in doc.chapters),
            )
            doc.parts.append(root_part)

        return doc
