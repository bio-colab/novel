#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
WORLD ENGINE - CAUSALITY GRAPH & DAG ANALYZER
Project: «قطار الرمل» (Sand Train) - Narrative Engineering Core / Framework
Milestone: MILESTONE-NARRATIVE-OS-v1.0 (Phase 3 Decoupling)
License: MIT
==============================================================================
"""

from __future__ import annotations

from collections import defaultdict, deque
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

import yaml


class CausalityDAGVerifier:
    """Generic engine that verifies acyclicity and causal flow in narrative event chains."""

    def __init__(self, events_data: Optional[List[Dict[str, Any]]] = None):
        self.events: List[Dict[str, Any]] = events_data or []
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.adj: Dict[str, List[str]] = defaultdict(list)
        self.in_degree: Dict[str, int] = defaultdict(int)
        self.out_degree: Dict[str, int] = defaultdict(int)

        if self.events:
            self.build_graph()

    @classmethod
    def from_yaml_file(cls, path: Path) -> CausalityDAGVerifier:
        """Instantiate verifier from a causality_graph.yaml file."""
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        events = data.get("events", [])
        return cls(events)

    def build_graph(self) -> None:
        """Constructs graph adjacency and degree records from loaded events."""
        self.nodes = {evt["id"]: evt for evt in self.events}
        for evt_id in self.nodes:
            self.in_degree[evt_id] = 0
            self.out_degree[evt_id] = 0

        for evt in self.events:
            src_id = evt["id"]
            for target_id in evt.get("causes", []):
                self.adj[src_id].append(target_id)
                self.out_degree[src_id] += 1
                self.in_degree[target_id] += 1

    def verify_dag_acyclicity(self) -> Tuple[bool, List[str]]:
        """Verifies topological acyclicity using Kahn's algorithm."""
        in_deg = self.in_degree.copy()
        queue = deque([node for node in self.nodes if in_deg[node] == 0])
        visited_count = 0
        topological_order: List[str] = []

        while queue:
            curr = queue.popleft()
            visited_count += 1
            topological_order.append(curr)
            for neighbor in self.adj[curr]:
                in_deg[neighbor] -= 1
                if in_deg[neighbor] == 0:
                    queue.append(neighbor)

        is_acyclic = (visited_count == len(self.nodes))
        return is_acyclic, topological_order
