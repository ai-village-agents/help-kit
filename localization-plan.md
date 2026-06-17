# Global Help Kit: Multi-Language Translation and Localization Architecture

To broaden the reach of this harm-reduction platform, the Help Kit may expand into multi-language, localized resource sets. Because the kit is designed for high-stress disaster and first-aid situations, the workflow must prioritize **offline-first reliability, static-site performance, and translation safety**.

**Safety boundary:** this document is a workflow plan, not approval to publish translated medical or first-aid pages. Do not publish, print, share, or train from machine-translated medical guidance until a fluent local speaker and a local clinical or first-aid-aware reviewer have checked it.

---

## 1. Directory and Navigation Architecture

This section describes the intended structure **only after a translation has passed review and is ready to publish**. To maintain zero runtime dependencies and maximum offline/PWA compatibility, reviewed translations can use **directory-based routing** (e.g., `/es/`, `/fr/`, `/hi/`). Each published language has a mirrored static structure.

Unreviewed machine or LLM-assisted drafts must not be placed in public root language directories. Current draft outputs belong under `_translation-drafts/<lang>/.../*.html.draft`, which is excluded from GitHub Pages artifacts, Jekyll processing, sitemap entries, and service-worker precaching. Public `/es/`, `/fr/`, `/hi/`, etc. should be created only when reviewed translations are intentionally promoted for live use.

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

## 2. Candidate Languages & Priority Contexts

Initial candidate languages should be chosen with local need, reviewer availability, and deployment partners in mind. The examples below are starting points, not a claim that these are the only or highest-priority languages:

| Language | Code | Example Regions | Example Risks Addressed |
|---|---|---|---|
| **Spanish** | `es` | Latin America, Caribbean, USA | Extreme heat, hurricanes, dehydration, lack of emergency services |
| **French** | `fr` | West & Central Africa, Haiti | Waterborne dehydration (ORS), choking, severe bleeding, limited clinics |
| **Hindi**| `hi` | South Asia (India, Nepal) | Intense heatwaves, agricultural smoke/pollution, respiratory illness |

---

## 3. HTML-Aware Translation Script: `translate_kit.py`

To prevent layout breakages, the translation workflow can use programmatic helpers to preserve CSS structures, navigation formats, and semantic metadata. Automation should create **review drafts**, not live pages.

### 3.1 Core Processing Algorithm
The current helper, `scripts/translate_kit.py`, uses `beautifulsoup4` and a translation engine interface to create draft files for review under `_translation-drafts/<lang>/.../*.html.draft`.

1. **HTML Parsing:** Parse English HTML files with BeautifulSoup.
2. **Structural Preservation:** Extract only raw text nodes from specific tags (`p`, `li`, `h1`, `h2`, `h3`, `strong`, `em`, `a`, `span`, `div.warn`). Keep all structural container elements, classes, IDs, and attributes untouched.
3. **Translation Preservation:**
   - Elements with `.site` or `.brand` (like navigation and brand logos) are replaced with localized terms or left as "Help Kit".
   - Links in `<a href="...">` are updated: if they point relative to `../[topic]/`, they remain correct, but any root links (like `../index.html` or `../localize.html`) must point to the target language root (`../index.html` within the subfolder, or `./localize.html`).
4. **Metadata Translation:** Programmatically translate `<title>`, `<meta name="description">`, and corresponding OpenGraph/Twitter card tags.
5. **Review Gates Before PDF Generation:** Do not generate public PDFs until the localized HTML has passed review and has been intentionally promoted from `_translation-drafts` into a public language route. After approval, re-run `weasyprint` on the reviewed localized HTML files to compile language-specific one-pagers and combined print packs.
6. **Do-Not-Translate Protections:** Mark URLs, emergency-number placeholders, measurement values, medication names, source names, `lang`/`dir` attributes, code, and structured data as protected tokens. Reviewers must confirm that numbers, doses, time windows, and emergency actions did not change.

### 3.2 Maintained Helper Contract (`scripts/translate_kit.py`)
Do not copy old pseudocode into a new translation generator. Use and maintain `scripts/translate_kit.py` as the canonical helper so every draft inherits the current safety controls:

- output stays under `_translation-drafts/<lang>/.../*.html.draft`, never public root language directories;
- root-path traversal and `.draft` inputs are rejected;
- HTML comments, doctypes, scripts, styles, code, URLs, emergency numbers, medication names, measurements, doses, timings, and other protected tokens are not translated accidentally;
- draft HTML gets the target `lang` attribute plus `noindex, nofollow, noarchive` robots metadata;
- every draft includes a visible "UNREVIEWED MACHINE TRANSLATION DRAFT" warning;
- review gates and CI must continue to reject public `es/`, `fr/`, or `hi` draft directories until translations are intentionally promoted.

---

## 4. Localized Safety Safeguards

1. **No unreviewed live medical translations:** Automated or LLM-assisted translations of first-aid guides must not be published live, printed, shared, trained from, placed in public root language directories, added to the service-worker precache, included in the sitemap, or promoted for public use until review is complete. Keep draft files under `_translation-drafts/<lang>/.../*.html.draft` with noindex/noarchive warnings.
2. **Human fluent/local and clinical/first-aid-aware review required:** At least one fluent human reviewer with local context and one local clinical or first-aid-aware reviewer should check translated medical guidance before publication, printing, sharing, PDF generation, service-worker precaching, or sitemap inclusion. AI peer review can help find issues, but it is not a substitute for human review.
3. **Explicit medical disclaimer:** Every translated page must keep a prominent, localized disclaimer that says the guide is general information, not medical advice or training, and that users should call the local emergency number and follow local/dispatcher guidance in emergencies.
4. **Emergency numbers and local services:** Keep emergency numbers as localizable placeholders until verified for the intended country/region. Avoid implying one number works everywhere. The `Localize & share` file should help local organizers set emergency numbers, poison/toxicology contacts, health authority links, and locally available services.
5. **Protected facts checklist:** Reviewers must compare the translation against the English source for all numbers, doses, timings, measurements, danger signs, “do not” warnings, and escalation instructions. Examples include ORS salt/sugar amounts, CPR compression depth/rate, naloxone repeat-dose timing, burn cooling time, and epinephrine second-dose timing.
6. **Versioning:** Each localized page should record the English source commit it was translated from, reviewer names or roles where safe to share, review date, and any local adaptations. When English source content changes, mark the translation as needing review before rebuilding public PDFs or cache entries.
