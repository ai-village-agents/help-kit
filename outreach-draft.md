# Help Kit — Safe Distribution & Outreach Guide

This guide is for community organizers, mutual-aid volunteers, and AI agents who want to share **Help Kit** resources with local groups, libraries, shelters, or health organizations.

We adhere to a strict **harm-reduction, non-spammy, and privacy-respecting** stance. Unsolicited outreach from AI agents can easily cause friction or clutter digital spaces. By preparing thoughtful, localized, and highly respectful templates, we ensure that any direct contact is genuinely welcome and valuable.

---

## SECTION 1: CORE OUTREACH PRINCIPLES

1. **Verify Local Relevancy First:** Do not send generic U.S.-focused materials to international organizations. Localize emergency numbers, resources, and translations *before* contacting any local organizer.
2. **Respect Online Spaces:** Never bulk-message, spam, or use automated scrapers to blast emails. Contact only specific organizations that explicitly list public contact channels for resource-sharing.
3. **Transparency:** Clearly state that this is an open-source, CC0 (public domain) resource. No logins, no ads, no trackers, and no funding requested.
4. **Agent Constraint (Strict):** AI agents must **never** send unsolicited emails or make posts to human websites without obtaining formal administrative approval first via the `request_approval_for_unsolicited_outreach` tool.

---

## SECTION 2: THE REUSABLE OUTREACH TEMPLATE

Below is the standard, conservative template designed for local community networks (e.g., public libraries, mutual aid coalitions, tenant associations, or disaster assistance groups).

```text
Subject: Free, open-source emergency first-aid & heat safety print-pack (CC0)

Dear [Contact Name / Organizer Team],

I hope this finds you well. I am writing on behalf of the Help Kit project, an open-source, public-good initiative that distills emergency health guidance into clean, printable, single-page reference sheets.

With extreme heat waves, smoke alerts, and other climate-related events placing a heavy burden on local communities, we wanted to share a free resource that your network can use or distribute. We have compiled a unified 18-page PDF "Print Pack" containing six essential emergency guides, fully cited to sources like the Red Cross, WHO, and CDC:

1. Extreme Heat & Buddy Checks (thermoregulation, fan dilemmas, cooling centers)
2. Wildfire Smoke Safety (cleaner air, low-cost room filters)
3. Opioid Overdose Response (step-by-step naloxone administration)
4. Dehydration & ORS (oral rehydration solution safety, pediatric/adult guidelines)
5. Choking First Aid (adult/infant maneuvers, CPR sequences)
6. Severe Bleeding (pressure, wound packing, and tourniquet basics)

The entire project is public domain (CC0). You are welcome to host it, print it, translate it, or adapt the text for your neighborhood's specific emergency numbers and local resources. No signup, no tracking, and no ads.

You can view the live site and download the PDFs here:
https://ai-village-agents.github.io/help-kit/

Our "Localize & Share" guide can help your team adapt these sheets for your area's local emergency protocols:
https://ai-village-agents.github.io/help-kit/localize.html

Thank you for your tireless work in supporting our community. If you have any feedback or would like help formatting a localized version, please let us know.

Warm regards,

[Your Name / Help Kit Team]
https://github.com/ai-village-agents/help-kit
```

---

## SECTION 3: RATIONALE & OUTREACH ARGUMENT

When submitting an approval request for unsolicited outreach, you must justify why the recipient will be glad to receive it. Here is the established rationale:

- **Direct Value:** Local volunteer coordinators and mutual aid groups are often resource-constrained and frequently spend hours drafting or seeking print-friendly safety flyers during emergencies.
- **Trusted Sources:** All protocols are strictly sourced from official public health bodies (AHA, ACS, SAMHSA, CDC, WHO, Red Cross, Resuscitation Council), reducing the risk of misinformation.
- **Zero Cost/Tracking:** Because the site is static, ad-free, tracking-free, and CC0, there is zero monetization or commercial incentive. It is built purely as a public good.
- **Print-Friendly Format:** The custom CSS stylesheet formats pages automatically for clean black-and-white or color printing, saving paper and ensuring high legibility for unhoused or offline neighbors.

---

## SECTION 4: INSTRUCTIONS FOR AI AGENTS (SUBMITTING APPROVALS)

If you identify a highly relevant, localized organization (such as a local disaster response hub or shelter network) that would benefit from this print pack:

1. **Verify:** Check that their public contact info is correct and that they actively distribute community guides.
2. **Draft:** Prepare the email verbatim, replacing bracketed terms (like `[Contact Name]`) with real, verified information.
3. **Submit:** Execute the `request_approval_for_unsolicited_outreach` tool with the following fields:
   - **medium**: `Email` or `Contact Form`
   - **recipient**: `[Insert specific organization/contact email]`
   - **message_content**: `[Insert completed verbatim text]`
   - **rationale**: `[Provide the specific localized value rationale, e.g., "This mutual aid group in SF distributes weekly food/cooling supplies to unhoused individuals and currently has no printable extreme heat flyers."]`
4. **Wait:** Never send the message until a village administrator explicitly approves your request.
