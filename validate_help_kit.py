from pathlib import Path
import html as html_lib
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

DISCOURAGED_HTML_PATTERNS = [
    ("911 (U.S./Canada)", "Use local emergency-number framing with examples such as 911, 112, or 999; avoid region-labeled shortcuts."),
    ("911 (US/Canada)", "Use local emergency-number framing with examples such as 911, 112, or 999; avoid region-labeled shortcuts."),
    ("112 (much of Europe)", "Use local emergency-number framing with examples such as 911, 112, or 999; avoid region-labeled shortcuts."),
    ("112 (Europe)", "Use local emergency-number framing with examples such as 911, 112, or 999; avoid region-labeled shortcuts."),
    ("999 (UK)", "Use local emergency-number framing with examples such as 911, 112, or 999; avoid region-labeled shortcuts."),
    ("911 in the US/Canada", "Use local emergency-number framing with examples such as 911, 112, or 999; avoid region-labeled shortcuts."),
    ("112 in much of Europe", "Use local emergency-number framing with examples such as 911, 112, or 999; avoid region-labeled shortcuts."),
    ("999 in the UK", "Use local emergency-number framing with examples such as 911, 112, or 999; avoid region-labeled shortcuts."),
    ("vulnerable populations", "Use dignity/access-barrier wording such as people facing higher risk or limited access."),
    ("elderly neighbors", "Use dignity/access-barrier wording such as older neighbors or people facing higher risk."),
    ("does not replace professional medical advice", "Use the current disclaimer: general information, not medical advice or first-aid training; follow local emergency guidance."),
    ("educational purposes", "Use plainer current disclaimer wording instead of the older educational-purposes phrase."),
    ("vulnerable neighbors", "Use dignity/access-barrier wording such as people facing higher risk or limited access."),
    ("vulnerable people", "Use dignity/access-barrier wording such as people facing higher risk or limited access."),
    ("save a life", "Avoid overclaiming outcomes; describe concrete actions and emergency handoff instead."),
    ("saves lives", "Avoid overclaiming outcomes; describe concrete actions and emergency handoff instead."),
    ("will save", "Avoid overclaiming outcomes; describe concrete actions and emergency handoff instead."),
    ("chew aspirin", "Avoid unsafe aspirin shorthand; say to ask about aspirin only after calling and only if dispatcher, clinician, or local protocol says."),
    ("give aspirin if appropriate", "Avoid unsafe aspirin shorthand; say to ask about aspirin only after calling and only if dispatcher, clinician, or local protocol says."),
]


DISCOURAGED_PUBLIC_TEXT_PATTERNS = DISCOURAGED_HTML_PATTERNS + [
    ("13 topics", "Current-facing public docs should describe the live 14-topic Help Kit."),
    ("13 topic", "Current-facing public docs should describe the live 14-topic Help Kit."),
    ("13 guides", "Current-facing public docs should describe the live 14-topic Help Kit."),
    ("37-page", "Current-facing public docs should describe the live 40-page print pack."),
    ("37 pages", "Current-facing public docs should describe the live 40-page print pack."),
    ("directly into the interface", "Do not imply localize.html has an in-browser customization interface; it is a safe-localization checklist."),
    ("custom PDF booklets", "Do not imply localize.html generates custom PDF booklets; describe editing, hosting, printing, or distributing a localized copy."),
]


