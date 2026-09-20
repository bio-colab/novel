#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
TEST SUITE: JEV SYSTEM ONE SEMANTIC PLAUSIBILITY & FALSIFICATION
Project: «قطار الرمل» (Sand Train) - Invariant & Semantic Verification
License: MIT
==============================================================================
"""

import os
import sys
import pytest
from pathlib import Path

# Ensure 02_TOOLS is on sys.path
TOOLS_DIR = Path(__file__).resolve().parent.parent / "02_TOOLS"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from jev_engine import (
    JevEngine,
    FeasibilityResult,
    PsychologyResult,
    SensoryResult,
    ChoiceResult,
)


@pytest.fixture
def jev_offline():
    """Fixture providing an offline-forced JEV engine for fast, isolated unit tests."""
    return JevEngine(offline_mode=True)


@pytest.fixture
def jev_live():
    """Fixture providing a live JEV engine (if key available), otherwise falls back to offline."""
    return JevEngine()


# ==============================================================================
# 1. OFFLINE & ARCHITECTURE UNIT TESTS
# ==============================================================================

def test_jev_offline_mock_behavior(jev_offline):
    """Test that JEV offline mode returns typed answers deterministically without network calls."""
    assert jev_offline.offline_mode is True
    assert jev_offline.is_live is False

    res = jev_offline.audit_sensory_grounding("حديد ومسامير وصدأ وعرق")
    assert isinstance(res, SensoryResult)
    assert res.sensory_score >= 1.5
    assert res.confidence > 0.5


def test_jev_offline_negative_detection(jev_offline):
    """Test that JEV offline mode correctly flags obvious negative keyword violations."""
    res_psy = jev_offline.audit_character_psychology(
        character="خالد",
        expected_archetype="الصرامة العسكرية",
        passage="جلس يلقي نكات مرحة ويضحك بمرح",
    )
    assert isinstance(res_psy, PsychologyResult)
    assert res_psy.is_consistent is False


# ==============================================================================
# 2. LIVE INTEGRATION TESTS
# ==============================================================================

def test_jev_live_connectivity_and_telemetry(jev_live):
    """Verify live API connectivity, model version, and telemetry tracking."""
    if not jev_live.is_live:
        pytest.skip("No live JEV credentials detected; skipping live network probe.")

    raw = jev_live.evaluate(
        state="اختبار الاتصال السريع بنظام جيف",
        questions={
            "is_arabic": {
                "type": "noul",
                "instructions": "هل النص مكتوب باللغة العربية؟",
            }
        },
    )
    assert "answers" in raw
    assert "is_arabic" in raw["answers"]
    assert raw["answers"]["is_arabic"]["noul"] >= 0.80
    assert jev_live.total_calls >= 1
    assert jev_live.total_latency_seconds > 0.0


def test_baseline_chapter_1_psychology(jev_live):
    """Verify that Khalid's canonical baseline portrayal passes psychological concordance."""
    khalid_passage = (
        "خالد جالس على صندوق ذخيرة خشبي مثبت بمسامير قرب الباب الداخلي. "
        "البندقية الكلاشنكوف موضوعة طولاً بين فخذيه، فوهتها تشير إلى الصاج الأسفل، "
        "وأصابعه تستقر على عقبها الخشبي المتآكل. كانت سبابته اليمنى ترتفع ببطء، تتحسس أثر الندبة الغائرة في فكه الأيمن."
    )
    res = jev_live.audit_character_psychology(
        character="خالد",
        expected_archetype="الصرامة العسكرية وحفظ التراتبية وكبت الهلع",
        passage=khalid_passage,
    )
    assert res.is_consistent is True
    assert res.is_teleportation is False
    assert res.teleportation_prob < 0.50


def test_baseline_chapter_1_sensory_density(jev_live):
    """Verify that Chapter 1 baseline opening exhibits high visceral sensory density."""
    opening_passage = (
        "الحديد لا ينام. يهتز بنبض واهن، رتيب، ينتقل من سكة الهضبة الغربية عبر المحاور الصدئة، "
        "ليصعد في صفائح الأرضية ويستقر في عظام الركب. الغبار لا يرتفع في سحب؛ ذراته رقيقة، ثقيلة، "
        "تلج من فتحات التهوية والشقوق الدقيقة حول المسامير المفقودة، فتستقر على الرموش، وفي ثنايا القمصان."
    )
    res = jev_live.audit_sensory_grounding(opening_passage)
    assert res.sensory_score >= 1.0
    assert res.contains_cliche is False
    assert res.cliche_prob < 0.40


