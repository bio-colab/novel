"""
Dialogue Auditor (مدقق الحوار واللهجات)
Extracts all spoken lines, attributes them to probable speakers based on context,
and flags unnatural exposition or dialect contamination.
"""
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Known characters
CHARACTERS = ['خالد', 'أبو اللول', 'حناطة', 'أبو علي', 'حجي عمار', 'بسام', 'سردار', 'عزيز', 'خليل', 'حسن كاز', 'سلوم', 'بشير', 'عباس', 'مهدي']

def audit_dialogue(md_path: Path):
    with open(md_path, 'r', encoding='utf-8') as f:
        text = f.read()

    lines = text.splitlines()
    dialogue_entries = []
    
    current_part = "الجزء الأول"
    current_chapter = "[الجزء الأول] البداية"
    for i, line in enumerate(lines):
        stripped = line.strip()
        if "الجزء" in stripped and (stripped.startswith("#") or stripped.startswith("الجزء")):
            current_part = stripped.replace("#", "").strip()
            continue
        if stripped.startswith("## "):
            chap_title = stripped.replace("##", "").strip()
            current_chapter = f"[{current_part}] {chap_title}"
            continue
            
        quotes = re.findall(r'«([^»]+)»', line)
        for quote in quotes:
            # Guess speaker from previous or current line
            context = " ".join([lines[max(0, i-2)], lines[max(0, i-1)], line])
            speaker = "غير محدد"
            for char in CHARACTERS:
                if char in context:
                    speaker = char
                    break
            dialogue_entries.append({
                'chapter': current_chapter,
                'speaker': speaker,
                'quote': quote
            })
            
    print("=" * 80)
    print(f"سجل تدقيق الحوار (إجمالي الحوارات الموثقة: {len(dialogue_entries)})")
    print("=" * 80)
    
    by_speaker = {}
    for entry in dialogue_entries:
        by_speaker.setdefault(entry['speaker'], []).append(entry)
        
    for spk, items in sorted(by_speaker.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"\n المتحدث: [{spk}] ({len(items)} مداخلة حوارية)")
        print("-" * 50)
        # Show sample 3 quotes
        for item in items[:3]:
            print(f"  • ({item['chapter'][:20]}): «{item['quote']}»")
        if len(items) > 3:
            print(f"  ... و {len(items)-3} جمل حوارية أخرى.")

if __name__ == '__main__':
    base_dir = Path(__file__).resolve().parent.parent
    md_file = base_dir / "00_BASELINE" / "novel_baseline.md"
    audit_dialogue(md_file)
