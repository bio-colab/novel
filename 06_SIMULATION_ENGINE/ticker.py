#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
EVENT-SOURCED STATE TICKER (محرك النبضات الزمني وسجل الأحداث الحتمي)
Project: «قطار الرمل» (Sand Train) - Narrative Engineering Simulation Engine
Framework Charter: «نحن نُحلل ونُقيّم.. ولا نُقوّم»
==============================================================================
"""

from typing import Dict, List, Any, Optional
try:
    from .registry import EntityRegistry
    from .schemas.events import SimulationEvent
    from .systems.thermodynamics import ThermodynamicSystem
    from .systems.neurology import NeurologySystem
    from .systems.acoustics import AcousticsSystem
    from .systems.resources import ResourcesSystem
    from .systems.moral_entropy import MoralEntropySystem
except (ImportError, ValueError):
    from registry import EntityRegistry
    from schemas.events import SimulationEvent
    from systems.thermodynamics import ThermodynamicSystem
    from systems.neurology import NeurologySystem
    from systems.acoustics import AcousticsSystem
    from systems.resources import ResourcesSystem
    from systems.moral_entropy import MoralEntropySystem


class EventSourcedTicker:
    """Advances simulation minute-by-minute and logs all deterministic transitions."""

    def __init__(self, registry: EntityRegistry):
        self.registry = registry
        self.moral_system = MoralEntropySystem()
        self.events_log: List[SimulationEvent] = []
        self.state_history: Dict[int, Dict[str, Any]] = {}
        self.current_minute: int = 0

    @staticmethod
    def minute_to_clock(minute: int) -> str:
        """Converts timeline minute [0..645] to wall clock string (base 19:00:00)."""
        base_h = 19
        total_m = base_h * 60 + minute
        h = (total_m // 60) % 24
        m = total_m % 60
        return f"{h:02d}:{m:02d}:00"

    def advance_minute(self, minute: int, external_events: Optional[List[Dict[str, Any]]] = None):
        """Executes one simulation step at minute."""
        self.current_minute = minute
        self.registry.timeline_minute = minute
        clock_str = self.minute_to_clock(minute)

        # 1. Physical Systems Execution Order (Thermodynamics -> Neurology -> Resources -> Moral)
        env_state = ThermodynamicSystem.update_environment(self.registry, minute)
        ambient_temp = env_state["ambient_temp_c"]

        ThermodynamicSystem.update_cars(self.registry, ambient_temp, minute)
        ThermodynamicSystem.update_characters(self.registry, ambient_temp, minute)
        NeurologySystem.update(self.registry, minute)
        ResourcesSystem.process_respiration(self.registry, minute)
        solidarity = self.moral_system.update(self.registry, minute)

        # 2. Process any external / narrative events at this exact minute
        if external_events:
            for evt_raw in external_events:
                etype = evt_raw.get("type", "ACTION_ATTEMPT")
                payload = evt_raw.get("payload", {})
                affected = evt_raw.get("affected", [])
                law = evt_raw.get("law")

                # If ballistic event, discharge ammo
                if etype == "BALLISTIC_DISCHARGE":
                    shooter = payload.get("shooter", "عباس")
                    rounds = payload.get("rounds", 1)
                    ResourcesSystem.discharge_weapon(self.registry, shooter, rounds)

                # Log event in event-sourcing ledger
                sim_event = SimulationEvent(
                    event_id=f"EVT-{minute:03d}-{len(self.events_log):03d}",
                    minute=minute,
                    time_clock=clock_str,
                    event_type=etype,
                    payload=payload,
                    affected_entities=affected,
                    law_cited=law
                )
                self.events_log.append(sim_event)

        # 3. Snapshot state at milestone intervals (every 15 minutes or when events occur)
        if minute % 15 == 0 or external_events or minute == 645:
            snap = self.registry.snapshot()
            snap["solidarity_index"] = solidarity
            snap["time_clock"] = clock_str
            self.state_history[minute] = snap

    def run_simulation(self, total_minutes: int = 645, key_events: Optional[Dict[int, List[Dict[str, Any]]]] = None):
        """Runs the entire timeline from minute 0 (19:00:00) to 645 (05:45:00)."""
        key_events = key_events or {}
        for m in range(total_minutes + 1):
            minute_events = key_events.get(m, None)
            self.advance_minute(m, minute_events)
