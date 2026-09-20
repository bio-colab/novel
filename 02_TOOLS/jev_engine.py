#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
JEV SYSTEM ONE ADAPTER & SEMANTIC PLAUSIBILITY ENGINE
Project: «قطار الرمل» (Sand Train) - Narrative Engineering Core
License: MIT
==============================================================================

Role & Purpose:
  Interfaces with TypeSafe AI System One models (model: jev-latest) to provide
  fast, typed, probability-calibrated judgment primitives (Choice, Noul, Score)
  for semantic dimensions of the novel that deterministic regex/Pydantic cannot
  evaluate directly:
    1. Physical Action Feasibility (Detecting non-physical Hollywood acrobatics).
    2. Character Psychological Concordance (Detecting emotional teleportation & unearned shifts).
    3. Visceral Sensory Grounding (Rating physical immersion vs abstract cliché).
    4. Autonomous Character Agency (Probabilistic decision selection for NPCs in simulation).

Security Note:
  API keys are resolved dynamically from environment variable JEV_API_KEY or
  external secure storage (e.g. D:\\JEV\\API key for test.txt). Keys are NEVER
  hardcoded, committed, or echoed to logs/console.
==============================================================================
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

DEFAULT_ENDPOINT = "https://api.typesafe.ai/v1/systemone"
DEFAULT_MODEL = "jev-latest"

EXTERNAL_KEY_PATHS = [
    Path(r"D:\JEV\API key for test.txt"),
    Path(r"D:\2\evolab\JEV\API key for test.txt"),
    Path(__file__).resolve().parent.parent / ".agents" / "JEV_API_KEY.txt",
]


@dataclass
class FeasibilityResult:
    """Result of physical action feasibility evaluation."""
    is_feasible: bool
    feasibility_prob: float
    kinetic_risk_score: float
    violation_type: str
    confidence: float
    raw_answers: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PsychologyResult:
    """Result of character psychological concordance evaluation."""
    is_teleportation: bool
    teleportation_prob: float
    defense_mechanism: str
    is_consistent: bool
    confidence: float
    raw_answers: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SensoryResult:
    """Result of sensory density and grounding evaluation."""
    sensory_score: float
    level_description: str
    confidence: float
    contains_cliche: bool
    cliche_prob: float
    raw_answers: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChoiceResult:
    """Result of character decision or categorical choice evaluation."""
    chosen_option: str
    probabilities: Dict[str, float]
    confidence: float
    raw_answers: Dict[str, Any] = field(default_factory=dict)


