#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JEV EVALUATION OF MEASUREMENT & JUDGMENT TOOLS
Project: «قطار الرمل» (Sand Train)
License: MIT
"""

import os
import sys
import json
import urllib.request
from pathlib import Path

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

KEY_PATH = Path(r"D:\JEV\API key for test.txt")
if not KEY_PATH.exists():
    KEY_PATH = Path(os.environ.get("JEV_KEY_PATH", ""))

api_key = KEY_PATH.read_text(encoding="utf-8").strip() if KEY_PATH.exists() else os.environ.get("JEV_API_KEY", "")

tools_profile = {
    "project": "قطار الرمل - Closed World Simulator",
    "architecture_concept": "نحن نُحلل ونُقيّم.. ولا نُقوّم (صفر تجميل خيالي، حتمية فيزيائية ورياضية صارمة)",
    "measurement_tools": {
        "WorldAuditor": {
            "scope": "الفيزياء المادية والحسابية الصلبة",
            "metrics": [
                "Spatial Non-Collision: Distinct (x,y) per character",
                "Boundary Confinement: [y_start, y_end] envelope",
                "Resource Balance: 118 rounds ammo exact, 14.0L water exact",
                "Pneumatics: 0.0 bar fail-safe clamping",
                "Acoustic Isolation: >35 dB inter-car attenuation"
            ],
            "methodology": "قواعد بيانات، حسابات جبرية مباشرة، معادلات Pydantic"
        },
        "EpistemicTracker": {
            "scope": "حدود المعرفة والوعي الإدراكي",
            "metrics": [
                "Epistemic Bubbles Isolation",
                "Omniscience Leaks Prevention",
                "Physical Channel Feasibility"
            ],
            "methodology": "تحليل مسار انتقال المعلومة عبر المكان والزمن"
        },
        "MoralEntropyMonitor": {
            "scope": "الديناميكا الأخلاقية والوجودية",
            "metrics": [
                "4-Quadrant Moral Typology Census (Zero ideological monopoly)",
                "Thermodynamic Entropy Curve (S_moral: 0.12 -> 0.45 -> 0.88 -> 0.62 -> 0.41)",
                "Causal Moral Debt Balance (Retribution invariant)",
                "Funerary Dignity & Sacred Memory Preservation"
            ],
            "methodology": "نمذجة ثيرموديناميكية وسوسيولوجية للبقاء المشترك"
        },
        "PsychologyDetector": {
            "scope": "الاتساق العصبي والنفسي للشخصيات",
            "metrics": [
                "Neurological Displacement Tics Manifestations (LAW-BIO-02)",
                "Panic Speech Fragmentation (Avg words/sentence <= 8.0)",
                "Defense Mechanism Concordance (Ammar denial, Khalid stoic)",
                "JEV Semantic Concordance & Anti-Teleportation"
            ],
            "methodology": "هجين بين Regex Lexical Patterns والتحكيم الدلالي الاحتمالي لـ JEV"
        },
        "SensoryLinter": {
            "scope": "كثافة التجسيد الحسي المادي",
            "metrics": [
                "Sensory Lexicon Density (Visual, Auditory, Tactile, Olfactory, Gustatory)",
                "Tactile Deficit Warning (< 5.0 per 1,000 words)",
                "JEV Semantic Immersion & Anti-Cliché Evaluation"
            ],
            "methodology": "إحصاء معجمي مشروط بتحكيم دلالي غامر"
        },
        "CausalityGraph": {
            "scope": "الترتيب السببي والزمني للأحداث",
            "metrics": [
                "Acyclic Event Directed Graph (DAG)",
                "Temporal Monotonicity",
                "Precondition-Effect Validity"
            ],
            "methodology": "نظرية الرسوم البيانية وفحص انعدام الحلقات (DFS Cycle Check)"
        },
        "EventReplayer": {
            "scope": "إعادة بناء الحالة ومطابقة الأثر المادي",
            "metrics": [
                "Event Sourcing Trace Fidelity",
                "State Replay Determinism",
                "Cryptographic Hash Integrity"
            ],
            "methodology": "إعادة تطبيق الأحداث من السجل الخام ومقارنة الـ Hash للحالة النهائية"
        }
    }
}

payload = {
    "state": tools_profile,
    "model": "jev-latest",
    "questions": {
        "most_rigorous_measurement": {
            "type": "choice",
            "instructions": "أي من أدوات القياس هذه تمتلك أعلى درجة من الحتمية والموثوقية الرياضية (Deterministic Rigor)؟",
            "criteria": {
                "EventReplayer": "محرك إعادة البناء (EventReplayer) لكونه يثبت مطابقة الحالة عبر التجزئة التشفيرية والسجل التراكمي",
                "WorldAuditor": "مدقق العالم الفيزيائي (WorldAuditor) لاعتماده على توازنات الكتلة ومحددات الفضاء الحسابية",
                "CausalityGraph": "محلل السببية (CausalityGraph) لكونه يستند لنظرية الرسوم البيانية الصارمة رياضياً"
            }
        },
        "measurement_paradox_tool": {
            "type": "choice",
            "instructions": "أي أداة تفرض أكبر مفارقة معرفية (Epistemic Paradox) بين صعوبة قياس الظاهرة وبين صرامة المعايير الموضوعة لها؟",
            "criteria": {
                "MoralEntropyMonitor": "مراقب الإنتروبيا الأخلاقية: لصعوبة تحويل التضامن الوجودي والكرامة الإنسانية إلى معادلات ثيرموديناميكية قطعية",
                "PsychologyDetector": "فاحص علم النفس: لصعوبة حصر البنية النفسية المعقدة في مجرد لوازم حركية وأطوال جمل",
                "SensoryLinter": "فاحص الحواس: لكون الانغماس الحسي أعمق من كثافة الألفاظ المعجمية"
            }
        },
        "system_maturity_score": {
            "type": "score",
            "instructions": "ما تقييم مستوى نضج هذه الترسانة القياسية في سياق هندسة السرد والأنظمة المعقدة؟",
            "criteria": [
                "أدوات فحص شكلية سهلة التحايل تفتقر للعمق الفيزيائي",
                "منظومة متقدمة ورائدة تزاوج بين الصرامة الحسابية والذكاء الدلالي مع فجوات قابلة للتطوير",
                "منظومة قياس معصومة تامة الإحكام تغطي الوجود السردي بنسبة 100%"
            ]
        },
        "false_sense_of_control": {
            "type": "noul",
            "instructions": "هل تمنح كثرة الفحوصات الرقمية الناجحة (59/59) إيحاءً مضللاً بالسيطرة الكاملة على العالم، بينما تبقى الجوانب الحيوية والإنسانية غير المرئية عرضة للخلل؟"
        },
        "key_blindspot": {
            "type": "choice",
            "instructions": "ما هي النقطة العمياء الرئيسية المشتركة بين كل أدوات القياس هذه؟",
            "criteria": {
                "discrete_vs_continuous": "قياس العالم بنقاط زمنية متقطعة (Discrete Milestones) وتفويت التدهور المستمر البطيء بين الفصول",
                "symbolic_literalism": "التعامل مع الرمز السردي بحرفية هندسية مفرطة قد تخنق النبض الدرامي الطبيعي للرواية",
                "author_intent_blindness": "العجز عن التمييز بين الخطأ الفيزيائي الحقيقي وبين التعبير المجازي المتعمد للشخصيات"
            }
        }
    }
}

req = urllib.request.Request(
    "https://api.typesafe.ai/v1/systemone",
    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    data=json.dumps(payload).encode("utf-8")
)

with urllib.request.urlopen(req, timeout=30) as resp:
    res = json.loads(resp.read().decode("utf-8"))

output_path = Path(__file__).parent / "jev_tools_evaluation_report.json"
output_path.write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
print("Evaluation saved successfully to", output_path)
