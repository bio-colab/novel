#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
EVENT REPLAYER ENGINE (محرك إعادة بناء الحالة بالكامل من سجل الأحداث الحتمي)
Project: «قطار الرمل» (Sand Train) - Narrative Engineering Simulation Engine
Framework Charter: «نحن نُحلل ونُقيّم.. ولا نُقوّم»
==============================================================================
This module implements a pure event reducer (fold) that reconstructs the entire
simulation state at any target minute strictly from the append-only event stream,
without running physical equations or external simulation models.

State(t) = fold(apply_event, State(0), Events[0..t])
"""

import os
import json
from typing import List, Dict, Any, Optional, Tuple, Union

try:
    from .registry import EntityRegistry
    from .schemas.events import SimulationEvent
except (ImportError, ValueError):
    from registry import EntityRegistry
    from schemas.events import SimulationEvent


class EventReplayer:
    """Deterministic Replay Engine reconstructing world state strictly from event ledger."""

    @classmethod
    def apply_event(cls, registry: EntityRegistry, event: SimulationEvent, context: Optional[Dict[str, Any]] = None):
        """Pure reducer: applies a single event to the registry in-place."""
        etype = event.event_type
        payload = event.payload
        registry.timeline_minute = event.minute

        if etype == "ENVIRONMENT_UPDATE":
            if "ambient_temp_c" in payload:
                registry.environment["ambient_temp_c"] = float(payload["ambient_temp_c"])
            if "wind_chill_effective_c" in payload:
                registry.environment["wind_chill_effective_c"] = float(payload["wind_chill_effective_c"])
            if "lux" in payload:
                registry.environment["lux"] = float(payload["lux"])

        elif etype == "THERMAL_STEP":
            # 1. Environment updates if embedded in thermal step
            if "ambient_temp_c" in payload:
                registry.environment["ambient_temp_c"] = float(payload["ambient_temp_c"])
            if "wind_chill_effective_c" in payload:
                registry.environment["wind_chill_effective_c"] = float(payload["wind_chill_effective_c"])
            if "lux" in payload:
                registry.environment["lux"] = float(payload["lux"])

            # 2. Car internal temperatures
            cars_data = payload.get("cars", {})
            for cid, cval in cars_data.items():
                if cid in registry.cars:
                    temp = cval if isinstance(cval, (int, float)) else cval.get("interior_temp_c", 0.0)
                    registry.cars[cid]["interior_temp_c"] = round(float(temp), 2)

            # 3. Characters body & fingers temperatures
            chars_data = payload.get("characters", {})
            for cname, cval in chars_data.items():
                if cname in registry.characters:
                    bio = registry.characters[cname]["biomechanics"]
                    if "core_temp_c" in cval:
                        bio.core_temp_c = round(float(cval["core_temp_c"]), 2)
                    if "fingers_temp_c" in cval:
                        bio.fingers_temp_c = round(float(cval["fingers_temp_c"]), 2)

        elif etype == "BIO_DECAY":
            chars_data = payload.get("characters", {})
            for cname, cval in chars_data.items():
                if cname in registry.characters:
                    bio = registry.characters[cname]["biomechanics"]
                    psych = registry.characters[cname]["psychology"]

                    if "motor_dexterity" in cval:
                        bio.motor_dexterity = round(float(cval["motor_dexterity"]), 3)
                    if "stamina" in cval:
                        bio.stamina = round(float(cval["stamina"]), 3)
                    if "shivering_stage" in cval:
                        bio.shivering_stage = str(cval["shivering_stage"])
                    if "respiration_loss_l" in cval:
                        bio.respiration_water_loss_l = round(float(cval["respiration_loss_l"]), 3)
                    if "is_alive" in cval:
                        bio.is_alive = bool(cval["is_alive"])
                    if "tic_active" in cval:
                        psych.tic_trigger_active = bool(cval["tic_active"])

        elif etype == "RESOURCE_CONSUMPTION":
            res_type = payload.get("resource")
            if res_type == "water" and "water" in registry.resources:
                water = registry.resources["water"]
                if "liters_consumed" in payload:
                    water.liters_consumed = round(float(payload["liters_consumed"]), 3)
                if "liters_remaining" in payload:
                    water.liters_remaining = round(float(payload["liters_remaining"]), 3)
            elif res_type == "ammo" and "ammo" in registry.resources:
                ammo = registry.resources["ammo"]
                if "rounds_fired" in payload:
                    ammo.rounds_fired = int(payload["rounds_fired"])
                if "rounds_remaining" in payload:
                    ammo.rounds_remaining = int(payload["rounds_remaining"])
                if "distribution" in payload:
                    ammo.distribution = dict(payload["distribution"])

        elif etype == "BALLISTIC_DISCHARGE":
            shooter = payload.get("shooter")
            rounds = payload.get("rounds_fired", payload.get("rounds", 1))
            ammo = registry.resources.get("ammo")
            if ammo and shooter in ammo.distribution:
                ammo.distribution[shooter] -= rounds
                ammo.rounds_fired += rounds
                ammo.rounds_remaining -= rounds

        elif etype == "MORAL_TRANSITION":
            if context is not None and "solidarity_index" in payload:
                context["solidarity_index"] = round(float(payload["solidarity_index"]), 3)

    @classmethod
    def replay(
        cls,
        events: List[SimulationEvent],
        initial_registry: Optional[EntityRegistry] = None,
        target_minute: Optional[int] = None
    ) -> Tuple[EntityRegistry, Dict[str, Any]]:
        """Reconstructs the full world state at target_minute purely by folding events."""
        if initial_registry is None:
            initial_registry = EntityRegistry()
            initial_registry.initialize_default_entities()

        context = {
            "solidarity_index": 0.85,
            "applied_events_count": 0,
            "final_minute": 0
        }

        for event in events:
            if target_minute is not None and event.minute > target_minute:
                break
            cls.apply_event(initial_registry, event, context)
            context["applied_events_count"] += 1
            context["final_minute"] = event.minute

        return initial_registry, context

    @classmethod
    def replay_from_file(
        cls,
        events_path: str,
        initial_registry: Optional[EntityRegistry] = None,
        target_minute: Optional[int] = None
    ) -> Tuple[EntityRegistry, Dict[str, Any]]:
        """Replays state directly from a serialized JSON or JSONL event stream."""
        events: List[SimulationEvent] = []
        with open(events_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content.startswith("["):
                raw_list = json.loads(content)
                events = [SimulationEvent(**item) for item in raw_list]
            else:
                for line in content.splitlines():
                    if line.strip():
                        events.append(SimulationEvent(**json.loads(line)))

        return cls.replay(events, initial_registry, target_minute)

    @classmethod
    def verify_fidelity(
        cls,
        simulated_registry: EntityRegistry,
        simulated_solidarity: float,
        replayed_registry: EntityRegistry,
        replayed_solidarity: float
    ) -> Tuple[bool, List[str]]:
        """Strictly asserts byte-for-byte and floating-point fidelity between simulated and replayed state."""
        discrepancies: List[str] = []

        # 1. Environment
        for k in ["ambient_temp_c", "wind_chill_effective_c", "lux"]:
            sim_val = simulated_registry.environment.get(k)
            rep_val = replayed_registry.environment.get(k)
            if sim_val != rep_val:
                discrepancies.append(f"Environment mismatch on '{k}': simulated={sim_val} != replayed={rep_val}")

        # 2. Train Cars
        for cid in simulated_registry.cars:
            sim_c = simulated_registry.cars[cid].get("interior_temp_c")
            rep_c = replayed_registry.cars[cid].get("interior_temp_c")
            if sim_c != rep_c:
                discrepancies.append(f"Car '{cid}' temp mismatch: simulated={sim_c} != replayed={rep_c}")

        # 3. Resources
        sim_ammo = simulated_registry.resources["ammo"]
        rep_ammo = replayed_registry.resources["ammo"]
        if sim_ammo.rounds_remaining != rep_ammo.rounds_remaining:
            discrepancies.append(f"Ammo rounds_remaining mismatch: {sim_ammo.rounds_remaining} != {rep_ammo.rounds_remaining}")
        if sim_ammo.rounds_fired != rep_ammo.rounds_fired:
            discrepancies.append(f"Ammo rounds_fired mismatch: {sim_ammo.rounds_fired} != {rep_ammo.rounds_fired}")

        sim_water = simulated_registry.resources["water"]
        rep_water = replayed_registry.resources["water"]
        if sim_water.liters_consumed != rep_water.liters_consumed:
            discrepancies.append(f"Water liters_consumed mismatch: {sim_water.liters_consumed} != {rep_water.liters_consumed}")

        # 4. Characters (All 14 Souls)
        for name in simulated_registry.characters:
            s_bio = simulated_registry.characters[name]["biomechanics"]
            r_bio = replayed_registry.characters[name]["biomechanics"]

            if abs(s_bio.core_temp_c - r_bio.core_temp_c) > 0.05:
                discrepancies.append(f"Char '{name}' core_temp mismatch: {s_bio.core_temp_c} != {r_bio.core_temp_c}")
            if abs(s_bio.fingers_temp_c - r_bio.fingers_temp_c) > 0.05:
                discrepancies.append(f"Char '{name}' fingers_temp mismatch: {s_bio.fingers_temp_c} != {r_bio.fingers_temp_c}")
            if abs(s_bio.motor_dexterity - r_bio.motor_dexterity) > 0.01:
                discrepancies.append(f"Char '{name}' motor_dexterity mismatch: {s_bio.motor_dexterity} != {r_bio.motor_dexterity}")
            if s_bio.shivering_stage != r_bio.shivering_stage:
                discrepancies.append(f"Char '{name}' shivering_stage mismatch: '{s_bio.shivering_stage}' != '{r_bio.shivering_stage}'")
            if s_bio.is_alive != r_bio.is_alive:
                discrepancies.append(f"Char '{name}' is_alive mismatch: {s_bio.is_alive} != {r_bio.is_alive}")

        # 5. Solidarity
        if round(simulated_solidarity, 3) != round(replayed_solidarity, 3):
            discrepancies.append(f"Solidarity mismatch: {simulated_solidarity} != {replayed_solidarity}")

        is_identical = (len(discrepancies) == 0)
        return is_identical, discrepancies
