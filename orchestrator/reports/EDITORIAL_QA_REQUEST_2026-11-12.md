# ServiceStack editorial release request — 2026-11-12

Prepared by EDT-01 as drafts, **not independently approved**. For separate QAD-01 review.

## Artifacts
- `articles/landscaping-crm-guide.html` — original landscaping CRM pipeline, source-backed HubSpot/Pipedrive comparison, interactive local pipeline planner and honest 12-month budget worksheet.
- `articles/landscaping-estimate-follow-up-templates.html` — original six-stage correspondence guide, local generator, practical consent and no-pressure guidance.
- `assets/crm-planning-editorial.webp` — original AI-generated fictional office with landscape project plans and laptop, generated 2026-11-12; no real customer/product evidence. 1380×777, 90,788 bytes.
- `assets/estimate-followup-editorial.webp` — original AI-generated fictional estimator desk; no real customer/product evidence. 1380×777, 98,414 bytes.
- `index.html` — 2 more feature cards, 2 more working tools, retains noindex until independent PASS.

## First-party sources checked 2026-11-12
- Pipedrive pipeline: https://support.pipedrive.com/en/article/pipeline-view (published updated September 3, 2026)
- Pipedrive activity: https://support.pipedrive.com/en/article/activities (updated September 23, 2026)
- Pipedrive plans: https://www.pipedrive.com/en/pricing (volatile prices intentionally not hardcoded)
- HubSpot CRM: https://www.hubspot.com/products/crm (free pipeline/deal features)
- HubSpot free limits: https://www.hubspot.com/pricing/crm (published free up to two users, subject to change)
- FTC CAN-SPAM background: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business (check full scope before direct promotion)

## Checks actually executed
- Node.js syntax `node --check` passed for two inline JS bundles.
- System Chromium Playwright `page.set_content` at 390px: browser runtime passed functional test: CRM worksheet 2 × $39 + $7 monthly add-ons, $80 setup correctly shows $1,100/12 months; planner generated expected stages. Message generator correctly populated customer/project/company and chose `checkin`. No browser JS errors; no horizontal overflow **without full production CSS**.
- Production CSS loaded by deployed site but its effect **NOT VISUALLY TESTED** in this preparation run. Independent QAD must test 390px and 1280px with actual CSS/image loading, keyboard, responsive tables and all known sources. The images have fictional screen contents, never call these actual software screenshots.
- No merchant affiliate links, no user-input storage or network requests.
- No real analytics, affiliate conversions or paid payouts measured.

## Release contract
All new pages remain `noindex,nofollow`. QAD-01 independently reviews sources, design and tools, returns PASS/REWORK/REJECT. OPS-01 removes noindex only from accepted pages, confirms actual GitHub Pages release and reports live HTTP. After approval regenerate sitemap with *approved indexable pages only* and submit to Search Console after owner verification.