import os
import re
from pathlib import Path

ROOT = Path("/home/computeruse/help-kit-repo")

# 1. Update sw.js
sw_path = ROOT / "sw.js"
sw_content = sw_path.read_text()
old_cache = 'const CACHE = "help-kit-v' + '17";'
new_cache = 'const CACHE = "help-kit-v' + '18";'
sw_content = sw_content.replace(old_cache, new_cache)

# insert assets
new_assets = [
    '  "/help-kit/heart/",',
    '  "/help-kit/heart/heart-onepager.pdf",',
]
if "/help-kit/heart/" not in sw_content:
    assets_match = re.search(r'const ASSETS = \[\n(.*?)\n\];', sw_content, re.DOTALL)
    if assets_match:
        assets_lines = assets_match.group(1).split('\n')
        assets_lines.extend(new_assets)
        # Sort them cleanly
        cleaned_assets = []
        for line in assets_lines:
            line_stripped = line.strip().strip(',').strip('"').strip("'")
            if line_stripped:
                cleaned_assets.append(line_stripped)
        cleaned_assets = sorted(list(set(cleaned_assets)))
        formatted_assets = 'const ASSETS = [\n' + ',\n'.join(f'  "{a}"' for a in cleaned_assets) + '\n];'
        sw_content = re.sub(r'const ASSETS = \[\n.*?\n\];', formatted_assets, sw_content, flags=re.DOTALL)
        sw_path.write_text(sw_content)
        print("[sw.js] Updated successfully.")

# 2. Update sitemap.xml
sitemap_path = ROOT / "sitemap.xml"
sitemap_content = sitemap_path.read_text()
new_sitemap_entries = """  <url>
    <loc>https://ai-village-agents.github.io/help-kit/heart/</loc>
    <lastmod>2026-06-15</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://ai-village-agents.github.io/help-kit/heart/heart-onepager.pdf</loc>
    <lastmod>2026-06-15</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.4</priority>
  </url>
"""
if "help-kit/heart/" not in sitemap_content:
    sitemap_content = sitemap_content.replace('</urlset>', new_sitemap_entries + '</urlset>')
    sitemap_path.write_text(sitemap_content)
    print("[sitemap.xml] Updated successfully.")

# 3. Update scripts/build-pdfs.py
build_pdfs_path = ROOT / "scripts/build-pdfs.py"
build_pdfs_content = build_pdfs_path.read_text()
if '"heart"' not in build_pdfs_content:
    old_topics = '    ("cold", "cold-onepager.pdf"),'
    new_topics = '    ("cold", "cold-onepager.pdf"),\n    ("heart", "heart-onepager.pdf"),'
    build_pdfs_content = build_pdfs_content.replace(old_topics, new_topics)
    build_pdfs_path.write_text(build_pdfs_content)
    print("[scripts/build-pdfs.py] Updated successfully.")

# 4. Update print-cover.html
cover_path = ROOT / "print-cover.html"
cover_content = cover_path.read_text()
old_heading = '<h2>What\'s inside (' + '13' + ' guides)</h2>'
cover_content = cover_content.replace(old_heading, '<h2>What\'s inside (14 guides)</h2>')
if 'Heart attack' not in cover_content:
    old_item = '    <li><b>Cold safety</b> — hypothermia &amp; frostbite</li>'
    new_item = '    <li><b>Cold safety</b> — hypothermia &amp; frostbite</li>\n    <li><b>Heart attack</b> — recognize signs, call emergency help, follow dispatcher guidance</li>'
    cover_content = cover_content.replace(old_item, new_item)
    cover_path.write_text(cover_content)
    print("[print-cover.html] Updated successfully.")

# 5. Update index.html
index_path = ROOT / "index.html"
index_content = index_path.read_text()
# Navbar update in index.html
if '<a href="heart/">Heart Attack</a>' not in index_content:
    old_nav = '    <a href="cold/">Cold Safety</a>\n    <a href="triage/">Triage</a>'
    new_nav = '    <a href="cold/">Cold Safety</a>\n    <a href="heart/">Heart Attack</a>\n    <a href="triage/">Triage</a>'
    index_content = index_content.replace(old_nav, new_nav)

# Card update in index.html
if 'href="heart/"' not in index_content:
    triage_card = """    <a class="card" href="triage/">
      <h3>🚦 Emergency Triage</h3>"""
    heart_card = """    <a class="card" href="heart/">
      <h3>💔 Heart Attack</h3>
      <p>Recognize possible symptoms, call emergency help immediately, follow dispatcher guidance, and avoid dangerous exertion.</p>
      <span class="go">Open the heart guide →</span>
    </a>
"""
    index_content = index_content.replace(triage_card, heart_card + triage_card)
    index_path.write_text(index_content)
    print("[index.html] Updated successfully.")

# 6. Update all other HTML files (excluding print-cover.html, index.html, and heart/index.html)
for root, dirs, files in os.walk(ROOT):
    # skip translation drafts
    if "_translation-drafts" in root or ".git" in root:
        continue
    for file in files:
        if file.endswith(".html"):
            file_path = Path(root) / file
            if file_path == index_path or file_path == cover_path or file_path == (ROOT / "heart/index.html"):
                continue
            content = file_path.read_text()
            updated = False
            
            # Check if it's in a subdirectory or root
            is_root = file_path.parent == ROOT
            
            if is_root:
                old_nav = '    <a href="cold/">Cold Safety</a>\n    <a href="triage/">Triage</a>'
                new_nav = '    <a href="cold/">Cold Safety</a>\n    <a href="heart/">Heart Attack</a>\n    <a href="triage/">Triage</a>'
                if old_nav in content and '<a href="heart/">' not in content:
                    content = content.replace(old_nav, new_nav)
                    updated = True
            else:
                old_nav = '    <a href="../cold/">Cold Safety</a>\n    <a href="../triage/">Triage</a>'
                new_nav = '    <a href="../cold/">Cold Safety</a>\n    <a href="../heart/">Heart Attack</a>\n    <a href="../triage/">Triage</a>'
                if old_nav in content and '<a href="../heart/">' not in content:
                    content = content.replace(old_nav, new_nav)
                    updated = True
            
            if updated:
                file_path.write_text(content)
                print(f"[{file_path.relative_to(ROOT)}] Navbar updated successfully.")

print("All integrations complete!")
