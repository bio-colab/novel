"""
Sensory Linter (فاحص التوازن الحسي)
Measures the distribution of sensory modalities (Visual, Auditory, Tactile, Olfactory, Gustatory)
across chapters and flags abstract/unsensory passages.
"""
import re
import sys
from pathlib import Path
from collections import defaultdict

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

SENSORY_LEXICON = {
    'Tactile (لمسي / حراري / ألم)': [
        'برد', 'بارد', 'قارص', 'صقيع', 'جليد', 'حرارة', 'ساخن', 'سخونة', 'جمر', 'لهيب',
        'ملمس', 'ناعم', 'خشن', 'صلب', 'لزج', 'رطب', 'مبلول', 'جاف', 'ناشف', 'يبس', 'يابس',
        'لسع', 'لسعة', 'وخز', 'إبر', 'ضغط', 'ارتطام', 'صدمة', 'اهتزاز', 'ارتجاف', 'رعشة',
        'ألم', 'وجع', 'كدمة', 'جرح', 'نزيف', 'تشنج', 'تصلب', 'خدر', 'ثقيل', 'خفيف'
    ],
    'Visual (بصري / ضوء وظل وتفاصيل)': [
        'ضوء', 'نور', 'شمس', 'شفق', 'ظل', 'ظلال', 'ظلمة', 'عتمة', 'سواد', 'بياض', 'أصفر',
        'أحمر', 'أزرق', 'رمادي', 'كاحل', 'باهت', 'وميض', 'شرارة', 'خيط', 'نجم', 'نجوم',
        'لمعان', 'بريق', 'سطوع', 'شاحب', 'عجاج', 'غبار', 'رصاصي', 'صدأ', 'ثقب', 'شق'
    ],
    'Auditory (سمعي / أصوات وإيقاع)': [
        'صوت', 'طنين', 'فحيح', 'صرير', 'طقطقة', 'دوي', 'انفجار', 'أزيز', 'خشخشة', 'هدير',
        'قرع', 'ضرب', 'رنين', 'سكون', 'صمت', 'مواء', 'عواء', 'صفير', 'شهيق', 'زفير',
        'أنّ', 'أنين', 'حشرجة', 'همس', 'صراخ', 'ضحكة', 'موال', 'نغمة', 'نبض', 'سعال'
    ],
    'Olfactory (شمي)': [
        'رائحة', 'ريحة', 'شحم', 'ديزل', 'كاز', 'زيت', 'بارود', 'عرق', 'شيح', 'بول',
        'عطن', 'تراب', 'دم', 'رماد', 'دخان', 'نتانة', 'فوح', 'يشم', 'خياشيم'
    ],
    'Gustatory (تذوقي)': [
        'طعم', 'مرارة', 'ملح', 'مالح', 'عذب', 'ريق', 'جفاف', 'عطش', 'ابتلاع', 'بلعوم',
        'لسان', 'مص', 'لعق', 'حلاوة', 'حموضة'
    ]
}

def analyze_sensory_density(md_path: Path):
    sys.path.insert(0, str(Path(__file__).parent))
    try:
        from grounding_auditor import parse_novel_structure
        parts, _ = parse_novel_structure(str(md_path))
        all_chapters = []
        for p in parts:
            all_chapters.extend(p["chapters"])
    except Exception:
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        raw_chaps = re.split(r'\n(?=## \d+\. )', content)
        all_chapters = []
        for idx, chap in enumerate(raw_chaps):
            lines = chap.strip().splitlines()
            title = lines[0].replace("##", "").strip() if lines[0].startswith("##") else f"مقطع {idx}"
            body = "\n".join(lines[1:]) if lines[0].startswith("##") else chap
            all_chapters.append({"full_title": title, "body": body})
    
    print("=" * 70)
    print("تقرير الفحص الحسي (Sensory Grounding Audit)")
    print("=" * 70)
    
    overall_counts = defaultdict(int)
    total_words_all = 0

    for chap in all_chapters:
        title = chap["full_title"]
        chapter_text = chap["body"]
        
        words = re.findall(r'\b\w+\b', chapter_text)
        word_count = len(words)
        total_words_all += word_count
        
        counts = {}
        for sense, keywords in SENSORY_LEXICON.items():
            pattern = r'\b(' + '|'.join(re.escape(k) for k in keywords) + r')\b'
            matches = len(re.findall(pattern, chapter_text))
            counts[sense] = matches
            overall_counts[sense] += matches
            
        print(f"\n{title} (عدد الكلمات: {word_count})")
        print("-" * 50)
        for sense, count in counts.items():
            density = (count / word_count * 1000) if word_count > 0 else 0
            bar = '█' * int(density)
            print(f"  {sense:<30}: {count:>3} مرات ({density:>4.1f} لكل 1000 كلمة) {bar}")
            
        # Warning if Olfactory or Tactile is very low
        tactile_density = counts['Tactile (لمسي / حراري / ألم)'] / word_count * 1000 if word_count else 0
        if tactile_density < 5:
            print("  ⚠️ تنبيه: الكثافة اللمسية منخفضة في هذا الفصل!")

    print("\n" + "=" * 70)
    print("الإحصائية الإجمالية للرواية:")
    print(f"إجمالي الكلمات: {total_words_all}")
    for sense, count in overall_counts.items():
        density = (count / total_words_all * 1000) if total_words_all > 0 else 0
        print(f"  {sense:<30}: {count:>4} مرة ({density:>4.1f} في الألف)")
    print("=" * 70)

if __name__ == '__main__':
    base_dir = Path(__file__).resolve().parent.parent
    md_file = base_dir / "00_BASELINE" / "novel_baseline.md"
    analyze_sensory_density(md_file)
