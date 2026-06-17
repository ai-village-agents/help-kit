import os
import re
import sys
from collections import Counter
from pathlib import Path
from bs4 import BeautifulSoup

# Translation drafts/cache are not public medical guidance, but stale source strings
# can be reused later when regenerating drafts. Keep this narrow: it catches
# overclaim phrases that have already caused regressions or stale draft text.
DISCOURAGED_TRANSLATION_PHRASES = [
    ("save a life", "Avoid overclaiming outcomes; use concrete actions and emergency handoff wording."),
    ("saves lives", "Avoid overclaiming outcomes; use concrete actions and emergency handoff wording."),
    ("save lives", "Avoid overclaiming outcomes; use concrete actions and emergency handoff wording."),
    ("will save", "Avoid overclaiming outcomes; use concrete actions and emergency handoff wording."),
    ("can prevent death", "Stale prevent-death overclaim; use reduce-risk wording before reuse."),
    ("give aspirin if appropriate", "Unsafe heart-attack shorthand; aspirin must be dispatcher/clinician/local-protocol gated with contraindications."),
    ("chew aspirin", "Unsafe heart-attack shorthand; aspirin must be dispatcher/clinician/local-protocol gated with contraindications."),
    ("donnez-lui de l'aspirine si nécessaire", "Unsafe French aspirin shorthand; update draft/cache wording before reuse."),
    ("mâcher de l'aspirine", "Unsafe French aspirin shorthand; update draft/cache wording before reuse."),
    ("dé aspirina si corresponde", "Unsafe Spanish aspirin shorthand; update draft/cache wording before reuse."),
    ("masticar aspirina", "Unsafe Spanish aspirin shorthand; update draft/cache wording before reuse."),
    ("यदि उचित हो तो एस्पिरिन दें", "Unsafe Hindi aspirin shorthand; update draft/cache wording before reuse."),
    ("एस्पिरिन चबाएं", "Unsafe Hindi aspirin shorthand; update draft/cache wording before reuse."),
    ("puede evitar la muerte", "Stale Spanish prevent-death overclaim; update draft/cache wording before reuse."),
    ("peut éviter la mort", "Stale French prevent-death overclaim; update draft/cache wording before reuse."),
    ("मृत्यु या मस्तिष्क की चोट को रोका जा सकता है", "Stale Hindi prevent-death overclaim; update draft/cache wording before reuse."),
    ("salvar vidas", "Stale Spanish save-lives overclaim; update draft/cache wording before reuse."),
    ("salvar una vida", "Stale Spanish save-life overclaim; update draft/cache wording before reuse."),
    ("sauver des vies", "Stale French save-lives overclaim; update draft/cache wording before reuse."),
    ("sauver une vie", "Stale French save-life overclaim; update draft/cache wording before reuse."),
    ("sauvez une vie", "Stale French save-life overclaim; update draft/cache wording before reuse."),
    ("जान बचा सकता है", "Stale Hindi save-life overclaim; update draft/cache wording before reuse."),
]

# Exact stale topic-roster fragments from older 12-topic/triage-only summaries.
# They omit the later cold-weather and heart-attack guides, so cached/draft text
# containing them should be regenerated instead of reused.
STALE_TOPIC_ROSTER_PHRASES = [
    (
        "severe allergy/anaphylaxis, and a quick emergency navigator",
        "Stale topic roster missing cold-weather and heart-attack guides.",
    ),
    (
        "allergie/anaphylaxie grave et un navigateur d'urgence rapide",
        "Stale French topic roster missing cold-weather and heart-attack guides.",
    ),
]


