#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
LAW COMPLIANCE VALIDATION GATEWAY (بوابة التحقق الدستوري للقوانين الفيزيائية)
Project: «قطار الرمل» (Sand Train) - Narrative Engineering Simulation Engine
Framework Charter: «نحن نُحلل ونُقيّم.. ولا نُقوّم»
==============================================================================
"""

from typing import Any, Tuple, List
from pydantic import BaseModel
try:
    from .biostate import BiostateModel
    from .resources import AmmoPoolModel, WaterReserveModel, FuelLineModel
    from .events import SimulationEvent, BallisticEventPayload, AcousticEventPayload
except (ImportError, ValueError):
    from schemas.biostate import BiostateModel
    from schemas.resources import AmmoPoolModel, WaterReserveModel, FuelLineModel
    from schemas.events import SimulationEvent, BallisticEventPayload, AcousticEventPayload


class LawViolationError(ValueError):
    """Raised when a simulation entity or event violates a constitutional physical law."""
    pass


def validate_law_compliance(model_or_payload: Any) -> Tuple[bool, List[str]]:
    """
    Examines an instance against PHYSICAL_LAWS.md statutory invariants.
    Returns (is_compliant, list_of_violations).
    """
    violations = []

    # 1. Biostate & Biomechanics Validation (LAW-BIO-01, LAW-BIO-04)
    if isinstance(model_or_payload, BiostateModel):
        bio: BiostateModel = model_or_payload
        if bio.is_alive and bio.core_temp_c < 28.0:
            violations.append(
                f"[LAW-BIO-04 VIOLATION]: Core temp {bio.core_temp_c}°C is below lethal hypothermic torpor threshold (28.0°C)"
            )
        if bio.fingers_temp_c <= 0.0 and bio.motor_dexterity > 0.10:
            violations.append(
                f"[LAW-BIO-01 VIOLATION]: Motor dexterity {bio.motor_dexterity} is physically impossible with frozen fingers at {bio.fingers_temp_c}°C"
            )
        if bio.shivering_stage == "shivering_exhaustion" and bio.stamina > 0.40:
            violations.append(
                f"[LAW-BIO-04 VIOLATION]: Shivering exhaustion requires depleted stamina (<= 0.40), found {bio.stamina}"
            )

    # 2. Ammunition Validation (LAW-AMMO-01)
    elif isinstance(model_or_payload, AmmoPoolModel):
        ammo: AmmoPoolModel = model_or_payload
        if ammo.caliber != "7.62x39mm":
            violations.append(
                f"[LAW-AMMO-01 VIOLATION]: Invalid cartridge caliber '{ammo.caliber}'. Only 7.62x39mm is physically available."
            )
        if ammo.rounds_fired + ammo.rounds_remaining != ammo.total_initial_rounds:
            violations.append(
                f"[LAW-AMMO-01 VIOLATION]: Non-conservation of rounds: {ammo.rounds_fired} + {ammo.rounds_remaining} != {ammo.total_initial_rounds}"
            )

    # 3. Water Reserve Validation (LAW-BIO-03)
    elif isinstance(model_or_payload, WaterReserveModel):
        water: WaterReserveModel = model_or_payload
        if water.canonical_car != "car_01":
            violations.append(
                f"[WORLD-BUG-010 / TOPOLOGY VIOLATION]: Water barrel location must be 'car_01', got '{water.canonical_car}'"
            )
        if water.liters_remaining < 0.0:
            violations.append(
                f"[LAW-BIO-03 VIOLATION]: Water reservoir cannot drop below 0.0L, found {water.liters_remaining}L"
            )

    # 4. Fuel Line Validation (LAW-THERMO-01 & WORLD-BUG-009)
    elif isinstance(model_or_payload, FuelLineModel):
        fuel: FuelLineModel = model_or_payload
        if fuel.is_breached and fuel.line_pressure_bar > 0.1:
            violations.append(
                f"[LAW-THERMO-01 VIOLATION]: Ruptured fuel line cannot maintain positive pressure ({fuel.line_pressure_bar} bar)"
            )

    # 5. Ballistic Event Validation
    elif isinstance(model_or_payload, BallisticEventPayload):
        bal: BallisticEventPayload = model_or_payload
        if bal.caliber != "7.62x39mm":
            violations.append(
                f"[LAW-AMMO-01 VIOLATION]: Expended round caliber must be 7.62x39mm, found '{bal.caliber}'"
            )

    # 6. Acoustic Event Validation (LAW-ACOUST-03)
    elif isinstance(model_or_payload, AcousticEventPayload):
        ac: AcousticEventPayload = model_or_payload
        if ac.attenuation_intercar_db < 35.0:
            violations.append(
                f"[LAW-ACOUST-03 VIOLATION]: Inter-car transmission attenuation must be >= 35.0 dB, found {ac.attenuation_intercar_db} dB"
            )

    is_compliant = len(violations) == 0
    return is_compliant, violations


def assert_law_compliance(model_or_payload: Any) -> None:
    """Raises LawViolationError if the model or payload violates physical invariants."""
    is_compliant, violations = validate_law_compliance(model_or_payload)
    if not is_compliant:
        raise LawViolationError(" | ".join(violations))
