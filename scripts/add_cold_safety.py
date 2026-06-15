import re
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def update_navigation():
    # Update navigation in all HTML files
    for root, dirs, files in os.walk(ROOT):
        if '.git' in root or '.github' in root:
            continue
        for file in files:
            if file.endswith('.html') and not file.endswith('.draft'):
                filepath = Path(root, file)
                content = filepath.read_text(encoding='utf-8')
                
                # Check relative depth of the file to use proper relative links
                rel_path = os.path.relpath(filepath, ROOT)
                depth = len(rel_path.split(os.sep)) - 1
                prefix = "../" * depth if depth > 0 else ""
                
                # Try replacing the subdirectory relative navigation
                sub_old = f'<a href="{prefix}allergy/">Severe Allergy</a>\n    <a href="{prefix}triage/">Triage</a>'
                sub_new = f'<a href="{prefix}allergy/">Severe Allergy</a>\n    <a href="{prefix}cold/">Cold Safety</a>\n    <a href="{prefix}triage/">Triage</a>'
                
                # Let's try flexible search and replace for navigation bar
                nav_pattern_old = re.compile(
                    r'<a\s+href="([^"]*?)allergy/">Severe\s+Allergy</a>\s*<a\s+href="([^"]*?)triage/">Triage</a>',
                    re.IGNORECASE | re.DOTALL
                )
                
                match = nav_pattern_old.search(content)
                if match:
                    # Determine current relative path for allergy and triage
                    p1 = match.group(1)
                    p2 = match.group(2)
                    replacement = f'<a href="{p1}allergy/">Severe Allergy</a>\n    <a href="{p1}cold/">Cold Safety</a>\n    <a href="{p2}triage/">Triage</a>'
                    content = nav_pattern_old.sub(replacement, content)
                    filepath.write_text(content, encoding='utf-8')
                    print(f"Updated navigation in {rel_path}")

def update_homepage_cards():
    index_path = ROOT / "index.html"
    if index_path.exists():
        content = index_path.read_text(encoding='utf-8')
        old_card = """    <a class="card" href="triage/">
      <h3>🚦 Emergency Triage</h3>
      <p>Quick decision guide for the first minutes of an emergency.</p>
      <span class="go">Open the triage guide →</span>
    </a>"""
        new_card = """    <a class="card" href="cold/">
      <h3>🥶 Cold Safety</h3>
      <p>Spot hypothermia and frostbite warning signs, rewarm safely, avoid direct high heat, and support people facing higher cold risk.</p>
      <span class="go">Open the cold safety guide →</span>
    </a>
    <a class="card" href="triage/">
      <h3>🚦 Emergency Triage</h3>
      <p>Quick decision guide for the first minutes of an emergency.</p>
      <span class="go">Open the triage guide →</span>
    </a>"""
        if old_card in content:
            content = content.replace(old_card, new_card)
            index_path.write_text(content, encoding='utf-8')
            print("Updated homepage cards in index.html")
        else:
            # Flexible re-search
            pattern = re.compile(r'<a class="card" href="triage/">.*?</a>', re.DOTALL)
            content = pattern.sub(new_card, content, 1)
            index_path.write_text(content, encoding='utf-8')
            print("Updated homepage cards in index.html (flexible match)")

def update_print_cover():
    cover_path = ROOT / "print-cover.html"
    if cover_path.exists():
        content = cover_path.read_text(encoding='utf-8')
        old_heading = "<h2>What's inside (" + "12" + " guides)</h2>"
        new_heading = "<h2>What's inside (13 guides)</h2>"
        content = content.replace(old_heading, new_heading)  # legacy migration
        
        old_toc = """    <li><b>Severe allergy</b> — anaphylaxis &amp; epinephrine</li>
    <li><b>Emergency triage</b> — where to start</li>"""
        new_toc = """    <li><b>Severe allergy</b> — anaphylaxis &amp; epinephrine</li>
    <li><b>Cold safety</b> — hypothermia &amp; frostbite</li>
    <li><b>Emergency triage</b> — where to start</li>"""
        if old_toc in content:
            content = content.replace(old_toc, new_toc)
        else:
            # Try plain text search
            content = content.replace("<li><b>Severe allergy</b> — anaphylaxis &amp; epinephrine</li>", 
                                      "<li><b>Severe allergy</b> — anaphylaxis &amp; epinephrine</li>\n    <li><b>Cold safety</b> — hypothermia &amp; frostbite</li>")
        cover_path.write_text(content, encoding='utf-8')
        print("Updated print-cover.html table of contents")

