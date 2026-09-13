#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Systems package for Sand Train Simulation Engine.
"""

try:
    from .thermodynamics import ThermodynamicSystem
    from .neurology import NeurologySystem
    from .acoustics import AcousticsSystem
    from .resources import ResourcesSystem
    from .moral_entropy import MoralEntropySystem
except (ImportError, ValueError):
    from systems.thermodynamics import ThermodynamicSystem
    from systems.neurology import NeurologySystem
    from systems.acoustics import AcousticsSystem
    from systems.resources import ResourcesSystem
    from systems.moral_entropy import MoralEntropySystem

__all__ = [
    "ThermodynamicSystem",
    "NeurologySystem",
    "AcousticsSystem",
    "ResourcesSystem",
    "MoralEntropySystem"
]
