# Contributing safely

Help Kit pages are meant for stressful, low-connectivity moments. Small wording
changes can affect safety, trust, translation, offline behavior, and printed copies.
Use this checklist before opening or merging changes.

## Before editing a guide

- Prefer fixing safety, clarity, accessibility, broken links, localization, or
  offline/print reliability over adding new topics.
- Keep guidance general and source-cited. Do not invent medical thresholds,
  medication instructions, or local rules.
- Use local-emergency-number framing: say to call the local emergency number and
  give examples such as `911`, `112`, or `999` only as examples.
- Avoid outcome guarantees and dramatic claims. Describe concrete actions,
  emergency handoff, and local verification instead.
- Use dignity-preserving wording: describe access barriers or higher-risk
  situations without shaming people.
- For translations or local adaptations, require fluent local review and local
  clinical or first-aid-aware review before publishing or printing.

## When changing public pages or PDFs

- If you change any HTML page, CSS, image, manifest, PDF, sitemap, or service
  worker behavior that users can receive, update `sw.js` when needed so offline
  users get the new version.
- If guide content changes, rebuild the affected per-topic PDF and the combined
  print pack with:

  ```bash
  python3 scripts/build-pdfs.py
  ```

- Keep `404.html` styled with root-absolute asset paths because the service worker
  uses it as the offline fallback for unknown URLs.
- If you change CSS, colors, or inline styles, check light and dark mode contrast,
  especially keyboard focus outlines and warning/status labels.
- Keep internal scripts, draft translations, outreach drafts, and validator files
  out of the GitHub Pages artifact.

## Required checks

Run these before committing:

```bash
python3 validate_help_kit.py
python3 scripts/audit_translations.py
rm -rf __pycache__ scripts/__pycache__
git status --short
```

The validator checks public HTML links and safety wording, canonical URLs,
structured data, sitemap/robots, service-worker precache coverage, Pages artifact
exclusions, public Markdown and text files, `llms.txt`, accessibility landmarks,
and generated PDF text.

## Review expectations

- Medical or first-aid changes should cite a public health authority and get a
  careful second review.
- Localization changes should identify what local emergency numbers, official
  guidance, access details, and review roles were verified.
- Do not publish, print, share, or train from machine-translated medical guidance until a fluent local speaker and a local clinical or first-aid-aware reviewer have checked it.
- Do not add tracking, analytics, sign-up gates, paywalls, or third-party scripts.
