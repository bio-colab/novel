#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
NARRATIVE ENTITY EXTRACTOR & ARABIC NER (مستخرج الكيانات والشخصيات السردية)
Project: Narrative World OS / Framework
License: MIT
==============================================================================
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass
class ExtractedCharacter:
    entity_id: str
    numeric_id: int
    name: str
    mentions_count: int
    first_seen_line: int
    inferred_role: str = "شخصية رئيسية / فاعل سردي"
    inferred_tic: Optional[str] = None
    inferred_location: Optional[str] = None
    aliases: List[str] = field(default_factory=list)


@dataclass
class ExtractedObject:
    entity_id: str
    name: str
    category: str  # VEHICLE, PROP, LANDMARK
    mentions_count: int
    first_seen_line: int
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExtractedEntities:
    characters: List[ExtractedCharacter] = field(default_factory=list)
    vehicles: List[ExtractedObject] = field(default_factory=list)
    props: List[ExtractedObject] = field(default_factory=list)
    landmarks: List[ExtractedObject] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "characters_count": len(self.characters),
            "vehicles_count": len(self.vehicles),
            "props_count": len(self.props),
            "landmarks_count": len(self.landmarks),
            "characters": [c.__dict__ for c in self.characters],
            "vehicles": [v.__dict__ for v in self.vehicles],
            "props": [p.__dict__ for p in self.props],
            "landmarks": [l.__dict__ for l in self.landmarks],
        }


