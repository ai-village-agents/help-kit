import os
import sys
from pathlib import Path

# Add the root directory to path so we can import scripts.translate_kit
sys.path.append("/home/computeruse/help-kit-repo")
from scripts.translate_kit import translate_html_file

ROOT = Path("/home/computeruse/help-kit-repo")
DRAFT_ROOT = ROOT / "_translation-drafts"

languages = ["es", "fr", "hi"]

html_files = []
for root, dirs, files in os.walk(ROOT):
    if "_translation-drafts" in root or ".git" in root or "scripts" in root:
        continue
    for file in files:
        if file.endswith(".html") and not file.startswith("."):
            html_files.append(Path(root) / file)

for lang in languages:
    for file_path in html_files:
        rel_path = file_path.relative_to(ROOT)
        output_dir = DRAFT_ROOT / lang / rel_path.parent
        output_file = output_dir / rel_path.name
        draft_file = output_file.with_suffix('.html.draft')
        translate_html_file(file_path, draft_file, lang)

print("Regeneration complete!")
