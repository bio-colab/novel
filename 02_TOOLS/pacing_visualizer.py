"""
Pacing & Tension Visualizer (راسم الإيقاع والتوتر السردي)
Calculates pacing metrics: average sentence length, dialogue ratio, and tension score
per chapter to map the narrative heartbeat.
"""
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

ACTION_KEYWORDS = [
    'رمى', 'ضرب', 'صرخ', 'سقط', 'قفز', 'زحف', 'ركض', 'طارت', 'انفجر', 'اخترق',
    'رصاص', 'دم', 'تمزق', 'انخلع', 'انكسر', 'طراخ', 'طخ', 'أطلق', 'قبض', 'اندفع',
    'دفع', 'سحب', 'انقض', 'انكسار', 'شلل', 'ارتطام'
]

def analyze_pacing(md_path: Path):
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split into numbered sections (e.g. ## 1. رائحة الصوف...)
    chapters = re.split(r'\n(?=## \d+\. )', content)
    
    print("=" * 85)
    print("تحليل الإيقاع والتوتر الدرامي عبر فصول الرواية (Pacing & Tension Audit)")
    print("=" * 85)
    print(f"{'الفصل':<32} | {'كلمات':>6} | {'جمل':>5} | {'م.طول الجملة':>12} | {'حوار %':>8} | {'مؤشر التوتر':>11}")
    print("-" * 85)
    
    for idx, chap in enumerate(chapters):
        if not chap.strip():
            continue
        lines = chap.strip().splitlines()
        title = lines[0].replace("##", "").strip() if lines[0].startswith("##") else f"مقدمة {idx}"
        body = "\n".join(lines[1:]) if lines[0].startswith("##") else chap
        
        words = re.findall(r'\b\w+\b', body)
        total_words = len(words)
        if total_words == 0:
            continue
            
        # Split sentences roughly by . / ! / ؟ / newline
        sentences = [s.strip() for s in re.split(r'[.!?؟\n]+', body) if len(s.strip().split()) > 1]
        sentence_count = max(1, len(sentences))
        avg_sentence_len = total_words / sentence_count
        
        # Dialogue ratio (quotes: «...» or "..." or '...')
        dialogue_matches = re.findall(r'«([^»]+)»|"([^"]+)"', body)
        dialogue_words = sum(len(re.findall(r'\b\w+\b', m[0] or m[1])) for m in dialogue_matches)
        dialogue_ratio = (dialogue_words / total_words) * 100 if total_words > 0 else 0
        
        # Action density (tension score)
        action_count = sum(len(re.findall(r'\b' + re.escape(w) + r'\b', body)) for w in ACTION_KEYWORDS)
        tension_score = (action_count / total_words) * 1000
        
        tension_bar = '⚡' * min(10, int(tension_score / 2.5))
        print(f"{title[:30]:<32} | {total_words:>6} | {sentence_count:>5} | {avg_sentence_len:>12.1f} | {dialogue_ratio:>7.1f}% | {tension_score:>6.1f} {tension_bar}")
        
    print("=" * 85)
    print("دلالات المؤشرات:")
    print("- م.طول الجملة القصير (< 10 كلمات): إيقاع سريع / لاهث / اشتباك.")
    print("- م.طول الجملة الطويل (> 16 كلمة): إيقاع تأملي / ترقب / تأسيس جوي.")
    print("- مؤشر التوتر (⚡): كثافة أفعال الصدمة والاشتباك والموت لكل 1000 كلمة.")
    print("=" * 85)

if __name__ == '__main__':
    base_dir = Path(__file__).resolve().parent.parent
    md_file = base_dir / "00_BASELINE" / "novel_baseline.md"
    analyze_pacing(md_file)
