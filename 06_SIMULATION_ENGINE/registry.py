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
    from .schemas.entity import EntityModel, EntityCategory
except (ImportError, ValueError):
    from components import (
        PositionComponent,
        ThermodynamicComponent,
        BiomechanicalComponent,
        PsychologicalComponent,
        EpistemicComponent
    )
    from schemas.resources import AmmoPoolModel, WaterReserveModel, FuelLineModel
    from schemas.entity import EntityModel, EntityCategory


class EntityRegistry:
    """Central registry tracking entities, characters, cars, environment and resources."""

    def __init__(self):
        self.characters: Dict[str, Dict[str, Any]] = {}
        self.cars: Dict[str, Dict[str, Any]] = {}
        self.resources: Dict[str, Any] = {}
        self.environment: Dict[str, Any] = {}
        self.timeline_minute: int = 0
        
        # Canonical Entity Catalog indexes
        self.entities: Dict[str, EntityModel] = {}
        self.entities_by_numeric_id: Dict[int, EntityModel] = {}
        self.entities_by_name: Dict[str, EntityModel] = {}
        self.entities_by_category: Dict[EntityCategory, List[EntityModel]] = {
            cat: [] for cat in EntityCategory
        }

    def register_entity(self, entity: EntityModel) -> None:
        """Registers an entity and maintains multi-dimensional indexes."""
        self.entities[entity.entity_id] = entity
        self.entities_by_numeric_id[entity.numeric_id] = entity
        self.entities_by_name[entity.canonical_name] = entity
        if entity.category in self.entities_by_category:
            if entity not in self.entities_by_category[entity.category]:
                self.entities_by_category[entity.category].append(entity)
        else:
            self.entities_by_category[entity.category] = [entity]

    def get_entity(self, identifier: Any) -> Optional[EntityModel]:
        """Look up entity by alphanumeric ID (e.g. 'ENT-CHAR-1001'), numeric ID (1001), or canonical name."""
        if isinstance(identifier, int):
            return self.entities_by_numeric_id.get(identifier)
        if isinstance(identifier, str):
            if identifier in self.entities:
                return self.entities[identifier]
            if identifier.isdigit():
                return self.entities_by_numeric_id.get(int(identifier))
            if identifier in self.entities_by_name:
                return self.entities_by_name[identifier]
        return None

    def get_entities_by_category(self, category: Any) -> List[EntityModel]:
        """Returns all entities belonging to a specific taxonomy category."""
        if isinstance(category, str):
            try:
                category = EntityCategory(category.upper())
            except ValueError:
                return []
        return self.entities_by_category.get(category, [])

    def get_props_in_car(self, car_entity_id: str) -> List[EntityModel]:
        """Returns all props physically located inside a specific car/vehicle."""
        return [
            ent for ent in self.get_entities_by_category(EntityCategory.PROP)
            if ent.location_id == car_entity_id
        ]

    def get_items_held_by(self, character_entity_id: str) -> List[EntityModel]:
        """Returns all props/items possessed by a specific character."""
        return [
            ent for ent in self.get_entities_by_category(EntityCategory.PROP)
            if ent.parent_entity_id == character_entity_id
        ]

    def export_catalog(self) -> Dict[str, Any]:
        """Exports the full canonical entity catalog as structured dictionary."""
        return {
            "metadata": {
                "schema_version": "1.0.0",
                "novel_id": "sand_train",
                "charter": "«نحن نُحلل ونُقيّم.. ولا نُقوّم»",
                "total_entities_count": len(self.entities),
                "breakdown": {
                    "characters_count": len(self.get_entities_by_category(EntityCategory.CHARACTER)),
                    "vehicles_count": len(self.get_entities_by_category(EntityCategory.VEHICLE)),
                    "props_count": len(self.get_entities_by_category(EntityCategory.PROP)),
                    "landmarks_count": len(self.get_entities_by_category(EntityCategory.LANDMARK)),
                }
            },
            "characters": [
                ent.model_dump(mode="json") for ent in self.get_entities_by_category(EntityCategory.CHARACTER)
            ],
            "vehicles": [
                ent.model_dump(mode="json") for ent in self.get_entities_by_category(EntityCategory.VEHICLE)
            ],
            "props": [
                ent.model_dump(mode="json") for ent in self.get_entities_by_category(EntityCategory.PROP)
            ],
            "landmarks": [
                ent.model_dump(mode="json") for ent in self.get_entities_by_category(EntityCategory.LANDMARK)
            ]
        }

    def initialize_default_entities(self, world_state_path: Optional[str] = None):
        """Loads canonical baseline entities from world_state.yaml and registers full catalog."""
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

        # 4. Canonical Entities Catalog Registration
        # A. Vehicles (ENT-VEH-2001 .. ENT-VEH-2005)
        canonical_vehicles = [
            EntityModel(
                entity_id="ENT-VEH-2001",
                numeric_id=2001,
                canonical_name="قاطرة الديزل الهيدروليكية Class 48",
                category=EntityCategory.VEHICLE,
                location_id="ENT-LOC-4001",
                mass_kg=82000.0,
                material_type="structural_steel",
                properties={"model": "diesel_hydraulic_class_48", "engine_status": "stalled", "length_m": 16.2}
            ),
            EntityModel(
                entity_id="ENT-VEH-2002",
                numeric_id=2002,
                canonical_name="العربة الأولى (الإدارة والحراسة)",
                category=EntityCategory.VEHICLE,
                location_id="ENT-LOC-4001",
                mass_kg=18000.0,
                material_type="steel_and_wood",
                properties={"train_car_id": "car_01", "length_m": 12.0, "y_start_m": 17.0, "y_end_m": 29.0}
            ),
            EntityModel(
                entity_id="ENT-VEH-2003",
                numeric_id=2003,
                canonical_name="العربة الوسطى (التكدس والسجناء)",
                category=EntityCategory.VEHICLE,
                location_id="ENT-LOC-4001",
                mass_kg=17500.0,
                material_type="steel_and_sheet_metal",
                properties={"train_car_id": "car_02", "length_m": 12.0, "y_start_m": 29.8, "y_end_m": 41.8}
            ),
            EntityModel(
                entity_id="ENT-VEH-2004",
                numeric_id=2004,
                canonical_name="العربة الأخيرة (الصاج العاري والعزل)",
                category=EntityCategory.VEHICLE,
                location_id="ENT-LOC-4001",
                mass_kg=17000.0,
                material_type="corrugated_steel",
                properties={"train_car_id": "car_03", "length_m": 12.0, "y_start_m": 42.6, "y_end_m": 54.6}
            ),
            EntityModel(
                entity_id="ENT-VEH-2005",
                numeric_id=2005,
                canonical_name="المنصة الخلفية المكشوفة",
                category=EntityCategory.VEHICLE,
                location_id="ENT-LOC-4001",
                mass_kg=3500.0,
                material_type="steel_gangway",
                properties={"train_car_id": "car_platform", "length_m": 2.0, "y_start_m": 55.4, "y_end_m": 57.4}
            )
        ]
        for v in canonical_vehicles:
            self.register_entity(v)

        # B. Characters (ENT-CHAR-1001 .. ENT-CHAR-1014)
        character_metadata = [
            ("خالد", 1001, "ENT-VEH-2002", 78.0, {"role": "قائد مفرزة الحراسة", "tic": "ندبة_الفك", "weapon": "ENT-PROP-3002"}),
            ("أبو_علي", 1002, "ENT-VEH-2002", 68.0, {"role": "عامل خدمة القطار", "tic": "مسح_الكفين_ببنطال_الديزل", "held_tool": "ENT-PROP-3008"}),
            ("أبو_اللول", 1003, "ENT-VEH-2002", 72.0, {"role": "حارس", "tic": "مسح_العرق_ونزيف_الأنف", "injury": "fractured_nasal_bone"}),
            ("حناطة", 1004, "ENT-VEH-2002", 70.0, {"role": "حارس متوتر", "tic": "الضحكة_الهستيرية_وفرك_الكفين", "weapon": "ENT-PROP-3004"}),
            ("عباس", 1005, "ENT-VEH-2005", 75.0, {"role": "حارس المنصة الخلفية", "tic": "إدارة_الحصاة_الصوانية", "weapon": "ENT-PROP-3003"}),
            ("سردار", 1006, "ENT-VEH-2003", 82.0, {"role": "سجين ومقاتل سابق وخبير ميكانيك", "tic": "فحص_مفاصل_القبضتين", "shackled": True}),
            ("عزيز", 1007, "ENT-VEH-2003", 65.0, {"role": "سجين صامت", "tic": "إبهام_عزيز_وسبابة_الدم"}),
            ("خليل", 1008, "ENT-VEH-2003", 74.0, {"role": "سجين تركماني وقور", "tic": "حذاء_خليل_الأسود"}),
            ("بسام", 1009, "ENT-VEH-2002", 69.0, {"role": "سجين ممرض", "tic": "الضغط_على_منبت_الظفر", "held_item": "ENT-PROP-3009"}),
            ("سلوم", 1010, "ENT-VEH-2004", 48.0, {"role": "فتى سجين مهمش", "tic": "جيب_سلوم_الفارغ", "frostbite": True}),
            ("بشير", 1011, "ENT-VEH-2004", 71.0, {"role": "سجين كتوم", "tic": "ورقة_بشير_المطوية"}),
            ("حجي_عمار", 1012, "ENT-VEH-2002", 85.0, {"role": "المدير العام السابق", "tic": "الزر_المخلوع_والساعة_المفقودة"}),
            ("حسن_كاز", 1013, "ENT-VEH-2003", 76.0, {"role": "مهرب وبائع عملة", "tic": "رزمة_الدنانير_المشتتة"}),
            ("مهدي", 1014, "ENT-VEH-2003", 70.0, {"role": "السجين الشبح", "tic": "السكون_الحيواني", "stealth_status": "calculating_jump"})
        ]

        chars_raw = data.get("characters", {})
        for cname, num_id, host_veh, mass, props in character_metadata:
            cdata = chars_raw.get(cname, {})
            loc = cdata.get("location", host_veh)
            coords = cdata.get("coordinates", {"x_m": 1.0, "y_m": 20.0})
            phys = cdata.get("physical", {})
            psych = cdata.get("psychological", {})
            tic = cdata.get("active_tic", {})
            epistemic = cdata.get("epistemic_bubble", {})

            # Register canonical EntityModel
            ent_char = EntityModel(
                entity_id=f"ENT-CHAR-{num_id}",
                numeric_id=num_id,
                canonical_name=cname,
                category=EntityCategory.CHARACTER,
                location_id=host_veh,
                coordinates={
                    "x_m": float(coords.get("x_m", 1.0)),
                    "y_m": float(coords.get("y_m", 20.0))
                },
                mass_kg=mass,
                temperature_c=float(phys.get("core_temp_c", 36.8)),
                material_type="flesh",
                properties=props
            )
            self.register_entity(ent_char)

            # ECS internal character record
            self.characters[cname] = {
                "name": cname,
                "entity_id": ent_char.entity_id,
                "numeric_id": ent_char.numeric_id,
                "role": cdata.get("role", props.get("role", "راكب")),
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

        # C. Props and Material Artifacts (ENT-PROP-3001 .. ENT-PROP-3015)
        canonical_props = [
            EntityModel(
                entity_id="ENT-PROP-3001",
                numeric_id=3001,
                canonical_name="برميل البولي إيثيلين الأزرق (مستودع الماء)",
                category=EntityCategory.PROP,
                location_id="ENT-VEH-2002",
                coordinates={"x_m": 2.4, "y_m": 20.5},
                mass_kg=16.5,
                material_type="polyethylene",
                properties={"volume_liters": 14.0, "current_liters": 14.0, "state": "liquid_subzero_verge"}
            ),
            EntityModel(
                entity_id="ENT-PROP-3002",
                numeric_id=3002,
                canonical_name="بندقية كلاشنكوف خالد",
                category=EntityCategory.PROP,
                parent_entity_id="ENT-CHAR-1001",
                location_id="ENT-VEH-2002",
                mass_kg=3.8,
                material_type="milled_steel_and_wood",
                properties={"caliber": "7.62x39mm", "rounds": 28, "capacity": 30}
            ),
            EntityModel(
                entity_id="ENT-PROP-3003",
                numeric_id=3003,
                canonical_name="بندقية كلاشنكوف عباس",
                category=EntityCategory.PROP,
                parent_entity_id="ENT-CHAR-1005",
                location_id="ENT-VEH-2005",
                mass_kg=3.8,
                material_type="milled_steel_and_wood",
                properties={"caliber": "7.62x39mm", "rounds": 30, "capacity": 30}
            ),
            EntityModel(
                entity_id="ENT-PROP-3004",
                numeric_id=3004,
                canonical_name="بندقية كلاشنكوف حناطة",
                category=EntityCategory.PROP,
                parent_entity_id="ENT-CHAR-1004",
                location_id="ENT-VEH-2002",
                mass_kg=3.8,
                material_type="milled_steel_and_wood",
                properties={"caliber": "7.62x39mm", "rounds": 28, "capacity": 30}
            ),
            EntityModel(
                entity_id="ENT-PROP-3005",
                numeric_id=3005,
                canonical_name="صندوق الذخيرة الخشبي (مخزن الطوارئ)",
                category=EntityCategory.PROP,
                location_id="ENT-VEH-2002",
                coordinates={"x_m": 2.4, "y_m": 21.8},
                mass_kg=5.2,
                material_type="pine_wood_and_tin",
                properties={"caliber": "7.62x39mm", "rounds": 60, "sealed": True}
            ),
            EntityModel(
                entity_id="ENT-PROP-3006",
                numeric_id=3006,
                canonical_name="سلك الحديد الصلب (2 ملم)",
                category=EntityCategory.PROP,
                location_id="ENT-VEH-2003",
                coordinates={"x_m": 2.2, "y_m": 31.0},
                mass_kg=0.85,
                material_type="galvanized_steel_wire",
                properties={"diameter_mm": 2.0, "length_m": 4.5, "yield_strength_mpa": 450.0}
            ),
            EntityModel(
                entity_id="ENT-PROP-3007",
                numeric_id=3007,
                canonical_name="مفتاح الربط الإنجليزي (12 بوصة)",
                category=EntityCategory.PROP,
                location_id="ENT-VEH-2002",
                coordinates={"x_m": 0.6, "y_m": 26.2},
                mass_kg=1.2,
                material_type="cast_iron",
                properties={"size_inches": 12, "condition": "functional_rusted"}
            ),
            EntityModel(
                entity_id="ENT-PROP-3008",
                numeric_id=3008,
                canonical_name="كماشة قطع الأسلاك (أبو علي)",
                category=EntityCategory.PROP,
                parent_entity_id="ENT-CHAR-1002",
                location_id="ENT-VEH-2002",
                mass_kg=0.45,
                material_type="tool_steel",
                properties={"condition": "functional", "cutting_capacity_mm": 3.0}
            ),
            EntityModel(
                entity_id="ENT-PROP-3009",
                numeric_id=3009,
                canonical_name="حقيبة الإسعافات الطبية (بسام)",
                category=EntityCategory.PROP,
                parent_entity_id="ENT-CHAR-1009",
                location_id="ENT-VEH-2002",
                mass_kg=1.5,
                material_type="canvas",
                properties={"gauze_rolls": 3, "alcohol_disinfectant_ml": 250, "splints": 2}
            ),
            EntityModel(
                entity_id="ENT-PROP-3010",
                numeric_id=3010,
                canonical_name="قفل الكابينة الداخلي (المزلاج النحاسي)",
                category=EntityCategory.PROP,
                location_id="ENT-VEH-2001",
                mass_kg=0.65,
                material_type="brass",
                properties={"status": "engaged_locked", "breach_resistance": "high"}
            ),
            EntityModel(
                entity_id="ENT-PROP-3011",
                numeric_id=3011,
                canonical_name="شظية الهاون العالقة في أنبوب الوقود",
                category=EntityCategory.PROP,
                location_id="ENT-VEH-2001",
                mass_kg=0.12,
                material_type="cast_iron_fragment",
                properties={"textual_baseline_line": 1297, "audit_ref": "WORLD-BUG-009", "breach_gap_mm": 14}
            ),
            EntityModel(
                entity_id="ENT-PROP-3012",
                numeric_id=3012,
                canonical_name="خرقة الديزل الزيتية (أبو علي)",
                category=EntityCategory.PROP,
                parent_entity_id="ENT-CHAR-1002",
                location_id="ENT-VEH-2002",
                mass_kg=0.18,
                material_type="cotton_saturated_with_diesel",
                properties={"diesel_saturation_percent": 80.0, "purpose": "seal_wrap_and_insulation"}
            ),
            EntityModel(
                entity_id="ENT-PROP-3013",
                numeric_id=3013,
                canonical_name="علبة سجائر سومر المبتلة (حناطة)",
                category=EntityCategory.PROP,
                parent_entity_id="ENT-CHAR-1004",
                location_id="ENT-VEH-2002",
                mass_kg=0.05,
                material_type="cardboard_and_tobacco",
                properties={"brand": "سومر", "cigarettes_remaining": 7, "damp": True}
            ),
            EntityModel(
                entity_id="ENT-PROP-3014",
                numeric_id=3014,
                canonical_name="إبريق الشاي المهشم (العربة الأولى)",
                category=EntityCategory.PROP,
                location_id="ENT-VEH-2002",
                mass_kg=0.40,
                material_type="enameled_steel",
                properties={"condition": "dented_dry", "tea_remains": "frozen_leaves"}
            ),
            EntityModel(
                entity_id="ENT-PROP-3015",
                numeric_id=3015,
                canonical_name="حذاء السائق المتروك (كابينة القاطرة)",
                category=EntityCategory.PROP,
                location_id="ENT-VEH-2001",
                mass_kg=0.70,
                material_type="leather_and_rubber",
                properties={"side": "right", "size": 42, "evidence_of": "hasty_abandonment"}
            )
        ]
        for p in canonical_props:
            self.register_entity(p)

        # D. Geographic Landmarks (ENT-LOC-4001 .. ENT-LOC-4005)
        canonical_landmarks = [
            EntityModel(
                entity_id="ENT-LOC-4001",
                numeric_id=4001,
                canonical_name="نقطة التوقف القسري (الكيلومتر 312.4)",
                category=EntityCategory.LANDMARK,
                coordinates={"lat_deg": 31.2333, "lon_deg": 42.5833},
                mass_kg=0.0,
                material_type="gravel_desert_soil",
                properties={"kilometer_point": 312.4, "elevation_m": 612.0, "region": "بادية الحماد"}
            ),
            EntityModel(
                entity_id="ENT-LOC-4002",
                numeric_id=4002,
                canonical_name="محطة قطار بادوش",
                category=EntityCategory.LANDMARK,
                coordinates={"lat_deg": 36.4167, "lon_deg": 42.9833},
                mass_kg=0.0,
                material_type="concrete_and_steel",
                properties={"role": "point_of_origin", "status": "militarized_terminal"}
            ),
            EntityModel(
                entity_id="ENT-LOC-4003",
                numeric_id=4003,
                canonical_name="سجن البير الصحراوي",
                category=EntityCategory.LANDMARK,
                coordinates={"lat_deg": 30.5000, "lon_deg": 43.1000},
                mass_kg=0.0,
                material_type="reinforced_concrete",
                properties={"distance_from_stall_km": 142.0, "kilometer_point": 454.4}
            ),
            EntityModel(
                entity_id="ENT-LOC-4004",
                numeric_id=4004,
                canonical_name="مخفر تل الصوان المهجور",
                category=EntityCategory.LANDMARK,
                coordinates={"lat_deg": 31.7000, "lon_deg": 42.2000},
                mass_kg=0.0,
                material_type="adobe_and_mudbrick",
                properties={"distance_from_stall_km": 68.0, "kilometer_point": 244.4}
            ),
            EntityModel(
                entity_id="ENT-LOC-4005",
                numeric_id=4005,
                canonical_name="تلة الرصد وحافة الكمين",
                category=EntityCategory.LANDMARK,
                coordinates={"bearing_deg": 250.0, "distance_m": 850.0},
                mass_kg=0.0,
                material_type="flint_ridge",
                properties={"elevation_m": +25.0, "ambush_posture": "silent_encirclement"}
            )
        ]
        for lmark in canonical_landmarks:
            self.register_entity(lmark)

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
                    "entity_id": c.get("entity_id"),
                    "numeric_id": c.get("numeric_id"),
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
            ],
            "total_entities_count": len(self.entities),
            "entities_catalog_summary": {
                "characters": len(self.get_entities_by_category(EntityCategory.CHARACTER)),
                "vehicles": len(self.get_entities_by_category(EntityCategory.VEHICLE)),
                "props": len(self.get_entities_by_category(EntityCategory.PROP)),
                "landmarks": len(self.get_entities_by_category(EntityCategory.LANDMARK)),
            }
        }