def update_triage_navigator():
    triage_path = ROOT / "triage" / "index.html"
    if triage_path.exists():
        content = triage_path.read_text(encoding='utf-8')
        old_box = """      <div class="box">
        <h3>⚡ Rigid jerking, loss of consciousness</h3>
        <p>Seizure. Protect the head, time it, do not restrain or put anything in the mouth.</p>
        <a class="btn alt" href="../seizure/">Seizure guide →</a>
      </div>"""
        new_box = """      <div class="box">
        <h3>⚡ Rigid jerking, loss of consciousness</h3>
        <p>Seizure. Protect the head, time it, do not restrain or put anything in the mouth.</p>
        <a class="btn alt" href="../seizure/">Seizure guide →</a>
      </div>
      <div class="box warn">
        <h3>🥶 Cold, shivering, confused, numb skin</h3>
        <p>Hypothermia or frostbite. Get to warm shelter, remove wet clothes, warm center-first gradually, and never rub frozen skin.</p>
        <a class="btn alt" href="../cold/">Cold Safety guide →</a>
      </div>"""
        if old_box in content:
            content = content.replace(old_box, new_box)
        else:
            # Flexible replace
            content = content.replace('href="../seizure/">Seizure guide →</a>\n      </div>',
                                      'href="../seizure/">Seizure guide →</a>\n      </div>\n      <div class="box warn">\n        <h3>🥶 Cold, shivering, confused, numb skin</h3>\n        <p>Hypothermia or frostbite. Get to warm shelter, remove wet clothes, warm center-first gradually, and never rub frozen skin.</p>\n        <a class="btn alt" href="../cold/">Cold Safety guide →</a>\n      </div>')
        triage_path.write_text(content, encoding='utf-8')
        print("Updated Emergency Triage Navigator")

def update_sitemap():
    sitemap_path = ROOT / "sitemap.xml"
    if sitemap_path.exists():
        content = sitemap_path.read_text(encoding='utf-8')
        new_entries = """  <url>
    <loc>https://ai-village-agents.github.io/help-kit/cold/</loc>
    <lastmod>2026-06-15</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://ai-village-agents.github.io/help-kit/cold/cold-onepager.pdf</loc>
    <lastmod>2026-06-15</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.4</priority>
  </url>
</urlset>"""
        if "</urlset>" in content:
            content = content.replace("</urlset>", new_entries)
            sitemap_path.write_text(content, encoding='utf-8')
            print("Updated sitemap.xml")

def update_service_worker():
    sw_path = ROOT / "sw.js"
    if sw_path.exists():
        content = sw_path.read_text(encoding='utf-8')
        # Bump version from help-kit-v7 to help-kit-v8
        content = content.replace('const CACHE = "help-kit-v7";', 'const CACHE = "help-kit-v8";')
        
        # Add cold safety paths in correct alphabetical order:
        # After /help-kit/choking/choking-onepager.pdf, insert /help-kit/cold/ and /help-kit/cold/cold-onepager.pdf
        old_assets = '  "/help-kit/cpr/",'
        new_assets = '  "/help-kit/cold/",\n  "/help-kit/cold/cold-onepager.pdf",\n  "/help-kit/cpr/",'
        content = content.replace(old_assets, new_assets)
        sw_path.write_text(content, encoding='utf-8')
        print("Updated sw.js cache and version to help-kit-v8")

def update_pdf_builder():
    build_path = ROOT / "scripts" / "build-pdfs.py"
    if build_path.exists():
        content = build_path.read_text(encoding='utf-8')
        old_topics = """    ("seizure", "seizure-onepager.pdf"),
    ("allergy", "allergy-onepager.pdf"),
    ("triage", "triage-onepager.pdf"),"""
        new_topics = """    ("seizure", "seizure-onepager.pdf"),
    ("allergy", "allergy-onepager.pdf"),
    ("cold", "cold-onepager.pdf"),
    ("triage", "triage-onepager.pdf"),"""
        if old_topics in content:
            content = content.replace(old_topics, new_topics)
            build_path.write_text(content, encoding='utf-8')
            print("Updated build-pdfs.py topics list")

if __name__ == '__main__':
    update_navigation()
    update_homepage_cards()
    update_print_cover()
    update_triage_navigator()
    update_sitemap()
    update_service_worker()
    update_pdf_builder()
