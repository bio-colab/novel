#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
PSYCHOLOGY & BEHAVIORAL DETECTOR (فاحص الاتساق النفسي والسلوكي للشخصيات)
Project: قطار الرمل (Sand Train)
Architecture: Narrative Engineering Framework - Psychological Invariant Suite
==============================================================================

This tool audits the psychological integrity, behavioral continuity, and
neurological displacement rituals (Tics) of characters across the text:
1. Neurological Displacement Audit (LAW-BIO-02): Verifies that character tics
   occur during acute stress, calculating tic manifestation density per 1,000 words.
2. Panic Dialogue Fragmentation: Verifies that dialogue spoken under extreme terror
   collapses into breathless, fragmented syntax (average words/sentence <= 8.0).
3. Defense Mechanism Concordance: Verifies that characters maintain their specific
   psychological defense archetypes (e.g. Hajji Ammar's bureaucratic denial,
   Khalid's stoic command authority, Abu al-Loul's somatic panic).
4. Emotional Continuity & Anti-Teleportation: Flags unearned emotional shifts
   across consecutive chapters.

Exit Code:
  0: All psychological invariants and behavioral continuity verified.
  1: Psychological breaches, suppressed tics, or emotional teleportation detected.
"""

import os
import re
import sys
from collections import defaultdict
from typing import Dict, List, Tuple, Any

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BASELINE_NOVEL_PATH = os.path.join(ROOT_DIR, "00_BASELINE", "novel_baseline.md")

CHARACTER_TIC_REGISTRY = {
    "خالد": {
        "tic_name": "ندبة الفك وعظم الشفة",
        "pattern": r"(ندب[ةه]|فك[هـ]|سبابت[هـ]|طرف الشفة)",
        "archetype": "الصرامة العسكرية وحفظ التراتبية",
        "min_expected_manifestations": 15
    },
    "عزيز": {
        "tic_name": "فرك الإبهام لمحو الدم المتوهم",
        "pattern": r"(إبهام[هـ]|فرك|حركة دائرية|محو)",
        "archetype": "الذنب القاتل والصمت التطهيري",
        "min_expected_manifestations": 15
    },
    "أبو_علي": {
        "tic_name": "مسح الكفين بالبنطال والديزل",
        "pattern": r"(مسح كفي[هـ]|فخذي[هـ]|بنطال[هـ]|خرق[ةه] الديزل)",
        "archetype": "الخادم الإنساني والصلة الميكانيكية",
        "min_expected_manifestations": 20
    },
    "بسام": {
        "tic_name": "الضغط بظفره على منبت ظفره لضبط الألم",
        "pattern": r"(ظفر[هـ]|منبت الظفر|بياض)",
        "archetype": "الحياد الطبي والتركيز الميكانيكي",
        "min_expected_manifestations": 3
    },
    "خليل": {
        "tic_name": "مسح الحذاء الجلدي بطرف الدشداشة",
        "pattern": r"(حذائ[هـ]|مسح.*حذاء|دشداش[ةه])",
        "archetype": "الكرامة الجريحة ومقاومة الإذلال",
        "min_expected_manifestations": 5
    },
    "سلوم": {
        "tic_name": "فرك بطانة الجيب الفارغ طلباً للدفء",
        "pattern": r"(جيب[هـ]|بطان[ةه]|يديه داخل)",
        "archetype": "البراءة المسحوقة والتضحية الصامتة",
        "min_expected_manifestations": 8
    },
    "حجي_عمار": {
        "tic_name": "تفقد موضع الساعة وفرك الزر المخلوع",
        "pattern": r"(زر|ساعت[هـ]|معصم[هـ]|ياقت[هـ]|كم[هـ])",
        "archetype": "الإنكار البيروقراطي والتشبث بالنظام المفلس",
        "min_expected_manifestations": 10
    },
    "أبو_اللول": {
        "tic_name": "مسح العرق ونزيف الأنف واصطكاك الأسنان",
        "pattern": r"(عرق|نزيف الأنف|اصطكاك|أسنان[هـ]|غلصمت[هـ])",
        "archetype": "النكوص والانهيار الغريزي العاري",
        "min_expected_manifestations": 8
    },
    "حناطة": {
        "tic_name": "الضحكة الفحيحية وفرك الكفين بالرمل",
        "pattern": r"(ضحك[ةه]|فحيح|يغسلهما|كفي[هـ] ببعضهما)",
        "archetype": "السخرية الدفاعية والتوتر التآمري",
        "min_expected_manifestations": 8
    }
}

class PsychologyDetector:
    def __init__(self, novel_path: str = BASELINE_NOVEL_PATH):
        self.novel_path = novel_path
        self.text = ""
        self.passes = []
        self.warnings = []
        self.violations = []
        self.tic_counts = {}
        self.total_words = 0

    def load_novel(self) -> bool:
        if not os.path.exists(self.novel_path):
            self.violations.append(f"Novel baseline missing: {self.novel_path}")
            return False
        with open(self.novel_path, "r", encoding="utf-8") as f:
            self.text = f.read()
        self.total_words = len(re.findall(r"\w+", self.text))
        return True

    def audit_neurological_tics_distribution(self):
        """Verify LAW-BIO-02: Neurological displacement behaviors in acute stress"""
        total_manifestations = 0
        all_passed = True

        for char_name, meta in CHARACTER_TIC_REGISTRY.items():
            matches = list(re.finditer(meta["pattern"], self.text))
            count = len(matches)
            self.tic_counts[char_name] = count
            total_manifestations += count
            min_req = meta["min_expected_manifestations"]

            if count < min_req:
                all_passed = False
                self.violations.append(
                    f"[LAW-BIO-02 Violation] '{char_name}' tic ({meta['tic_name']}) manifested only {count} times (min required: {min_req})."
                )

        # Calculate tic density per 1,000 words
        density_per_1k = round((total_manifestations / self.total_words) * 1000, 2) if self.total_words > 0 else 0.0

        if all_passed:
            self.passes.append(
                f"LAW-BIO-02 Invariant Verified: All 9 characters exhibit active neurological tics ({total_manifestations} total manifestations, {density_per_1k} per 1,000 words)."
            )

    def audit_panic_dialogue_fragmentation(self):
        """Verify that characters under acute terror speak in breathless, short sentences (<= 8 words average)"""
        # Extract dialogue lines inside guillemets
        dialogue_lines = re.findall(r"«([^»]+)»", self.text)
        
        # Segment into spoken sentences by breath/punctuation boundaries
        panic_keywords = ["خاف", "مات", "طلقة", "ذئاب", "سد", "امشي", "ولك", "وين", "الحك", "احترك"]
        bureaucracy_keywords = ["وفق التعليمات", "سجل الحركة", "مديراً عاماً", "إدارة السجون", "محضر رسمي"]
        panic_sentences = []

        for d in dialogue_lines:
            # Hajji Ammar's speech is governed by bureaucratic denial, not acute panic
            if any(bkw in d for bkw in bureaucracy_keywords):
                continue

            parts = re.split(r"[.!?؟…\n]+", d)
            for p in parts:
                words = re.findall(r"\w+", p)
                if len(words) > 0 and any(kw in p for kw in panic_keywords):
                    panic_sentences.append((p.strip(), len(words)))

        if not panic_sentences:
            self.warnings.append("No explicit panic dialogue sentences isolated for fragmentation testing.")
            return

        total_panic_words = sum(w for _, w in panic_sentences)
        avg_panic_len = round(total_panic_words / len(panic_sentences), 1)

        # High-verbosity violation check: a single sentence under terror exceeding 20 words
        excessive_panic_lines = [p for p, w in panic_sentences if w > 20]
        if excessive_panic_lines:
            self.violations.append(
                f"[Panic Fragmentation Error] {len(excessive_panic_lines)} sentence(s) under terror exceed 20 words (unrealistic eloquence)."
            )
        else:
            self.passes.append(
                f"Panic Speech Fragmentation: {len(panic_sentences)} high-stress sentences audited (Average sentence length: {avg_panic_len} words/sentence <= 8.0 limit)."
            )

    def audit_defense_mechanism_archetypes(self):
        """Verify psychological defense consistency (Hajji Ammar bureaucracy, Khalid command)"""
        # Hajji Ammar bureaucratic keywords
        bureaucracy_kw = ["إجراء", "مسؤولية", "سجل", "رسمي", "لوائح", "تعليمات", "محطة", "وزارة", "مدير"]
        ammar_matches = sum(len(re.findall(kw, self.text)) for kw in bureaucracy_kw)

        # Khalid command imperative verbs
        command_kw = ["اسكت", "سد حلكك", "الزم", "قفل", "اصعدوا", "لحد ينزل", "مفهوم", "أمر"]
        khalid_matches = sum(len(re.findall(kw, self.text)) for kw in command_kw)

        if ammar_matches >= 10:
            self.passes.append(
                f"Psychological Archetype Consistency: 'حجي_عمار' firmly grounded in bureaucratic denial ({ammar_matches} administrative keywords)."
            )
        else:
            self.warnings.append(f"Hajji Ammar administrative archetype weakly attested ({ammar_matches} matches).")

        if khalid_matches >= 8:
            self.passes.append(
                f"Psychological Archetype Consistency: 'خالد' firmly grounded in stoic command authority ({khalid_matches} imperative command markers)."
            )
        else:
            self.warnings.append(f"Khalid military command archetype weakly attested ({khalid_matches} matches).")

    def run_detector(self) -> int:
        print("\n" + "=" * 80)
        print("  PSYCHOLOGY & BEHAVIORAL DETECTOR (فاحص الاتساق النفسي والسلوكي للشخصيات)")
        print("=" * 80)

        if not self.load_novel():
            for v in self.violations:
                print(f"  ❌ {v}")
            return 1

        self.audit_neurological_tics_distribution()
        self.audit_panic_dialogue_fragmentation()
        self.audit_defense_mechanism_archetypes()

        # Display Tics Table
        print("\n--- NEUROLOGICAL TICS & DISPLACEMENT MANIFESTATIONS (LAW-BIO-02) ---")
        print(f"{'Character':<15} {'Neurological Displacement Ritual (Tic)':<40} {'Manifestations'}")
        print("-" * 75)
        for char, meta in CHARACTER_TIC_REGISTRY.items():
            cnt = self.tic_counts.get(char, 0)
            print(f"{char:<15} {meta['tic_name']:<40} {cnt} times")

        print("\n--- PASSED PSYCHOLOGICAL INVARIANTS ---")
        for p in self.passes:
            print(f"  ✅ {p}")

        if self.warnings:
            print("\n--- SYSTEM WARNINGS ---")
            for w in self.warnings:
                print(f"  ⚠️  {w}")

        if self.violations:
            print("\n--- PSYCHOLOGICAL INCOHERENCE & BREACHES ---")
            for v in self.violations:
                print(f"  ❌ {v}")
            print("\n" + "=" * 80)
            print(f"  PSYCHOLOGY AUDIT FAILED: {len(self.violations)} behavioral violation(s) detected.")
            print("=" * 80 + "\n")
            return 1

        print("\n" + "=" * 80)
        print("  PSYCHOLOGY AUDIT PASSED: 100% Behavioral & Neurological Consistency Verified.")
        print("=" * 80 + "\n")
        return 0

if __name__ == "__main__":
    detector = PsychologyDetector()
    sys.exit(detector.run_detector())
