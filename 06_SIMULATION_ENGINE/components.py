#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
COMPONENT DEFINITIONS (مكونات الكيانات التركيبية للمحاكاة)
Project: «قطار الرمل» (Sand Train) - Narrative Engineering Simulation Engine
Framework Charter: «نحن نُحلل ونُقيّم.. ولا نُقوّم»
==============================================================================
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class PositionComponent:
    """Spatial coordinates and carriage assignment."""
    car_id: str
    x_m: float
    y_m: float
    is_outside: bool = False


@dataclass
class ThermodynamicComponent:
    """Body thermodynamics and exposure resistance."""
    clothing_insulation_clo: float = 1.3  # Standard desert winter wool/felt
    surface_area_m2: float = 1.8          # Adult human surface area
    metabolic_rate_w: float = 85.0        # Resting/shivering metabolic output


@dataclass
class BiomechanicalComponent:
    """Thermal states, motor skills, and shivering progression."""
    core_temp_c: float = 36.8
    fingers_temp_c: float = 24.5
    motor_dexterity: float = 1.0
    shivering_stage: str = "none"
    respiration_water_loss_l: float = 0.0
    stamina: float = 1.0
    is_conscious: bool = True
    is_alive: bool = True


@dataclass
class PsychologicalComponent:
    """Stress, panic index, and neurotic motor tic triggers."""
    stress_level: float = 0.5
    panic_index: float = 0.1
    authority_weight: float = 0.5
    tic_name: Optional[str] = None
    tic_trigger_active: bool = False


@dataclass
class EpistemicComponent:
    """Perceptual boundaries and sensory channels."""
    ambient_lux: float = 0.8
    auditory_reach_db: float = 65.0
    active_listening_cars: List[str] = field(default_factory=list)
    known_facts: List[str] = field(default_factory=list)
    blind_spots: List[str] = field(default_factory=list)
