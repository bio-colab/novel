# دليل المساهمة في منصة «قطار الرمل» (Contributing Guide)
### معمارية الهندسة السردية والمحاكاة الحتمية (Platform Engine v2.0.0)

مرحباً بك في مشروع **«قطار الرمل»**. هذا المشروع يمثل تجربة ريادية في تطبيق هندسة البرمجيات الكبرى ونظرية المعرفة على السرد الروائي. إذا كنت ترغب في المساهمة في تطوير الأدوات البرمجية، المحاكاة الحتمية، أو البنية المعرفية، يُرجى قراءة هذا الدليل بعناية.

---

## 1. الدستور الحاكم: ميثاق الحياد الإبداعي (Creative Non-Interference Charter)

> [!IMPORTANT]
> **«نحن نُحلل ونُقيّم.. ولا نُقوّم»**
> * أدوات المنظومة مصممة لرصد الاتساق السببي، الفيزيائي، والمعرفي الذي وضعه العالم الروائي لنفسه.
> * يُحظر قطعياً تدخل الأدوات في أسلوب الكاتب الأدبي، صياغاته البلاغية، أو فرض تعديلات على النص.
> * ملف المتن الأصلي [`00_BASELINE/novel_baseline.md`](00_BASELINE/novel_baseline.md) **محمي ومجمد بشكل مطلق**، ولا يجوز تعديله بأي شكل من الأشكال.

---

## 2. بيئة التطوير والتشغيل (Development Setup)

المشروع مصمم ليعمل دون تعقيد أو اعتماديات خارجية ثقيلة:
```bash
# 1. استنساخ المستودع
git clone https://github.com/bio-colab/novel.git
cd novel

# 2. تثبيت الاعتماديات الوحيدة (PyYAML)
pip install -r requirements.txt
```

---

## 3. تشغيل حزمة الاختبارات والمنسق المركزي

قبل تقديم أي مساهمة أو Pull Request، يجب أن تجتاز جميع الفحوصات بنسبة 100%:

### أ. تشغيل اختبارات الوحدة المؤتمتة (Unit Tests):
```bash
python -m unittest discover -s tests -v
```

### ب. تشغيل المنسق المركزي الشامل (Master Auditor):
```bash
python 02_TOOLS/master_auditor.py
```
يقوم المنسق المركزي بتنفيذ 6 مراحل فحص كاملة:
1. حزمة اختبارات الوحدة (`tests/`).
2. المدقق الحتمي العام بـ 20 فحصاً فرعياً (`world_auditor.py`).
3. المعايرة والربط المعرفي والسببي (`grounding_auditor.py`, `epistemic_tracker.py`, `causality_graph.py`).
4. محركات الأخلاق والسلوك والسياسة (`moral_entropy_monitor.py`, `psychology_detector.py`, `socio_demography_analyzer.py`, `historical_political_analyzer.py`, `chrono_event_engine.py`).
5. مقاييس الكثافة الحسية والإيقاع والحوار (`sensory_linter.py`, `dialogue_auditor.py`, `pacing_visualizer.py`, `character_tracker.py`).
6. مولد الرسم البياني المعرفي لأوبسيديان (`world_graph_builder.py`).

---

## 4. إرشادات إضافة ميزات وأدوات جديدة

### أ. إضافة قانون حتمي جديد:
1. عرّف القانون في [`01_SPECS_AND_RULES/PHYSICAL_LAWS.md`](01_SPECS_AND_RULES/PHYSICAL_LAWS.md) بنمط `[LAW-CATEGORY-NUMBER]`.
2. شغّل `python 02_TOOLS/meta_auditor.py` للتأكد من عدم وجود خروقات مرجعية.

### ب. إضافة أداة فحص جديدة:
1. ضع الأداة داخل مجلد `02_TOOLS/`.
2. احرص على تضمين دعم الترميز الدولي:
   ```python
   import sys
   if sys.stdout.encoding != 'utf-8':
       sys.stdout.reconfigure(encoding='utf-8')
   ```
3. اكتب اختبار وحدة مقابل داخل مجلد `tests/`.
4. ادمج الأداة في `02_TOOLS/world_auditor.py` أو `02_TOOLS/master_auditor.py`.

### ج. التعامل مع النص والاستشهاد:
* لا تستخدم أرقام الأسطر المطلقة المجردة؛ استخدم دائماً المحلل الدلالي [`02_TOOLS/semantic_text_parser.py`](02_TOOLS/semantic_text_parser.py):
  ```python
  from semantic_text_parser import SemanticNovelParser
  parser = SemanticNovelParser()
  loc = parser.locate_anchor("العبارة المستهدفة", part_num=3, chapter_num=2)
  ```

---

## 5. معايير رسائل الالتزام (Commit Message Conventions)

نتبع معايير [Conventional Commits](https://www.conventionalcommits.org/):
* `feat(...)`: ميزة أو أداة برمجية جديدة.
* `fix(...)`: تصحيح لخلل سببي أو فيزيائي أو برمجي.
* `test(...)`: إضافة أو تحديث اختبارات الوحدة.
* `docs(...)`: تحديث التوثيق أو سجلات القرارات المعمارية.
* `refactor(...)`: إعادة هيكلة الكود دون تغيير السلوك.

---

## 6. سجلات القرارات المعمارية (ADRs)

يرجى مراجعة مجلد [`docs/adr/`](docs/adr/) لفهم الأسس المعمارية والفلسفية التي بُنيت عليها قرارات المشروع الكبرى.
