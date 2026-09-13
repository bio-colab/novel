#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
NARRATIVE CONSTRAINT GENERATOR (مولد بطاقات القيود والحدود الفيزيائية للكاتب)
Project: «قطار الرمل» (Sand Train) - Narrative Engineering Simulation Engine
Framework Charter: «نحن نُحلل ونُقيّم.. ولا نُقوّم» (Advisory Physical Affordances)
==============================================================================
"""

from typing import Dict, List, Any
try:
    from .ticker import EventSourcedTicker
except (ImportError, ValueError):
    from ticker import EventSourcedTicker


class NarrativeConstraintGenerator:
    """Generates physical feasibility and affordance cards for novel chapters."""

    CHAPTER_MILESTONES = [
        {
            "id": "CARD-01-STALL-COLD",
            "minute": 15,
            "chapter": "الجزء الأول / الفصل السادس",
            "title": "صدمة التوقف الأولى وتفقد القاطرة",
            "character": "أبو_علي",
            "intended_action": "فحص المحرك ولمس حديد القاطرة البارد",
            "required_dexterity": 0.70
        },
        {
            "id": "CARD-02-AMBUSH-SHOOTING",
            "minute": 315,
            "chapter": "الجزء الثالث / الفصل الثاني",
            "title": "اشتباك الكمين الليلي وإطلاق النار من المنصة",
            "character": "عباس",
            "intended_action": "تلقيم البندقية والضغط على الزناد بأصابع متصلبة",
            "required_dexterity": 0.40
        },
        {
            "id": "CARD-03-NIGHT-MAWWAL",
            "minute": 420,
            "chapter": "الجزء الرابع / الفصل الرابع",
            "title": "موال عزيز وانتقال الصوت بين العربات",
            "character": "عزيز",
            "intended_action": "الغناء بنبرة شجية وانعكاس الصوت في تجويف العربة",
            "required_dexterity": 0.00
        },
        {
            "id": "CARD-04-UNDER-CHASSIS-WIRE",
            "minute": 570,
            "chapter": "الجزء الخامس / الفصل الثاني",
            "title": "شد سلك الحديد حول أنبوب الوقود في ذروة الصقيع (-8°C)",
            "character": "سردار",
            "intended_action": "عقد السلك المعدني حول شق أنبوب الديزل بالأصابع",
            "required_dexterity": 0.55
        },
        {
            "id": "CARD-05-LEVER-PUMP-RESTART",
            "minute": 645,
            "chapter": "الجزء الخامس / الفصل الثالث",
            "title": "تشغيل مضخة التحضير اليدوية بكتلة الجذع",
            "character": "أبو_علي",
            "intended_action": "سحب ذراع مضخة التحضير بالخرقة ووزن الجسد",
            "required_dexterity": 0.05
        }
    ]

    @classmethod
    def generate_constraint_cards(cls, ticker: EventSourcedTicker) -> List[Dict[str, Any]]:
        """Evaluates simulated physical states against intended narrative actions."""
        cards = []

        for m in cls.CHAPTER_MILESTONES:
            minute = m["minute"]
            snap = ticker.state_history.get(minute, ticker.registry.snapshot())
            char_name = m["character"]
            char_data = snap.get("characters", {}).get(char_name)
            if not char_data:
                char_obj = ticker.registry.get_character(char_name)
                if not char_obj:
                    continue
                bio_temp = char_obj["biomechanics"]
                char_data = {
                    "core_temp_c": bio_temp.core_temp_c,
                    "fingers_temp_c": bio_temp.fingers_temp_c,
                    "motor_dexterity": bio_temp.motor_dexterity,
                    "shivering_stage": bio_temp.shivering_stage
                }

            env = snap.get("environment", ticker.registry.environment)

            dexterity = char_data["motor_dexterity"]
            req_dex = m["required_dexterity"]
            is_feasible = dexterity >= req_dex

            constraints = []
            if char_data["fingers_temp_c"] <= 2.0:
                constraints.append(
                    "تصلب شبه تام في أطراف الأصابع: الحركات الدقيقة (عقد، خياطة، فتح أقفال صغيرة) ممتنعة بيوميكانيكياً."
                )
            if char_data["shivering_stage"] in ["shivering_exhaustion", "hypothermic_torpor"]:
                constraints.append(
                    "إنهاك ارتعاشي: ثبات السلاح مفقود ورجفان العضلات يمنع التهديف الدقيق."
                )
            if env.get("lux", 0.8) < 1.0:
                constraints.append(
                    "عتمة ليلية شبه تامة: التهديف البصري مستحيل بدون وميض النيران أو ضوء كشاف."
                )

            # Advisory recommendation honoring the charter
            if not is_feasible:
                advisory = (
                    f"الفعل يتطلب مهارة حركية ({req_dex}) تتجاوز طاقة الشخصية الحالية ({dexterity}). "
                    "يُنصح باستخدام أداة مساعدة، أو عزم الجذع، أو الاستعانة برفيق (مثل مقترح PR-005)."
                )
            else:
                advisory = "الفعل ممكن ومطابق تماماً لحدود الفيزياء والمحيط البيئي."

            cards.append({
                "card_id": m["id"],
                "minute": minute,
                "wall_clock": ticker.minute_to_clock(minute),
                "chapter": m["chapter"],
                "title": m["title"],
                "character": char_name,
                "ambient_temp_c": env.get("ambient_temp_c"),
                "biomechanics": {
                    "core_temp_c": char_data["core_temp_c"],
                    "fingers_temp_c": char_data["fingers_temp_c"],
                    "motor_dexterity": dexterity,
                    "shivering_stage": char_data["shivering_stage"]
                },
                "action_evaluation": {
                    "intended_action": m["intended_action"],
                    "required_dexterity": req_dex,
                    "is_strictly_feasible": is_feasible,
                    "physical_constraints": constraints,
                    "author_advisory_note": advisory
                }
            })

        return cards
