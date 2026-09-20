# قالب العوالم الروائية (Narrative World Template Boilerplate)

هذا المجلد يمثل القالب القياسي المعياري لتأسيس وتوليد أي رواية أو دراما حتمية جديدة باستخدام **نظام تشغيل العوالم السردية (World Engine)**.

---

## بنية ملفات العالم الجديد
عند تشغيل الأمر:
```bash
python -m world_engine init --name "YourNovelTitle" --output path/to/world
```
يقوم المحرك بإنشاء الملفات الأربعة التالية:
1. `world_manifest.yaml`: مواصفات البيئة، الطوبولوجيا، الموارد، والزمن.
2. `rules_manifest.yaml`: القوانين الدستورية الحاكمة (فيزياء، كيمياء، بيولوجيا، سوسيولوجيا).
3. `entities_catalog.yaml`: الشخصيات والكائنات ومراسي المتاحيات الحسيّة (Affordance Anchors).
4. `causality_graph.yaml`: شبكة تدفق الأحداث السببية (DAG).

---

## التدقيق الآلي
لفحص اتساق عالمك الروائي الجديد:
```bash
python -m world_engine audit --manifest path/to/world/world_manifest.yaml
```
سيقوم المحرك بالتحقق من:
* سلامة المخططات القياسية (Draft 2020-12).
* خلو شبكة الأحداث من أي حلقات سببية مفرغة (Acyclic Causality).
* التزام حالة العالم بكافة القوانين الحتمية المصاغة.
