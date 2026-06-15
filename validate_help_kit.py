from pathlib import Path
import os
import re
import sys
import xml.etree.ElementTree as ET

DISCOURAGED_HTML_PATTERNS = [
    ("911 (U.S./Canada)", "Use local emergency-number framing with examples such as 911, 112, or 999; avoid region-labeled shortcuts."),
    ("112 (Europe)", "Use local emergency-number framing with examples such as 911, 112, or 999; avoid region-labeled shortcuts."),
    ("999 (UK)", "Use local emergency-number framing with examples such as 911, 112, or 999; avoid region-labeled shortcuts."),
    ("does not replace professional medical advice", "Use the current disclaimer: general information, not medical advice or first-aid training; follow local emergency guidance."),
    ("educational purposes", "Use plainer current disclaimer wording instead of the older educational-purposes phrase."),
    ("vulnerable neighbors", "Use dignity/access-barrier wording such as people facing higher risk or limited access."),
    ("vulnerable people", "Use dignity/access-barrier wording such as people facing higher risk or limited access."),
]

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
    if not noindex and 'disclaimer' not in content_lower and rel_path != 'index.html':
        issues.append("Missing disclaimer class/text reference")

    # Check safety/dignity wording that has previously regressed.
    for phrase, guidance in DISCOURAGED_HTML_PATTERNS:
        if phrase.lower() in content_lower:
            issues.append(f"Discouraged wording '{phrase}': {guidance}")
    if '911' in content and not ('112' in content and '999' in content):
        issues.append("Mentions 911 without also giving local-number examples such as 112 and 999")

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
        
    if total_issues == 0:
        print("\n🎉 ALL LOCAL VALIDATIONS PASSED! The Help Kit is clean and safe.")
    else:
        print(f"\n❌ Validation finished with {total_issues} total issues.")
    return 0 if total_issues == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
