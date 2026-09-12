# مقترح تعديل سردي حتمي: PR-006-MEHDI-EXIT
## اجتياز مهدي لقوس نيران الكمين واختفاؤه دون بصمة تتبع فيزيائية

**تاريخ الصياغة:** 2026-09-12  
**الحالة:** `قيد المراجعة والاعتماد (Under Review)`  
**المحرر:** مهندس السرد ونظام المحاكاة  
**المعرف المرتبط:** [`WORLD-BUG-006`](../../03_AUDIT_AND_ISSUES/WORLD_BUGS.yaml)  
**القانون المنتهك:** `LAW-SPATIAL-02 (Mass and Spatial Trajectory Conservation)`  
**الطابع الزمني الحتمي:** `00:15:00 (Minute 315 - Breach Confusion)`  
**المرساة الدلالية:** الجزء 3، الفصل 4 (تقريب السطر: 717)  
**النص المستهدف:** «قفز مهدي»

---

## 1. التوصيف الحتمي للخلل المرجعي (Diagnostic Invariant)
وثّق النص خروج مهدي بالقفز من الباب الجانبي المنزلق للعربة الوسطى بعد أن سحبه حناطة (الجزء الثالث، الفصل 4، سطر 717)، لكن الخرق الفيزيائي الحتمي يكمن في كيفية نجاته من القفز بمحاذاة السكة واجتيازه قوس نيران الكمين المنهمر على الجانبين واختفائه التام في العراء دون أن يصاب برصاصة ودون أن يترك أي بصمة دم أو أثر حركي على الحصى.

---

## 2. الشرط الفيزيائي والسببي الحاكم (Required Invariant)
حركة أي كتلة حيوية بشرية (>60 كغم) تقفز إلى فضاء اشتباك مكشوف محاط بقوس نيران رشاشة تخضع لحتمية الاحتمال البالستي وترك آثار مادية ملموسة (انزلاق حصى، قطرات دم، أو تمزق قماش).
* **الحد الأدنى المطلوب:** `Ballistic survival probability and physical ground trace required.`

---

## 3. حزمة الأدلة والافتراضات (Evidence & Grounding)
* **الأدلة النصية المثبتة:**
  * `exit_aperture: middle_car_sliding_side_door (source: Part 3, Ch 4, Lines 701-717: Hannata unlatched sliding door, Mahdi jumped out into darkness)`
  * `ambush_firing_arc: covering both flanks (source: Part 3, Ch 1, Line 611 & Ch 4, Line 713)`
* **افتراضات المحاكاة:**
  * `ballast_surface_trace: zero footprints or blood detected (class: assumption; physical anomaly in open gravel)`
  * `ballistic_crossfire_exposure_seconds: 4.5 (class: assumption; exposure time between door threshold and dead zone)`

---

## 4. مقترح الإصلاح الذري للكاتب (Atomic Remediation Proposal)
تأسيس الغطاء البيئي والبالستي للقفزة: استغلال كثافة دخان احتراق شحم المحور المتجه مع الريح (سمت 135°)، واستتار مهدي بالزاوية الميتة لكتلة عجلات البوجي (Bogie) الضخمة أثناء تدحرجه في منخفض الحصى المحاذي للسكة قبل الانسلال في سواد وادي الظل.

---

## 5. حالة الاعتماد وميثاق الحياد الإبداعي
* [ ] **معتمد من الكاتب (Author Blessed):** (بانتظار موافقة الكاتب الصريحة قبل أي دمج في المتن المرجعي)
* **ميثاق المنظومة:** «نحن نُحلل ونُقيّم.. ولا نُقوّم». المتن الأصلي في `00_BASELINE/novel_baseline.md` محمي ومجمد بنسبة 100%.