def normalized_visible_text(html_content):
    text = re.sub(r'<script\b[^>]*>.*?</script>', ' ', html_content, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'<style\b[^>]*>.*?</style>', ' ', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = html_lib.unescape(text)
    return re.sub(r'\s+', ' ', text).strip()

def get_html_files(root_dir):
    html_files = []
    for root, dirs, files in os.walk(root_dir):
        if '.git' in root or '.github' in root:
            continue
        for file in files:
            path = Path(root, file)
            if file.endswith('.html') and '.draft' not in path.suffixes:
                html_files.append(os.path.relpath(os.path.join(root, file), root_dir))
    return html_files

def is_noindex_html(root_dir, rel_path):
    try:
        content = Path(root_dir, rel_path).read_text(encoding="utf-8").lower()
    except OSError:
        return False
    return 'name="robots"' in content and "noindex" in content

def canonical_url_for_html(rel_path):
    if rel_path == 'index.html':
        return 'https://ai-village-agents.github.io/help-kit/'
    if rel_path.endswith('/index.html'):
        return 'https://ai-village-agents.github.io/help-kit/' + rel_path[:-len('index.html')]
    return 'https://ai-village-agents.github.io/help-kit/' + rel_path

def canonical_hrefs(html_content):
    class _CanonicalParser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.hrefs = []

        def handle_starttag(self, tag, attrs):
            if tag.lower() != 'link':
                return
            attrs = {k.lower(): v for k, v in attrs}
            if attrs.get('rel', '').lower() == 'canonical' and attrs.get('href'):
                self.hrefs.append(attrs['href'])

    parser = _CanonicalParser()
    parser.feed(html_content)
    return parser.hrefs

def validate_html(root_dir, rel_path):
    full_path = os.path.join(root_dir, rel_path)
    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues = []
    noindex = is_noindex_html(root_dir, rel_path)
    
    # Check doctype
    if not re.search(r'<!doctype\s+html>', content, re.IGNORECASE):
        issues.append("Missing <!doctype html>")
        
    # Check viewport
    if 'name="viewport"' not in content:
        issues.append("Missing viewport meta tag")
        
    # Check stylesheet
    if 'style.css' not in content:
        issues.append("Possibly missing style.css link reference")
        
    # Check disclaimers
    content_lower = content.lower()
    visible_lower = normalized_visible_text(content).lower()
    if not noindex and 'disclaimer' not in content_lower and rel_path != 'index.html':
        issues.append("Missing disclaimer class/text reference")

    # Check safety/dignity wording that has previously regressed. Search both
    # source and normalized visible text so phrases split by markup still fail.
    for phrase, guidance in DISCOURAGED_HTML_PATTERNS:
        phrase_lower = phrase.lower()
        if phrase_lower in content_lower or phrase_lower in visible_lower:
            issues.append(f"Discouraged wording '{phrase}': {guidance}")
    class _JsonLdParser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.in_json_ld = False
            self.buffer = []
            self.blocks = []

        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if tag.lower() == 'script' and attrs.get('type', '').lower() == 'application/ld+json':
                self.in_json_ld = True
                self.buffer = []

        def handle_endtag(self, tag):
            if tag.lower() == 'script' and self.in_json_ld:
                self.blocks.append(''.join(self.buffer))
                self.in_json_ld = False

        def handle_data(self, data):
            if self.in_json_ld:
                self.buffer.append(data)

    json_ld_parser = _JsonLdParser()
    json_ld_parser.feed(content)
    for block in json_ld_parser.blocks:
        try:
            json.loads(block)
        except json.JSONDecodeError as exc:
            issues.append(f"JSON-LD structured data is not valid JSON: {exc}")
        if re.search(r'</?[a-z][^>]*>', block, re.IGNORECASE):
            issues.append("JSON-LD structured data should not contain HTML markup such as <em> in text fields")

    if '911' in content and not ('112' in content and '999' in content):
        issues.append("Mentions 911 without also giving local-number examples such as 112 and 999")

    if not noindex:
        canonicals = canonical_hrefs(content)
        expected_canonical = canonical_url_for_html(rel_path)
        if not canonicals:
            issues.append(f"Missing canonical URL: {expected_canonical}")
        elif canonicals != [expected_canonical]:
            issues.append(f"Canonical URL should be exactly {expected_canonical}, found {canonicals}")

    # Topic index pages with a sibling onepager PDF should expose print/PDF actions.
    rel = Path(rel_path)
    if rel.name == 'index.html' and len(rel.parts) > 1:
        topic_dir = Path(root_dir, *rel.parts[:-1])
        expected_pdf = f"{rel.parts[-2]}-onepager.pdf"
        if Path(topic_dir, expected_pdf).exists():
            if 'class="actions no-print"' not in content and "class='actions no-print'" not in content:
                issues.append("Missing .actions.no-print print/PDF action block")
            if 'Print this page' not in content:
                issues.append("Missing 'Print this page' action")
            if expected_pdf not in content:
                issues.append(f"Missing printable PDF link to {expected_pdf}")
        
    # Find all local links and verify they exist
    links = re.findall(r'href=[\"\']([^\"\'#?]+)[\"\']', content)
    for link in links:
        if link.startswith('http://') or link.startswith('https://') or link.startswith('#') or link.startswith('javascript:'):
            continue
        # Standardize query or anchor params
        link_clean = link.split('#')[0].split('?')[0]
        if not link_clean:
            continue
        
        # Check relative resolution
        if link_clean.startswith('/help-kit/'):
            # Strip '/help-kit/' and resolve relative to root_dir
            target_path = os.path.normpath(os.path.join(root_dir, link_clean[len('/help-kit/'):]))
        elif link_clean.startswith('/'):
            # Strip '/' and resolve relative to root_dir
            target_path = os.path.normpath(os.path.join(root_dir, link_clean[1:]))
        else:
            file_dir = os.path.dirname(full_path)
            target_path = os.path.normpath(os.path.join(file_dir, link_clean))
        
        # If target is a directory, look for index.html
        if os.path.isdir(target_path):
            target_path = os.path.join(target_path, 'index.html')
            
        if not os.path.exists(target_path):
            issues.append(f"Broken relative link: '{link}' (resolved to '{os.path.relpath(target_path, root_dir)}')")
            
    return issues

def validate_robots_txt(root_dir):
    robots = root_dir / "robots.txt"
    issues = []
    if not robots.exists():
        return ["Missing robots.txt with sitemap location"]
    text = robots.read_text(encoding="utf-8")
    normalized = re.sub(r'\s+', ' ', text).lower()
    expected_sitemap = "sitemap: https://ai-village-agents.github.io/help-kit/sitemap.xml"
    if expected_sitemap not in text.lower():
        issues.append("robots.txt should list the canonical Help Kit sitemap URL")
    if "allow: /help-kit/" not in text.lower():
        issues.append("robots.txt should explicitly allow /help-kit/ for crawlers")
    if "disallow: /help-kit/" in normalized:
        issues.append("robots.txt must not disallow the public /help-kit/ site")
    return issues

def validate_sitemap(root_dir, html_files):
    sitemap_path = os.path.join(root_dir, 'sitemap.xml')
    if not os.path.exists(sitemap_path):
        return ["sitemap.xml is missing"]
        
    issues = []
    try:
        tree = ET.parse(sitemap_path)
        root = tree.getroot()
        # Handle namespaces
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = [loc.text for loc in root.findall('.//ns:loc', namespace)]
        
        # Check that all html files are represented in the sitemap (except template or temp files)
        for html in html_files:
            # Skip intentionally non-indexed pages
            if is_noindex_html(root_dir, html):
                continue
            # Format the expected URL
            clean_html = html.replace('index.html', '')
            expected_suffix = f"help-kit/{clean_html}".replace('//', '/')
            matched = False
            for url in urls:
                if expected_suffix in url or (html == 'index.html' and url.endswith('help-kit/')):
                    matched = True
                    break
            if not matched:
                issues.append(f"HTML file '{html}' not found in sitemap.xml")
    except Exception as e:
        issues.append(f"Error parsing sitemap.xml: {str(e)}")
        
    return issues


def parse_service_worker_assets(root_dir):
    sw_path = Path(root_dir, 'sw.js')
    if not sw_path.exists():
        return None, [], ["sw.js is missing"]
    content = sw_path.read_text(encoding="utf-8")
    issues = []
    cache_match = re.search(r'const\s+CACHE\s*=\s*"([^"]+)"', content)
    cache_name = cache_match.group(1) if cache_match else None
    if not cache_name:
        issues.append("sw.js is missing const CACHE name")
    array_match = re.search(r'const\s+ASSETS\s*=\s*\[(.*?)\];', content, re.DOTALL)
    if not array_match:
        issues.append("sw.js is missing const ASSETS array")
        return cache_name, [], issues
    assets = re.findall(r'"([^"]+)"', array_match.group(1))
    if len(assets) != len(set(assets)):
        issues.append("sw.js ASSETS contains duplicate entries")
    return cache_name, assets, issues

def asset_path_for_html(rel_path):
    if rel_path == 'index.html':
        return '/help-kit/'
    if rel_path.endswith('/index.html'):
        return '/help-kit/' + rel_path[:-len('index.html')]
    return '/help-kit/' + rel_path

def get_public_markdown_files(root_dir):
    markdown_files = []
    for path in Path(root_dir).rglob('*.md'):
        rel = path.relative_to(root_dir)
        if any(part.startswith('.') or part == '_translation-drafts' for part in rel.parts):
            continue
        markdown_files.append(rel.as_posix())
    return markdown_files

def validate_public_markdown_text(root_dir):
    issues = []
    for rel in get_public_markdown_files(root_dir):
        text = Path(root_dir, rel).read_text(encoding='utf-8', errors='replace')
        text_lower = re.sub(r'\s+', ' ', text).lower()
        for phrase, guidance in DISCOURAGED_PUBLIC_TEXT_PATTERNS:
            if phrase.lower() in text_lower:
                issues.append(f"{rel} contains discouraged wording '{phrase}': {guidance}")
    return issues


PAGES_WORKFLOW_REQUIRED_EXCLUDES = [
    "--exclude='./_translation-drafts'",
    "--exclude='./scripts'",
    "--exclude='./validate_help_kit.py'",
    "--exclude='./outreach-*.md'",
    "--exclude='./.gitignore'",
    "--exclude='./_config.yml'",
    "--exclude='*.draft'",
]

PAGES_WORKFLOW_REQUIRED_GUARDS = [
    "Draft translation files must not be deployed to Pages.",
    "Internal scripts and translation caches must not be deployed to Pages.",
    "Internal maintenance file must not be deployed to Pages:",
]

def validate_pages_artifact_policy(root_dir):
    workflow = Path(root_dir, '.github', 'workflows', 'pages.yml')
    if not workflow.exists():
        return [".github/workflows/pages.yml is missing"]

    text = workflow.read_text(encoding='utf-8')
    issues = []
    for token in PAGES_WORKFLOW_REQUIRED_EXCLUDES:
        if token not in text:
            issues.append(f"Pages workflow is missing artifact exclude token: {token}")
    for guard in PAGES_WORKFLOW_REQUIRED_GUARDS:
        if guard not in text:
            issues.append(f"Pages workflow is missing deploy guard text: {guard}")
    return issues

def get_public_plain_text_files(root_dir):
    text_files = []
    for path in Path(root_dir).rglob('*.txt'):
        rel = path.relative_to(root_dir)
        if any(part.startswith('.') or part == '_translation-drafts' for part in rel.parts):
            continue
        text_files.append(rel.as_posix())
    return text_files

def validate_public_plain_text(root_dir):
    issues = []
    for rel in get_public_plain_text_files(root_dir):
        text = Path(root_dir, rel).read_text(encoding='utf-8', errors='replace')
        text_lower = re.sub(r'\s+', ' ', text).lower()
        for phrase, guidance in DISCOURAGED_PUBLIC_TEXT_PATTERNS:
            if phrase.lower() in text_lower:
                issues.append(f"{rel} contains discouraged wording '{phrase}': {guidance}")
    return issues

def validate_llms_txt(root_dir, html_files):
    llms_path = Path(root_dir, 'llms.txt')
    if not llms_path.exists():
        return ["llms.txt is missing"]

    text = llms_path.read_text(encoding='utf-8', errors='replace')
    issues = []
    if 'https://ai-village-agents.github.io/help-kit/' not in text:
        issues.append("llms.txt should include the canonical Help Kit home URL")
    if '911' in text and not ('112' in text and '999' in text):
        issues.append("llms.txt mentions 911 without also giving local-number examples such as 112 and 999")

    topic_pages = sorted(
        rel for rel in html_files
        if Path(rel).name == 'index.html'
        and len(Path(rel).parts) == 2
        and not is_noindex_html(root_dir, rel)
    )
    expected_count = len(topic_pages)
    if f'Topics ({expected_count})' not in text:
        issues.append(f"llms.txt should label the current topic count as 'Topics ({expected_count})'")
    for rel in topic_pages:
        expected_url = canonical_url_for_html(rel)
        if expected_url not in text:
            issues.append(f"llms.txt is missing top-level topic URL: {expected_url}")

    forbidden_tokens = [
        '_translation-drafts',
        '/scripts/',
        'validate_help_kit.py',
        'outreach-draft',
        '.draft',
    ]
    for token in forbidden_tokens:
        if token in text:
            issues.append(f"llms.txt should not reference internal maintenance path/token: {token}")
    return issues

def validate_pdf_text(root_dir):
    issues = []
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        return [f"pypdf is required for PDF text validation: {exc}"]

    for pdf in sorted(Path(root_dir).rglob('*.pdf')):
        rel = pdf.relative_to(root_dir)
        if any(part.startswith('.') or part == '_translation-drafts' for part in rel.parts):
            continue
        try:
            reader = PdfReader(str(pdf))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception as exc:
            issues.append(f"Could not extract PDF text from {rel.as_posix()}: {exc}")
            continue
        text_lower = re.sub(r'\s+', ' ', text).lower()
        for phrase, guidance in DISCOURAGED_HTML_PATTERNS:
            if phrase.lower() in text_lower:
                issues.append(f"{rel.as_posix()} contains discouraged wording '{phrase}': {guidance}")
    return issues

def validate_service_worker_assets(root_dir, html_files):
    cache_name, assets, issues = parse_service_worker_assets(root_dir)
    if not assets:
        return issues
    asset_set = set(assets)

    for asset in assets:
        if not asset.startswith('/help-kit/'):
            issues.append(f"sw.js asset is outside /help-kit/: {asset}")
            continue
        rel = asset[len('/help-kit/'):]
        if rel == '':
            local = Path(root_dir, 'index.html')
        elif asset.endswith('/'):
            local = Path(root_dir, rel, 'index.html')
        else:
            local = Path(root_dir, rel)
        if not local.exists():
            issues.append(f"sw.js asset does not exist locally: {asset}")

    for html in html_files:
        if is_noindex_html(root_dir, html):
            continue
        expected = asset_path_for_html(html)
        if expected not in asset_set:
            issues.append(f"Active HTML file '{html}' is missing from sw.js ASSETS as {expected}")

    for pdf in sorted(Path(root_dir).rglob('*.pdf')):
        rel = pdf.relative_to(root_dir).as_posix()
        if rel == 'print-cover.pdf' or any(part.startswith('.') or part == '_translation-drafts' for part in pdf.relative_to(root_dir).parts):
            continue
        expected = '/help-kit/' + rel
        if expected not in asset_set:
            issues.append(f"Public PDF '{rel}' is missing from sw.js ASSETS as {expected}")

    return issues

def main():
    root_dir = Path(__file__).resolve().parent
    html_files = get_html_files(root_dir)
    
    print(f"--- Validating Help Kit repo at {root_dir} ---")
    print(f"Found {len(html_files)} HTML files to audit: {html_files}\n")
    
    total_issues = 0
    for path in html_files:
        issues = validate_html(root_dir, path)
        if issues:
            print(f"[!] Issues in {path}:")
            for iss in issues:
                print(f"  - {iss}")
            total_issues += len(issues)
        else:
            print(f"[OK] {path} passed HTML & local link audits.")
            
    robots_issues = validate_robots_txt(root_dir)
    if robots_issues:
        print("\n[!] robots.txt issues:")
        for issue in robots_issues:
            print("  - " + issue)
        total_issues += len(robots_issues)
    else:
        print("\n[OK] robots.txt points crawlers at the canonical Help Kit sitemap.")

    sitemap_issues = validate_sitemap(root_dir, html_files)
    if sitemap_issues:
        print(f"\n[!] Issues in sitemap.xml:")
        for iss in sitemap_issues:
            print(f"  - {iss}")
        total_issues += len(sitemap_issues)
    else:
        print(f"\n[OK] sitemap.xml matched all active HTML files perfectly.")

    sw_issues = validate_service_worker_assets(root_dir, html_files)
    if sw_issues:
        print(f"\n[!] Issues in sw.js offline precache:")
        for iss in sw_issues:
            print(f"  - {iss}")
        total_issues += len(sw_issues)
    else:
        cache_name, assets, _ = parse_service_worker_assets(root_dir)
        print(f"\n[OK] sw.js offline precache is complete ({cache_name}, {len(assets)} assets).")

    artifact_policy_issues = validate_pages_artifact_policy(root_dir)
    if artifact_policy_issues:
        print(f"\n[!] Issues in Pages artifact policy:")
        for iss in artifact_policy_issues:
            print(f"  - {iss}")
        total_issues += len(artifact_policy_issues)
    else:
        print(f"\n[OK] Pages artifact policy excludes internal scripts, drafts, and maintenance files.")

    markdown_issues = validate_public_markdown_text(root_dir)
    if markdown_issues:
        print(f"\n[!] Issues in public Markdown docs:")
        for iss in markdown_issues:
            print(f"  - {iss}")
        total_issues += len(markdown_issues)
    else:
        print(f"\n[OK] Public Markdown docs avoid known stale safety/count wording.")

    text_issues = validate_public_plain_text(root_dir)
    if text_issues:
        print(f"\n[!] Issues in public plain-text files:")
        for iss in text_issues:
            print(f"  - {iss}")
        total_issues += len(text_issues)
    else:
        print(f"\n[OK] Public plain-text files avoid known stale safety/count wording.")

    llms_issues = validate_llms_txt(root_dir, html_files)
    if llms_issues:
        print(f"\n[!] Issues in llms.txt:")
        for iss in llms_issues:
            print(f"  - {iss}")
        total_issues += len(llms_issues)
    else:
        print(f"\n[OK] llms.txt lists every top-level topic and avoids internal references.")

    pdf_issues = validate_pdf_text(root_dir)
    if pdf_issues:
        print(f"\n[!] Issues in generated PDF text:")
        for iss in pdf_issues:
            print(f"  - {iss}")
        total_issues += len(pdf_issues)
    else:
        print(f"\n[OK] Generated PDF text avoids known stale emergency/disclaimer/dignity wording.")
        
    if total_issues == 0:
        print("\n🎉 ALL LOCAL VALIDATIONS PASSED! The Help Kit is clean and safe.")
    else:
        print(f"\n❌ Validation finished with {total_issues} total issues.")
    return 0 if total_issues == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
