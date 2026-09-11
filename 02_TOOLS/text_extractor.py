"""
Text Extractor & Normalizer
Extracts plain text / clean markdown from RTF source preserving chapters and structural marks.
"""
import os
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

def extract_rtf_to_txt(rtf_path: Path, output_txt_path: Path):
    cmd = [
        "powershell",
        "-NoProfile",
        "-Command",
        f"""
        Add-Type -AssemblyName System.Windows.Forms
        $rtb = New-Object System.Windows.Forms.RichTextBox
        $rtfFile = (Get-Item -LiteralPath '{rtf_path.resolve()}').FullName
        $bytes = [System.IO.File]::ReadAllBytes($rtfFile)
        $content = [System.Text.Encoding]::UTF8.GetString($bytes)
        if (-not $content.StartsWith('{{\\rtf')) {{
            $content = [System.Text.Encoding]::Default.GetString($bytes)
        }}
        $rtb.Rtf = $content
        [System.IO.File]::WriteAllText('{output_txt_path.resolve()}', $rtb.Text, [System.Text.Encoding]::UTF8)
        """
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if res.returncode != 0:
        print(f"Error extracting RTF: {res.stderr}", file=sys.stderr)
        sys.exit(1)
    print(f"Successfully extracted to txt ({os.path.getsize(output_txt_path)} bytes)")

def convert_to_clean_markdown(txt_path: Path, md_path: Path):
    with open(txt_path, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()

    lines = text.splitlines()
    cleaned_lines = []
    
    for line in lines:
        stripped = line.strip()
        # Detect main parts
        if stripped.startswith("الجزء الأول") or stripped.startswith("الجزء الثاني") or \
           stripped.startswith("الجزء الثالث") or stripped.startswith("الجزء الرابع") or \
           stripped.startswith("الجزء الخامس"):
            cleaned_lines.append(f"\n# {stripped}\n")
        # Detect chapters (e.g., 1. رائحة الصوف والشحم)
        elif len(stripped) > 2 and stripped[0].isdigit() and (stripped[1] == '.' or (stripped[1].isdigit() and stripped[2] == '.')):
            cleaned_lines.append(f"\n## {stripped}\n")
        else:
            cleaned_lines.append(line)

    md_content = "\n".join(cleaned_lines)
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"Successfully formatted clean markdown ({os.path.getsize(md_path)} bytes)")

if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent
    rtf_file = base_dir / "00_BASELINE" / "رواية_الأصلية.rtf"
    if not rtf_file.exists():
        rtf_file = base_dir / "رواية.rtf"
    
    txt_output = base_dir / "00_BASELINE" / "novel_baseline.txt"
    md_output = base_dir / "00_BASELINE" / "novel_baseline.md"
    
    extract_rtf_to_txt(rtf_file, txt_output)
    convert_to_clean_markdown(txt_output, md_output)
