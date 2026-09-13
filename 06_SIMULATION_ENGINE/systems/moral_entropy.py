#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
MORAL ENTROPY SYSTEM (نظام الإنتروبيا الأخلاقية والتضامن الوجودي)
Project: «قطار الرمل» (Sand Train) - Narrative Engineering Simulation Engine
Framework Charter: «نحن نُحلل ونُقيّم.. ولا نُقوّم»
==============================================================================
"""

import math
from typing import Dict, Any, List


class MoralEntropySystem:
    """Computes existential solidarity dynamics and causal debt conservation (LAW-ETHIC-01..03)."""

    def __init__(self):
        self.solidarity_index: float = 0.85
        self.active_causal_debts: List[Dict[str, Any]] = []
        self.funerary_dignity_preserved: bool = True

    def update(self, registry, minute: int) -> float:
        """Calculates current solidarity index S(t) across timeline [0..645]."""
        hours = minute / 60.0

        # Baseline moral entropy decay due to cold torpor and biological exhaustion
        # S(t) decreases during cold night, but rebounds during collective solidarity events
        base_s = max(0.30, 0.85 - (0.07 * (hours ** 0.95)))

        # Rebound events based on canonical timeline milestones:
        # At minute 420 (Aziz song / Mawwal), solidarity rebounds (+0.18)
        if minute >= 420:
            base_s = min(1.0, base_s + 0.18)
        # At minute 570 (Repairing fuel line under chassis together), solidarity rises (+0.12)
        if minute >= 570:
            base_s = min(1.0, base_s + 0.12)

        self.solidarity_index = round(base_s, 3)
        return self.solidarity_index

    def log_causal_debt(self, debtor: str, creditor: str, action: str, minute: int):
        """Records a causal/existential debt between characters (LAW-ETHIC-02)."""
        self.active_causal_debts.append({
            "debtor": debtor,
            "creditor": creditor,
            "action": action,
            "minute": minute,
            "settled": False
        })
