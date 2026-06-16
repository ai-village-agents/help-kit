import os
import re
import sys
from pathlib import Path
from bs4 import BeautifulSoup

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
    return set(links)

def audit_all_translations():
    repo_dir = str(Path(__file__).resolve().parents[1])
    drafts_dir = os.path.join(repo_dir, "_translation-drafts")
    
    if not os.path.exists(drafts_dir):
        print("No translation drafts directory found.")
        return
    
    languages = ["es", "fr", "hi"]
    issues_found = 0
    
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
                        missing_links = eng_links - draft_links
                        extra_links = draft_links - eng_links
                        if missing_links or extra_links:
                            print(f"[WARNING] Link discrepancy in {lang.upper()} translation of {relative_path}:")
                            if missing_links:
                                print(f"  Missing links in draft: {sorted(list(missing_links))}")
                            if extra_links:
                                print(f"  Extra links in draft: {sorted(list(extra_links))}")
                            print()
                            issues_found += 1
                                
    if issues_found == 0:
        print("[SUCCESS] Numeric and link audits complete: no numeric or href discrepancies found between English files and existing drafts.")
    else:
        print(f"[AUDIT COMPLETE] Found {issues_found} potential discrepancy issues.")
        sys.exit(1)

if __name__ == "__main__":
    audit_all_translations()