def test_character_choice_simulation(jev_live):
    """Verify that JEV can simulate an autonomous character decision with calibrated probabilities."""
    res = jev_live.simulate_character_choice(
        character="خالد",
        dilemma="عاصفة رملية تقترب وصوت هواء مكابح العربة الأخيرة يتسرب؛ السائق متردد بين التوقف أو مواصلة السير.",
        options={
            "enforce_protocol": "إصدار أمر فوري بالتحقق من ضغط المكابح وتأمين القوافل عسكرياً",
            "abandon_post": "الهروب والقفز من القطار في الظلام",
            "cry_helplessly": "البكاء والانهيار دون إصدار أي تعليمات",
        },
    )
    assert isinstance(res, ChoiceResult)
    assert res.chosen_option == "enforce_protocol"
    assert res.probabilities.get("enforce_protocol", 0) > 0.60


# ==============================================================================
# 3. NEGATIVE MUTATION & FALSIFICATION TESTS
# ==============================================================================

def test_negative_mutation_hollywood_acrobatics(jev_live):
    """
    Falsification Test: Inject a non-physical action violation.
    Mutated action: Character jumps from carriage window at 90 km/h in storm to run on roof.
    Expected: JEV flags is_feasible == False and identifies hollywood_acrobatics.
    """
    mutated_action = (
        "أبو اللول يقفز بخفة من نافذة العربة الأولى أثناء سير القطار بسرعة 90 كم/ساعة "
        "فوق جسر وادي الحجر المتجمد ليصل إلى العربة الخامسة ركضاً على السقف في قلب عاصفة رملية بلغت 70 عقدة."
    )
    res = jev_live.audit_physical_feasibility(
        action_text=mutated_action,
        context={"train_speed_kmh": 90, "wind_knots": 70, "character": "أبو اللول - نحيل ومدخن ومذعور"},
    )
    assert res.is_feasible is False
    assert res.violation_type in ("hollywood_acrobatics", "character_incoherence")
    assert res.feasibility_prob < 0.35


def test_negative_mutation_psychological_teleportation(jev_live):
    """
    Falsification Test: Inject character psychological teleportation.
    Mutated text: Khalid cracks jokes, chats lightheartedly, and weeps nostalgically about romantic memories.
    Expected: JEV flags is_consistent == False and defense_concordance != 'consistent'.
    """
    corrupted_khalid = (
        "جلس خالد وأخذ يضحك بمرح ويلقي النكات اللطيفة على أبي اللول، قائلاً: يا صديقي الحياة حلوة لمَ كل هذا القلق؟ "
        "ثم بدأ يشعر بحزن رومانسي عميق وذرف دمعة دافئة على خدّه وهو يتذكر حبيبته القديمة في القرية البعيدة."
    )
    res = jev_live.audit_character_psychology(
        character="خالد",
        expected_archetype="الصرامة العسكرية والانضباط الدفاعي وكبت الهلع",
        passage=corrupted_khalid,
    )
    assert res.is_consistent is False
    assert (res.is_teleportation is True) or (res.defense_mechanism == "severe_violation")


def test_negative_mutation_abstract_cliche_prose(jev_live):
    """
    Falsification Test: Inject abstract, sentimental, unsensory prose.
    Expected: JEV detects cliché or gives low sensory immersion score.
    """
    cliche_passage = (
        "كان الحزن يخيم على القلوب كغمامة سوداء، والألم يعتصر الأفئدة في بحر من الدموع اللانهائية، "
        "حيث شعر الجميع أن الأمل قد مات في ظلمة اليأس الدامس دون أي تفاصيل أخرى."
    )
    res = jev_live.audit_sensory_grounding(cliche_passage)
    # Must flag either low sensory score (< 1.0) or high cliché probability
    assert (res.sensory_score < 1.0) or (res.contains_cliche is True) or (res.cliche_prob > 0.50)
