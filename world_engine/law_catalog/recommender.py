#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
DOMAIN LAW RECOMMENDER (مستكشف ومقترح القوانين الفيزيائية الذكي)
Project: Narrative World OS / Framework
License: MIT
==============================================================================
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from world_engine.law_catalog.catalog import DOMAIN_PACKS


@dataclass
class LawRecommendationReport:
    recommended_pack_id: str
    pack_title: str
    confidence_score: float
    matched_keywords: List[str]
    suggested_rules: List[Dict[str, Any]]
    explanation: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "recommended_pack_id": self.recommended_pack_id,
            "pack_title": self.pack_title,
            "confidence_score": round(self.confidence_score, 2),
            "matched_keywords": self.matched_keywords,
            "suggested_rules_count": len(self.suggested_rules),
            "explanation": self.explanation,
        }

    def to_rules_manifest_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": "1.0.0",
            "domain_count": len(set(r.get("domain", "general") for r in self.suggested_rules)),
            "rules": self.suggested_rules,
        }


class DomainLawRecommender:
    """Analyzes text setting and genre to recommend domain-specific physical law packs."""

    PACK_KEYWORDS: Dict[str, List[str]] = {
        "deep_sea_submarine": [
            "غواصة", "أعماق", "بحر", "محيط", "طوربيد", "ضغط الماء", "سونار",
            "غطس", "عمق", "بدن", "غرق", "submarine", "sonar", "depth", "torpedo"
        ],
        "orbital_space_station": [
            "فضاء", "محطة مدارية", "مدار", "انعدام الجاذبية", "صاروخ", "إشعاع",
            "كويكب", "فراغ", "أكسجين مداري", "نيزك", "space", "orbit", "vacuum", "station"
        ],
        "desert_caravan_survival": [
            "صحراء", "عطش", "قيظ", "رمضاء", "شمس حارقة", "سموم", "سراب",
            "قافلة", "كثبان", "هجير", "ناقة", "جمل", "desert", "dune", "mirage"
        ],
        "closed_cold_transport": [
            "قطار", "عربة", "سكة", "صقيع", "ثلج", "ديزل", "مكابح", "قاطرة",
            "حديد", "صاج", "برد قارس", "train", "railway", "freezing", "diesel"
        ],
    }

    def __init__(self):
        pass

    def recommend_for_text(self, text: str, genre_hint: Optional[str] = None) -> LawRecommendationReport:
        scores: Dict[str, int] = {}
        matched_kw: Dict[str, List[str]] = {}

        for pack_id, kw_list in self.PACK_KEYWORDS.items():
            hits = []
            for kw in kw_list:
                # Prefix tolerant regex
                pattern = rf"(?:^|[\s\.\،\,\:\!\؟\(\)\«\»\-\"\'\[\]])(?:(?:و|ف|ب|ك|ل)?(?:ال)?|(?:لل))?{re.escape(kw)}(?:$|[\s\.\،\,\:\!\؟\(\)\«\»\-\"\'\[\]])"
                if re.search(pattern, text, re.IGNORECASE | re.UNICODE):
                    hits.append(kw)
            matched_kw[pack_id] = hits
            scores[pack_id] = len(hits)

        # Genre hint bonus
        if genre_hint:
            for pack_id, pack_data in DOMAIN_PACKS.items():
                if pack_data.get("genre") == genre_hint:
                    scores[pack_id] = scores.get(pack_id, 0) + 5

        # Select highest score
        best_pack_id = max(scores, key=lambda k: scores[k])
        best_score = scores[best_pack_id]

        if best_score == 0:
            # Default fallback to closed cold transport
            best_pack_id = "closed_cold_transport"
            confidence = 0.5
        else:
            confidence = min(1.0, 0.5 + (best_score * 0.1))

        pack_info = DOMAIN_PACKS[best_pack_id]
        suggested_rules = pack_info["rules"]
        hits = matched_kw.get(best_pack_id, [])

        explanation = (
            f"تم التعرف على بيئة الرواية كـ [{pack_info['title']}] استناداً إلى الكلمات الدلالية: "
            f"({', '.join(hits[:5]) if hits else 'السياق الافتراضي'}). "
            f"تقترح المنظومة تفعيل {len(suggested_rules)} قوانين حتمية لمطابقة فيزياء هذا الفضاء السردي."
        )

        return LawRecommendationReport(
            recommended_pack_id=best_pack_id,
            pack_title=pack_info["title"],
            confidence_score=confidence,
            matched_keywords=hits,
            suggested_rules=suggested_rules,
            explanation=explanation,
        )
