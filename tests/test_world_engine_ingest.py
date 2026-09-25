#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
TEST SUITE: WORLD ENGINE NARRATIVE INGESTION (حزمة اختبارات مستورد النصوص السردية)
Project: Narrative World OS / Framework
License: MIT
==============================================================================
"""

import argparse
import os
import shutil
import tempfile
from pathlib import Path

import pytest
import yaml

from world_engine.ingest.narrative_ner import NarrativeEntityExtractor
from world_engine.ingest.sensory_grounder import SensoryPhysicalGrounder
from world_engine.ingest.text_chunker import NarrativeTextChunker
from world_engine.ingest.manifest_synthesizer import WorldManifestSynthesizer
from world_engine.validator import WorldSchemaValidator
from world_engine.cli import audit_world, cmd_ingest


SAMPLE_ARABIC_NOVEL = """
# الجزء الأول: ارتداد الحديد

## 1. عتمة الصقيع
كان البرد يعض العظام في بادية السماوة المظلمة. زمهرير الشتاء يصفع صاج العربة المتهالكة بقسوة.
قال خالد وهو يتحسس ندبة الفك بالسبابة: "تأكد من إغلاق القفل يا أبا علي".
رد أبو علي وهو يمسح كفيه بالبنطال: "المفتاح معلق قرب الباب، والريح تشتد في الخارج".
صرخ سردار من زاوية الصندوق: "هل انكسر أنبوب الديزل؟ أسمع دوي الرصاص في البعيد".
تطلع بسام في العتمة وهو يضغط على منبت ظفره حتى يبيض. كان السلك المعدني ملقى قرب برميل الماء.
"""


SAMPLE_SCORCHING_NOVEL = """
# الجزء الأول: رمضاء القيظ

## 1. الهجير
كانت الشمس الحارقة تسلخ الجلود في الصحراء القاحلة. حر شديد وعطش يلهب الحناجر.
قال الشيخ منصور: "الماء شارف على النفاد، والسراب يملأ الأفق".
"""


@pytest.fixture
def temp_output_dir():
    temp_dir = tempfile.mkdtemp(prefix="test_ingest_")
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


class TestNarrativeTextChunker:
    def test_chunker_structure(self):
        chunker = NarrativeTextChunker()
        doc = chunker.parse_text(SAMPLE_ARABIC_NOVEL)

        assert doc.total_lines > 5
        assert doc.total_words > 20
        assert len(doc.parts) == 1
        assert doc.parts[0].title == "ارتداد الحديد"
        assert len(doc.chapters) == 1
        assert doc.chapters[0].chapter_index == 1
        assert "عتمة الصقيع" in doc.chapters[0].title
        assert len(doc.paragraphs) >= 1


class TestNarrativeEntityExtractor:
    def test_character_and_tic_extraction(self):
        extractor = NarrativeEntityExtractor()
        entities = extractor.extract(SAMPLE_ARABIC_NOVEL)

        char_names = [c.name for c in entities.characters]
        # Should extract characters like خالد, سردار, أبو علي, بسام
        assert any("خالد" in n for n in char_names)
        assert any("سردار" in n for n in char_names)
        assert any("أبو علي" in n for n in char_names)
        assert any("بسام" in n for n in char_names)

        # Check extracted props
        prop_names = [p.name for p in entities.props]
        assert any("مفتاح" in p for p in prop_names)
        assert any("برميل" in p for p in prop_names)
        assert any("سلك" in p for p in prop_names)

        # Check extracted vehicles / spaces
        veh_names = [v.name for v in entities.vehicles]
        assert any("عربة" in v for v in veh_names)


class TestSensoryPhysicalGrounder:
    def test_freezing_grounding(self):
        grounder = SensoryPhysicalGrounder()
        env = grounder.ground(SAMPLE_ARABIC_NOVEL)

        assert env.temperature.regime == "freezing"
        assert env.temperature.min <= -5.0
        assert env.temperature.initial <= 0.0
        assert env.lux.regime in ("dim_analog", "pitch_black")
        assert env.wind.speed_kmh >= 20.0
        assert env.atmosphere.enclosed is True

    def test_scorching_grounding(self):
        grounder = SensoryPhysicalGrounder()
        env = grounder.ground(SAMPLE_SCORCHING_NOVEL)

        assert env.temperature.regime == "scorching"
        assert env.temperature.initial >= 30.0
        assert env.lux.regime == "daylight"


class TestManifestSynthesizerAndAudit:
    def test_synthesis_creates_valid_world(self, temp_output_dir):
        synthesizer = WorldManifestSynthesizer()
        res = synthesizer.synthesize_from_text(
            text=SAMPLE_ARABIC_NOVEL,
            output_dir=temp_output_dir,
            world_id="sample_sand_train",
            title="Sample Sand Train",
        )

        assert (temp_output_dir / "world_manifest.yaml").exists()
        assert (temp_output_dir / "entities_catalog.yaml").exists()
        assert (temp_output_dir / "world_state.yaml").exists()
        assert (temp_output_dir / "rules_manifest.yaml").exists()
        assert (temp_output_dir / "causality_graph.yaml").exists()
        assert res["characters_count"] >= 3
        assert res["grounded_regime"] == "freezing"

        # Schema Validation
        validator = WorldSchemaValidator()
        report = validator.validate_world_contract(temp_output_dir / "world_manifest.yaml")
        assert report["overall_success"] is True
        assert report["manifest_valid"] is True
        assert report["rules_valid"] is True
        assert report["entities_valid"] is True
        assert report["cross_references_valid"] is True

        # Audit World Command
        audit_res = audit_world(temp_output_dir / "world_manifest.yaml")
        assert audit_res["is_valid"] is True
        assert audit_res["dag_valid"] is True
        assert len(audit_res["invariant_violations"]) == 0

    def test_cli_ingest_invocation(self, temp_output_dir):
        # Create a sample text file
        sample_file = temp_output_dir / "sample_novel.md"
        sample_file.write_text(SAMPLE_ARABIC_NOVEL, encoding="utf-8")
        out_sub = temp_output_dir / "out_world"

        args = argparse.Namespace(
            input=sample_file,
            output=out_sub,
            world_id="cli_test_world",
            title="CLI Test World",
            genre="existential_survival_tragedy",
        )

        exit_code = cmd_ingest(args)
        assert exit_code == 0
        assert (out_sub / "world_manifest.yaml").exists()
        assert (out_sub / "entities_catalog.yaml").exists()
