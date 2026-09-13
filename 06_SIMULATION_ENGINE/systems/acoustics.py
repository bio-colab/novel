#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
ACOUSTICS & EPISTEMIC BOUNDARY SYSTEM (نظام الصوتيات والحدود المعرفية)
Project: «قطار الرمل» (Sand Train) - Narrative Engineering Simulation Engine
Framework Charter: «نحن نُحلل ونُقيّم.. ولا نُقوّم»
==============================================================================
"""

from typing import Dict, List, Tuple, Any


class AcousticsSystem:
    """Computes sound propagation and inter-car isolation (LAW-ACOUST-01..03)."""

    CAR_ORDER = ["locomotive", "car_01_guard", "car_02_prisoners", "car_03_hospital", "car_04_cargo"]
    INTERCAR_ATTENUATION_DB = 35.0  # Certified per LAW-ACOUST-03

    @classmethod
    def can_hear(cls, source_car: str, target_car: str, source_spl_db: float) -> Tuple[bool, float]:
        """
        Determines if a sound emitted in source_car reaches target_car above auditory threshold (20 dB).
        Returns (can_hear_boolean, perceived_spl_db).
        """
        if source_car == target_car:
            return True, source_spl_db

        # Inter-car distance count
        try:
            idx1 = cls.CAR_ORDER.index(source_car)
            idx2 = cls.CAR_ORDER.index(target_car)
            barriers_count = abs(idx1 - idx2)
        except ValueError:
            barriers_count = 2  # default exterior/interior barrier

        total_attenuation = barriers_count * cls.INTERCAR_ATTENUATION_DB
        perceived_spl = max(0.0, source_spl_db - total_attenuation)

        # Human threshold of hearing in train background noise is ~30 dB
        audible = perceived_spl >= 30.0
        return audible, round(perceived_spl, 1)

    @classmethod
    def update_epistemic_channels(cls, registry, active_sound_events: List[Dict[str, Any]]):
        """Updates characters' hearing channels based on active sound emissions."""
        for char in registry.characters.values():
            char_car = char["position"].car_id
            epistemic = char["epistemic"]
            epistemic.active_listening_cars = [char_car]

            for evt in active_sound_events:
                src_car = evt.get("origin_car", "exterior")
                spl = evt.get("source_spl_db", 90.0)
                audible, perceived_db = cls.can_hear(src_car, char_car, spl)
                if audible and src_car not in epistemic.active_listening_cars:
                    epistemic.active_listening_cars.append(src_car)
