#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
BIOSTATE SCHEMA (مخطط الحالة البيولوجية والحركية الصارم)
Project: «قطار الرمل» (Sand Train) - Narrative Engineering Simulation Engine
Framework Charter: «نحن نُحلل ونُقيّم.. ولا نُقوّم»
==============================================================================
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator


class BiostateModel(BaseModel):
    """Deterministic biological and motor state for characters during simulation."""
    character_name: str = Field(..., description="Canonical character name (e.g. خالد, أبو_علي)")
    core_temp_c: float = Field(36.8, ge=24.0, le=38.5, description="Core body temperature in Celsius")
    fingers_temp_c: float = Field(24.5, ge=-10.0, le=37.0, description="Extremity / finger temperature in Celsius")
    motor_dexterity: float = Field(1.0, ge=0.0, le=1.0, description="Fine motor dexterity index [0.0 = total paralysis, 1.0 = optimal]")
    shivering_stage: Literal[
        "none",
        "moderate_shivering",
        "violent_shivering",
        "shivering_exhaustion",
        "hypothermic_torpor"
    ] = Field("none", description="Biomechanical shivering phase per LAW-BIO-04")
    dehydration_loss_liters: float = Field(0.0, ge=0.0, le=10.0, description="Cumulative water loss via respiration per LAW-BIO-03")
    stamina: float = Field(1.0, ge=0.0, le=1.0, description="Physical endurance and reserve energy [0.0..1.0]")
    active_tic: Optional[str] = Field(None, description="Active motor tic triggered by stress/cold (LAW-BIO-02)")
    is_alive: bool = Field(True, description="Biological vitality status")

    @field_validator("motor_dexterity")
    @classmethod
    def validate_motor_temp_consistency(cls, v: float, info) -> float:
        """Ensures fine motor dexterity collapses when fingers freeze (< 4°C)."""
        fingers_temp = info.data.get("fingers_temp_c")
        if fingers_temp is not None and fingers_temp <= 2.0 and v > 0.35:
            raise ValueError(f"Motor dexterity {v} is physically impossible with frozen fingers at {fingers_temp}°C (LAW-BIO-01/04)")
        return v
