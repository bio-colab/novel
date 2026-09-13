#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
ENTITY REGISTRY (سجل الكيانات المركزي لإدارة عالم المحاكاة)
Project: «قطار الرمل» (Sand Train) - Narrative Engineering Simulation Engine
Framework Charter: «نحن نُحلل ونُقيّم.. ولا نُقوّم»
==============================================================================
"""

import os
import yaml
from typing import Dict, Any, Optional, List
try:
    from .components import (
        PositionComponent,
        ThermodynamicComponent,
        BiomechanicalComponent,
        PsychologicalComponent,
        EpistemicComponent
    )
    from .schemas.resources import AmmoPoolModel, WaterReserveModel, FuelLineModel
except (ImportError, ValueError):
    from components import (
        PositionComponent,
        ThermodynamicComponent,
        BiomechanicalComponent,
        PsychologicalComponent,
        EpistemicComponent
    )
    from schemas.resources import AmmoPoolModel, WaterReserveModel, FuelLineModel


class EntityRegistry:
    """Central registry tracking characters, cars, environment and resources."""

    def __init__(self):
        self.characters: Dict[str, Dict[str, Any]] = {}
        self.cars: Dict[str, Dict[str, Any]] = {}
        self.resources: Dict[str, Any] = {}
        self.environment: Dict[str, Any] = {}
        self.timeline_minute: int = 0

    def initialize_default_entities(self, world_state_path: Optional[str] = None):
        """Loads canonical baseline entities from world_state.yaml."""
        if not world_state_path:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            world_state_path = os.path.join(base_dir, "05_WORLD_BRAIN", "world_state.yaml")

        with open(world_state_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        # 1. Environment initialization
        env_raw = data.get("environment", {})
        self.environment = {
            "ambient_temp_c": env_raw.get("ambient_temperature_c", 0.0),
            "wind_speed_kmh": env_raw.get("wind", {}).get("speed_kmh", 38.0),
            "wind_chill_effective_c": env_raw.get("wind", {}).get("wind_chill_effective_c", -5.4),
            "lux": env_raw.get("illumination_lux", 0.8)
        }

        # 2. Car geometry and internal conditions
        cars_raw = data.get("train", {}).get("cars", {})
        for cid, cinfo in cars_raw.items():
            self.cars[cid] = {
                "id": cinfo.get("id", cid),
                "name": cinfo.get("name", cid),
                "interior_temp_c": cinfo.get("interior_temp_c", 4.0),
                "interior_lux": cinfo.get("interior_lux", 10.0),
                "length_m": cinfo.get("length_m", 12.0),
                "y_start_m": cinfo.get("y_start_m", 0.0),
                "y_end_m": cinfo.get("y_end_m", 12.0)
            }

        # 3. Resources initialization
        self.resources["ammo"] = AmmoPoolModel(
            total_initial_rounds=118,
            rounds_fired=0,
            rounds_remaining=118,
            distribution={"عباس": 27, "خالد": 28, "حناطة": 28, "مخزن_طوارئ": 35}
        )
        self.resources["water"] = WaterReserveModel(
            total_initial_liters=14.0,
            liters_consumed=0.0,
            liters_remaining=14.0,
            canonical_car="car_01"
        )
        self.resources["fuel_line"] = FuelLineModel(
            line_pressure_bar=0.0,
            is_breached=True,
            breach_cause="thermal_contraction_crack",
            airlock_present=True
        )

        # 4. Characters initialization (14 canonical souls)
        chars_raw = data.get("characters", {})
        for cname, cdata in chars_raw.items():
            loc = cdata.get("location", "car_01_guard")
            coords = cdata.get("coordinates", {"x_m": 1.0, "y_m": 20.0})
            phys = cdata.get("physical", {})
            psych = cdata.get("psychological", {})
            tic = cdata.get("active_tic", {})
            epistemic = cdata.get("epistemic_bubble", {})

            self.characters[cname] = {
                "name": cname,
                "role": cdata.get("role", "راكب"),
                "position": PositionComponent(
                    car_id=loc,
                    x_m=float(coords.get("x_m", 1.0)),
                    y_m=float(coords.get("y_m", 20.0))
                ),
                "thermodynamics": ThermodynamicComponent(),
                "biomechanics": BiomechanicalComponent(
                    core_temp_c=float(phys.get("core_temp_c", 36.8)),
                    fingers_temp_c=float(phys.get("fingers_temp_c", 24.5)),
                    motor_dexterity=float(phys.get("motor_dexterity", 1.0)),
                    stamina=float(phys.get("stamina", 1.0))
                ),
                "psychology": PsychologicalComponent(
                    stress_level=float(psych.get("stress_level", 0.5)),
                    panic_index=float(psych.get("panic_index", 0.1)),
                    authority_weight=float(psych.get("authority_weight", 0.5)),
                    tic_name=tic.get("name") if isinstance(tic, dict) else None,
                    tic_trigger_active=bool(tic.get("active_now", False)) if isinstance(tic, dict) else False
                ),
                "epistemic": EpistemicComponent(
                    known_facts=epistemic.get("known_truths", []),
                    blind_spots=epistemic.get("blind_spots", [])
                )
            }

    def get_character(self, name: str) -> Optional[Dict[str, Any]]:
        return self.characters.get(name)

    def snapshot(self) -> Dict[str, Any]:
        """Creates a serializable snapshot of the current world state."""
        return {
            "minute": self.timeline_minute,
            "environment": dict(self.environment),
            "cars": {k: dict(v) for k, v in self.cars.items()},
            "resources": {
                "ammo": self.resources["ammo"].model_dump(),
                "water": self.resources["water"].model_dump(),
                "fuel_line": self.resources["fuel_line"].model_dump()
            },
            "characters": {
                name: {
                    "core_temp_c": c["biomechanics"].core_temp_c,
                    "fingers_temp_c": c["biomechanics"].fingers_temp_c,
                    "motor_dexterity": c["biomechanics"].motor_dexterity,
                    "shivering_stage": c["biomechanics"].shivering_stage,
                    "stamina": c["biomechanics"].stamina,
                    "is_alive": c["biomechanics"].is_alive
                }
                for name, c in self.characters.items()
            },
            "characters_count": len(self.characters),
            "living_characters": [
                name for name, c in self.characters.items()
                if c["biomechanics"].is_alive
            ]
        }
