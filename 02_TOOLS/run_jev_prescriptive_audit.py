"""
run_jev_prescriptive_audit.py
Queries JEV for actionable prescriptions to resolve the findings:
1. Codifying biological excretion & enclosed air (LAW-BIO-05)
2. Tightening sociology-physics fusion (power erosion driven by shivering/caloric debt)
3. Diesel paraffin gelling threshold (LAW-CHEM-01)
4. Pruning Cartesian micro-coordinates in favor of dynamic affordance zones
"""

import sys
import json
from pathlib import Path

tools_dir = Path(__file__).parent
sys.path.insert(0, str(tools_dir))

from jev_engine import JevEngine

def main():
    engine = JevEngine()
    
    state = {
        "context": "نتائج الفحص الشامل لعالم رواية قطار الرمل عبر JEV",
        "findings": {
            "missing": ["biological_excretion_and_air (76%)", "diesel_gelling_risk (65%)"],
            "weakest_joint": "sociology_physics_fusion (53%)",
            "redundancy": "dual_auditing_specs (67%)",
            "excess": "micro_spatial_coordinates (70%)"
        }
    }

    questions = {
        "excretion_narrative_treatment": {
            "type": "choice",
            "instructions": "كيف ينبغي معالجة مسألة الإخراج البشري في صقيع -8C داخل عربة السجناء بأعلى قيمة تراجيدية وأدبية؟",
            "criteria": {
                "corner_bucket_humiliation": "تخصيص زاوية في العربة بصفيحة صدئة أو جردل، حيث يصبح التعري في البرد المطبق أقصى درجات الإذلال البيولوجي وسقوط الكبرياء",
                "suppression_and_spasm": "حبس البول القهري خوفاً من الصقيع، مما يسبب تشنجات مثانة حادة وآلاماً بطنية تفكك الانضباط الجسدي للشخصيات",
                "shared_shame_solidarity": "تحول عملية الإخراج إلى طقس تضامني مهين حيث يتكاتف السجناء لحجب الشخص بسترة صوفية اتقاء للريح والعار"
            }
        },
        "sociology_physics_bridge": {
            "type": "choice",
            "instructions": "ما هي الأداة الفيزيائية الأكثر حسماً لربط تآكل سلطة الحراس بفيزياء الصقيع؟",
            "criteria": {
                "trigger_finger_stiffness": "تيبس سبابة الحراس في البرد (LAW-BIO-01) وفقدان القدرة على سحب زناد الكلاشينكوف بدقة وسرعة",
                "shivering_voice_tremor": "الارتعاش اللاإرادي للفكين والحبال الصوتية الذي يسلب الأوامر العسكرية هيبتها ونبرتها الآمرة",
                "caloric_hypoglycemic_confusion": "ارتباك التفكير ونوبات الهذيان الناتجة عن هبوط السكر واستنزاف السعرات (LAW-BIO-04)"
            }
        },
        "pruning_micro_coordinates_action": {
            "type": "choice",
            "instructions": "ما هو البديل الأفضل لشطب الإحداثيات الديكارتية المفرطة (x, y بالسنتيمتر)؟",
            "criteria": {
                "zone_affordance_anchoring": "استبدالها بربط الشخصيات بالمتاحيات المكانية (قرب الباب، ملاصق للبرميل، تحت الرف، محشور في الزاوية الميتة)",
                "cluster_distance_matrix": "استبدالها بمصفوفة مسافات نسبية (متلاصق، على بعد خطوتين، خارج مدى الرؤية)",
                "pure_narrative_vagueness": "ترك المواقع مرنة تماماً دون أي قيد مكاني برمجي"
            }
        }
    }

    prescriptive_res = engine.evaluate(state, questions)
    print("\n--- PRESCRIPTIVE RECOMMENDATIONS FROM JEV ---")
    print(json.dumps(prescriptive_res, indent=2, ensure_ascii=False))

    out_file = tools_dir.parent / "03_AUDIT_AND_ISSUES" / "JEV_PRESCRIPTIVE_RECOMMENDATIONS.json"
    out_file.write_text(json.dumps(prescriptive_res, indent=2, ensure_ascii=False), encoding="utf-8")

if __name__ == "__main__":
    main()
