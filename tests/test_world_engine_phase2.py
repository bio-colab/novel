#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
TEST SUITE: WORLD ENGINE PHASE 2 - CAUSALITY, EPISTEMICS & LAW RECOMMENDATION
Project: Narrative World OS / Framework
License: MIT
==============================================================================
"""

import argparse
import shutil
import tempfile
from pathlib import Path

import pytest

from world_engine.dag_miner import NarrativeCausalityMiner
from world_engine.spatial_epistemics import (
    EpistemicLeakViolation,
    PerceivedState,
    SoundEvent,
    SpatialAcousticEpistemicField,
)
from world_engine.law_catalog.catalog import DOMAIN_PACKS
from world_engine.law_catalog.recommender import DomainLawRecommender
from world_engine.cli import cmd_recommend_rules


SAMPLE_SAND_TRAIN_TEXT = """
# الجزء الأول: ارتداد الحديد
تخريب السكة وزرع اللغم الأرضي أدى إلى صدمة الارتداد عند نقطة الكيلومتر 312.4.
انكسار أنبوب الوقود تسبب في تفريغ الهواء وإطباق المكابح الهوائية لسكون العجلات.
في منتصف الليل، انطلق الكمين وسقط الرصاص على الصاج مما جعل مهدي يقفز من الباب المنزلق.
"""

SAMPLE_SUBMARINE_TEXT = """
كانت الغواصة تغوص في أعماق المحيط المظلم على عمق 450 متراً.
ضغط الماء يهدد بهدم الهيكل الخارجي، بينما أجهزة السونار ترصد ارتداد الصدى تحت طبقة الميل الحراري.
تعطلت مضخات الأكسجين مما أدى إلى هبوط نسبته وتسمم الهواء داخل الكابينة.
"""

SAMPLE_SPACE_TEXT = """
في المحطة المدارية المعلقة في الفضاء، تسبب ثقب نيزكي في تفريغ الضغط الفضائي المتفجر.
انعدام الجاذبية واشتداد الإشعاع الكوني فرضا عزلة تامة على رواد المحطة في الفراغ.
"""

SAMPLE_DESERT_TEXT = """
في رمضاء الصحراء القاحلة والقيظ الحارق، هبت ريح السموم واشتد العطش في القافلة.
ارتفعت حرارة الشمس الحارقة فوق 45 درجة مئوية والسراب يخدع البصر فوق الكثبان الرملية.
"""


class TestNarrativeCausalityMiner:
    def test_causality_event_mining(self):
        miner = NarrativeCausalityMiner()
        report = miner.mine_and_report(SAMPLE_SAND_TRAIN_TEXT)

        assert report.total_events >= 3
        assert report.total_causal_edges >= 2
        assert report.is_acyclic is True
        assert report.causal_density > 0.0
        assert len(report.topological_order) == report.total_events

        # Check event types
        event_types = [e.event_type for e in report.events]
        assert any("Sabotage" in t or "Shock" in t for t in event_types)


class TestSpatialAcousticEpistemicField:
    def test_attenuation_and_perception(self):
        field = SpatialAcousticEpistemicField()

        whisper = SoundEvent(
            event_id="EVT-01",
            location_id="car_01_guard",
            intensity_db=field.INTENSITIES["WHISPER"],  # 25 dB
            description="همس خافت في العربة الأولى"
        )
        gunshot = SoundEvent(
            event_id="EVT-02",
            location_id="car_01_guard",
            intensity_db=field.INTENSITIES["GUNSHOT"],  # 150 dB
            description="إطلاق نار في العربة الأولى"
        )

        # Attenuation between adjacent cars
        loss_adj = field.compute_acoustic_attenuation("car_01_guard", "car_02_middle")
        assert 20.0 <= loss_adj <= 25.0

        # Attenuation between separated cars (Car 1 to Car 3)
        loss_remote = field.compute_acoustic_attenuation("car_01_guard", "car_03_rear")
        assert 38.0 <= loss_remote <= 45.0

        # Co-present perception
        p_copresent = field.evaluate_perception(whisper, "خالد", "car_01_guard")
        assert p_copresent.is_perceived is True
        assert p_copresent.channel == "DIRECT_PRESENCE"

        # Remote perception of whisper (in Car 3)
        p_whisper_remote = field.evaluate_perception(whisper, "بسام", "car_03_rear")
        assert p_whisper_remote.is_perceived is False
        assert p_whisper_remote.channel is None
        assert p_whisper_remote.received_db < field.HUMAN_AUDITORY_THRESHOLD_DB

        # Remote perception of gunshot (in Car 3)
        p_gunshot_remote = field.evaluate_perception(gunshot, "بسام", "car_03_rear")
        assert p_gunshot_remote.is_perceived is True
        assert p_gunshot_remote.channel == "AUDITORY"
        assert p_gunshot_remote.received_db > 100.0

    def test_automated_epistemic_bubbles_and_leak_detection(self):
        field = SpatialAcousticEpistemicField()
        whisper = SoundEvent(
            event_id="EVT-WHISPER",
            location_id="car_01_guard",
            intensity_db=field.INTENSITIES["WHISPER"],
            description="محادثة همس سرية"
        )

        locs = {
            "خالد": "car_01_guard",
            "بسام": "car_03_rear",
        }
        bubbles = field.derive_automated_epistemic_bubbles(locs, [whisper])

        # Khaled knows, Bassam is blind
        assert len(bubbles["خالد"]["known_truths"]) == 1
        assert len(bubbles["خالد"]["blind_spots"]) == 0
        assert len(bubbles["بسام"]["known_truths"]) == 0
        assert len(bubbles["بسام"]["blind_spots"]) == 1

        # Leak detection
        leak = field.audit_omniscience_leak("بسام", "car_03_rear", whisper)
        assert leak is not None
        assert leak.severity == "FATAL"
        assert "Fatal Epistemic Leak" in leak.violation_message


class TestDomainLawCatalogAndRecommender:
    def test_catalog_structure(self):
        assert "closed_cold_transport" in DOMAIN_PACKS
        assert "deep_sea_submarine" in DOMAIN_PACKS
        assert "orbital_space_station" in DOMAIN_PACKS
        assert "desert_caravan_survival" in DOMAIN_PACKS

        for pack_id, pack in DOMAIN_PACKS.items():
            assert "pack_id" in pack
            assert "rules" in pack
            assert len(pack["rules"]) >= 2
            for rule in pack["rules"]:
                assert rule["id"].startswith("LAW-")
                assert "domain" in rule
                assert "severity" in rule

    def test_recommender_submarines(self):
        recommender = DomainLawRecommender()
        rep = recommender.recommend_for_text(SAMPLE_SUBMARINE_TEXT)
        assert rep.recommended_pack_id == "deep_sea_submarine"
        assert rep.confidence_score >= 0.7
        assert len(rep.suggested_rules) >= 3

    def test_recommender_space(self):
        recommender = DomainLawRecommender()
        rep = recommender.recommend_for_text(SAMPLE_SPACE_TEXT)
        assert rep.recommended_pack_id == "orbital_space_station"
        assert rep.confidence_score >= 0.7
        assert len(rep.suggested_rules) >= 2

    def test_recommender_desert(self):
        recommender = DomainLawRecommender()
        rep = recommender.recommend_for_text(SAMPLE_DESERT_TEXT)
        assert rep.recommended_pack_id == "desert_caravan_survival"
        assert rep.confidence_score >= 0.7

    def test_recommender_sand_train(self):
        recommender = DomainLawRecommender()
        rep = recommender.recommend_for_text(SAMPLE_SAND_TRAIN_TEXT)
        assert rep.recommended_pack_id == "closed_cold_transport"

    def test_cli_recommend_rules(self, tmp_path):
        sample_path = tmp_path / "sub_novel.txt"
        sample_path.write_text(SAMPLE_SUBMARINE_TEXT, encoding="utf-8")
        out_yaml = tmp_path / "rules_manifest.yaml"

        args = argparse.Namespace(
            input=sample_path,
            genre="submarine_depth_thriller",
            output=out_yaml
        )
        exit_code = cmd_recommend_rules(args)
        assert exit_code == 0
        assert out_yaml.exists()
