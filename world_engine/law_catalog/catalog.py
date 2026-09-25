#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
DOMAIN LAW CATALOG (مكتبة حزم القوانين الفيزيائية متعددة المجالات)
Project: Narrative World OS / Framework
License: MIT
==============================================================================
"""

from __future__ import annotations

from typing import Any, Dict, List


DOMAIN_PACKS: Dict[str, Dict[str, Any]] = {
    # 1. Closed Cold Transport (Sand Train Instance)
    "closed_cold_transport": {
        "pack_id": "closed_cold_transport",
        "title": "حزمة النقل البري المغلق في الصقيع (Closed Cold Transport)",
        "genre": "existential_survival_tragedy",
        "description": "قوانين التكتل الحراري، تبلور شمع الديزل، انكماش الصاج، والمكابح الهوائية الحتمية.",
        "rules": [
            {
                "id": "LAW-THERMO-01",
                "name": "قانون الحفظ الحراري وانكماش الصاج (Sheet Metal Contraction)",
                "domain": "thermodynamics",
                "description": "انكماش الصاج المعدني بطقطقة جافة وهبوط الحرارة الداخلية في الصقيع.",
                "mathematical_expression": "dQ/dt = -k * A * (T_in - T_out)",
                "severity": "VIOLATION",
                "trigger": {
                    "description": "هبوط درجة الحرارة المحيطة إلى ما دون الصفر",
                    "conditions": [
                        {"parameter": "ambient_temperature", "operator": "<=", "value": 0.0, "unit": "celsius"}
                    ],
                },
                "invariants": [
                    {
                        "target": "environment.temperature_celsius.min",
                        "assertion": "الحرارة الصغرى لا تهبط تحت حد الصقيع المسموح",
                        "operator": ">=",
                        "expected_value": -15.0,
                    }
                ],
            },
            {
                "id": "LAW-CHEM-01",
                "name": "قانون تبلور وتصلب شمع البرافين للديزل (Fuel Paraffin Gelling)",
                "domain": "chemistry",
                "description": "تجمد وتكتل شمع الديزل الصيفي عند هبوط الحرارة دون -6°C مانعاً تشغيل المحرك.",
                "mathematical_expression": "Viscosity_fuel = mu_0 * exp(E / R*T)",
                "severity": "FATAL",
                "trigger": {
                    "description": "هبوط حرارة الوقود دون نقطة التغيم",
                    "conditions": [
                        {"parameter": "diesel_fuel_temperature", "operator": "<=", "value": -6.0, "unit": "celsius"}
                    ],
                },
                "invariants": [
                    {
                        "target": "locomotive.engine.cold_restart_possible",
                        "assertion": "استحالة تشغيل المحرك الميكانيكي دون تسخين مسبق",
                        "operator": "==",
                        "expected_value": False,
                    }
                ],
            },
            {
                "id": "LAW-BIO-06",
                "name": "قانون ديناميكا فرط ثاني أكسيد الكربون الحبيس (Hypercapnia Dynamics)",
                "domain": "biology",
                "description": "تراكم غاز CO2 في الصندوق المعدني المحكم بمعدل 280 لتر/ساعة وبلبلة الإدراك.",
                "mathematical_expression": "d[CO2]/dt = (N_humans * 20.0 L/h) / V_chamber",
                "severity": "VIOLATION",
                "trigger": {
                    "description": "تجاوز تركيز ثاني أكسيد الكربون 1.5%",
                    "conditions": [
                        {"parameter": "environment.co2_concentration_percent", "operator": ">=", "value": 1.5}
                    ],
                },
                "invariants": [
                    {
                        "target": "characters.allostatic_load",
                        "assertion": "تصاعد الإجهاد العصبي والبلبلة الإدراكية الحتمية",
                        "operator": ">=",
                        "expected_value": 0.4,
                    }
                ],
            },
            {
                "id": "LAW-ACOUST-04",
                "name": "قانون التوصيل الصوتي الهيكلي للحديد (Structure-Borne Acoustics)",
                "domain": "acoustics",
                "description": "انتقال صدمات الطرق عبر شاسيه السكة والفولاذ بسرعة 5000 م/ث بفقد طفيف.",
                "mathematical_expression": "v_steel = sqrt(E / rho) = 5000 m/s",
                "severity": "WARNING",
                "trigger": {
                    "description": "وقوع صدمة ميكانيكية أو طرقة على الهيكل المعدني",
                    "conditions": [
                        {"parameter": "structural_mechanical_strike", "operator": "==", "value": True}
                    ],
                },
                "invariants": [
                    {
                        "target": "train.structural_vibration_detected",
                        "assertion": "اهتزاز الشاسيه وسماع الصوت في كافة العربات",
                        "operator": "==",
                        "expected_value": True,
                    }
                ],
            },
        ],
    },

    # 2. Deep Sea Submarine
    "deep_sea_submarine": {
        "pack_id": "deep_sea_submarine",
        "title": "حزمة غواصات الأعماق (Deep Sea Submarine Pack)",
        "genre": "submarine_depth_thriller",
        "description": "قوانين الضغط الهيدروستاتيكي، صدى السونار، الطفو، ونقص الأكسجين في الأعماق.",
        "rules": [
            {
                "id": "LAW-KIN-01",
                "name": "قانون الضغط الهيدروستاتيكي للأعماق (Hydrostatic Depth Pressure)",
                "domain": "kinetics",
                "description": "تزايد الضغط الهيدروليكي بمعدل 1 بار لكل 10 أمتار عمق حتى سحق الهيكل.",
                "mathematical_expression": "P_depth = P_atm + (rho_water * g * depth_meters)",
                "severity": "FATAL",
                "trigger": {
                    "description": "تجاوز عمق الغوص حد الانهيار الإنشائي للهيكل",
                    "conditions": [
                        {"parameter": "submarine.depth_meters", "operator": ">=", "value": 450.0, "unit": "meters"}
                    ],
                },
                "invariants": [
                    {
                        "target": "submarine.hull_breach_imminent",
                        "assertion": "خطر سحق الهيكل الحتمي عند تجاوز العمق الأقصى",
                        "operator": "==",
                        "expected_value": True,
                    }
                ],
            },
            {
                "id": "LAW-BIO-02",
                "name": "قانون استنزاف الأكسجين في البدن الغاطس (Submerged Hypoxia)",
                "domain": "biology",
                "description": "استهلاك الأكسجين الحبيس وتسمم الهواء عند تعطل منقيات ثاني أكسيد الكربون.",
                "mathematical_expression": "O2_remaining = O2_initial - (0.04 * Headcount * Hours)",
                "severity": "VIOLATION",
                "trigger": {
                    "description": "هبوط نسبة الأكسجين دون 16%",
                    "conditions": [
                        {"parameter": "submarine.o2_percent", "operator": "<=", "value": 16.0, "unit": "percent"}
                    ],
                },
                "invariants": [
                    {
                        "target": "crew.consciousness_impaired",
                        "assertion": "فقدان التركيز والذهول الحتمي للطاقم",
                        "operator": "==",
                        "expected_value": True,
                    }
                ],
            },
            {
                "id": "LAW-ACOUST-02",
                "name": "قانون ارتداد السونار الصوتي والميل الحراري (Sonar Thermocline Reflection)",
                "domain": "acoustics",
                "description": "انكسار وارتداد الأمواج الصوتية عند طبقة الميل الحراري المائي وخلق مناطق الظل.",
                "mathematical_expression": "theta_crit = arcsin(c1 / c2)",
                "severity": "WARNING",
                "trigger": {
                    "description": "دخول الغواصة أسفل طبقة الميل الحراري المائي",
                    "conditions": [
                        {"parameter": "submarine.below_thermocline", "operator": "==", "value": True}
                    ],
                },
                "invariants": [
                    {
                        "target": "sonar.surface_detection_shadow",
                        "assertion": "تلاشي إشارة السونار السطحي وحصانة الاختفاء",
                        "operator": "==",
                        "expected_value": True,
                    }
                ],
            },
        ],
    },

    # 3. Orbital Space Station
    "orbital_space_station": {
        "pack_id": "orbital_space_station",
        "title": "حزمة المحطات المدارية والفضاء (Orbital Space Station Pack)",
        "genre": "hard_sci_fi_orbital_survival",
        "description": "قوانين انعدام الوزن، تفريغ الضغط المتفجر، الإشعاع الكوني، والإشعاع الحراري الفراغي.",
        "rules": [
            {
                "id": "LAW-PNEUM-02",
                "name": "قانون تفريغ الضغط الفضائي المتفجر (Explosive Decompression)",
                "domain": "pneumatics",
                "description": "التفريغ الفوري لضغط الكابينة إلى الصفر المطلق عند حدوث ثقب نيزكي.",
                "mathematical_expression": "dP/dt = -(C_d * A * P / V) * sqrt(gamma * R * T)",
                "severity": "FATAL",
                "trigger": {
                    "description": "حدوث ثقب غير مسدود في هيكل المحطة",
                    "conditions": [
                        {"parameter": "station.hull_puncture_area_cm2", "operator": ">=", "value": 5.0}
                    ],
                },
                "invariants": [
                    {
                        "target": "station.decompression_active",
                        "assertion": "تفريغ الغلاف الجوي فورياً في الفراغ",
                        "operator": "==",
                        "expected_value": True,
                    }
                ],
            },
            {
                "id": "LAW-THERMO-02",
                "name": "قانون الإشعاع الحراري الفراغي (Vacuum Radiative Heat Loss)",
                "domain": "thermodynamics",
                "description": "انعدام التوصيل الحراري الخارجي واعتماد التبريد حصراً على إشعاع ستيفان بولتزمان.",
                "mathematical_expression": "P_rad = epsilon * sigma * A * (T^4 - T_space^4)",
                "severity": "VIOLATION",
                "trigger": {
                    "description": "انقطاع دائرة تدوير سوائل التبريد المدارية",
                    "conditions": [
                        {"parameter": "station.cooling_radiator_operational", "operator": "==", "value": False}
                    ],
                },
                "invariants": [
                    {
                        "target": "station.core_overheating",
                        "assertion": "تراكم الحرارة الحبيسة في فراغ العزل",
                        "operator": "==",
                        "expected_value": True,
                    }
                ],
            },
        ],
    },

    # 4. Desert Caravan Survival
    "desert_caravan_survival": {
        "pack_id": "desert_caravan_survival",
        "title": "حزمة الحصار الصحراوي والقيظ (Desert Caravan Survival Pack)",
        "genre": "arid_desert_survival",
        "description": "قوانين التجفاف المتسارع، ضربات الشمس الحتمية، البصريات السرابية، وتآكل الرمال.",
        "rules": [
            {
                "id": "LAW-BIO-03",
                "name": "قانون التجفاف المتسارع بالتعرق (Acute Sweat Dehydration)",
                "domain": "biology",
                "description": "فقدان سوائل الجسم بمعدل يتجاوز 1.5 لتر/ساعة في درجات الحرارة فوق 40°C.",
                "mathematical_expression": "Water_loss_rate = 1.5 L/h + 0.1 * (T_amb - 40.0)",
                "severity": "FATAL",
                "trigger": {
                    "description": "ارتفاع الحرارة فوق 40 درجة مئوية مع انعدام الماء",
                    "conditions": [
                        {"parameter": "ambient_temperature", "operator": ">=", "value": 40.0, "unit": "celsius"}
                    ],
                },
                "invariants": [
                    {
                        "target": "caravan.water_ration_liters_per_capita",
                        "assertion": "استنزاف مخزون الماء واقتراب الصدمة الوعائية",
                        "operator": "<=",
                        "expected_value": 0.5,
                    }
                ],
            },
            {
                "id": "LAW-OPT-02",
                "name": "قانون انكسار السراب البصري الحتمي (Atmospheric Heat Mirage)",
                "domain": "optics",
                "description": "تشوه الخطوط والأفق وانكسار الأشعة الضوئية فوق الرمضاء شديدة الحرارة.",
                "mathematical_expression": "n(y) = 1 + (P / R*T(y)) * (n_0 - 1)",
                "severity": "WARNING",
                "trigger": {
                    "description": "بلوغ فارق حرارة سطح الأرض مع الهواء أكثر من 15°C",
                    "conditions": [
                        {"parameter": "ground_surface_temperature_delta", "operator": ">=", "value": 15.0}
                    ],
                },
                "invariants": [
                    {
                        "target": "vision.mirage_distortion_active",
                        "assertion": "استحالة تمييز المعالم البعيدة بدقة بصرية",
                        "operator": "==",
                        "expected_value": True,
                    }
                ],
            },
        ],
    },
}
