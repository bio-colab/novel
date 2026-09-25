#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
WORLD ENGINE - NARRATIVE INGESTION SUBSYSTEM (محرك استيراد وتأريض النصوص السردية)
Project: Narrative World OS / Framework
Milestone: MILESTONE-NARRATIVE-OS-v1.0 (Phase 1 Universal Ingestion)
License: MIT
==============================================================================
"""

from world_engine.ingest.text_chunker import NarrativeTextChunker, ChunkedDocument
from world_engine.ingest.narrative_ner import NarrativeEntityExtractor, ExtractedEntities
from world_engine.ingest.sensory_grounder import SensoryPhysicalGrounder, GroundedEnvironment
from world_engine.ingest.manifest_synthesizer import WorldManifestSynthesizer

__all__ = [
    "NarrativeTextChunker",
    "ChunkedDocument",
    "NarrativeEntityExtractor",
    "ExtractedEntities",
    "SensoryPhysicalGrounder",
    "GroundedEnvironment",
    "WorldManifestSynthesizer",
]
