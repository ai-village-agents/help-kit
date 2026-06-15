#!/usr/bin/env python3
"""HTML-Aware Translation Scaffold Helper for Help Kit.

This script parses our emergency HTML pages, extracts translatable text nodes,
and demonstrates how to integrate automated drafts with strict clinical preservation.
It is intended as a scaffolding tool to generate draft translations (*.html.draft)
which MUST be reviewed by fluent local humans before deployment.
"""

import os
import sys
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("BeautifulSoup4 is required. Installing bs4...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "beautifulsoup4"])
    from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]

# Protected medical/first-aid tokens that should not be auto-translated to protect critical dosages/timings
PROTECTED_TOKENS = [
    "911", "112", "999", "100-120", "5 cm", "2 inches", "6 cm", "2.4 inches", 
    "30:2", "15:2", "5-15", "20", "20mg", "10mg", "10-14", "4mg", "2-3", "5", 
    "103°F", "39.4°C", "95°F", "35°C", "1/2", "6", "AHA", "ERC", "WHO", "CDC", 
    "EPA", "NHS", "SAMHSA", "Naloxone", "Narcan", "Epinephrine", "AED"
]

def mock_translate(text, target_lang):
    """A mock translation function that appends a language suffix.
    In real usage, this would call a secure translation API.
    """
    if not text.strip():
        return text
    # Preserve formatting while marking text for translation
    return f"[{target_lang.upper()}]: {text}"

def is_protected_element(parent_name, parent_classes):
    """Determine if an element should not be machine-translated."""
    if parent_name in ['script', 'style', 'code', 'pre']:
        return True
    if parent_classes:
        # Avoid translating pure structural buttons or brand indicators
        if any(cls in parent_classes for cls in ['brand', 'site-title', 'tag']):
            return True
    return False

def translate_html_file(input_path, output_path, target_lang):
    print(f"Processing: {input_path.relative_to(ROOT)}")
    with open(input_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        
    # Translate meta description and title
    title_tag = soup.find('title')
    if title_tag and title_tag.string:
        title_tag.string = f"{mock_translate(title_tag.string, target_lang)} | Help Kit"
        
    desc_tag = soup.find('meta', attrs={'name': 'description'})
    if desc_tag and desc_tag.get('content'):
        desc_tag['content'] = mock_translate(desc_tag['content'], target_lang)

    # Safely traverse and translate text nodes
    for element in soup.find_all(string=True):
        parent = element.parent
        parent_classes = parent.get('class', []) if parent else []
        parent_name = parent.name if parent else ''
        
        if is_protected_element(parent_name, parent_classes):
            continue
            
        text = element.strip()
        # Only translate meaningful text blocks
        if len(text) > 1 and not text.isdigit():
            # Check for protected numbers/dosages
            contains_protected = any(token in text for token in PROTECTED_TOKENS)
            if contains_protected:
                # Wrap or prefix with a critical review warning flag for localizers
                translated_text = f"🚨[REVIEW_REQUIRED] {mock_translate(text, target_lang)}"
            else:
                translated_text = mock_translate(text, target_lang)
            element.replace_with(translated_text)

    # Save as a draft file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(soup.prettify())
    print(f"Draft written to: {output_path.relative_to(ROOT)}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/translate_kit.py <target_language_code> [html_file_path]")
        print("Example: python3 scripts/translate_kit.py es index.html")
        sys.exit(1)
        
    target_lang = sys.argv[1].lower()
    
    if len(sys.argv) >= 3:
        files_to_process = [ROOT / sys.argv[2]]
    else:
        # Default to translating index.html as a test candidate
        files_to_process = [ROOT / "index.html"]
        
    for file_path in files_to_process:
        if not file_path.exists():
            print(f"File not found: {file_path}")
            continue
        output_dir = ROOT / target_lang
        output_file = output_dir / file_path.name
        # Write draft filename with .draft suffix to prevent unreviewed active publishing
        draft_file = output_file.with_suffix('.html.draft')
        translate_html_file(file_path, draft_file, target_lang)

if __name__ == "__main__":
    main()
