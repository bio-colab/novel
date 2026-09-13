#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
NEUROLOGY & BIOMECHANICS SYSTEM (نظام الأعصاب والحركة الحتمي)
Project: «قطار الرمل» (Sand Train) - Narrative Engineering Simulation Engine
Framework Charter: «نحن نُحلل ونُقيّم.. ولا نُقوّم»
==============================================================================
"""

import math
from typing import Dict, Any


class NeurologySystem:
    """Computes fine motor dexterity, shivering exhaustion, and tic triggers (LAW-BIO-01, 02, 04)."""

    @staticmethod
    def update(registry, minute: int):
        """Updates all living characters' neurological, motor, and stress parameters."""
        for name, char in registry.characters.items():
            bio = char["biomechanics"]
            psych = char["psychology"]

            if not bio.is_alive:
                bio.motor_dexterity = 0.0
                bio.shivering_stage = "hypothermic_torpor"
                continue

            # 1. Fine Motor Dexterity vs Finger Temperature (LAW-BIO-01)
            # Sigmoid / linear transition between 20°C and 0°C
            tf = bio.fingers_temp_c
            if tf >= 20.0:
                dexterity = 0.90 + (0.10 * (tf - 20.0) / 4.5)
            elif tf >= 10.0:
                dexterity = 0.50 + (0.40 * (tf - 10.0) / 10.0)
            elif tf > 2.0:
                dexterity = 0.15 + (0.35 * (tf - 2.0) / 8.0)
            else:
                dexterity = max(0.02, 0.05 + (0.10 * max(0.0, tf) / 2.0))

            bio.motor_dexterity = round(min(1.0, max(0.0, dexterity)), 3)

            # 2. Stamina Depletion
            stamina_burn = 0.0008 + (0.0005 if bio.core_temp_c < 35.0 else 0.0)
            bio.stamina = round(max(0.10, 1.0 - (stamina_burn * minute)), 3)

            # 3. Shivering Progression (LAW-BIO-04)
            tc = bio.core_temp_c
            if tc > 36.2:
                bio.shivering_stage = "none"
            elif tc >= 35.0:
                bio.shivering_stage = "moderate_shivering"
            elif tc >= 33.5:
                if bio.stamina < 0.35 or minute >= 420:
                    bio.shivering_stage = "shivering_exhaustion"
                else:
                    bio.shivering_stage = "violent_shivering"
            elif tc >= 31.0:
                bio.shivering_stage = "shivering_exhaustion"
            else:
                bio.shivering_stage = "hypothermic_torpor"

            # 4. Neurotic Motor Tic Triggering (LAW-BIO-02)
            # Tics activate under cold shivering, psychological panic, or mechanical stress
            if psych.panic_index > 0.40 or bio.shivering_stage in ["moderate_shivering", "violent_shivering"]:
                psych.tic_trigger_active = True
            else:
                psych.tic_trigger_active = False
