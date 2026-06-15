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
- **Hands-Only CPR** (`/cpr/`) — recognizing sudden cardiac arrest and keeping
  someone alive with chest compressions and an AED until help arrives.
- **Stroke (FAST)** (`/stroke/`) — spotting a stroke fast (Face, Arm, Speech,
  Time, plus Balance and Eyes) and calling for help without delay.
- **Burns & Scalds** (`/burns/`) — cool a burn with running water for 20 minutes,
  what not to put on a burn, and when to get medical help.

Each topic has a web page (with a clean print layout) and a downloadable PDF. The combined [`help-kit-print-pack.pdf`](help-kit-print-pack.pdf) includes all current topic one-pagers in one file for easier offline printing; localize emergency numbers and resources before distributing.

## Sources
Guidance is summarized from public health authorities — U.S. CDC, U.S. National
Weather Service, the World Health Organization, U.S. SAMHSA, NIDA, FDA, UNICEF, the American Red Cross, and the Resuscitation Council UK — with
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
