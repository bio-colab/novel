#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
NARRATIVE CAUSALITY & TEMPORAL DAG MINER (منقب السببية والكرونولوجيا التلقائي)
Project: Narrative World OS / Framework
License: MIT
==============================================================================
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from world_engine.dag import CausalityDAGVerifier, CausalCycleError


@dataclass
class MinedEvent:
    id: str
    numeric_id: int
    name: str
    event_type: str
    line_number: int
    minute_estimate: int
    causes: List[str] = field(default_factory=list)
    caused_by: List[str] = field(default_factory=list)
    raw_trigger: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.event_type,
            "line": self.line_number,
            "minute": self.minute_estimate,
            "causes": self.causes,
        }


@dataclass
class CausalityMiningReport:
    total_events: int
    total_causal_edges: int
    causal_density: float
    is_acyclic: bool
    topological_order: List[str]
    orphan_causes: List[str]
    orphan_effects: List[str]
    events: List[MinedEvent] = field(default_factory=list)

    def to_yaml_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": "1.0.0",
            "events_count": self.total_events,
            "causal_edges_count": self.total_causal_edges,
            "causal_density": round(self.causal_density, 3),
            "is_acyclic": self.is_acyclic,
            "events": [e.to_dict() for e in self.events],
        }


class NarrativeCausalityMiner:
    """Extracts chronological narrative events and infers directed causal links from Arabic text."""

    # Event signature patterns (action/failure keywords)
    EVENT_SIGNATURES = [
        # Combat & Sabotage
        (re.compile(r"تخريب\s+السكة|لغم\s+أرضي|تفجير|عبوة"), "Combat_Sabotage", "تخريب السكة وزرع اللغم"),
        (re.compile(r"صدمة\s+الارتداد|ارتداد\s+الحديد|صدمة\s+التوقف"), "Physical_Shock", "صدمة الارتداد الميكانيكي"),
        (re.compile(r"انكسار\s+أنبوب|انكسر\s+أنبوب|كسر\s+أنبوب\s+الوقود|تسرب\s+الديزل"), "Mechanical_Failure", "انكسار أنبوب الوقود وتسرب الديزل"),
        (re.compile(r"إطباق\s+المكابح|أطبقت\s+المكابح|تفريغ\s+الهواء|مكابح\s+ويستنغهاوس"), "Pneumatic_Lock", "تفريغ الهواء وإطباق المكابح الهوائية"),
        (re.compile(r"توقف\s+القطار|توقف\s+المحرك|سكون\s+العجلات"), "Locomotive_Stall", "توقف حركة المحرك وانحباس القطار"),
        (re.compile(r"انغلاق\s+الكابينة|سقوط\s+السقاطة|إقفال\s+الباب"), "Mechanical_State", "سقوط السقاطة وانغلاق كابينة السائق"),
        (re.compile(r"الكمين|إطلاق\s+النار|دوي\s+الرصاص|هجوم\s+المسلحين|زخات\s+الرصاص"), "Tactical_Ambush", "وقوع الكمين الليلي وإطلاق النار"),
        (re.compile(r"استشهاد\s+عباس|مقتل\s+عباس|إصابة\s+عباس"), "Casualty_Event", "إصابة عباس على المنصة الخلفية"),
        (re.compile(r"موال\s+عزيز|غناء\s+عزيز|صوت\s+المحمداوي"), "Psychological_Resonance", "انطلاق موال عزيز ورنين العتمة"),
        (re.compile(r"قفز\s+مهدي|هروب\s+مهدي|وثوب\s+مهدي"), "Tactical_Breach", "قفز مهدي من الباب المنزلق واختفاؤه"),
        (re.compile(r"انطفاء\s+البطاريات|انطفأت\s+المصابيح|العتمة\s+التامة"), "Electrical_Depletion", "نفاد البطاريات وانطفاء الإضاءة التلقائي"),
        (re.compile(r"إصلاح\s+أنبوب|ربط\s+السلك|سد\s+الأنبوب"), "Physical_Repair", "إصلاح أنبوب الوقود بالسلك المعدني"),
        (re.compile(r"تصلب\s+شمع\s+الديزل|تبلور\s+البارافين|تجمد\s+الوقود"), "Chemical_Transition", "تصلب شمع البارافين في ريح الصقيع"),
        (re.compile(r"بزوغ\s+الفجر|الفجر\s+الكاذب|طلوع\s+الضوء"), "Chrono_Milestone", "بزوغ الفجر الكاذب واستنزاف الأكسجين"),
    ]

    # Explicit causal conjunctions in Arabic
    CAUSAL_CONNECTORS = [
        re.compile(r"بسبب\s+(.*?)(?:،|,|\.|\n|$)"),
        re.compile(r"أدى\s+إلى\s+(.*?)(?:،|,|\.|\n|$)"),
        re.compile(r"تسبب\s+في\s+(.*?)(?:،|,|\.|\n|$)"),
        re.compile(r"إثر\s+(.*?)(?:،|,|\.|\n|$)"),
        re.compile(r"في\s+أعقاب\s+(.*?)(?:،|,|\.|\n|$)"),
        re.compile(r"مما\s+جعل\s+(.*?)(?:،|,|\.|\n|$)"),
        re.compile(r"فـ(أدى|انكسر|أطبق|توقف|تسرب|انطفأ|انقطع)"),
    ]

    # Temporal milestone indicators to calibrate minute progression
    TEMPORAL_ANCHORS = [
        (re.compile(r"السابعة\s+مساء|غروب\s+الشمس|العطل\s+الأول"), 0),
        (re.compile(r"التاسعة\s+ليلا|مرور\s+ساعتين|اشتداد\s+الصقيع"), 120),
        (re.compile(r"منتصف\s+الليل|الساعة\s+الثانية\s+عشرة|الكمين"), 300),
        (re.compile(r"الثالثة\s+صباحا|ذروة\s+التجمد|انطفاء\s+الضوء"), 480),
        (re.compile(r"الفجر|الضوء\s+الأول|السادسة\s+صباحا"), 645),
    ]

    def __init__(self):
        pass

    def mine_events_from_text(self, text: str) -> List[MinedEvent]:
        lines = text.splitlines()
        detected_events: List[MinedEvent] = []
        event_counter = 1
        seen_event_types: Set[str] = set()

        current_minute = 0

        for line_no, line in enumerate(lines, start=1):
            stripped = line.strip()
            if not stripped:
                continue

            # Update temporal minute if temporal anchor hits
            for t_re, t_min in self.TEMPORAL_ANCHORS:
                if t_re.search(stripped):
                    current_minute = max(current_minute, t_min)

            # Match event signatures
            for sig_re, evt_type, default_name in self.EVENT_SIGNATURES:
                if sig_re.search(stripped):
                    # Dedup multiple mentions of same event type if within 5 lines
                    if evt_type in seen_event_types:
                        # Allow recurrence only if significantly later
                        prev_same = [e for e in detected_events if e.event_type == evt_type]
                        if prev_same and (line_no - prev_same[-1].line_number) < 5:
                            continue

                    evt = MinedEvent(
                        id=f"EVT-{event_counter:03d}",
                        numeric_id=event_counter,
                        name=default_name,
                        event_type=evt_type,
                        line_number=line_no,
                        minute_estimate=current_minute,
                        raw_trigger=stripped[:80],
                    )
                    detected_events.append(evt)
                    seen_event_types.add(evt_type)
                    event_counter += 1

        # If no specific events were captured, synthesize chronological events from chapters/paragraphs
        if len(detected_events) < 2:
            return self._synthesize_fallback_events(text)

        # Infer directed causal edges between adjacent and related events
        self._infer_causal_edges(detected_events, text)

        return detected_events

    def _infer_causal_edges(self, events: List[MinedEvent], text: str) -> None:
        """Infers directed causal edges based on temporal sequence and causal affinity rules."""
        # Canonical causal affinities (Event_A type -> naturally causes Event_B type)
        AFFINITIES = {
            "Combat_Sabotage": ["Physical_Shock", "Mechanical_Failure"],
            "Physical_Shock": ["Mechanical_Failure", "Pneumatic_Lock", "Mechanical_State"],
            "Mechanical_Failure": ["Pneumatic_Lock", "Locomotive_Stall"],
            "Pneumatic_Lock": ["Locomotive_Stall"],
            "Tactical_Ambush": ["Casualty_Event", "Tactical_Breach"],
            "Casualty_Event": ["Psychological_Resonance"],
            "Electrical_Depletion": ["Chrono_Milestone"],
            "Chemical_Transition": ["Locomotive_Stall"],
            "Physical_Repair": ["Chrono_Milestone"],
        }

        # 1. Connect affinity matches forward in time
        for i, src in enumerate(events):
            possible_targets = AFFINITIES.get(src.event_type, [])
            for j in range(i + 1, len(events)):
                tgt = events[j]
                if tgt.event_type in possible_targets:
                    if tgt.id not in src.causes:
                        src.causes.append(tgt.id)
                        tgt.caused_by.append(src.id)
                    break

        # 2. Sequential fallback: ensure every event has at least one chronological successor
        # (avoid completely disconnected orphan chains)
        for i in range(len(events) - 1):
            curr = events[i]
            nxt = events[i + 1]
            if not curr.causes:
                curr.causes.append(nxt.id)
                nxt.caused_by.append(curr.id)

    def _synthesize_fallback_events(self, text: str) -> List[MinedEvent]:
        """Synthesizes minimal chronological events for short snippets or generic texts."""
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        total_lines = len(lines)
        events = []
        ev_defs = [
            ("EVT-001", "الحدث التأسيسي الأولي وتغير البيئة", 0, "Initial_State"),
            ("EVT-002", "تصاعد الأزمة وانحباس الشخصيات", 180, "Crisis_Climax"),
            ("EVT-003", "محاولة النجاة والمصير الختامي", 360, "Resolution"),
        ]
        for idx, (e_id, e_name, e_min, e_type) in enumerate(ev_defs, start=1):
            line_pos = max(1, int((idx / len(ev_defs)) * total_lines))
            events.append(MinedEvent(
                id=e_id,
                numeric_id=idx,
                name=e_name,
                event_type=e_type,
                line_number=line_pos,
                minute_estimate=e_min,
                causes=[ev_defs[idx][0]] if idx < len(ev_defs) else [],
            ))
        return events

    def analyze_causal_graph(self, events: List[MinedEvent]) -> CausalityMiningReport:
        """Audits the mined event graph with CausalityDAGVerifier."""
        raw_events = [e.to_dict() for e in events]
        verifier = CausalityDAGVerifier(raw_events)

        is_acyclic, topo_order = verifier.verify_dag_acyclicity()

        total_nodes = len(events)
        total_edges = sum(len(e.causes) for e in events)
        causal_density = (total_edges / total_nodes) if total_nodes > 0 else 0.0

        # Orphan detection
        orphan_causes = [e.id for e in events if not e.causes and e.id != events[-1].id]
        orphan_effects = [e.id for e in events if not e.caused_by and e.id != events[0].id]

        return CausalityMiningReport(
            total_events=total_nodes,
            total_causal_edges=total_edges,
            causal_density=causal_density,
            is_acyclic=is_acyclic,
            topological_order=topo_order,
            orphan_causes=orphan_causes,
            orphan_effects=orphan_effects,
            events=events,
        )

    def mine_and_report(self, text: str) -> CausalityMiningReport:
        events = self.mine_events_from_text(text)
        return self.analyze_causal_graph(events)
