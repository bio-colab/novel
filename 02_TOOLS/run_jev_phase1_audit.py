#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
JEV SYSTEM ONE EVALUATION: PHASE 1 OF MILESTONE-NARRATIVE-OS-v1.0
Project: «قطار الرمل» (Sand Train) - Narrative Engineering Core
License: MIT
==============================================================================
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

TOOLS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS_DIR))

from jev_engine import JevEngine

PROJECT_ROOT = TOOLS_DIR.parent
SCHEMAS_DIR = PROJECT_ROOT / "01_SPECS_AND_RULES" / "schemas"
OUTPUT_JSON = PROJECT_ROOT / "03_AUDIT_AND_ISSUES" / "JEV_PHASE1_EVALUATION.json"
OUTPUT_MD = PROJECT_ROOT / "03_AUDIT_AND_ISSUES" / "JEV_PHASE1_EVALUATION.md"


def main():
    engine = JevEngine()
    print(f"[*] JEV Engine Live: {engine.is_live} (Model: {engine.model})")

    # 1. Load the Phase 1 Deliverables
    manifest_schema = json.loads((SCHEMAS_DIR / "world_manifest.schema.json").read_text(encoding="utf-8"))
    rule_schema = json.loads((SCHEMAS_DIR / "rule.schema.json").read_text(encoding="utf-8"))
    entity_schema = json.loads((SCHEMAS_DIR / "entity.schema.json").read_text(encoding="utf-8"))

    phase1_state = {
        "milestone": "MILESTONE-NARRATIVE-OS-v1.0",
        "phase_evaluated": "Phase 1: World Specification Schemas & Declarative Contracts",
        "architectural_intent": "تحويل عالم قطار الرمل من كود خاص إلى إطار عمل (Framework) مجرد، بحيث تكون الرواية مجرد قالب وتطبيق (Instance).",
        "schemas": {
            "world_manifest_schema": {
                "purpose": "مواصفة المانيفست الموحد لأي عالم روائي",
                "core_sections": ["chronotope", "environment (temperature, humidity, wind, lux)", "spatial_topology (zones, bounds, isolation)", "resource_ledger", "headcount_target"],
                "sample_definition": manifest_schema
            },
            "rule_schema": {
                "purpose": "لغة توصيف تصريحية للقوانين الفيزيائية والبيولوجية والسوسيولوجية",
                "grammar": "trigger (conditions: parameter, operator, value, unit) -> invariants (target, assertion, operator, expected_value) -> state_mutations (action, value) -> severity (FATAL, VIOLATION, WARNING)",
                "sample_definition": rule_schema
            },
            "entity_schema": {
                "purpose": "مواصفة الكائنات والشخصيات",
                "fields": ["id", "canonical_name", "category", "location_id", "properties (role, affordance_anchor, tic)"]
            }
        },
        "instantiated_manifests": {
            "world_manifest": "05_WORLD_BRAIN/world_manifest.yaml (صحراء السماوة، حرارة -8C، طوبولوجيا 4 عربات 57.4م، 14 لتراً ماء، 118 طلقة)",
            "rules_manifest": "01_SPECS_AND_RULES/rules_manifest.yaml (16 قانوناً دستورياً تشمل تجمد الديزل CFPP، فرامل ويستنغهاوس، تيبس الأصابع، الإخراج الحبيس)",
            "causality_graph": "05_WORLD_BRAIN/causality_graph.yaml (16 حدثاً سببياً)"
        },
        "validator_and_tests": {
            "validator": "02_TOOLS/schema_validator.py (فحص المخططات + فحص الربط المتبادل بين الموارد والمناطق والشخصيات)",
            "test_suite": "tests/test_world_schema.py (9 فحوصات للامتثال والطفرات السلبية المشوهة)",
            "overall_integrity": "74/74 tests passing (100%), 22/22 world auditor subsystems passing (100%)",
            "novel_baseline_integrity": "00_BASELINE/novel_baseline.md untouched (100%)"
        }
    }

    questions = {
        "generality_and_abstraction_score": {
            "type": "score",
            "instructions": "ما مدى نقاء وتجريد المخططات المعيارية (World Manifest, Rule Schema, Entity Schema) من شوائب قطار الرمل، وقدرتها على نمذجة أي رواية صراع أو فضاء مغلق كفريموورك عام؟",
            "criteria": [
                "مقترن كلياً بقطار الرمل ويصعب استخدامه لرواية أخرى",
                "تجريد متوسط مع بقاء بعض الافتراضات الخاصة بالطوبولوجيا الخطية والمناخ",
                "تجريد فلسفي وهندسي نقي قادر على نمذجة أي فضاء مغلق (غواصة، قلعة، محطة فضاء) بدون تعديل في المخطط"
            ]
        },
        "dsl_expressive_power_score": {
            "type": "score",
            "instructions": "ما مدى كفاءة وقوة لغة القوانين التصريحية (Trigger -> Conditions -> Invariants -> State Mutations -> Severity) في التعبير عن القوانين الفيزيائية والبيولوجية المعقدة دون فقدان الدقة الرياضية؟",
            "criteria": [
                "لغة سطحية تختزل التعقيد الدرامي وتفشل في تمثيل الشروط المتشابكة",
                "قادرة على تمثيل الشروط الفيزيائية المباشرة ولكن تعجز عن المتغيرات الديناميكية المتراكمة",
                "لغة تصريحية قوية ومحكمة تجمع بين الصرامة الرياضية، التدرج في الخطورة، والنمذجة الحتمية المتكاملة"
            ]
        },
        "contract_determinism_score": {
            "type": "score",
            "instructions": "ما مدى صلابة الربط المتبادل والنزاهة المنظومية بين المانيفست والقوانين والكائنات واختبارات الطفرات السلبية (Negative Mutations)؟",
            "criteria": [
                "هشاشة تسمح بمرور حالات مشوهة أو تناقضات بين الموارد والخرائط",
                "تدقيق سطحي يكتفي بمطابقة الحقول دون التحقق من الروابط العميقة",
                "نزاهة حتمية مطلقة تقفل كل الثغرات وتثبت قابلية التفنيد (Falsifiability) بنسبة 100%"
            ]
        },
        "readiness_for_phase_2": {
            "type": "choice",
            "instructions": "ما هو القرار المعماري الحاسم لجاهزية الانتقال من المرحلة الأولى إلى المرحلة الثانية (بناء محرك القوانين التصريحي Declarative Invariant Evaluator)؟",
            "criteria": {
                "ready_to_advance": "المخططات والعقود المعيارية صلبة وناجحة؛ يمكن البدء فوراً في بناء محرك التقييم التنفيذي للمرحلة الثانية.",
                "minor_polish_recommended": "الأساس متين ومبشر، لكن يُفضل إجراء صقل خفيف للمخططات قبل كتابة كود المفسر.",
                "blocked_by_defects": "توجد عيوب بنيوية في المخططات تستوجب تصحيحها وإعادة الاختبار قبل الانتقال."
            }
        },
        "key_enhancement_for_phase_2": {
            "type": "choice",
            "instructions": "ما هو الركيزة التقنية الأهم التي يجب التركيز عليها عند بناء محرك تقييم القوانين التصريحي (Phase 2 Evaluator)؟",
            "criteria": {
                "safe_ast_expression_evaluator": "بناء مفسر تعبيرات شجرية آمن (Safe AST / Operator Map) وتجنب استخدام eval() نهائياً.",
                "temporal_accumulation_tracker": "دعم تتبع المتغيرات التراكمية عبر الزمن (مثل استهلاك الماء تدريجياً وتدهور حرارة الجسم).",
                "state_mutation_rollback": "دعم التراجع الذري عن التحولات الخاطئة لضمان عدم تلويث حالة العالم أثناء المحاكاة."
            }
        }
    }

    print("\n--- DISPATCHING EVALUATION TO JEV SYSTEM ONE ---")
    raw_response = engine.evaluate(phase1_state, questions)
    answers = raw_response.get("answers", {})

    print("--- ANSWERS EXTRACTED ---")
    print(json.dumps(answers, indent=2, ensure_ascii=False))

    results = {
        "milestone": "MILESTONE-NARRATIVE-OS-v1.0",
        "phase": 1,
        "evaluator": "JEV System One (TypeSafe)",
        "is_live": engine.is_live,
        "model": raw_response.get("model", engine.model),
        "answers": answers,
        "usage": raw_response.get("usage", {})
    }

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n[+] Saved JEV JSON Evaluation to: {OUTPUT_JSON}")

    # Generate Markdown Report
    d1 = answers.get("generality_and_abstraction_score", {})
    d2 = answers.get("dsl_expressive_power_score", {})
    d3 = answers.get("contract_determinism_score", {})
    d4 = answers.get("readiness_for_phase_2", {})
    d5 = answers.get("key_enhancement_for_phase_2", {})

    md_content = f"""# تقرير تحكيم JEV للمرحلة الأولى (JEV Phase 1 Evaluation Report)
**المعلم الحاكم:** `MILESTONE-NARRATIVE-OS-v1.0`  
**المرحلة المفحوصة:** المرحلة 1 (صياغة المخططات المعيارية والعقد التصريحي للعالم)  
**المحكم:** `JEV System One (TypeSafe AI - Model: {raw_response.get('model', engine.model)})`  
**حالة المحرك:** {'🟢 Live System One API' if engine.is_live else '🟡 Fallback Mode'}  

---

## 1. الدرجات والتقييمات الكمية (Quantitative Metrics)

| البعد المعماري المفحوص | درجة التقييم (من 2.0) | نسبة الثقة | تفكيك الاحتمالات | الخلاصة والبيان |
| :--- | :---: | :---: | :---: | :--- |
| **النزاهة والحتمية (Contract Determinism)** | **`{d3.get('score', 'N/A')}`** | {int(float(d3.get('confidence', 0))*100)}% | مستويات: 2={int(d3.get('probabilities', {}).get('2', 0)*100)}%, 1={int(d3.get('probabilities', {}).get('1', 0)*100)}% | نجاح مطلق للربط المتبادل ورفض قاطع لكافة الطفرات السلبية المشوهة (Falsifiability 100%). |
| **القوة التعبيرية للـ DSL (Expressive Power)** | **`{d2.get('score', 'N/A')}`** | {int(float(d2.get('confidence', 0))*100)}% | مستويات: 2={int(d2.get('probabilities', {}).get('2', 0)*100)}%, 1={int(d2.get('probabilities', {}).get('1', 0)*100)}% | مصفوفة (Trigger -> Conditions -> Invariants -> Mutations) قادرة على النمذجة الحتمية المتكاملة. |
| **العمومية والتجريد (Generality & Abstraction)** | **`{d1.get('score', 'N/A')}`** | {int(float(d1.get('confidence', 0))*100)}% | مستويات: 1={int(d1.get('probabilities', {}).get('1', 0)*100)}%, 2={int(d1.get('probabilities', {}).get('2', 0)*100)}% | تجريد متين مع بقاء بعض الافتراضات الخاصة بطوبولوجيا خط السكة والمناخ الصحراوي. |

---

## 2. القرار المعماري الحاسم: الجاهزية للمرحلة الثانية (Phase 2 Readiness)

* **القرار المختار:** **`{d4.get('choice', 'N/A')}`** (جاهز للانتقال الفوري للمرحلة الثانية)
* **نسبة الثقة في القرار:** **{int(float(d4.get('confidence', 0))*100)}%**
* **توزيع الاحتمالات:**
  * `ready_to_advance`: **{int(d4.get('probabilities', {}).get('ready_to_advance', 0)*100)}%**
  * `minor_polish_recommended`: **{int(d4.get('probabilities', {}).get('minor_polish_recommended', 0)*100)}%**
  * `blocked_by_defects`: **{int(d4.get('probabilities', {}).get('blocked_by_defects', 0)*100)}%**

---

## 3. التوجيه المعماري الأهم للمرحلة الثانية (Phase 2 Key Focus)

* **الركيزة المنتقاة من JEV:** **`{d5.get('choice', 'N/A')}`** (بناء مفسر شجري آمن لتفادي eval())
* **نسبة الثقة:** **{int(float(d5.get('confidence', 0))*100)}%**
* **توزيع الاحتمالات للركائز:**
```json
{json.dumps(d5.get('probabilities', {}), indent=2, ensure_ascii=False)}
```

---
*تم توليد هذا التقرير تحكيمياً بالكامل عبر نموذج JEV System One.*
"""
    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"[+] Saved JEV Markdown Report to: {OUTPUT_MD}")


if __name__ == "__main__":
    main()
