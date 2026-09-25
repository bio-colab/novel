#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
WORLD MANIFEST SYNTHESIZER (مؤلف عقد ومواصفة العالم السردي التلقائي)
Project: Narrative World OS / Framework
License: MIT
==============================================================================
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from world_engine.dag_miner import NarrativeCausalityMiner
from world_engine.ingest.narrative_ner import ExtractedEntities, NarrativeEntityExtractor
from world_engine.ingest.sensory_grounder import GroundedEnvironment, SensoryPhysicalGrounder
from world_engine.ingest.text_chunker import ChunkedDocument, NarrativeTextChunker
from world_engine.law_catalog.recommender import DomainLawRecommender
from world_engine.spatial_epistemics import SpatialAcousticEpistemicField, SoundEvent


class WorldManifestSynthesizer:
    """Orchestrates parsing, extraction, and synthesis of a full narrative world instance from raw text."""

    def __init__(self):
        self.chunker = NarrativeTextChunker()
        self.ner = NarrativeEntityExtractor()
        self.grounder = SensoryPhysicalGrounder()
        self.miner = NarrativeCausalityMiner()
        self.law_recommender = DomainLawRecommender()
        self.epistemic_field = SpatialAcousticEpistemicField()

    def slugify(self, text: str) -> str:
        s = text.lower().strip()
        s = re.sub(r"[^\w\s-]", "", s)
        s = re.sub(r"[\s_-]+", "_", s)
        return s or "narrative_world"

    def synthesize_from_file(
        self,
        file_path: str | Path,
        output_dir: str | Path,
        world_id: Optional[str] = None,
        title: Optional[str] = None,
        genre: Optional[str] = None,
    ) -> Dict[str, Any]:
        path = Path(file_path).resolve()
        raw_text = path.read_text(encoding="utf-8", errors="replace")
        default_title = path.stem.replace("_", " ").title()
        return self.synthesize_from_text(
            text=raw_text,
            output_dir=output_dir,
            source_path=str(path),
            world_id=world_id or self.slugify(path.stem),
            title=title or default_title,
            genre=genre,
        )

    def synthesize_from_text(
        self,
        text: str,
        output_dir: str | Path,
        source_path: Optional[str] = None,
        world_id: Optional[str] = None,
        title: Optional[str] = None,
        genre: Optional[str] = None,
    ) -> Dict[str, Any]:
        out_path = Path(output_dir).resolve()
        out_path.mkdir(parents=True, exist_ok=True)

        effective_title = title or "عالم سردي مستورد"
        effective_world_id = world_id or self.slugify(effective_title)
        effective_genre = genre or "existential_survival_tragedy"

        # 1. Structural Chunker
        doc = self.chunker.parse_text(text, source_path=source_path)

        # 2. Narrative NER
        entities = self.ner.extract(text)

        # 3. Sensory Grounder
        env = self.grounder.ground(text)

        # 4. Synthesize world_manifest.yaml
        manifest_data = self._build_manifest(
            world_id=effective_world_id,
            title=effective_title,
            genre=effective_genre,
            doc=doc,
            entities=entities,
            env=env,
        )

        # 5. Synthesize entities_catalog.yaml
        entities_data = self._build_entities_catalog(
            world_id=effective_world_id,
            entities=entities,
        )

        # 6. Synthesize world_state.yaml
        state_data = self._build_world_state(
            doc=doc,
            entities=entities,
            env=env,
        )

        # 7. Synthesize rules_manifest.yaml
        rules_data = self._build_rules_manifest(text=text, genre=effective_genre)

        # 8. Synthesize causality_graph.yaml
        causality_data = self._build_causality_graph(text=text, doc=doc)

        # Write files
        manifest_file = out_path / "world_manifest.yaml"
        entities_file = out_path / "entities_catalog.yaml"
        state_file = out_path / "world_state.yaml"
        rules_file = out_path / "rules_manifest.yaml"
        causality_file = out_path / "causality_graph.yaml"

        with open(manifest_file, "w", encoding="utf-8") as f:
            yaml.dump(manifest_data, f, allow_unicode=True, sort_keys=False)

        with open(entities_file, "w", encoding="utf-8") as f:
            yaml.dump(entities_data, f, allow_unicode=True, sort_keys=False)

        with open(state_file, "w", encoding="utf-8") as f:
            yaml.dump(state_data, f, allow_unicode=True, sort_keys=False)

        with open(rules_file, "w", encoding="utf-8") as f:
            yaml.dump(rules_data, f, allow_unicode=True, sort_keys=False)

        with open(causality_file, "w", encoding="utf-8") as f:
            yaml.dump(causality_data, f, allow_unicode=True, sort_keys=False)

        return {
            "output_dir": str(out_path),
            "world_id": effective_world_id,
            "title": effective_title,
            "total_lines": doc.total_lines,
            "total_words": doc.total_words,
            "parts_count": len(doc.parts),
            "chapters_count": len(doc.chapters),
            "characters_count": len(entities.characters),
            "vehicles_count": len(entities.vehicles),
            "props_count": len(entities.props),
            "landmarks_count": len(entities.landmarks),
            "grounded_regime": env.temperature.regime,
            "files_created": [
                "world_manifest.yaml",
                "entities_catalog.yaml",
                "world_state.yaml",
                "rules_manifest.yaml",
                "causality_graph.yaml",
            ],
        }

    def _build_manifest(
        self,
        world_id: str,
        title: str,
        genre: str,
        doc: ChunkedDocument,
        entities: ExtractedEntities,
        env: GroundedEnvironment,
    ) -> Dict[str, Any]:
        # Estimate duration: chapters * 20 minutes or min 360
        estimated_duration = max(360, len(doc.chapters) * 20)

        # Setting description
        landmarks_names = [l.name for l in entities.landmarks[:3]]
        setting_desc = " - ".join(landmarks_names) if landmarks_names else "الفضاء السردي الحبيس"

        # Determine spatial topology zones
        zones = []
        if entities.vehicles:
            for idx, v in enumerate(entities.vehicles[:4], start=1):
                zones.append({
                    "id": f"zone_{idx}_{self.slugify(v.name)}",
                    "name": f"{v.name} ({v.properties.get('type', 'vessel')})",
                    "bounds_meters": [(idx - 1) * 15.0, idx * 15.0],
                    "acoustic_isolation_db": 35.0,
                    "thermal_conduction_factor": 1.1,
                })
        else:
            zones = [
                {
                    "id": "zone_alpha",
                    "name": "الحجرة / المنطقة الرئيسية (Primary Zone)",
                    "bounds_meters": [0.0, 15.0],
                    "acoustic_isolation_db": 30.0,
                    "thermal_conduction_factor": 1.0,
                },
                {
                    "id": "zone_beta",
                    "name": "المنطقة الثانوية (Secondary Zone)",
                    "bounds_meters": [15.0, 30.0],
                    "acoustic_isolation_db": 35.0,
                    "thermal_conduction_factor": 1.2,
                },
            ]

        # Inventory from props
        inventories = []
        for idx, p in enumerate(entities.props[:4], start=1):
            category = "misc"
            p_lower = p.name.lower()
            if "ماء" in p_lower or "برميل" in p_lower:
                category = "water"
            elif "رصاص" in p_lower or "طلقات" in p_lower or "بندقية" in p_lower or "كلاشينكوف" in p_lower:
                category = "ammunition"
            elif "ديزل" in p_lower or "وقود" in p_lower:
                category = "fuel"
            elif "مفتاح" in p_lower or "سلك" in p_lower or "خرطوم" in p_lower:
                category = "tool"

            amount = 14.0 if category == "water" else float(max(1, p.mentions_count))
            unit = "liters" if category == "water" else "units"
            inventories.append({
                "resource_id": f"res_{idx}_{self.slugify(p.name)}",
                "category": category,
                "amount": amount,
                "unit": unit,
                "location_zone_id": zones[0]["id"],
                "consumption_rate_per_hour_per_capita": 0.05 if category == "water" else 0.0,
            })

        if not inventories:
            inventories.append({
                "resource_id": "water_supply_primary",
                "category": "water",
                "amount": 20.0,
                "unit": "liters",
                "location_zone_id": zones[0]["id"],
                "consumption_rate_per_hour_per_capita": 0.05,
            })

        total_chars = max(1, len(entities.characters))
        primary_chars_count = min(6, total_chars)

        return {
            "schema_version": "1.0.0",
            "world_id": world_id,
            "title": title,
            "genre": genre,
            "chronotope": {
                "setting": setting_desc,
                "coordinates": "31.3°N, 45.3°E",
                "historical_epoch": "1980s_analog",
                "start_timestamp": "198X-01-18T19:00:00",
                "total_duration_minutes": estimated_duration,
                "timestep_minutes": 1.0,
            },
            "environment": env.to_manifest_dict(),
            "spatial_topology": {
                "coordinate_type": "1D_linear_track" if ("قطار" in title or "سكة" in doc.raw_text) else "3D_bounded_box",
                "total_envelope_meters": len(zones) * 15.0,
                "zones": zones,
            },
            "resource_ledger": {
                "initial_inventories": inventories,
            },
            "headcount_target": {
                "initial_total": total_chars,
                "demographic_breakdown": {
                    "primary_agents": primary_chars_count,
                    "cohort_agents": max(0, total_chars - primary_chars_count),
                },
            },
            "rules_manifest_ref": "rules_manifest.yaml",
            "entities_catalog_ref": "entities_catalog.yaml",
            "causality_graph_ref": "causality_graph.yaml",
        }

    def _build_entities_catalog(self, world_id: str, entities: ExtractedEntities) -> Dict[str, Any]:
        default_loc = entities.vehicles[0].entity_id if entities.vehicles else "zone_alpha"
        chars_list = []
        for c in entities.characters:
            chars_list.append({
                "entity_id": c.entity_id,
                "numeric_id": c.numeric_id,
                "canonical_name": c.name,
                "category": "CHARACTER",
                "parent_entity_id": None,
                "location_id": default_loc,
                "properties": {
                    "role": c.inferred_role,
                    "affordance_anchor": f"موضع_{self.slugify(c.name)}",
                    "tic": c.inferred_tic or "التأمل_الصامت_في_العتمة",
                    "mentions_count": c.mentions_count,
                },
            })

        # Ensure at least 1 character if none detected
        if not chars_list:
            chars_list.append({
                "entity_id": "ENT-CHAR-1001",
                "numeric_id": 1001,
                "canonical_name": "الفاعل_الرئيسي",
                "category": "CHARACTER",
                "parent_entity_id": None,
                "location_id": default_loc,
                "properties": {
                    "role": "بطل الرواية",
                    "affordance_anchor": "المركز_الداخلي",
                    "tic": "الترقب_الدائم",
                },
            })

        vehicles_list = [
            {
                "entity_id": v.entity_id,
                "canonical_name": v.name,
                "category": "VEHICLE",
                "properties": v.properties,
            }
            for v in entities.vehicles
        ]

        props_list = [
            {
                "entity_id": p.entity_id,
                "canonical_name": p.name,
                "category": "PROP",
                "properties": p.properties,
            }
            for p in entities.props
        ]

        landmarks_list = [
            {
                "entity_id": l.entity_id,
                "canonical_name": l.name,
                "category": "LANDMARK",
                "properties": l.properties,
            }
            for l in entities.landmarks
        ]

        return {
            "metadata": {
                "schema_version": "1.0.0",
                "novel_id": world_id,
                "charter": "نحن نُحلل ونُقيّم.. ولا نُقوّم",
                "total_entities_count": len(chars_list) + len(vehicles_list) + len(props_list) + len(landmarks_list),
                "breakdown": {
                    "characters_count": len(chars_list),
                    "vehicles_count": len(vehicles_list),
                    "props_count": len(props_list),
                    "landmarks_count": len(landmarks_list),
                },
            },
            "characters": chars_list,
            "vehicles": vehicles_list,
            "props": props_list,
            "landmarks": landmarks_list,
        }

    def _build_world_state(
        self,
        doc: ChunkedDocument,
        entities: ExtractedEntities,
        env: GroundedEnvironment,
    ) -> Dict[str, Any]:
        chars_state = {}
        for idx, c in enumerate(entities.characters, start=1):
            agency = "primary_agent" if idx <= 6 or c.mentions_count > 10 else "cohort_agent"
            chars_state[self.slugify(c.name)] = {
                "name_ar": c.name,
                "agency_type": agency,
                "affordance_slot": f"slot_{self.slugify(c.name)}",
                "vitals": {
                    "core_temp_c": 36.8 if agency == "primary_agent" else 36.5,
                    "dexterity_percent": 90,
                    "allostatic_load": 0.2,
                },
                "epistemic_bubble": {
                    "known_truths": [f"وجوده في المشهد السردي ({c.name})"],
                    "blind_spots": ["ما يدور خلف الحواجز المكانية المعزولة"],
                },
            }

        return {
            "schema_version": "1.0.0",
            "timestamp": "19:00:00",
            "environment": {
                "ambient_temperature_c": env.temperature.initial,
                "lux_ambient": env.lux.initial,
                "wind_speed_kmh": env.wind.speed_kmh,
                "co2_concentration_percent": 0.04,
            },
            "characters": chars_state,
            "spatial_slots": {
                "active_occupants_count": len(chars_state),
            },
        }

    def _build_rules_manifest(self, text: str, genre: Optional[str] = None) -> Dict[str, Any]:
        report = self.law_recommender.recommend_for_text(text, genre_hint=genre)
        return report.to_rules_manifest_dict()

    def _build_causality_graph(self, text: str, doc: ChunkedDocument) -> Dict[str, Any]:
        mining_report = self.miner.mine_and_report(text)
        if mining_report.total_events >= 2:
            return mining_report.to_yaml_dict()

        # Fallback to chapters if fewer events detected
        events = []
        for idx, ch in enumerate(doc.chapters[:10], start=1):
            events.append({
                "id": f"EVT-{idx:03d}",
                "name": f"حدث الفصل {ch.chapter_index}: {ch.title}",
                "chapter_index": ch.chapter_index,
                "causes": [f"EVT-{idx+1:03d}"] if idx < min(10, len(doc.chapters)) else [],
            })

        if not events:
            events.append({
                "id": "EVT-001",
                "name": "العطل والحدث التأسيسي الأولي",
                "causes": [],
            })

        return {
            "schema_version": "1.0.0",
            "events_count": len(events),
            "events": events,
        }
