# Global Help Kit: Multi-Language Translation and Localization Architecture

To dramatically scale the impact of our harm-reduction platform and reduce global suffering, the Help Kit will expand into a multi-language, localized resource center. Since the kit is designed for high-stress disaster situations, our architecture prioritizes **offline-first reliability, static-site performance, and precise translation safety**.

---

## 1. Directory and Navigation Architecture

To maintain zero runtime dependencies and maximum offline/PWA compatibility, we use **directory-based routing** (e.g., `/es/`, `/fr/`, `/hi/`). Each language has a mirrored static structure.

```
help-kit/
│
├── index.html                   # English Homepage
├── style.css                    # Unified Design System Stylesheet
│
├── es/                          # Spanish Root
│   ├── index.html               # Spanish Homepage
│   ├── style.css                # Symlinked or relative path to root style.css
│   ├── heat/
│   │   ├── index.html           # Spanish Heat Guide
│   │   └── heat-onepager.pdf    # Spanish Heat PDF
│   └── triage/
│       └── index.html           # Spanish Triage Navigator
│
└── fr/                          # French Root
    └── ...
```

### 1.1 Localized Navigation Redirection
- When a user lands on the English homepage (`index.html`), the system displays a language selector dropdown in the header.
- Users can switch between English, Spanish, French, and Hindi. This updates the cookie or local storage preference and redirects them to the chosen folder.
- All internal links within a localized folder are relative and point exclusively to files in that language's directory (e.g., `<a href="../cpr/">` within `/es/heat/index.html` resolves to `/es/cpr/index.html`).

---

## 2. Target Languages & High-Suffering Priority Regions

We prioritize languages that serve regions facing acute climatic, health, or infrastructure-deficit challenges:

| Language | Code | Primary Target Regions | Key High-Suffering Risks Addressed |
|---|---|---|---|
| **Spanish** | `es` | Latin America, Caribbean, USA | Extreme heat, hurricanes, dehydration, lack of emergency services |
| **French** | `fr` | West & Central Africa, Haiti | Waterborne dehydration (ORS), choking, severe bleeding, limited clinics |
| **Hindi**| `hi` | South Asia (India, Nepal) | Intense heatwaves, agricultural smoke/pollution, respiratory illness |

---

## 3. HTML-Aware Translation Script: `translate_kit.py`

To prevent layout breakages, the translation workflow must be entirely programmatically controlled, preserving CSS structures, navigation formats, and semantic metadata.

### 3.1 Core Processing Algorithm
We will implement an automated Python script, `translate_kit.py`, using `beautifulsoup4` and an LLM/translation API.

1. **HTML Parsing:** Parse English HTML files with BeautifulSoup.
2. **Structural Preservation:** Extract only raw text nodes from specific tags (`p`, `li`, `h1`, `h2`, `h3`, `strong`, `em`, `a`, `span`, `div.warn`). Keep all structural container elements, classes, IDs, and attributes untouched.
3. **Translation Preservation:**
   - Elements with `.site` or `.brand` (like navigation and brand logos) are replaced with localized terms or left as "Help Kit".
   - Links in `<a href="...">` are updated: if they point relative to `../[topic]/`, they remain correct, but any root links (like `../index.html` or `../localize.html`) must point to the target language root (`../index.html` within the subfolder, or `./localize.html`).
4. **Metadata Translation:** Programmatically translate `<title>`, `<meta name="description">`, and corresponding OpenGraph/Twitter card tags.
5. **PDF Generation Integration:** Re-run `weasyprint` on the generated localized HTML files to compile language-specific one-pagers and combined print packs.

### 3.2 HTML-Safe Parser Draft (`scripts/translate_kit.py`)
```python
import os
import re
from bs4 import BeautifulSoup

def translate_html_file(input_path, output_path, target_lang):
    with open(input_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        
    # Translate meta tags
    title_tag = soup.find('title')
    if title_tag:
        title_tag.string = call_translation_api(title_tag.string, target_lang)
        
    desc_tag = soup.find('meta', attrs={'name': 'description'})
    if desc_tag:
        desc_tag['content'] = call_translation_api(desc_tag['content'], target_lang)
        
    # Translate text blocks safely
    # Extract only visible text nodes, avoiding scripts, CSS, and structural blocks
    for element in soup.find_all(text=True):
        if element.parent.name in ['script', 'style', 'code']:
            continue
        # Skip empty space or linebreaks
        text = element.strip()
        if len(text) > 1 and not text.isdigit():
            translated = call_translation_api(text, target_lang)
            element.replace_with(translated)
            
    # Write translated file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(str(soup))
```

---

## 4. Localized Safety Safeguards

1. **Explicit Legal and Clinical Disclaimer:** Every translated page must maintain a prominent, localized medical disclaimer:
   - *Spanish:* "Este kit de ayuda es únicamente de carácter educativo y de primeros auxilios. En caso de una emergencia real, llame a su número local de emergencia de inmediato."
2. **Dynamic Emergency Numbers:** Ensure the `Localize & share` file (`localize.html`) lets local organizers set their country's specific emergency number (e.g., 911 for USA/Mexico, 112 for EU/India, 999 for UK).
3. **Accuracy Auditing:** Automated translations of critical medical guides (like Narcan/Naloxone dosage or CPR compression depth) must be audited by an AI-safety peer model or native speaker agent before deployment to prevent lethal instructional errors.
