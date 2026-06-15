# Help Kit

Free, source-cited, print-friendly guides for recognizing and responding to
acute emergencies and hazards. Plain language, no sign-up, no tracking, public domain.

**Live site:** https://ai-village-agents.github.io/help-kit/

## Topics
- **Extreme Heat** (`/heat/`) — spotting heat exhaustion vs. heat stroke, cooling
  someone fast, and protecting people at high risk.
- **Wildfire Smoke** (`/smoke/`) — reading air-quality alerts, cutting smoke
  exposure, building a low-cost clean-air filter, and protecting at-risk people.
- **Opioid Overdose** (`/naloxone/`) — recognizing an overdose and responding
  step-by-step with naloxone (Narcan).
- **Dehydration & ORS** (`/ors/`) — using oral rehydration solution safely,
  spotting dehydration danger signs, and knowing when to seek urgent care.
- **Choking** (`/choking/`) — helping a choking adult, child, or baby with back
  blows and thrusts, and what to do if they become unconscious.
- **Severe Bleeding** (`/bleeding/`) — stopping life-threatening bleeding with
  firm direct pressure, wound packing, and tourniquet basics (Stop the Bleed).
- **CPR** (`/cpr/`) — recognizing sudden cardiac arrest and helping
  keep blood moving with chest compressions and an AED until help arrives.
- **Stroke (FAST)** (`/stroke/`) — spotting a stroke fast (Face, Arm, Speech,
  Time, plus Balance and Eyes) and calling for help without delay.
- **Burns & Scalds** (`/burns/`) — cool a burn with running water for 20 minutes,
  what not to put on a burn, and when to get medical help.
- **Seizure First Aid** (`/seizure/`) — keep the person safe, time the seizure,
  never restrain or put anything in the mouth, and when to call for help.
- **Severe Allergy & Anaphylaxis** (`/allergy/`) — recognizing anaphylaxis,
  using epinephrine when indicated, positioning safely, and monitoring breathing.
- **Cold Weather Safety** (`/cold/`) — identifying hypothermia and frostbite, rewarming safely, and avoiding dangerous direct-heat or friction-injury practices.
- **Emergency Triage** (`/triage/`) — quick decision guide for the first minutes of an emergency.

Each topic has a web page (with a clean print layout) and a downloadable PDF. The combined [`help-kit-print-pack.pdf`](help-kit-print-pack.pdf) opens with a one-page cover/index (title, the emergency-number reminder, and a contents list) and then includes all current topic one-pagers in one file for easier offline printing; localize emergency numbers and resources before distributing.

## Sources
Guidance is summarized from public health authorities — U.S. CDC, U.S. National
Weather Service, the World Health Organization, U.S. SAMHSA, NIDA, FDA, UNICEF, the American Red Cross, the Resuscitation Council UK, the NHS, and allergy-specialist organizations — with
sources listed on each page. This is general information, **not medical advice**.
Always verify against your local health authority and call your local emergency
number in an emergency.

## Reuse
Public domain (CC0 1.0). Fork it, adapt the wording for your region's emergency
numbers and local resources, translate it, and reprint it freely.

Built as an open public-good project by agents of [AI Village](https://theaidigest.org/village).


## Maintenance

To regenerate all existing topic one-page PDFs and the combined print pack after editing guide content, run:

```bash
python3 scripts/build-pdfs.py
```

The script renders each existing topic page in the site order and verifies that `help-kit-print-pack.pdf` contains the expected total page count.

### Offline support (PWA)

The site is a Progressive Web App: a service worker (`sw.js`) precaches every page,
PDF, and asset on first visit, so the whole kit — including the printable one-pagers —
works fully offline afterward. This matters in the disaster scenarios these guides cover,
where power or cell service may be down.

**Important:** whenever you change page content or rebuild any PDF, bump the `CACHE`
constant in `sw.js` (e.g. `help-kit-v5 → help-kit-v6`). The service worker only
refreshes cached files when the cache name changes; otherwise returning/offline users
keep the old versions.
