"""
Character Tracker & Tic Auditor (متتبع الشخصيات واللوازم الحركية)
Tracks character presence, dialogue frequency, and involuntary tics (اللاوعي الجسدي)
across the narrative to ensure continuity and psychological depth.
"""
import re
import sys
from pathlib import Path
from collections import defaultdict

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

CHARACTERS = {
    'خالد': {
        'aliases': ['خالد', 'أبو وليد'],
        'tics': ['ندبة', 'فكه', 'أخدود', 'سبابته', 'سبابة', 'ندبته'],
        'role': 'قائد الحرس'
    },
    'أبو علي': {
        'aliases': ['أبو علي'],
        'tics': ['بنطاله', 'يمسح', 'كفيه', 'خرقة', 'فخذيه', 'طاسة'],
        'role': 'خادم القطار'
    },
    'أبو اللول': {
        'aliases': ['أبو اللول'],
        'tics': ['عرق', 'أنفه', 'نزيف', 'يرتجف', 'اصطكت', 'بوله', 'بول'],
        'role': 'حارس منهار'
    },
    'حناطة': {
        'aliases': ['حناطة'],
        'tics': ['ضحكة', 'فحيح', 'يغسل', 'كفيه', 'هستيرية', 'سجائر'],
        'role': 'حارس متوتر'
    },
    'عباس': {
        'aliases': ['عباس'],
        'tics': ['حصاة', 'صوانية', 'ملساء', 'شال', 'الهور'],
        'role': 'حارس المنصة الخلفية'
    },
    'سردار': {
        'aliases': ['سردار'],
        'tics': ['قبضتيه', 'كفيه', 'مفاصل', 'ندوب', 'يفتح', 'يغلق'],
        'role': 'سجين كردي / مقاتل'
    },
    'عزيز': {
        'aliases': ['عزيز'],
        'tics': ['إبهامه', 'سبابته', 'يفرك', 'يمسح', 'صامت', 'صخرة', 'موال'],
        'role': 'سجين صامت'
    },
    'خليل': {
        'aliases': ['خليل', 'التركماني'],
        'tics': ['حذائه', 'حذاء', 'يمسح', 'دشداشته'],
        'role': 'سجين تركماني وقور'
    },
    'بسام': {
        'aliases': ['بسام'],
        'tics': ['ظفر', 'سبابته', 'إبهامه', 'يضغط', 'يبيض', 'شاش'],
        'role': 'سجين ممرض'
    },
    'حجي عمار': {
        'aliases': ['حجي عمار', 'عمار'],
        'tics': ['ياقته', 'كمه', 'زر', 'ساعة', 'معصمه', 'التخطيط', 'محضر'],
        'role': 'مدير عام سابق'
    },
    'سلوم': {
        'aliases': ['سلوم'],
        'tics': ['جيب', 'جيبه', 'فارغ', 'يفرك', 'بطانة'],
        'role': 'فتى فقير'
    },
    'بشير': {
        'aliases': ['بشير'],
        'tics': ['ورقة', 'يطوي', 'يفرد', 'ثنية', 'وصل'],
        'role': 'سجين كتوم'
    },
    'حسن كاز': {
        'aliases': ['حسن كاز', 'حسن'],
        'tics': ['ساعته', 'نقود', 'دنانير', 'جيبه الداخلي', 'مفتاح'],
        'role': 'مهرب'
    },
    'مهدي': {
        'aliases': ['مهدي'],
        'tics': ['هادئ', 'ظل', 'ينسل', 'يقفز'],
        'role': 'سجين غامض'
    }
}

def audit_characters(md_path: Path):
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    parts = re.split(r'\n(?=# الجزء )', content)
    
    print("=" * 80)
    print("مصفوفة تتبع الشخصيات واللوازم الحركية (Character & Tic Audit Matrix)")
    print("=" * 80)
    
    matrix = defaultdict(lambda: defaultdict(lambda: {'mentions': 0, 'tics': 0}))
    part_names = []

    for part_idx, part in enumerate(parts):
        if not part.strip():
            continue
        first_line = part.strip().splitlines()[0]
        part_name = first_line.replace("#", "").strip() if first_line.startswith("#") else f"مقدمة {part_idx}"
        part_names.append(part_name)

        for char_name, meta in CHARACTERS.items():
            # Mention count
            alias_pattern = r'\b(' + '|'.join(re.escape(a) for a in meta['aliases']) + r')\b'
            mentions = len(re.findall(alias_pattern, part))
            
            # Tic count
            tic_pattern = r'\b(' + '|'.join(re.escape(t) for t in meta['tics']) + r')\b'
            tics = len(re.findall(tic_pattern, part))
            
            matrix[char_name][part_name] = {'mentions': mentions, 'tics': tics}

    # Print summary table
    header = f"{'الشخصية':<15} | {'الدور':<22} | " + " | ".join(f"{p[:10]:<10}" for p in part_names) + " | الإجمالي"
    print(header)
    print("-" * len(header))
    
    for char_name, meta in CHARACTERS.items():
        row = f"{char_name:<15} | {meta['role']:<22} | "
        total_m = 0
        total_t = 0
        for p in part_names:
            m = matrix[char_name][p]['mentions']
            t = matrix[char_name][p]['tics']
            total_m += m
            total_t += t
            cell = f"{m}m/{t}t"
            row += f"{cell:<10} | "
        row += f"({total_m}m / {total_t}t)"
        print(row)
        
    print("\nملاحظة: m = مرات الورود بالاسم، t = مرات تكرار الحركة العصابية/اللاإرادية")
    print("=" * 80)

if __name__ == '__main__':
    base_dir = Path(__file__).resolve().parent.parent
    md_file = base_dir / "00_BASELINE" / "novel_baseline.md"
    audit_characters(md_file)
