#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
EVENTS SCHEMA (مخطط الأحداث والنبضات الزمنية الصارم)
Project: «قطار الرمل» (Sand Train) - Narrative Engineering Simulation Engine
Framework Charter: «نحن نُحلل ونُقيّم.. ولا نُقوّم»
==============================================================================
"""

from typing import Dict, List, Any, Literal, Optional
from pydantic import BaseModel, Field


class SimulationEvent(BaseModel):
    """Immutable discrete event in the simulation event-sourcing ledger."""
    event_id: str = Field(..., description="Unique event identifier (e.g. EVT-015-THERMAL)")
    minute: int = Field(..., ge=0, le=646, description="Timeline minute relative to t0=19:00 [0..645]")
    time_clock: str = Field(..., description="Wall clock time (e.g. '19:15:00', '05:45:00')")
    event_type: Literal[
        "THERMAL_STEP",
        "BALLISTIC_DISCHARGE",
        "ACOUSTIC_EMISSION",
        "BIO_DECAY",
        "ACTION_ATTEMPT",
        "MORAL_CHOICE",
        "RESOURCE_CONSUMPTION",
        "ENVIRONMENT_UPDATE",
        "MORAL_TRANSITION"
    ] = Field(..., description="Categorical event type")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Event-specific physics/narrative parameters")
    affected_entities: List[str] = Field(default_factory=list, description="IDs of affected characters or cars")
    law_cited: Optional[str] = Field(None, description="Physical law governing the event (e.g. LAW-THERMO-01)")


class BallisticEventPayload(BaseModel):
    """Specific payload for weapon firing events (LAW-AMMO-01)."""
    shooter: str = Field(..., description="Name of shooter")
    rounds_fired: int = Field(1, ge=1, le=30, description="Rounds expended in burst/shot")
    caliber: Literal["7.62x39mm"] = Field("7.62x39mm", description="Strict physical caliber")
    weapon_jammed: bool = Field(False, description="Did weapon suffer stoppage")
    target_zone: str = Field(..., description="Target direction or coordinate")


class AcousticEventPayload(BaseModel):
    """Specific payload for sound emissions and inter-car attenuation (LAW-ACOUST-03)."""
    origin_car: str = Field(..., description="Originating car ID (e.g. car_01, exterior)")
    sound_type: str = Field(..., description="Nature of acoustic emission (e.g. gunshot, scream, engine_crank)")
    source_spl_db: float = Field(..., ge=0.0, le=180.0, description="Sound pressure level at source in dB")
    attenuation_intercar_db: float = Field(35.0, ge=30.0, description="Inter-car transmission loss (>35 dB)")