class JevEngine:
    """TypeSafe System One (Jev) semantic judgment engine for 'قطار الرمل'."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: str = DEFAULT_ENDPOINT,
        model: str = DEFAULT_MODEL,
        offline_mode: bool = False,
        timeout: float = 20.0,
    ) -> None:
        if api_key is None:
            api_key = os.environ.get("JEV_API_KEY")
            if not api_key:
                for candidate_path in EXTERNAL_KEY_PATHS:
                    if candidate_path.exists():
                        try:
                            content = candidate_path.read_text(encoding="utf-8").strip()
                            if content:
                                api_key = content
                                break
                        except Exception:
                            continue

        self.api_key: Optional[str] = api_key
        self.endpoint: str = endpoint
        self.model: str = model
        self.offline_mode: bool = offline_mode or (not bool(self.api_key))
        self.timeout: float = timeout

        # Telemetry metrics
        self.total_calls: int = 0
        self.total_input_tokens: int = 0
        self.total_output_tokens: int = 0
        self.total_latency_seconds: float = 0.0

    @property
    def is_live(self) -> bool:
        """Returns True if live API credentials are configured and offline mode is False."""
        return not self.offline_mode and bool(self.api_key)

    def evaluate(
        self,
        state: Any,
        questions: Dict[str, Dict[str, Any]],
        model: Optional[str] = None,
        max_retries: int = 3,
    ) -> Dict[str, Any]:
        """Evaluates state against typed questions (Choice, Noul, Score) via TypeSafe System One."""
        target_model = model or self.model

        if self.offline_mode:
            return self._generate_offline_mock(state, questions, target_model)

        payload = {
            "state": state,
            "model": target_model,
            "questions": questions,
        }
        body = json.dumps(payload).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        req = urllib.request.Request(self.endpoint, headers=headers, data=body)

        for attempt in range(max_retries):
            t0 = time.perf_counter()
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    duration = time.perf_counter() - t0
                    raw_data = resp.read().decode("utf-8")
                    data = json.loads(raw_data)

                    self.total_calls += 1
                    self.total_latency_seconds += duration
                    usage = data.get("usage", {})
                    self.total_input_tokens += usage.get("input_tokens", 0)
                    self.total_output_tokens += usage.get("output_tokens", 0)
                    return data
            except urllib.error.HTTPError as err:
                duration = time.perf_counter() - t0
                if err.code in (429, 529) and attempt < max_retries - 1:
                    time.sleep(2.0 ** attempt)
                    continue
                err_msg = err.read().decode("utf-8") if hasattr(err, "read") else str(err)
                raise RuntimeError(f"Jev API HTTP {err.code}: {err_msg}") from err
            except Exception as exc:
                if attempt < max_retries - 1:
                    time.sleep(1.0)
                    continue
                # If network fails repeatedly, fallback gracefully if permitted
                raise RuntimeError(f"Jev API connection failed after {max_retries} attempts: {exc}") from exc

        raise RuntimeError("Jev API max retries exceeded.")

    def audit_physical_feasibility(
        self,
        action_text: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> FeasibilityResult:
        """
        Audits the physical and biomechanical feasibility of a character action in the novel.
        Detects non-physical acrobatics, excessive kinetic energy, or impossible feats.
        """
        eval_state = {
            "action": action_text,
            "world_context": context or {
                "environment": "قطار رملي مصفح في بادية باردة",
                "temperature_c": -2,
                "wind_condition": "عاصفة رملية",
            },
        }

        questions = {
            "physical_feasibility": {
                "type": "noul",
                "instructions": "هل يمكن لشخص بهذه البنية والظروف الجوية والفيزيائية تنفيذ هذا الفعل دون سقوط حتمي أو موت فوري؟",
            },
            "kinetic_risk_score": {
                "type": "score",
                "instructions": "ما تصنيف النتيجة الحركية والميكانيكية لهذا الفعل؟",
                "criteria": [
                    "إنجاز آمن دون إصابات بالغة",
                    "إصابات ميكانيكية وكسور مع احتمال نجاة ضئيل",
                    "سقوط مميت وارتطام حتمي بالصخور أو المجرى",
                ],
            },
            "violation_type": {
                "type": "choice",
                "instructions": "ما التصنيف الدقيق لهذا الفعل في سياق الفيزياء السردية للرواية؟",
                "criteria": {
                    "hollywood_acrobatics": "خرق فيزياء البقاء وبهلوانية سينمائية غير واقعية",
                    "character_incoherence": "تناقض مع البنية الفسيولوجية والنفسية المحددة للشخصية",
                    "realistic_survival": "فعل واقعي ومقبول فيزيائياً وسردياً ضمن حدود البقاء",
                },
            },
        }

        resp = self.evaluate(eval_state, questions)
        answers = resp.get("answers", {})

        feasibility_noul = answers.get("physical_feasibility", {}).get("noul", 0.5)
        risk_score = answers.get("kinetic_risk_score", {}).get("score", 1.0)
        violation_choice = answers.get("violation_type", {}).get("choice", "realistic_survival")
        confidence = answers.get("violation_type", {}).get("confidence", 0.7)

        # Action is feasible if feasibility probability >= 0.35 and not flagged as acrobatics
        is_feasible = (feasibility_noul >= 0.35) and (violation_choice != "hollywood_acrobatics")

        return FeasibilityResult(
            is_feasible=is_feasible,
            feasibility_prob=feasibility_noul,
            kinetic_risk_score=risk_score,
            violation_type=violation_choice,
            confidence=confidence,
            raw_answers=answers,
        )

    def audit_character_psychology(
        self,
        character: str,
        expected_archetype: str,
        passage: str,
    ) -> PsychologyResult:
        """
        Audits character psychological continuity and defense mechanisms (LAW-BIO-02).
        Detects unearned emotional shifts (teleportation) and archetype breaks.
        """
        eval_state = {
            "character": character,
            "expected_archetype": expected_archetype,
            "passage": passage,
        }

        questions = {
            "is_teleportation": {
                "type": "noul",
                "instructions": "هل يمثل هذا السلوك طفرة غير مبررة وانقطاعاً كارثياً (Teleportation) عن السمات النفسية والعصبية المحددة للشخصية؟",
            },
            "defense_concordance": {
                "type": "choice",
                "instructions": "كيف تصنف هذا السلوك بالنسبة لشخصية تعيش أزمة انحصار قاسية؟",
                "criteria": {
                    "consistent": "متسق مع السمات والانضباط والآليات الدفاعية للشخصية تحت ضغط الحصار والتوتر",
                    "mild_drift": "انحراف طفيف غير مألوف لكنه مفسر بضغط الموقف الآني المفاجئ",
                    "severe_violation": "انتهاك صارخ وتشويه لطبيعة الشخصية المحددة",
                },
            },
        }

        resp = self.evaluate(eval_state, questions)
        answers = resp.get("answers", {})

        teleportation_noul = answers.get("is_teleportation", {}).get("noul", 0.2)
        concordance_choice = answers.get("defense_concordance", {}).get("choice", "consistent")
        confidence = answers.get("defense_concordance", {}).get("confidence", 0.8)

        is_teleportation = teleportation_noul >= 0.60
        is_consistent = (concordance_choice in ("consistent", "mild_drift")) and not is_teleportation

        return PsychologyResult(
            is_teleportation=is_teleportation,
            teleportation_prob=teleportation_noul,
            defense_mechanism=concordance_choice,
            is_consistent=is_consistent,
            confidence=confidence,
            raw_answers=answers,
        )

    def audit_sensory_grounding(
        self,
        passage: str,
    ) -> SensoryResult:
        """
        Audits visceral sensory immersion and material grounding of a text excerpt.
        Differentiates deep physical texture (heat, iron, grit, cold) from superficial abstraction.
        """
        eval_state = {
            "passage": passage,
        }

        questions = {
            "sensory_immersion": {
                "type": "score",
                "instructions": "ما مستوى التجسيد الحسي المادي في هذا النص (الملمس، الحرارة، تفاصيل حركة المكان والأجساد)؟",
                "criteria": [
                    "تجريدي/عاطفي مبتذل يفتقر للملمس الفيزيائي للقطار",
                    "إشارات حسية عابرة أو متوسطة",
                    "تجسيد حسي فيزيائي غامر ومكثف يربط الأجساد بمادة المكان",
                ],
            },
            "contains_cliche": {
                "type": "noul",
                "instructions": "هل يحتوي النص على استعطاف وجداني مبتذل أو كليشيهات تضعف الواقعية الصارمة؟",
            },
        }

        resp = self.evaluate(eval_state, questions)
        answers = resp.get("answers", {})

        score_data = answers.get("sensory_immersion", {})
        sensory_score = score_data.get("score", 1.0)
        confidence = score_data.get("confidence", 0.8)
        legend = score_data.get("legend", {})
        int_score = min(max(int(round(sensory_score)), 0), 2)
        level_desc = legend.get(str(int_score), "إشارات حسية عابرة")

        cliche_noul = answers.get("contains_cliche", {}).get("noul", 0.2)
        contains_cliche = cliche_noul >= 0.55

        return SensoryResult(
            sensory_score=sensory_score,
            level_description=level_desc,
            confidence=confidence,
            contains_cliche=contains_cliche,
            cliche_prob=cliche_noul,
            raw_answers=answers,
        )

    def simulate_character_choice(
        self,
        character: str,
        dilemma: str,
        options: Dict[str, str],
        context: Optional[Dict[str, Any]] = None,
    ) -> ChoiceResult:
        """
        Simulates an autonomous character decision (System One Choice) under crisis.
        Returns the chosen action and calibrated probability distribution over options.
        """
        eval_state = {
            "character": character,
            "dilemma": dilemma,
            "context": context or {},
        }

        questions = {
            "decision": {
                "type": "choice",
                "instructions": f"ما القرار الأكثر ترجيحاً واتساقاً الذي ستتخذه شخصية '{character}' في هذه اللحظة؟",
                "criteria": options,
            }
        }

        resp = self.evaluate(eval_state, questions)
        answers = resp.get("answers", {})
        decision_data = answers.get("decision", {})

        chosen = decision_data.get("choice", list(options.keys())[0] if options else "unknown")
        probs = decision_data.get("probabilities", {})
        confidence = decision_data.get("confidence", 0.7)

        return ChoiceResult(
            chosen_option=chosen,
            probabilities=probs,
            confidence=confidence,
            raw_answers=answers,
        )

    def _generate_offline_mock(
        self,
        state: Any,
        questions: Dict[str, Dict[str, Any]],
        model: str,
    ) -> Dict[str, Any]:
        """Generates deterministic, rule-calibrated mock responses when offline."""
        answers = {}
        state_str = json.dumps(state, ensure_ascii=False) if isinstance(state, (dict, list)) else str(state)

        for q_id, q_spec in questions.items():
            q_type = q_spec.get("type", "choice")

            if q_type == "noul":
                # Check for negative signals
                is_negative = any(w in state_str for w in ["بهلوان", "نكات", "ضحك بمرح", "ركض على السقف", "حبيبته", "رومانسي"])
                noul_val = 0.85 if is_negative else 0.15
                answers[q_id] = {"type": "noul", "noul": noul_val}

            elif q_type == "choice":
                crit = q_spec.get("criteria", {})
                probs = {}
                keys = list(crit.keys())
                has_violation = any(w in state_str for w in ["نكات", "ضحك بمرح", "ركض على السقف", "قفز من نافذة"])

                for k in keys:
                    if has_violation and k in ("severe_violation", "hollywood_acrobatics"):
                        probs[k] = 0.85
                    elif not has_violation and k in ("consistent", "realistic_survival", "stoic_rigidity"):
                        probs[k] = 0.85
                    else:
                        probs[k] = 0.15 / max(len(keys) - 1, 1)

                tot = sum(probs.values()) or 1.0
                norm_probs = {k: round(v / tot, 3) for k, v in probs.items()}
                best_choice = max(norm_probs, key=norm_probs.get) if norm_probs else (keys[0] if keys else "")

                answers[q_id] = {
                    "type": "choice",
                    "choice": best_choice,
                    "confidence": 0.85,
                    "probabilities": norm_probs,
                }

            elif q_type == "score":
                has_violation = any(w in state_str for w in ["نكات", "ضحك بمرح", "رومانسي"])
                has_deep_sensory = any(w in state_str for w in ["حديد", "مسامير", "عرق", "ندبة", "صندوق ذخيرة"])

                if has_violation:
                    score_val = 0.2
                    probs = {"0": 0.80, "1": 0.18, "2": 0.02}
                elif has_deep_sensory:
                    score_val = 2.0
                    probs = {"0": 0.0, "1": 0.05, "2": 0.95}
                else:
                    score_val = 1.0
                    probs = {"0": 0.1, "1": 0.8, "2": 0.1}

                answers[q_id] = {
                    "type": "score",
                    "score": score_val,
                    "confidence": 0.9,
                    "legend": {"0": "منخفض", "1": "متوسط", "2": "مرتفع"},
                    "probabilities": probs,
                }

        return {
            "model": f"{model}-offline-mock",
            "answers": answers,
            "usage": {"input_tokens": 100, "output_tokens": 30},
            "offline_mode": True,
        }
