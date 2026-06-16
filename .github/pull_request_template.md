## What changed?

- 

## Safety checklist

- [ ] I kept emergency instructions general, source-cited, and aligned with public-health guidance.
- [ ] I used local-emergency-number framing and included examples like 911, 112, or 999 only as examples when needed.
- [ ] I avoided outcome guarantees, dramatic claims, or unsafe shorthand.
- [ ] I checked dignity/privacy wording and did not add tracking, sign-up gates, paywalls, or third-party scripts.
- [ ] If this changes medical/first-aid guidance, I cited sources and requested a careful second review.

## Localization checklist, if applicable

- [ ] I verified local emergency numbers, official guidance, access details, and local resources.
- [ ] Any translation was reviewed by a fluent local speaker and a local clinician or first-aid-aware reviewer before publication.
- [ ] I did not publish machine-translation drafts as live guidance.

## Offline/print checklist, if applicable

- [ ] If public HTML/CSS/assets/PDFs/service-worker behavior changed, I considered whether `sw.js` needs a cache bump.
- [ ] If guide content changed, I rebuilt the affected one-page PDF(s) and `help-kit-print-pack.pdf`.
- [ ] I kept `404.html` compatible with the styled offline fallback.
- [ ] If I changed CSS, colors, or inline styles, I checked light and dark mode contrast and keyboard focus visibility.

## Required local checks

- [ ] `python3 validate_help_kit.py`
- [ ] `python3 scripts/audit_translations.py`
- [ ] `rm -rf __pycache__ scripts/__pycache__ && git status --short`
