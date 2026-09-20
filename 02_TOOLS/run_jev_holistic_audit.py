"""
run_jev_holistic_audit.py
Executes a comprehensive holistic audit of the novel's world architecture using JEV System One.
Connects the threads across Physics, Semiotics, Sociology, and Dramaturgy,
and identifies:
1. What is MISSING (ناقص)
2. What is REDUNDANT (مكرر)
3. What is EXCESS/SUPERFLUOUS (زائد)
"""

import os
import sys
import json
from pathlib import Path

# Add 02_TOOLS to path
tools_dir = Path(__file__).parent
sys.path.insert(0, str(tools_dir))

from jev_engine import JevEngine

def main():
    engine = JevEngine()
    print(f"[*] JEV Engine initialized (Live: {engine.is_live}, Model: {engine.model})")

    # 1. Holistic State Representation of the World Architecture (Updated after upgrades)
    world_architecture_state = {
        "novel_title": "قطار الرمل",
        "premise": "قطار ترحيل سجناء سوفيتي/عراقي عسكري يتعطل ليلاً (19:00 إلى 05:45) في بادية الحماد الغربية بصقيع -8C، يحمل 14 شخصاً (حراس وسجناء)، في صراع بقاء ضد البرد، شح الماء (14 لتر)، وتآكل السلطة.",
        "subsystems_count": 22,
        "physical_laws_count": 34,
        "newly_codified_laws": [
            "LAW-BIO-05: بيولوجيا الإخراج الحبيس، تشنج المثانة، واحتجاز البخار والكرامة في الصقيع",
            "LAW-CHEM-01: نقطة التغيم وتصلب شمع البرافين لوقود الديزل (Diesel Paraffin Gelling)"
        ],
        "sociology_physics_bridge": "تآكل السلطة وسقوط الرتب مرتبط ميكانيكياً بتيبس سبابة الزناد (LAW-BIO-01) ورعشة الصوت والفك وتضامن العار المشترك في زاوية الإخراج (LAW-BIO-05)",
        "spatial_layout": "قاطرة ديزل + 3 عربات + منصة (57.4م، مقسمة لـ 7 مناطق مع مراسي متاحيات مكانية Affordance Anchors لكل شخصية)",
        "characters_count": 14,
        "character_use_values": "كل شخصية تمتلك قيمة استعمالية حصرية في البقاء (Unique Survival Use-Value) لمنع أي تكرار وظيفي",
        "documented_bugs_count": 12,
        "resources": "14 لتر ماء، 118 طلقة كلاشينكوف، 1 أنبوب وقود متصدع، بطاريات رصاص تتفرغ خلال 3-4.5 ساعات",
        "current_tools": [
            "world_auditor.py (22 deterministic subsystems passing 100%)",
            "epistemic_tracker.py (information horizon & metaphor filter)",
            "moral_entropy_monitor.py (thermodynamic moral entropy S_moral)",
            "chrono_event_engine.py (caloric depletion & metabolic collapse)",
            "socio_demography_analyzer.py (sociology-physics bridge & use-value dominance)",
            "sensory_linter.py (visceral density)",
            "psychology_detector.py (neurotic tics & panic syntax)",
            "causality_graph (DAG of 16 events)",
            "entities_catalog.yaml (39 entities anchored to zone affordances)"
        ],
        "world_brain_layers": [
            "01_CHARACTERS (14 dossiers with physical tics & unique survival use-values)",
            "02_SEMIOTICS_AND_SYMBOLS (flint pebble, jaw scar, diesel stain, black shoe, folded paper, lost watch)",
            "03_PHYSICS_AND_LAWS (34 laws: thermodynamics, pneumatics, ballistics, acoustics, biophysics, chemistry, ethics)",
            "04_SOCIOLOGY_AND_POWER (military hierarchy erosion, Iraqi mosaic, use-value dominance)",
            "05_DRAMATURGY_AND_GRAPH (relationship matrix, mawal turning point, death cascade)"
        ]
    }

    # =========================================================================
    # AUDIT PHASE 1: CONNECTING THE THREADS & SYSTEMIC COHESION (ربط الخيوط)
    # =========================================================================
    print("\n--- PHASE 1: CONNECTING THE THREADS (ربط الخيوط) ---")
    thread_questions = {
        "systemic_connectivity_score": {
            "type": "score",
            "instructions": "ما مدى ترابط الخيوط بين القوانين الفيزيائية الصارمة (البرد والآلة) وبين الصراع البشري والرموز السيميائية في هذا العالم؟",
            "criteria": [
                "مفكك ومجرد قواعد منفصلة لا تنعكس على سلوك الشخصيات",
                "مترابط جزئياً مع ثغرات في مفاصل التحول الدرامي",
                "عالم عضوي محكم حيث تولد التراجيديا الإنسانية من صلب القوانين الفيزيائية"
            ]
        },
        "weakest_joint": {
            "type": "choice",
            "instructions": "أين يقع المفصل الأضعف في شبكة ترابط الخيوط الحالية؟",
            "criteria": {
                "driver_mystery_isolation": "انقطاع خيط مقصورة السائق المغلقة عن بقية أحداث العربات",
                "flint_symbol_vs_thermo": "عدم كفاية التأثير المادي لرمزية الحصاة الصوانية والندبة على حركة البقاء",
                "external_world_silence": "انقطاع القطار التام عن المؤسسة العسكرية الخارجية دون آلية تواصل واضحة",
                "sociology_physics_fusion": "انفصال التحول الاجتماعي (سقوط الرتب) عن منحنى الاستنزاف الحراري المباشر"
            }
        },
        "is_causally_unbreakable": {
            "type": "noul",
            "instructions": "هل سلسلة السببية المادية (تعطل المحرك -> تجمد المكابح -> استنزاف السعرات -> تآكل التراتبية -> الموت) محكمة ومترابطة حتمياً بدون قفزات مصطنعة؟"
        }
    }
    thread_res = engine.evaluate(world_architecture_state, thread_questions)
    print(json.dumps(thread_res, indent=2, ensure_ascii=False))

    # =========================================================================
    # AUDIT PHASE 2: WHAT IS MISSING? (ما هو ناقص لاكتمال العالم)
    # =========================================================================
    print("\n--- PHASE 2: WHAT IS MISSING? (النواقص الحرجة) ---")
    missing_questions = {
        "primary_missing_dimension": {
            "type": "choice",
            "instructions": "ما هو البعد الأكثر نقصاً وإلحاحاً الذي يحتاجه هذا العالم ليكتمل كبيئة روائية وواقعية متكاملة؟",
            "criteria": {
                "biological_excretion_and_air": "فيزياء الهواء المغلق (تراكم CO2) والبيولوجيا الحتمية للإخراج والنظافة في الحصار المطبق",
                "diesel_chemistry_cloud_point": "نقطة التغيم والتجمد لوقود الديزل (Diesel Cloud Point & Gelling) في الريح الباردة",
                "desert_predators_and_ecology": "البيئة الحية للبادية (الذئاب، الضباع، الصدى الصحراوي للفرائس العالقة)",
                "locomotive_cab_resolution": "الحسم الميكانيكي أو الجنائي لمصير السائق داخل المقصورة المقفلة"
            }
        },
        "excretion_and_atmosphere_urgency": {
            "type": "noul",
            "instructions": "هل إهمال مسألة قضاء الحاجة والتنفس في عربة مسدودة تضم 14 شخصاً لـ 11 ساعة يمثل فجوة واقعية تشوه كمال العالم؟"
        },
        "diesel_gelling_risk": {
            "type": "noul",
            "instructions": "هل يستلزم الهبوط إلى -8C تضمين قانون تجمد شمع الديزل (Paraffin Gelling) الذي يمنع إعادة تشغيل المحرك حتى لو أُصلح الأنبوب؟"
        }
    }
    missing_res = engine.evaluate(world_architecture_state, missing_questions)
    print(json.dumps(missing_res, indent=2, ensure_ascii=False))

    # =========================================================================
    # AUDIT PHASE 3: WHAT IS REDUNDANT? (ما هو مكرر)
    # =========================================================================
    print("\n--- PHASE 3: WHAT IS REDUNDANT? (المكررات والتكرار غير المفيد) ---")
    redundant_questions = {
        "primary_redundancy_source": {
            "type": "choice",
            "instructions": "أين يوجد أكبر قدر من التكرار والازدواجية غير الضرورية في بنية هذا العالم؟",
            "criteria": {
                "character_trauma_overlap": "تشابه أدوار بعض السجناء السلبيين (بشير، خليل، حجي عمار) في الاستسلام للبرد والذكريات",
                "dual_auditing_specs": "تكرار القوانين بين ملف PHYSICAL_LAWS وملف SYSTEMIC_BEHAVIORS والأدوات البرمجية",
                "guard_neurosis_duplication": "تكرار تيمة ذعر الحراس بين أبي اللول وحناطة دون تمايز وظيفي كافٍ",
                "spatial_metric_redundancy": "تكرار إحداثيات المواقع بالسنتيمتر مع وجود تعريف المناطق (Zones)"
            }
        },
        "has_character_overlap": {
            "type": "noul",
            "instructions": "هل هناك حشو وتكرار في وظائف الشخصيات الـ 14 يمكن دمجه أو شحذه لتكثيف الأثر الدرامي؟"
        },
        "law_duplication_detected": {
            "type": "noul",
            "instructions": "هل التكرار بين التوثيق النظري (Markdown) والتحقق البرمجي (Python Invariants) يعيق رشاقة النظام؟"
        }
    }
    redundant_res = engine.evaluate(world_architecture_state, redundant_questions)
    print(json.dumps(redundant_res, indent=2, ensure_ascii=False))

    # =========================================================================
    # AUDIT PHASE 4: WHAT IS EXCESS / SUPERFLUOUS? (ما هو زائد ويعيق السرد)
    # =========================================================================
    print("\n--- PHASE 4: WHAT IS EXCESS / OVER-ENGINEERING? (الزوائد والتعقيد الفائض) ---")
    excess_questions = {
        "primary_excess_element": {
            "type": "choice",
            "instructions": "ما هو العنصر الأكثر فائضاً وزائداً عن الحاجة الروائية (Over-engineering) الذي يثقل العالم دون إضافة قيمة حقيقية؟",
            "criteria": {
                "micro_spatial_coordinates": "الإحداثيات الديكارتية الدقيقة للشخصيات (x=2.2m, y=18.2m) في عربة مهتزة بلا مقاعد ثابتة",
                "astronomical_angles_overkill": "الحساب الفلكي لزاوية انخفاض الشمس ومراحل الشفق الأربعة المنفصلة",
                "hyper_thermo_equations": "المعادلات التفاضلية الدقيقة للحرارة بدلاً من التدرج الحسي الملموس للبرودة",
                "bureaucratic_cataloging": "فهرسة 39 كياناً برمجياً (Props, Vehicles, Entities) لقصة محصورة في عربات قطار"
            }
        },
        "is_micro_coordinates_excessive": {
            "type": "noul",
            "instructions": "هل تحديد موقع جسد السجين بدقة 10 سم يمثل تعقيداً زائداً لا يخدم كتابة النص السردي ويتعارض مع فوضى الازدحام البشري؟"
        },
        "world_readiness_score": {
            "type": "score",
            "instructions": "ما هي الدرجة الإجمالية لنضج هذا العالم واكتماله للمضي قدماً في السرد والإنتاج الأدبي النهائي؟",
            "criteria": [
                "غير جاهز ويحتاج إعادة هيكلة جذرية",
                "شبه مكتمل ويحتاج تشذيب الزوائد الهندسية وسد النواقص البيولوجية",
                "مكتمل واستثنائي وفائق الإحكام والحتمية"
            ]
        }
    }
    excess_res = engine.evaluate(world_architecture_state, excess_questions)
    print(json.dumps(excess_res, indent=2, ensure_ascii=False))

    # Output combined results to json for synthesis
    full_audit = {
        "threads": thread_res,
        "missing": missing_res,
        "redundant": redundant_res,
        "excess": excess_res,
        "engine_telemetry": {
            "total_calls": engine.total_calls,
            "total_latency_seconds": engine.total_latency_seconds
        }
    }
    out_file = tools_dir.parent / "03_AUDIT_AND_ISSUES" / "JEV_HOLISTIC_WORLD_AUDIT.json"
    out_file.write_text(json.dumps(full_audit, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n[+] Full JEV audit written to {out_file}")

if __name__ == "__main__":
    main()
