#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
SPATIAL-ACOUSTIC EPISTEMIC FIELD AUTOMATOR (الحقل الإبستيمولوجي الطوبولوجي الصوتي الآلي)
Project: Narrative World OS / Framework
License: MIT
==============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass
class SoundEvent:
    event_id: str
    location_id: str
    intensity_db: float
    description: str
    is_structure_borne: bool = False
    requires_line_of_sight: bool = False


@dataclass
class PerceivedState:
    event_id: str
    character_name: str
    character_location: str
    is_perceived: bool
    channel: Optional[str]  # AUDITORY, VISUAL, STRUCTURE_VIBRATION, DIRECT_PRESENCE
    received_db: float
    reason: str


@dataclass
class EpistemicLeakViolation:
    character_name: str
    character_location: str
    event_id: str
    event_location: str
    violation_message: str
    severity: str = "FATAL"


class SpatialAcousticEpistemicField:
    """Computes automated auditory and spatial perception boundaries across partitioned narrative zones."""

    # Standard narrative sound intensities (dB)
    INTENSITIES: Dict[str, float] = {
        "WHISPER": 25.0,           # همس خافت
        "LOW_SPEECH": 45.0,        # حديث هادئ
        "NORMAL_SPEECH": 65.0,     # كلام طبيعي
        "SHOUT": 85.0,             # صراخ واستغاثة
        "GUNSHOT": 150.0,          # طلقة نارية
        "BULLET_SPALLING": 120.0,  # تشظي رصاص في صاج
        "METAL_CLANK": 75.0,       # ارتطام معدني / مفتاح
        "DOOR_SLAM": 80.0,         # انطباق باب ثقيل
    }

    # Minimum human hearing threshold considering background noise (e.g. 38 km/h desert wind)
    HUMAN_AUDITORY_THRESHOLD_DB = 25.0

    def __init__(self, zones_topology: Optional[Dict[str, Any]] = None):
        """
        Initializes epistemic field with a spatial topology.
        If None, initializes default Sand Train 4-zone train topology.
        """
        self.zones: Dict[str, Dict[str, Any]] = {}
        self.adjacency: Dict[str, List[str]] = {}
        self.partition_losses: Dict[Tuple[str, str], float] = {}

        if zones_topology:
            self._load_custom_topology(zones_topology)
        else:
            self._init_default_train_topology()

    def _init_default_train_topology(self) -> None:
        """Initializes canonical 4-zone linear train topology (Locomotive -> Car 1 -> Car 2 -> Car 3)."""
        self.zones = {
            "car_00_locomotive": {"name": "القاطرة والكابينة", "position": 0.0},
            "car_01_guard": {"name": "العربة الأولى (الحرس)", "position": 1.0},
            "car_02_middle": {"name": "العربة الثانية (الوسطى)", "position": 2.0},
            "car_03_rear": {"name": "العربة الثالثة (الأخيرة)", "position": 3.0},
            "platform_rear": {"name": "المنصة الخلفية المكشوفة", "position": 3.5},
        }

        # Linear car adjacencies
        self.adjacency = {
            "car_00_locomotive": ["car_01_guard"],
            "car_01_guard": ["car_00_locomotive", "car_02_middle"],
            "car_02_middle": ["car_01_guard", "car_03_rear"],
            "car_03_rear": ["car_02_middle", "platform_rear"],
            "platform_rear": ["car_03_rear"],
        }

    def _load_custom_topology(self, topology: Dict[str, Any]) -> None:
        """Loads topology from manifest spatial_topology dictionary."""
        zones_list = topology.get("zones", [])
        for idx, z in enumerate(zones_list):
            z_id = z.get("id", f"zone_{idx}")
            self.zones[z_id] = {
                "name": z.get("name", z_id),
                "position": float(idx),
                "isolation_db": float(z.get("acoustic_isolation_db", 35.0)),
            }

        # Build adjacency linearly or from graph
        zone_keys = list(self.zones.keys())
        for i in range(len(zone_keys)):
            k = zone_keys[i]
            adj = []
            if i > 0:
                adj.append(zone_keys[i - 1])
            if i < len(zone_keys) - 1:
                adj.append(zone_keys[i + 1])
            self.adjacency[k] = adj

    def compute_acoustic_attenuation(
        self,
        src_zone: str,
        dst_zone: str,
        is_structure_borne: bool = False
    ) -> float:
        """
        Calculates sound loss in decibels (dB) between two zones.
        Accounts for steel partition boundaries, air distance, and solid metal conduction.
        """
        if src_zone == dst_zone:
            return 0.0

        # Solid structure-borne shock (LAW-ACOUST-04): steel rail and chassis conduct shocks with minimal loss
        if is_structure_borne:
            pos_src = self.zones.get(src_zone, {}).get("position", 0.0)
            pos_dst = self.zones.get(dst_zone, {}).get("position", 1.0)
            car_hops = abs(pos_dst - pos_src)
            return float(car_hops * 3.5)  # Less than 5 dB loss per car in solid steel

        # Airborne acoustic loss through enclosed partitions
        pos_src = self.zones.get(src_zone, {}).get("position", 0.0)
        pos_dst = self.zones.get(dst_zone, {}).get("position", 1.0)
        car_hops = abs(pos_dst - pos_src)

        if car_hops <= 1.0:
            # Adjacent cars separated by double bulkhead door
            return 22.0
        elif car_hops <= 2.0:
            # Separated by an intermediate car (e.g. Car 1 to Car 3): ~38 to 44 dB loss
            return 40.0
        else:
            # Remote end to end
            return 55.0

    def evaluate_perception(
        self,
        event: SoundEvent,
        character_name: str,
        character_location: str
    ) -> PerceivedState:
        """Evaluates whether a character at a given location physically perceives an event."""
        # 1. Direct co-presence
        if event.location_id == character_location:
            return PerceivedState(
                event_id=event.event_id,
                character_name=character_name,
                character_location=character_location,
                is_perceived=True,
                channel="DIRECT_PRESENCE",
                received_db=event.intensity_db,
                reason=f"Co-present in same physical zone '{character_location}'",
            )

        # 2. Line of sight only events
        if event.requires_line_of_sight and event.location_id != character_location:
            return PerceivedState(
                event_id=event.event_id,
                character_name=character_name,
                character_location=character_location,
                is_perceived=False,
                channel=None,
                received_db=0.0,
                reason="Line of sight blocked by enclosed opaque partition",
            )

        # 3. Acoustic attenuation calculation
        loss_db = self.compute_acoustic_attenuation(
            src_zone=event.location_id,
            dst_zone=character_location,
            is_structure_borne=event.is_structure_borne,
        )
        received_db = event.intensity_db - loss_db

        if received_db >= self.HUMAN_AUDITORY_THRESHOLD_DB:
            channel = "STRUCTURE_VIBRATION" if event.is_structure_borne else "AUDITORY"
            return PerceivedState(
                event_id=event.event_id,
                character_name=character_name,
                character_location=character_location,
                is_perceived=True,
                channel=channel,
                received_db=round(received_db, 1),
                reason=f"Acoustic signal ({received_db:.1f} dB) exceeds threshold ({self.HUMAN_AUDITORY_THRESHOLD_DB} dB)",
            )
        else:
            return PerceivedState(
                event_id=event.event_id,
                character_name=character_name,
                character_location=character_location,
                is_perceived=False,
                channel=None,
                received_db=round(received_db, 1),
                reason=f"Acoustic signal attenuated ({received_db:.1f} dB) below threshold ({self.HUMAN_AUDITORY_THRESHOLD_DB} dB)",
            )

    def derive_automated_epistemic_bubbles(
        self,
        characters_locations: Dict[str, str],
        events_pool: List[SoundEvent]
    ) -> Dict[str, Dict[str, List[str]]]:
        """
        Automatically derives known_truths and blind_spots for all characters
        without any manual configuration!
        """
        bubbles: Dict[str, Dict[str, List[str]]] = {}

        for char_name, char_loc in characters_locations.items():
            knowns: List[str] = []
            blinds: List[str] = []

            for evt in events_pool:
                state = self.evaluate_perception(
                    event=evt,
                    character_name=char_name,
                    character_location=char_loc,
                )
                if state.is_perceived:
                    knowns.append(f"{evt.description} [{state.channel}]")
                else:
                    blinds.append(f"{evt.description} ({state.reason})")

            bubbles[char_name] = {
                "known_truths": knowns,
                "blind_spots": blinds,
            }

        return bubbles

    def audit_omniscience_leak(
        self,
        speaker_name: str,
        speaker_location: str,
        event_referenced: SoundEvent,
        attested_transmission_vector: Optional[str] = None
    ) -> Optional[EpistemicLeakViolation]:
        """
        Detects if a character references an unattenuated or unperceived event
        without a physical transmission medium.
        """
        if attested_transmission_vector is not None:
            return None

        state = self.evaluate_perception(
            event=event_referenced,
            character_name=speaker_name,
            character_location=speaker_location,
        )

        if not state.is_perceived:
            return EpistemicLeakViolation(
                character_name=speaker_name,
                character_location=speaker_location,
                event_id=event_referenced.event_id,
                event_location=event_referenced.location_id,
                violation_message=(
                    f"Fatal Epistemic Leak: Character '{speaker_name}' at '{speaker_location}' "
                    f"acted on or referenced '{event_referenced.description}' occurring in '{event_referenced.location_id}' "
                    f"despite signal being imperceptible ({state.received_db:.1f} dB <= {self.HUMAN_AUDITORY_THRESHOLD_DB} dB). "
                    f"Partition attenuation: {self.compute_acoustic_attenuation(event_referenced.location_id, speaker_location):.1f} dB."
                ),
            )
        return None