class NarrativeEntityExtractor:
    """Extracts narrative characters, vehicles, props, and landmarks from Arabic text."""

    # Common non-character words following speech/action verbs
    STOP_WORDS: Set[str] = {
        "أحدهم", "الآخر", "أحد", "الجميع", "الكل", "الصوت", "الظلام", "البرد", "الريح",
        "الرصاص", "المحرك", "القطار", "الوقت", "الضوء", "الليل", "الفجر", "الرمل",
        "شيء", "أحدنا", "كلهم", "أحدكم", "الرجل", "الضابط", "السجين", "الحارس", "العامل",
        "نفسه", "هذا", "ذلك", "تلك", "هؤلاء", "هنا", "هناك", "فجأة", "قائلاً", "بصوت",
        "دون", "حين", "بعد", "قبل", "ثم", "كيف", "أين", "متى", "ماذا", "لماذا", "هل",
        "سوى", "إلا", "غير", "مع", "في", "من", "إلى", "على", "عن", "حتى"
    }

    # Dialogue and narrative action trigger verbs
    SPEECH_VERBS = [
        "قال", "قالت", "صاح", "صرخ", "تمتم", "هتف", "سأل", "أجاب",
        "رد", "همس", "التفت", "تطلع", "تابع", "أضاف", "أردف", "غمغم"
    ]

    # Titles and naming patterns
    HONORIFICS = ["أبو", "حجي", "سيد", "الشيخ", "الضابط", "الملازم", "الشاويش", "الحارس", "السجين"]

    # Known recurring props and artifacts in dramatic survival narratives
    PROP_PATTERNS = [
        ("بندقية", "سلاح ناري فردي"),
        ("كلاشينكوف", "بندقية آلية"),
        ("مسدس", "سلاح ناري خفيف"),
        ("سلك", "أداة صيانة وربط معدني"),
        ("مفتاح", "أداة ميكانيكية وربط"),
        ("برميل", "وعاء تخزين سوائل"),
        ("طلقات", "ذخيرة بالستية"),
        ("ساعة", "أداة قياس زمنية"),
        ("وصل", "وثيقة ورقية إدارية"),
        ("حذاء", "ملبس واقٍ"),
        ("حصاة", "أثر طبيعي رمزي"),
        ("حقيبة", "وعاء حفظ أمتعة"),
        ("خرطوم", "أنبوب نقل مائع"),
        ("بطارية", "مصدر طاقة كهروحراري"),
    ]

    # Vehicle / Container patterns
    VEHICLE_PATTERNS = [
        ("قطار", "train_convoy"),
        ("قاطرة", "locomotive_engine"),
        ("كابينة", "driver_cabin"),
        ("عربة", "enclosed_car"),
        ("منصة", "observation_platform"),
        ("غواصة", "submarine_vessel"),
        ("سفينة", "marine_ship"),
        ("مركبة", "surface_vehicle"),
        ("شاحنة", "cargo_truck"),
    ]

    # Spatial landmarks
    LANDMARK_PATTERNS = [
        ("سكة", "railway_track"),
        ("صحراء", "arid_desert"),
        ("بادية", "desert_steppe"),
        ("هور", "marshland"),
        ("تل", "desert_ridge"),
        ("محطة", "remote_station"),
        ("سجن", "prison_fortress"),
    ]

    # Roles vocabulary mapping
    ROLE_HINTS = {
        "قائد": "قائد الحرس / آمر القوة",
        "سجان": "حارس سجون / سلطة ميدانية",
        "حارس": "حارس أمني",
        "سجين": "سجين محتجز",
        "ممرض": "مسعف طبي",
        "عامل": "عامل خدمة وصيانة",
        "مقاتل": "مقاتل / محارب عسكري",
        "مهرب": "مهرب / وسيط تجاري",
        "مدير": "مسؤول إداري",
    }

    # Tics and compulsive behavioral gestures patterns
    TIC_PATTERNS = [
        (re.compile(r"مسح\s+الكفين|يمسح\s+كفيه"), "مسح الكفين الدائم بالبنطال"),
        (re.compile(r"فرك\s+الجيب|يفرك\s+بطانة"), "فرك بطانة الجيب الفارغ"),
        (re.compile(r"اصطكاك\s+الأسنان|تصطك\s+أسنانه"), "اصطكاك الأسنان اللاإرادي من الرعب والصقيع"),
        (re.compile(r"تدوير\s+الإبهام|يدور\s+إبهامه"), "تدوير الإبهام لمحو أثر الدم"),
        (re.compile(r"الضغط\s+على\s+الظفر|يضغط\s+ظفره"), "الضغط على منبت الظفر حتى يبيض"),
        (re.compile(r"تحسس\s+الندبة|يتحسس\s+ندبته"), "تحسس ندبة الفك بالسبابة"),
        (re.compile(r"فحص\s+المفاصل|يفحص\s+مفاصل"), "فحص مفاصل القبضتين في العتمة"),
        (re.compile(r"غسل\s+الكفين\s+بالرمل|يغسل\s+يديه"), "غسل الكفين بالرمل والضحك العصبي"),
    ]

    def __init__(self):
        pass

    def extract(self, text: str) -> ExtractedEntities:
        lines = text.splitlines()
        candidate_names: Counter[str] = Counter()
        name_first_seen: Dict[str, int] = {}
        name_roles: Dict[str, Counter[str]] = defaultdict(Counter)
        name_tics: Dict[str, str] = {}
        name_contexts: Dict[str, List[str]] = defaultdict(list)

        # 1. Regex for speech patterns: e.g. "قال خالد", "صاح سردار", "همس أبو علي"
        speech_verbs_pattern = "|".join(self.SPEECH_VERBS)
        honorifics_pattern = "|".join(self.HONORIFICS)

        # Pattern: [Speech Verb] + optional honorific + [Name (1 to 2 words)]
        speech_regex = re.compile(
            rf"\b(?:{speech_verbs_pattern})\s+(?:({honorifics_pattern})\s+)?([^\s\.\،\,\:\!\؟\(\)\«\»]+(?:\s+[^\s\.\،\,\:\!\؟\(\)\«\»]+)?)\b",
            re.UNICODE
        )

        # Direct honorifics pattern anywhere: "أبو علي", "حجي عمار"
        honorific_regex = re.compile(
            rf"\b({honorifics_pattern})\s+([^\s\.\،\,\:\!\؟\(\)\«\»]+)\b",
            re.UNICODE
        )

        for line_no, line in enumerate(lines, start=1):
            stripped = line.strip()
            if not stripped:
                continue

            # Detect speech occurrences
            for match in speech_regex.finditer(stripped):
                hon = match.group(1)
                raw_name = match.group(2).strip()
                full_name = f"{hon} {raw_name}".strip() if hon else raw_name

                # Clean name tokens
                full_name = re.sub(r"[^\u0621-\u064A\s]", "", full_name).strip()
                tokens = full_name.split()
                if not tokens:
                    continue

                lead_token = tokens[0]
                if lead_token in self.STOP_WORDS:
                    continue

                # Take first word or two words if prefixed with honorific
                norm_name = " ".join(tokens[:2]) if (hon or tokens[0] in self.HONORIFICS) else tokens[0]

                if len(norm_name) >= 3 and norm_name not in self.STOP_WORDS:
                    candidate_names[norm_name] += 1
                    if norm_name not in name_first_seen:
                        name_first_seen[norm_name] = line_no
                    if len(name_contexts[norm_name]) < 5:
                        name_contexts[norm_name].append(stripped)

            # Detect honorific mentions
            for match in honorific_regex.finditer(stripped):
                hon = match.group(1).strip()
                raw_name = match.group(2).strip()
                full_name = f"{hon} {raw_name}".strip()
                full_name = re.sub(r"[^\u0621-\u064A\s]", "", full_name).strip()
                if full_name and raw_name not in self.STOP_WORDS and len(raw_name) >= 3:
                    candidate_names[full_name] += 1
                    if full_name not in name_first_seen:
                        name_first_seen[full_name] = line_no

            # Look for tics and link to nearby character mentions
            for tic_re, tic_desc in self.TIC_PATTERNS:
                if tic_re.search(stripped):
                    # Check which known character is mentioned in this line
                    for cand in candidate_names:
                        if cand in stripped and cand not in name_tics:
                            name_tics[cand] = tic_desc

        # Determine frequency threshold: for short texts or snippets (< 200 lines), count >= 1 is accepted
        min_threshold = 1 if len(lines) < 200 else 2

        characters: List[ExtractedCharacter] = []
        char_id_counter = 1001

        # Sort candidate names by frequency descending
        for name, count in candidate_names.most_common():
            if count < min_threshold and not any(name.startswith(h) for h in ["أبو ", "حجي "]):
                continue

            # Incur role from contexts
            contexts = " ".join(name_contexts[name])
            inferred_role = "شخصية رئيسية / فاعل سردي"
            for role_kw, role_title in self.ROLE_HINTS.items():
                if role_kw in contexts:
                    inferred_role = role_title
                    break

            inferred_tic = name_tics.get(name)

            char_obj = ExtractedCharacter(
                entity_id=f"ENT-CHAR-{char_id_counter}",
                numeric_id=char_id_counter,
                name=name,
                mentions_count=count,
                first_seen_line=name_first_seen.get(name, 1),
                inferred_role=inferred_role,
                inferred_tic=inferred_tic,
            )
            characters.append(char_obj)
            char_id_counter += 1

        props, vehicles, landmarks = self._extract_objects(text)

        return ExtractedEntities(
            characters=characters,
            vehicles=vehicles,
            props=props,
            landmarks=landmarks,
        )

    @classmethod
    def _match_keyword_occurrences(cls, kw: str, text: str) -> List[re.Match]:
        pattern = rf"(?:^|[\s\.\،\,\:\!\؟\(\)\«\»\-\"\'\[\]])(?:(?:و|ف|ب|ك|ل)?(?:ال)?|(?:لل))?{re.escape(kw)}(?:$|[\s\.\،\,\:\!\؟\(\)\«\»\-\"\'\[\]])"
        return list(re.finditer(pattern, text, re.UNICODE))

    def _extract_objects(self, text: str) -> Tuple[List[ExtractedObject], List[ExtractedObject], List[ExtractedObject]]:
        # 2. Extract Props
        props: List[ExtractedObject] = []
        prop_id_counter = 3001
        for kw, prop_type in self.PROP_PATTERNS:
            matches = self._match_keyword_occurrences(kw, text)
            if matches:
                p_obj = ExtractedObject(
                    entity_id=f"ENT-PROP-{prop_id_counter}",
                    name=kw,
                    category="PROP",
                    mentions_count=len(matches),
                    first_seen_line=text[:matches[0].start()].count("\n") + 1,
                    properties={"type": prop_type}
                )
                props.append(p_obj)
                prop_id_counter += 1

        # 3. Extract Vehicles
        vehicles: List[ExtractedObject] = []
        veh_id_counter = 2001
        for kw, veh_type in self.VEHICLE_PATTERNS:
            matches = self._match_keyword_occurrences(kw, text)
            if matches:
                v_obj = ExtractedObject(
                    entity_id=f"ENT-VEH-{veh_id_counter}",
                    name=kw,
                    category="VEHICLE",
                    mentions_count=len(matches),
                    first_seen_line=text[:matches[0].start()].count("\n") + 1,
                    properties={"type": veh_type}
                )
                vehicles.append(v_obj)
                veh_id_counter += 1

        # 4. Extract Landmarks
        landmarks: List[ExtractedObject] = []
        land_id_counter = 4001
        for kw, land_type in self.LANDMARK_PATTERNS:
            matches = self._match_keyword_occurrences(kw, text)
            if matches:
                l_obj = ExtractedObject(
                    entity_id=f"ENT-LAND-{land_id_counter}",
                    name=kw,
                    category="LANDMARK",
                    mentions_count=len(matches),
                    first_seen_line=text[:matches[0].start()].count("\n") + 1,
                    properties={"type": land_type}
                )
                landmarks.append(l_obj)
                land_id_counter += 1

        return props, vehicles, landmarks
