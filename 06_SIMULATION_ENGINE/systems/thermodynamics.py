#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
THERMODYNAMICS SYSTEM (نظام الديناميكا الحرارية الحتمي)
Project: «قطار الرمل» (Sand Train) - Narrative Engineering Simulation Engine
Framework Charter: «نحن نُحلل ونُقيّم.. ولا نُقوّم»
==============================================================================
"""

import math
from typing import Dict, Any


class ThermodynamicSystem:
    """Computes environmental and human thermal decay curves (LAW-THERMO-01 & LAW-BIO-01)."""

    @staticmethod
    def update_environment(registry, minute: int) -> Dict[str, float]:
        """Calculates ambient temp, wind chill, and radiation cooling for minute [0..645]."""
        hours = minute / 60.0
        # Formula calibrated with alpha=0.60 to reach -8.0°C floor at minute 570 (04:30)
        if minute >= 570:
            ambient_temp = -8.0
        else:
            ambient_temp = max(-8.0, round(0.0 - (0.60 * (hours ** 1.15)), 2))

        wind_chill = round(ambient_temp - 5.4, 2)

        # Illumination lux: Astronomical dawn begins at minute 502 (05:22)
        lux = 0.8 if minute < 502 else (2.5 if minute < 588 else 45.0)

        registry.environment["ambient_temp_c"] = ambient_temp
        registry.environment["wind_chill_effective_c"] = wind_chill
        registry.environment["lux"] = lux

        return {
            "ambient_temp_c": ambient_temp,
            "wind_chill_effective_c": wind_chill,
            "lux": lux
        }

    @staticmethod
    def update_cars(registry, ambient_temp: float, minute: int):
        """Calculates temperature drop inside each train carriage."""
        # Cars cool with thermal inertia: Car 01 (insulated), Car 02/03 (cold metal drafts)
        hours = minute / 60.0
        for cid, car in registry.cars.items():
            base_temp = 4.2 if "01" in cid else (2.0 if "02" in cid else 1.0)
            # Interior car temp lags ambient cooling
            interior_temp = max(ambient_temp + 1.5, base_temp - (0.45 * (hours ** 1.10)))
            car["interior_temp_c"] = round(interior_temp, 2)

    @staticmethod
    def update_characters(registry, ambient_temp: float, minute: int):
        """Calculates core and extremity temperature drop for each living character."""
        for name, char in registry.characters.items():
            bio = char["biomechanics"]
            if not bio.is_alive:
                # Dead bodies cool directly toward ambient
                bio.core_temp_c = max(ambient_temp, bio.core_temp_c - 0.05)
                bio.fingers_temp_c = max(ambient_temp, bio.fingers_temp_c - 0.08)
                continue

            # Core temperature decay: slow defense via clothing & shivering
            decay_rate = 0.0035  # °C per minute for healthy adult
            if "جريح" in char.get("role", "") or name in ["أبو_اللول", "خليل", "سردار"]:
                decay_rate = 0.0050  # accelerated by trauma / blood loss

            bio.core_temp_c = round(max(31.5, 36.8 - (decay_rate * minute)), 2)

            # Finger extremity temperature decay toward ambient
            cooling_progression = min(1.0, minute / 450.0)
            target_finger_temp = ambient_temp + 2.0
            bio.fingers_temp_c = round(24.5 - (cooling_progression * (24.5 - target_finger_temp)), 2)
