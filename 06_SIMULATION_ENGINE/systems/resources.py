#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
RESOURCES SYSTEM (نظام الموارد والذخيرة والاستهلاك المائي الحتمي)
Project: «قطار الرمل» (Sand Train) - Narrative Engineering Simulation Engine
Framework Charter: «نحن نُحلل ونُقيّم.. ولا نُقوّم»
==============================================================================
"""

from typing import Dict, Any, Optional


class ResourcesSystem:
    """Manages closed-system resources: ammunition, water reserves, and respiration loss (LAW-AMMO-01 & LAW-BIO-03)."""

    RESPIRATION_LOSS_L_PER_MIN_PER_PERSON = 0.000667  # 6.02L / (14 * 645 mins)

    @classmethod
    def process_respiration(cls, registry, elapsed_minutes: int):
        """Updates cumulative water loss through cold arid breath exhalation."""
        living_count = sum(1 for c in registry.characters.values() if c["biomechanics"].is_alive)
        total_loss = living_count * cls.RESPIRATION_LOSS_L_PER_MIN_PER_PERSON * elapsed_minutes

        for char in registry.characters.values():
            if char["biomechanics"].is_alive:
                char["biomechanics"].respiration_water_loss_l = round(
                    cls.RESPIRATION_LOSS_L_PER_MIN_PER_PERSON * elapsed_minutes, 3
                )

        return round(total_loss, 3)

    @classmethod
    def discharge_weapon(cls, registry, shooter: str, count: int) -> bool:
        """Expends ammunition from shooter's magazine (LAW-AMMO-01)."""
        ammo = registry.resources["ammo"]
        if shooter not in ammo.distribution or ammo.distribution[shooter] < count:
            return False

        ammo.distribution[shooter] -= count
        ammo.rounds_fired += count
        ammo.rounds_remaining -= count
        return True

    @classmethod
    def consume_water(cls, registry, liters: float) -> bool:
        """Distributes water rations from the 14.0L reservoir."""
        water = registry.resources["water"]
        if water.liters_remaining < liters:
            return False

        water.liters_consumed += liters
        water.liters_remaining = round(water.liters_remaining - liters, 3)
        return True
