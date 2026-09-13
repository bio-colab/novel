#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
UNIFIED ENTITY SCHEMA (مخطط الكيانات والمُعرّفات الموحد)
Project: «قطار الرمل» (Sand Train) - Narrative Engineering Simulation Engine
Framework Charter: «نحن نُحلل ونُقيّم.. ولا نُقوّم»
==============================================================================
"""

import re
from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, model_validator


class EntityCategory(str, Enum):
    """Categorical classification for all novel entities."""
    CHARACTER = "CHARACTER"  # الأرواح والشخصيات (1001-1099)
    VEHICLE = "VEHICLE"      # القطار والعربات (2001-2099)
    PROP = "PROP"            # الأعيان والمقتنيات والأسلحة (3001-3099)
    LANDMARK = "LANDMARK"    # المعالم الجغرافية والزمكانية (4001-4099)


class EntityModel(BaseModel):
    """Strict canonical entity model for everything in the novel world."""
    entity_id: str = Field(
        ...,
        pattern=r"^ENT-(CHAR|VEH|PROP|LOC)-\d{4}$",
        description="Canonical alphanumeric ID (e.g. ENT-CHAR-1001, ENT-PROP-3001)"
    )
    numeric_id: int = Field(
        ...,
        ge=1001,
        le=4999,
        description="Canonical numeric ID matching category range"
    )
    canonical_name: str = Field(..., description="Authentic Arabic canonical name")
    category: EntityCategory = Field(..., description="Entity taxonomy classification")
    parent_entity_id: Optional[str] = Field(None, description="Possessor or container entity ID")
    location_id: Optional[str] = Field(None, description="Host car or location ID")
    coordinates: Optional[Dict[str, float]] = Field(None, description="Spatial coordinates (x_m, y_m)")
    mass_kg: Optional[float] = Field(None, ge=0.0, description="Physical mass in kilograms for conservation checks")
    temperature_c: Optional[float] = Field(None, description="Physical temperature in Celsius")
    material_type: Optional[str] = Field(None, description="Constituent material (steel, wood, flesh, plastic, wool)")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Custom mechanical, narrative or biometric traits")

    @model_validator(mode="after")
    def validate_taxonomy_ranges_and_id_alignment(self):
        """Validates that entity_id prefix and numeric_id strictly align with category."""
        # 1. Check numeric match between string ID and integer ID
        match = re.match(r"^ENT-(CHAR|VEH|PROP|LOC)-(\d{4})$", self.entity_id)
        if not match:
            raise ValueError(f"Malformed entity_id format: '{self.entity_id}'")

        prefix, num_str = match.groups()
        num_val = int(num_str)
        if num_val != self.numeric_id:
            raise ValueError(
                f"Numeric mismatch in entity '{self.entity_id}': prefix numeric '{num_str}' "
                f"does not match numeric_id {self.numeric_id}"
            )

        # 2. Check taxonomy prefix and range alignment
        category_rules = {
            EntityCategory.CHARACTER: ("CHAR", 1001, 1099),
            EntityCategory.VEHICLE: ("VEH", 2001, 2099),
            EntityCategory.PROP: ("PROP", 3001, 3099),
            EntityCategory.LANDMARK: ("LOC", 4001, 4099),
        }

        expected_prefix, min_id, max_id = category_rules[self.category]
        if prefix != expected_prefix:
            raise ValueError(
                f"Category {self.category} requires ID prefix 'ENT-{expected_prefix}-', got '{self.entity_id}'"
            )
        if not (min_id <= self.numeric_id <= max_id):
            raise ValueError(
                f"Category {self.category} requires numeric_id in range [{min_id}..{max_id}], got {self.numeric_id}"
            )

        return self
