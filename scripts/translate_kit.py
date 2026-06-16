import json
from deep_translator import GoogleTranslator
import time
#!/usr/bin/env python3
"""HTML-Aware Translation Scaffold Helper for Help Kit.

This script parses our emergency HTML pages, extracts translatable text nodes,
and demonstrates how to integrate automated drafts with strict clinical preservation.
It is intended as a scaffolding tool to generate draft translations (*.html.draft)
which MUST be reviewed by fluent local humans before deployment.
"""

import os
import re
import sys
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("BeautifulSoup4 is required. Install it before running this draft helper.", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[1]
DRAFT_ROOT = ROOT / "_translation-drafts"

# Protected medical/first-aid tokens that should not be auto-translated to protect critical dosages/timings
PROTECTED_TOKENS = [
    "911", "112", "999", "100-120", "100–120", "5 cm", "2 inches", "6 cm", "2.4 inches",
    "30:2", "15:2", "5-15", "5–15", "20", "20mg", "20 mg", "10mg", "10 mg",
    "10-14", "10–14", "4mg", "4 mg", "2-3", "2–3", "5", "1 liter", "1 litre",
    "103°F", "39.4°C", "95°F", "35°C", "1/2", "6", "AHA", "ERC", "WHO", "CDC",
    "EPA", "NHS", "SAMHSA", "Naloxone", "naloxone", "Narcan", "Epinephrine", "epinephrine", "AED"
]

CACHE_PATH = ROOT / "scripts/translation_cache.json"
TRANSLATION_CACHE = {}

def load_cache():
    global TRANSLATION_CACHE
    if CACHE_PATH.exists():
        try:
            with open(CACHE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                # keys are "clean_text||target_lang"
                for k, v in data.items():
                    if "||" in k:
                        parts = k.split("||", 1)
                        TRANSLATION_CACHE[(parts[0], parts[1])] = v
                print(f"Loaded {len(TRANSLATION_CACHE)} cached translations from disk.")
        except Exception as e:
            import sys
            print(f"Failed to load cache: {e}", file=sys.stderr)

def save_cache():
    try:
        with open(CACHE_PATH, "w", encoding="utf-8") as f:
            data = {f"{k[0]}||{k[1]}": v for k, v in TRANSLATION_CACHE.items()}
            json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Saved {len(TRANSLATION_CACHE)} translations to disk cache.")
    except Exception as e:
        import sys
        print(f"Failed to save cache: {e}", file=sys.stderr)

load_cache()

def mock_translate(text, target_lang):
    """A translation function that uses deep-translator to translate text.
    Uses a persistent local disk cache to avoid duplicate API calls and prevent rate limiting.
    """
    if not text.strip():
        return text
    
    clean_text = " ".join(text.split())
    if not clean_text:
        return text
        
    cache_key = (clean_text, target_lang)
    if cache_key in TRANSLATION_CACHE:
        return TRANSLATION_CACHE[cache_key]
        
    try:
        # Small delay to prevent rate limiting
        time.sleep(0.05)
        translated = GoogleTranslator(source='auto', target=target_lang).translate(clean_text)
        
        # Preserve original leading and trailing whitespaces
        lead_ws = text[:len(text)-len(text.lstrip())]
        trail_ws = text[len(text.rstrip()):]
        res = f"{lead_ws}{translated}{trail_ws}"
        
        TRANSLATION_CACHE[cache_key] = res
        # Save cache periodically
        if len(TRANSLATION_CACHE) % 10 == 0:
            save_cache()
            
        return res
    except Exception as e:
        import sys
        print(f"Translation failed for '{clean_text}' to {target_lang}: {e}", file=sys.stderr)
        # Sleep on failure to let rate limiting cool down
        time.sleep(2.0)
        return f"[{target_lang.upper()}]: {text}"

def is_protected_element(parent_name, parent_classes):
    """Determine if an element should not be machine-translated."""
    if parent_name in ['script', 'style', 'code', 'pre', 'title']:
        return True
    if parent_classes:
        # Avoid translating pure structural buttons or brand indicators
        if any(cls in parent_classes for cls in ['brand', 'site-title', 'tag']):
            return True
    return False


def mark_translation_draft(soup, target_lang):
    """Mark generated translations as unreviewed drafts if directly opened."""
    head = soup.find('head')
    if head and not soup.find('meta', attrs={'name': 'robots'}):
        robots = soup.new_tag('meta')
        robots['name'] = 'robots'
        robots['content'] = 'noindex, nofollow, noarchive'
        head.insert(0, robots)
    elif head:
        for robots in soup.find_all('meta', attrs={'name': 'robots'}):
            robots['content'] = 'noindex, nofollow, noarchive'

    body = soup.find('body')
    if body and not soup.find(attrs={'data-draft-warning': 'true'}):
        warning = soup.new_tag('div')
        warning['class'] = ['notice', 'danger']
        warning['data-draft-warning'] = 'true'
        warning.string = (
            f'UNREVIEWED MACHINE TRANSLATION DRAFT ({target_lang}). '
            'Do not use for medical guidance, sharing, printing, or training until fluent local reviewers verify all emergency numbers, doses, timings, and local guidance against the English source.'
        )
        body.insert(0, warning)

def translate_html_file(input_path, output_path, target_lang):
    print(f"Processing: {input_path.relative_to(ROOT)}")
    with open(input_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        
    # Update html lang attribute
    html_tag = soup.find('html')
    if html_tag:
        html_tag['lang'] = target_lang

    # Translate meta description and title
    title_tag = soup.find('title')
    if title_tag and title_tag.string:
        title_tag.string = f"{mock_translate(title_tag.string, target_lang)} | Help Kit"
        
    desc_tag = soup.find('meta', attrs={'name': 'description'})
    if desc_tag and desc_tag.get('content'):
        desc_tag['content'] = mock_translate(desc_tag['content'], target_lang)

    # Safely traverse and translate text nodes
    for element in soup.find_all(string=True):
        if type(element).__name__ in ['Comment', 'Doctype', 'Declaration']:
            continue
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

    mark_translation_draft(soup, target_lang)

    # Save as a draft file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(soup.prettify())
    print(f"Draft written to: {output_path.relative_to(ROOT)}")
    save_cache()

def resolve_input_path(arg):
    candidate = (ROOT / arg).resolve()
    try:
        rel = candidate.relative_to(ROOT)
    except ValueError:
        raise ValueError(f"Input path must stay inside the Help Kit repo: {arg}")
    if candidate.suffix != ".html" or ".draft" in candidate.suffixes:
        raise ValueError(f"Input path must be an active .html file, not a draft or other file: {arg}")
    return candidate, rel

def validate_target_lang(target_lang):
    if not re.fullmatch(r"[a-z]{2,3}(?:-[a-z0-9]{2,8})*", target_lang):
        raise ValueError("Language code must be a simple BCP-47-style code such as es, fr, pt-br, or zh-hant")
    return target_lang

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/translate_kit.py <target_language_code> [html_file_path]")
        print("Example: python3 scripts/translate_kit.py es index.html")
        sys.exit(1)
        
    try:
        target_lang = validate_target_lang(sys.argv[1].lower())
    except ValueError as e:
        print(e, file=sys.stderr)
        sys.exit(1)

    raw_files = sys.argv[2:] if len(sys.argv) >= 3 else ["index.html"]

    for raw_path in raw_files:
        try:
            file_path, rel_path = resolve_input_path(raw_path)
        except ValueError as e:
            print(e, file=sys.stderr)
            sys.exit(1)
        if not file_path.exists():
            print(f"File not found: {file_path}", file=sys.stderr)
            sys.exit(1)
        output_dir = DRAFT_ROOT / target_lang / rel_path.parent
        output_file = output_dir / rel_path.name
        # Write draft filename with .draft suffix to prevent unreviewed active publishing
        draft_file = output_file.with_suffix('.html.draft')
        translate_html_file(file_path, draft_file, target_lang)

if __name__ == "__main__":
    main()
