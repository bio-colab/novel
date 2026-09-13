#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
SIMULATION RUNNER (المشغل المركزي لمحاكي التوأم الرقمي للرواية)
Project: «قطار الرمل» (Sand Train) - Narrative Engineering Simulation Engine
Framework Charter: «نحن نُحلل ونُقيّم.. ولا نُقوّم»
==============================================================================
"""

import os
import sys
import json
import yaml
import time
from typing import Dict, Any

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

SIM_DIR = os.path.abspath(os.path.dirname(__file__))
if SIM_DIR not in sys.path:
    sys.path.insert(0, SIM_DIR)

try:
    from .registry import EntityRegistry
    from .ticker import EventSourcedTicker
    from .constraints import NarrativeConstraintGenerator
    from .schemas.validation import validate_law_compliance
    from .replayer import EventReplayer
except ImportError:
    from registry import EntityRegistry
    from ticker import EventSourcedTicker
    from constraints import NarrativeConstraintGenerator
    from schemas.validation import validate_law_compliance
    from replayer import EventReplayer


class SimulationRunner:
    """Orchestrates end-to-end event-sourced simulation of the novel."""

    def __init__(self):
        self.registry = EntityRegistry()
        self.ticker = EventSourcedTicker(self.registry)
        self.output_dir = os.path.join(os.path.dirname(__file__), "output")

    def setup(self):
        """Initializes entities from world_state.yaml."""
        self.registry.initialize_default_entities()

    def run(self) -> int:
        """Executes full 645-minute simulation with canonical narrative events."""
        t0 = time.time()
        print("━" * 80)
        print("  SAND TRAIN: EVENT-SOURCED CHRONO-SIMULATION ENGINE (v1.0)")
        print("  ميثاق المنظومة: «نحن نُحلل ونُقيّم.. ولا نُقوّم»")
        print("━" * 80)

        self.setup()

        # Define canonical narrative events across the timeline
        key_events = {
            15: [
                {
                    "type": "ACTION_ATTEMPT",
                    "payload": {"character": "أبو_علي", "action": "تفتيش الصمامات"},
                    "affected": ["أبو_علي", "locomotive"],
                    "law": "LAW-THERMO-01"
                }
            ],
            315: [
                {
                    "type": "BALLISTIC_DISCHARGE",
                    "payload": {"shooter": "عباس", "rounds": 3, "caliber": "7.62x39mm"},
                    "affected": ["عباس", "car_01_guard"],
                    "law": "LAW-AMMO-01"
                },
                {
                    "type": "ACOUSTIC_EMISSION",
                    "payload": {"origin_car": "car_01_guard", "sound_type": "gunfire", "source_spl_db": 150.0},
                    "affected": ["car_01_guard", "car_02_prisoners"],
                    "law": "LAW-ACOUST-03"
                }
            ],
            420: [
                {
                    "type": "MORAL_CHOICE",
                    "payload": {"character": "عزيز", "action": "غناء الموال لكسر وحشة الموت"},
                    "affected": ["عزيز", "car_02_prisoners"],
                    "law": "LAW-ETHIC-01"
                }
            ],
            570: [
                {
                    "type": "ACTION_ATTEMPT",
                    "payload": {"character": "سردار", "action": "شد سلك الحديد حول الأنبوب"},
                    "affected": ["سردار", "أبو_علي", "locomotive"],
                    "law": "LAW-BIO-01"
                }
            ],
            645: [
                {
                    "type": "ACTION_ATTEMPT",
                    "payload": {"character": "أبو_علي", "action": "سحب ذراع مضخة التحضير"},
                    "affected": ["أبو_علي", "locomotive"],
                    "law": "LAW-SPATIAL-01"
                }
            ]
        }

        # Run 645-minute ticker
        self.ticker.run_simulation(total_minutes=645, key_events=key_events)

        # Generate narrative constraints cards
        cards = NarrativeConstraintGenerator.generate_constraint_cards(self.ticker)

        # Validate law compliance across final state
        ammo_ok, ammo_viols = validate_law_compliance(self.registry.resources["ammo"])
        water_ok, water_viols = validate_law_compliance(self.registry.resources["water"])
        fuel_ok, fuel_viols = validate_law_compliance(self.registry.resources["fuel_line"])

        all_compliant = ammo_ok and water_ok and fuel_ok
        duration = time.time() - t0

        # Export outputs
        os.makedirs(self.output_dir, exist_ok=True)
        summary_path = os.path.join(self.output_dir, "simulation_summary.json")
        constraints_path = os.path.join(self.output_dir, "narrative_constraints.json")
        catalog_json_path = os.path.join(self.output_dir, "entities_catalog.json")
        events_json_path = os.path.join(self.output_dir, "events_log.json")
        events_jsonl_path = os.path.join(self.output_dir, "events_log.jsonl")

        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        catalog_yaml_path = os.path.join(base_dir, "05_WORLD_BRAIN", "entities_catalog.yaml")

        # 1. Full canonical entity catalog export
        catalog = self.registry.export_catalog()
        with open(catalog_json_path, "w", encoding="utf-8") as f:
            json.dump(catalog, f, ensure_ascii=False, indent=2)

        with open(catalog_yaml_path, "w", encoding="utf-8") as f:
            yaml.dump(catalog, f, allow_unicode=True, sort_keys=False)

        # 2. Immutable Event Sourcing Ledger exports
        self.ticker.export_events_json(events_json_path)
        self.ticker.export_events_jsonl(events_jsonl_path)

        # 3. Deterministic Event Replay Verification (Full State Reconstruction from Event Ledger)
        replayed_registry, replay_ctx = EventReplayer.replay(self.ticker.events_log)
        replay_ok, discrepancies = EventReplayer.verify_fidelity(
            self.registry,
            self.ticker.moral_system.solidarity_index,
            replayed_registry,
            replay_ctx["solidarity_index"]
        )

        all_compliant = ammo_ok and water_ok and fuel_ok and replay_ok

        summary_data = {
            "simulation_engine": "Sand Train Event-Sourced Chrono-Simulator",
            "timeline_span_minutes": 645,
            "wall_clock_range": "19:00:00 -> 05:45:00",
            "total_events_logged": len(self.ticker.events_log),
            "state_snapshots_count": len(self.ticker.state_history),
            "law_compliance": {
                "ammo_pool": "COMPLIANT" if ammo_ok else ammo_viols,
                "water_reserve": "COMPLIANT" if water_ok else water_viols,
                "fuel_line": "COMPLIANT" if fuel_ok else fuel_viols,
                "status": "PASSED" if all_compliant else "FAILED"
            },
            "event_sourcing": {
                "total_events_recorded": len(self.ticker.events_log),
                "events_log_file": "output/events_log.json",
                "events_log_jsonl": "output/events_log.jsonl",
                "replay_verification": {
                    "status": "PASSED" if replay_ok else "FAILED",
                    "applied_events_count": replay_ctx["applied_events_count"],
                    "discrepancies": discrepancies
                }
            },
            "entities_catalog": {
                "total_entities_count": catalog["metadata"]["total_entities_count"],
                "breakdown": catalog["metadata"]["breakdown"]
            },
            "final_environment": self.registry.environment,
            "final_solidarity_index": self.ticker.moral_system.solidarity_index,
            "duration_seconds": round(duration, 3)
        }

        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, ensure_ascii=False, indent=2)

        with open(constraints_path, "w", encoding="utf-8") as f:
            json.dump({"constraint_cards": cards}, f, ensure_ascii=False, indent=2)

        print(f"  ✅ Simulation Completed: 645 minutes advanced ({duration:.2f}s).")
        print(f"  📝 Total Events Recorded: {len(self.ticker.events_log)} discrete events in immutable ledger.")
        print(f"  🔁 Event Sourcing Replay: {'100% VERIFIED (Zero Discrepancies)' if replay_ok else 'FAILED'}")
        print(f"  🎯 Constraint Cards Generated: {len(cards)} advisory cards.")
        print(f"  🏷️ Canonical Entities Indexed: {catalog['metadata']['total_entities_count']} (14 Char, 5 Veh, 15 Prop, 5 Loc).")
        print(f"  ⚖️ Physical Law Compliance: {'100% COMPLIANT' if all_compliant else 'VIOLATIONS DETECTED'}")
        print(f"  📁 Artifacts Saved: 06_SIMULATION_ENGINE/output/ & 05_WORLD_BRAIN/")
        print("━" * 80)

        return 0 if all_compliant else 1


if __name__ == "__main__":
    runner = SimulationRunner()
    sys.exit(runner.run())
