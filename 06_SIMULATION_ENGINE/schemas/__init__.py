#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Schemas module for Sand Train Simulation Engine.
"""

try:
    from .biostate import BiostateModel
    from .resources import AmmoPoolModel, WaterReserveModel, FuelLineModel
    from .events import SimulationEvent, BallisticEventPayload, AcousticEventPayload
    from .validation import validate_law_compliance, assert_law_compliance, LawViolationError
    from .entity import EntityModel, EntityCategory
except (ImportError, ValueError):
    from schemas.biostate import BiostateModel
    from schemas.resources import AmmoPoolModel, WaterReserveModel, FuelLineModel
    from schemas.events import SimulationEvent, BallisticEventPayload, AcousticEventPayload
    from schemas.validation import validate_law_compliance, assert_law_compliance, LawViolationError
    from schemas.entity import EntityModel, EntityCategory

__all__ = [
    "BiostateModel",
    "AmmoPoolModel",
    "WaterReserveModel",
    "FuelLineModel",
    "SimulationEvent",
    "BallisticEventPayload",
    "AcousticEventPayload",
    "validate_law_compliance",
    "assert_law_compliance",
    "LawViolationError",
    "EntityModel",
    "EntityCategory"
]