def normalized_text(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    for element in soup(["script", "style"]):
        element.decompose()
    return re.sub(r'\s+', ' ', soup.get_text()).strip().lower()


def audit_discouraged_translation_text(repo_dir, drafts_dir):
    issues = []

    cache_path = Path(repo_dir, "scripts", "translation_cache.json")
    if cache_path.exists():
        import json
        try:
            cache = json.loads(cache_path.read_text(encoding='utf-8'))
        except Exception as exc:
            issues.append(f"Could not parse translation cache: {exc}")
        else:
            for key, value in cache.items():
                source = key.rsplit("||", 1)[0]
                haystacks = [("source key", source.lower()), ("cached value", str(value).lower())]
                for phrase, guidance in DISCOURAGED_TRANSLATION_PHRASES:
                    phrase_lower = phrase.lower()
                    for label, haystack in haystacks:
                        if phrase_lower in haystack:
                            issues.append(f"translation_cache.json {label} contains discouraged phrase '{phrase}': {guidance}")
                for phrase, guidance in STALE_TOPIC_ROSTER_PHRASES:
                    phrase_lower = phrase.lower()
                    for label, haystack in haystacks:
                        if phrase_lower in haystack:
                            issues.append(f"translation_cache.json {label} contains stale topic roster '{phrase}': {guidance}")

    for draft_path in sorted(Path(drafts_dir).rglob('*.draft')):
        try:
            draft_text = normalized_text(draft_path.read_text(encoding='utf-8'))
        except OSError as exc:
            issues.append(f"Could not read {draft_path.relative_to(repo_dir)}: {exc}")
            continue
        for phrase, guidance in DISCOURAGED_TRANSLATION_PHRASES:
            if phrase.lower() in draft_text:
                rel = draft_path.relative_to(repo_dir)
                issues.append(f"{rel} contains discouraged phrase '{phrase}': {guidance}")
        for phrase, guidance in STALE_TOPIC_ROSTER_PHRASES:
            if phrase.lower() in draft_text:
                rel = draft_path.relative_to(repo_dir)
                issues.append(f"{rel} contains stale topic roster '{phrase}': {guidance}")
    return issues

def audit_draft_safety_gates(repo_dir, drafts_dir):
    issues = []
    repo_path = Path(repo_dir)

    for lang in ('es', 'fr', 'hi'):
        public_root = repo_path / lang
        if public_root.exists():
            issues.append(f"{lang}: public translation directory must not exist before review")

        draft_root = Path(drafts_dir) / lang
        if draft_root.exists():
            active_html = [
                path.relative_to(repo_path)
                for path in sorted(draft_root.rglob('*.html'))
                if '.draft' not in path.suffixes
            ]
            if active_html:
                preview = ', '.join(str(path) for path in active_html[:5])
                suffix = '...' if len(active_html) > 5 else ''
                issues.append(f"{lang}: active .html files present in draft area: {preview}{suffix}")

    sitemap_path = repo_path / 'sitemap.xml'
    if sitemap_path.exists():
        sitemap = sitemap_path.read_text(encoding='utf-8')
        for needle in ('/es/', '/fr/', '/hi/', '.draft'):
            if needle in sitemap:
                issues.append(f"sitemap.xml contains {needle}")

    sw_path = repo_path / 'sw.js'
    if sw_path.exists():
        sw = sw_path.read_text(encoding='utf-8')
        for needle in ('/es/', '/fr/', '/hi/', '.draft'):
            if needle in sw:
                issues.append(f"sw.js contains {needle}")

    for draft_path in sorted(Path(drafts_dir).rglob('*.draft')):
        rel = draft_path.relative_to(repo_path)
        try:
            html_content = draft_path.read_text(encoding='utf-8')
        except OSError as exc:
            issues.append(f"Could not read {rel}: {exc}")
            continue

        soup = BeautifulSoup(html_content, 'html.parser')
        robots = ''
        robots_meta = soup.find('meta', attrs={'name': re.compile(r'^robots$', re.I)})
        if robots_meta and robots_meta.has_attr('content'):
            robots = robots_meta.get('content', '').lower()

        missing_robot_tokens = [
            token for token in ('noindex', 'nofollow', 'noarchive')
            if token not in robots
        ]
        if missing_robot_tokens:
            issues.append(
                f"{rel} missing noindex/nofollow/noarchive robots meta "
                f"(missing: {', '.join(missing_robot_tokens)})"
            )

        body_text = normalized_text(html_content)
        if 'unreviewed machine translation draft' not in body_text:
            issues.append(f"{rel} missing visible unreviewed-draft warning")
        if 'do not use for medical guidance' not in body_text:
            issues.append(f"{rel} missing visible medical-use warning")
    return issues

def extract_numbers(html_content, lang=None):
    soup = BeautifulSoup(html_content, 'html.parser')
    # Remove script and style elements
    for element in soup(["script", "style"]):
        element.decompose()
    
    text = soup.get_text()
    if lang in ["es", "fr"]:
        # Replace commas between digits with dots (e.g., 39,4 -> 39.4) to match English decimal formatting
        text = re.sub(r'(\d+),(\d+)', r'\1.\2', text)
    # Find all sequences of digits, decimal numbers, and percentages
    numbers = re.findall(r'\b\d+(?:\.\d+)?%?\b', text)
    return set(numbers)

def extract_links(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    links = [a['href'] for a in soup.find_all('a', href=True)]
    return Counter(links)

def audit_all_translations():
    repo_dir = str(Path(__file__).resolve().parents[1])
    drafts_dir = os.path.join(repo_dir, "_translation-drafts")
    
    if not os.path.exists(drafts_dir):
        print("No translation drafts directory found.")
        return
    
    languages = ["es", "fr", "hi"]
    issues_found = 0

    safety_gate_issues = audit_draft_safety_gates(repo_dir, drafts_dir)
    if safety_gate_issues:
        print("[WARNING] Translation drafts missing safety gates:")
        for issue in safety_gate_issues:
            print(f"  - {issue}")
        print()
        issues_found += len(safety_gate_issues)

    discouraged_issues = audit_discouraged_translation_text(repo_dir, drafts_dir)
    if discouraged_issues:
        print("[WARNING] Discouraged wording found in translation drafts/cache:")
        for issue in discouraged_issues:
            print(f"  - {issue}")
        print()
        issues_found += len(discouraged_issues)
    
    # We will traverse the repo to find all active HTML files (English)
    for root, dirs, files in os.walk(repo_dir):
        # Skip translation drafts, .git, and scripts directories
        if "_translation-drafts" in root or ".git" in root or "scripts" in root:
            continue
            
        for file in files:
            if file.endswith(".html") and not file.startswith("."):
                english_path = os.path.join(root, file)
                relative_path = os.path.relpath(english_path, repo_dir)
                
                # Read English content
                with open(english_path, 'r', encoding='utf-8') as f:
                    eng_content = f.read()
                eng_numbers = extract_numbers(eng_content)
                eng_links = extract_links(eng_content)
                
                # Check drafts for each language
                for lang in languages:
                    # In drafts, the structure is _translation-drafts/<lang>/<relative_path>.draft
                    draft_relative = os.path.join(lang, relative_path) + ".draft"
                    draft_path = os.path.join(drafts_dir, draft_relative)
                    
                    if os.path.exists(draft_path):
                        with open(draft_path, 'r', encoding='utf-8') as f:
                            draft_content = f.read()
                        draft_numbers = extract_numbers(draft_content, lang=lang)
                        draft_links = extract_links(draft_content)
                        
                        # Compare numbers
                        missing_in_draft = eng_numbers - draft_numbers
                        if missing_in_draft:
                            critical_missing = {num for num in missing_in_draft if num not in ["2026", "2.0", "3.5", "5.5"]}
                            if critical_missing:
                                print(f"[WARNING] Numeric discrepancy in {lang.upper()} translation of {relative_path}:")
                                print(f"  English contains numbers not found in translation: {sorted(list(critical_missing))}")
                                print(f"  English numbers: {sorted(list(eng_numbers))}")
                                print(f"  Draft numbers:   {sorted(list(draft_numbers))}\n")
                                issues_found += 1
                                
                        # Compare links
                        eng_link_targets = set(eng_links)
                        draft_link_targets = set(draft_links)
                        missing_links = eng_link_targets - draft_link_targets
                        extra_links = draft_link_targets - eng_link_targets
                        count_differences = {
                            href: (eng_links[href], draft_links[href])
                            for href in sorted(eng_link_targets & draft_link_targets)
                            if eng_links[href] != draft_links[href]
                        }
                        if missing_links or extra_links or count_differences:
                            print(f"[WARNING] Link discrepancy in {lang.upper()} translation of {relative_path}:")
                            if missing_links:
                                print(f"  Missing links in draft: {sorted(list(missing_links))}")
                            if extra_links:
                                print(f"  Extra links in draft: {sorted(list(extra_links))}")
                            if count_differences:
                                formatted = [
                                    f"{href} (English {eng_count}, draft {draft_count})"
                                    for href, (eng_count, draft_count) in count_differences.items()
                                ]
                                print(f"  Link count differences: {formatted}")
                            print()
                            issues_found += 1
                                
    if issues_found == 0:
        print("[SUCCESS] Translation audits complete: all draft safety gates are present, with no discouraged wording, numeric discrepancies, or href target/count discrepancies found between English files and existing drafts.")
    else:
        print(f"[AUDIT COMPLETE] Found {issues_found} potential discrepancy issues.")
        sys.exit(1)

if __name__ == "__main__":
    audit_all_translations()
