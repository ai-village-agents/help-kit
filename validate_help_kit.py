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
        
    if total_issues == 0:
        print("\n🎉 ALL LOCAL VALIDATIONS PASSED! The Help Kit is clean and safe.")
    else:
        print(f"\n❌ Validation finished with {total_issues} total issues.")
    return 0 if total_issues == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
