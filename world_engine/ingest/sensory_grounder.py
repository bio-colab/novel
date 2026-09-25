#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
SENSORY PHYSICAL GROUNDER (مؤرض الحواس والترجمة الفيزيائية للسرد)
Project: Narrative World OS / Framework
License: MIT
==============================================================================
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class TemperatureTelemetry:
    initial: float
    min: float
    max: float
    regime: str  # freezing, temperate, scorching
    inferred_from: List[str] = field(default_factory=list)


@dataclass
class LuxTelemetry:
    min: float
    max: float
    initial: float
    regime: str  # pitch_black, dim_analog, daylight
    inferred_from: List[str] = field(default_factory=list)


@dataclass
class WindTelemetry:
    speed_kmh: float
    gust_kmh: float
    direction_degrees: float
    regime: str
    inferred_from: List[str] = field(default_factory=list)


@dataclass
class AtmosphereTelemetry:
    enclosed: bool
    hypoxia_risk: bool
    dominant_odor: Optional[str] = None
    inferred_from: List[str] = field(default_factory=list)


@dataclass
class GroundedEnvironment:
    temperature: TemperatureTelemetry
    lux: LuxTelemetry
    wind: WindTelemetry
    atmosphere: AtmosphereTelemetry
    detected_sensory_tokens_count: int

    def to_manifest_dict(self) -> Dict[str, Any]:
        return {
            "temperature_celsius": {
                "initial": self.temperature.initial,
                "min": self.temperature.min,
                "max": self.temperature.max,
            },
            "humidity_percent": {
                "min": 8 if self.temperature.regime == "freezing" else 20,
                "max": 14 if self.temperature.regime == "freezing" else 75,
            },
            "wind": {
                "speed_kmh": self.wind.speed_kmh,
                "direction_degrees": self.wind.direction_degrees,
                "gust_kmh": self.wind.gust_kmh,
            },
            "lux_ambient": {
                "min": self.lux.min,
                "max": self.lux.max,
            },
        }


