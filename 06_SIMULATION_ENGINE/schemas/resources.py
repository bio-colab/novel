#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
RESOURCES SCHEMA (مخطط الموارد والذخيرة الصارم)
Project: «قطار الرمل» (Sand Train) - Narrative Engineering Simulation Engine
Framework Charter: «نحن نُحلل ونُقيّم.. ولا نُقوّم»
==============================================================================
"""

from typing import Dict, Literal
from pydantic import BaseModel, Field, field_validator, model_validator


class AmmoPoolModel(BaseModel):
    """Deterministic closed-system ammunition pool (LAW-AMMO-01)."""
    caliber: Literal["7.62x39mm"] = Field(
        "7.62x39mm",
        description="Strict physical cartridge caliber per LAW-AMMO-01"
    )
    total_initial_rounds: int = Field(118, ge=0, description="Total ammunition count across all magazines")
    rounds_fired: int = Field(0, ge=0, description="Total expended rounds")
    rounds_remaining: int = Field(118, ge=0, description="Current unfired ammunition reserve")
    distribution: Dict[str, int] = Field(
        default_factory=lambda: {
            "عباس": 27,
            "خالد": 28,
            "حناطة": 28,
            "مخزن_طوارئ": 35
        },
        description="Individual magazine allocations"
    )

    @model_validator(mode="after")
    def verify_conservation_of_rounds(self):
        """Ensures conservation of mass/ammunition: initial == remaining + fired."""
        if self.rounds_fired + self.rounds_remaining != self.total_initial_rounds:
            raise ValueError(
                f"Ammunition conservation violated: {self.rounds_fired} fired + "
                f"{self.rounds_remaining} remaining != {self.total_initial_rounds} total"
            )
        dist_sum = sum(self.distribution.values())
        if dist_sum != self.rounds_remaining:
            raise ValueError(
                f"Distribution sum ({dist_sum}) does not match remaining rounds ({self.rounds_remaining})"
            )
        return self


class WaterReserveModel(BaseModel):
    """Deterministic closed-system water reserve (LAW-BIO-03)."""
    total_initial_liters: float = Field(14.0, ge=0.0, description="Total water reserve volume")
    liters_consumed: float = Field(0.0, ge=0.0, description="Liters drunk by passengers")
    liters_remaining: float = Field(14.0, ge=0.0, description="Current volume in barrel")
    container_type: str = Field("blue_plastic_barrel", description="Semiotic blue plastic container")
    canonical_car: Literal["car_01"] = Field("car_01", description="Canonical location per WORLD-BUG-010")

    @model_validator(mode="after")
    def verify_water_conservation(self):
        """Verifies initial == remaining + consumed."""
        if round(self.liters_consumed + self.liters_remaining, 3) != round(self.total_initial_liters, 3):
            raise ValueError(
                f"Water conservation violated: {self.liters_consumed} consumed + "
                f"{self.liters_remaining} remaining != {self.total_initial_liters}"
            )
        return self


class FuelLineModel(BaseModel):
    """Locomotive diesel fuel line mechanical state (LAW-THERMO-01 & WORLD-BUG-009)."""
    line_pressure_bar: float = Field(0.0, ge=0.0, le=10.0, description="Diesel feed pressure")
    is_breached: bool = Field(True, description="Physical rupture state")
    breach_cause: Literal["thermal_contraction_crack", "shrapnel_cut"] = Field(
        "thermal_contraction_crack",
        description="Physical cause of line failure"
    )
    airlock_present: bool = Field(True, description="Air bubble block preventing restart")
    pipe_diameter_mm: float = Field(12.0, ge=5.0, le=30.0, description="Fuel line outer diameter")