class SensoryPhysicalGrounder:
    """Scans Arabic narrative text and deduces calibrated physical environmental variables."""

    # Thermal Keywords
    FREEZING_KEYWORDS = [
        "برد", "صقيع", "ثلج", "عض العظام", "تجمد", "ارتجاف", "زمهرير",
        "قارس", "شتاء", "جليد", "كانون", "اصطكاك الأسنان", "أطراف متيبسة",
        "بخار الزفير", "تخثر الدم", "برودة"
    ]
    SCORCHING_KEYWORDS = [
        "حر", "قيظ", "شمس حارقة", "رمضاء", "سموم", "لهيب", "عرق يتصبب",
        "جفاف", "عطش", "سراب", "هجير", "صيف"
    ]

    # Optical Keywords
    DARKNESS_KEYWORDS = [
        "عتمة", "ظلام", "سواد", "ليل", "محاق", "لا يرى كفه", "انطفأ",
        "مصباح باهت", "شمعة", "فتيل", "غبش", "دجى"
    ]
    DAYLIGHT_KEYWORDS = [
        "شمس", "نهار", "ضوء ساطع", "سطوع", "فجر", "أشرقت", "ضياء"
    ]

    # Wind Keywords
    GALE_KEYWORDS = [
        "عاصفة", "عصف", "ريح عاتية", "رياح", "ريح", "الريح", "هواء بارد", "صفير الريح", "زوبعة"
    ]

    # Atmosphere / Enclosure Keywords
    ENCLOSURE_KEYWORDS = [
        "خانق", "ضيق تنفس", "ثقل الصدر", "رائحة ديزل", "غاز", "دخان",
        "صندوق مغلق", "كتمة", "احتجاز", "حبس"
    ]

    def __init__(self):
        pass

    @classmethod
    def _match_arabic_kw(cls, kw: str, text: str) -> bool:
        """Matches an Arabic keyword with tolerance for common prefixes (ال، و، ف، ب، ك، ل)."""
        pattern = rf"(?:^|[\s\.\،\,\:\!\؟\(\)\«\»\-\"\'\[\]])(?:(?:و|ف|ب|ك|ل)?(?:ال)?|(?:لل))?{re.escape(kw)}(?:$|[\s\.\،\,\:\!\؟\(\)\«\»\-\"\'\[\]])"
        return bool(re.search(pattern, text, re.UNICODE))

    def ground(self, text: str) -> GroundedEnvironment:
        # Match counters with prefix tolerance
        freezing_hits = [kw for kw in self.FREEZING_KEYWORDS if self._match_arabic_kw(kw, text)]
        scorching_hits = [kw for kw in self.SCORCHING_KEYWORDS if self._match_arabic_kw(kw, text)]
        darkness_hits = [kw for kw in self.DARKNESS_KEYWORDS if self._match_arabic_kw(kw, text)]
        daylight_hits = [kw for kw in self.DAYLIGHT_KEYWORDS if self._match_arabic_kw(kw, text)]
        gale_hits = [kw for kw in self.GALE_KEYWORDS if self._match_arabic_kw(kw, text)]
        enclosure_hits = [kw for kw in self.ENCLOSURE_KEYWORDS if self._match_arabic_kw(kw, text)]

        total_tokens = sum(len(h) for h in [
            freezing_hits, scorching_hits, darkness_hits, daylight_hits, gale_hits, enclosure_hits
        ])

        # 1. Thermal Grounding
        if len(freezing_hits) > len(scorching_hits):
            temp = TemperatureTelemetry(
                initial=0.0,
                min=-8.0,
                max=2.0,
                regime="freezing",
                inferred_from=freezing_hits[:5]
            )
        elif len(scorching_hits) > len(freezing_hits):
            temp = TemperatureTelemetry(
                initial=38.0,
                min=28.0,
                max=48.0,
                regime="scorching",
                inferred_from=scorching_hits[:5]
            )
        else:
            temp = TemperatureTelemetry(
                initial=20.0,
                min=15.0,
                max=25.0,
                regime="temperate",
                inferred_from=[]
            )

        # 2. Optical Grounding
        if len(darkness_hits) > len(daylight_hits):
            lux = LuxTelemetry(
                min=0.0,
                max=15.0,
                initial=0.8,
                regime="dim_analog" if len(darkness_hits) > 2 else "pitch_black",
                inferred_from=darkness_hits[:5]
            )
        elif len(daylight_hits) > len(darkness_hits):
            lux = LuxTelemetry(
                min=50.0,
                max=10000.0,
                initial=500.0,
                regime="daylight",
                inferred_from=daylight_hits[:5]
            )
        else:
            if temp.regime == "scorching":
                lux = LuxTelemetry(
                    min=50.0,
                    max=10000.0,
                    initial=500.0,
                    regime="daylight",
                    inferred_from=[]
                )
            else:
                lux = LuxTelemetry(
                    min=1.0,
                    max=100.0,
                    initial=10.0,
                    regime="dim_analog",
                    inferred_from=[]
                )

        # 3. Wind Grounding
        if gale_hits:
            wind = WindTelemetry(
                speed_kmh=38.0,
                gust_kmh=55.0,
                direction_degrees=315.0,
                regime="strong_breeze",
                inferred_from=gale_hits[:5]
            )
        else:
            wind = WindTelemetry(
                speed_kmh=8.0,
                gust_kmh=15.0,
                direction_degrees=0.0,
                regime="light_breeze",
                inferred_from=[]
            )

        # 4. Atmosphere Grounding
        is_enclosed = len(enclosure_hits) >= 2 or ("عربة" in text or "كابينة" in text or "غواصة" in text)
        dominant_odor = "ديزل وعرق بارد" if "ديزل" in text else None
        atmosphere = AtmosphereTelemetry(
            enclosed=is_enclosed,
            hypoxia_risk=is_enclosed and (len(enclosure_hits) > 0 or temp.regime == "freezing"),
            dominant_odor=dominant_odor,
            inferred_from=enclosure_hits[:5]
        )

        return GroundedEnvironment(
            temperature=temp,
            lux=lux,
            wind=wind,
            atmosphere=atmosphere,
            detected_sensory_tokens_count=total_tokens,
        )
