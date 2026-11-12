# AffiliateOS — Executive Editorial Design System v2.0
**Design family:** ORIGINAL premium business-media aesthetic (inspired by the clarity of leading financial/business publications; do not reproduce any trademarked publication identity, page or typography).
Applies to **every future site**, homepage, comparison, buyer guide, useful tool and card. Each vertical has its own name, images and restrained accent; underlying design rules remain consistent. This is a DESIGN CONTRACT for code review, not a substitute for browser tests.

## Personality
Authoritative, calm, precise, journalistic, legible; focus on evidence, not ornamental UI. Treat readers as busy decision makers. Aim for high perceived trust without fabricated awards, testimonials, author credentials or review scores.

## Colors — CSS custom properties
- `--paper: #FAF9F6` (main)
- `--surface: #FFFFFF` (cards / controls where needed)
- `--ink: #191C20` (body and headings)
- `--muted: #59636B` (secondary text; check contrast)
- `--rule: #D8D9D5` (dividers)
- `--brand: #9E392F` (editorial emphasis for ServiceStack)
- `--brand-ink: #234A42` (solid darker alternative)
Use no colored fill for ordinary highlight boxes; rely on typography, light line borders, a slim brand accent. New verticals may change `--brand` only if contrast and hierarchy pass.

## Type: no paid webfonts required
- Display/H1/H2: Georgia / modern OS serif (strong old-style editorial).
- Body: system sans serif; for longer reading 18px desktop, >=16px mobile; line-height 1.7–1.8.
- Headlines: 48–76px desktop hero, 34–46px mobile; article H1 max 66px.
- Content line length 63–75 characters (`max-width: 68ch`); headings line length <=22ch where sensible.
- Eyebrow ~11–12px uppercase with 0.08em tracking, byline 12–13px, captions 12–13px.
- H2 every meaningful section; avoid endless H3 nesting. Short paragraphs (2–4 sentences).
- Lists and tables for decisions, not keyword stuffing.

## Layout and spacing
- Page container max 1180–1240px, desktop padding 28–36px, mobile 16–20px.
- Article reading column max 760px; sidebar optional for 1024px+ only. Never compress reading text to fit an aggressive sidebar.
- Editorial grid: lead story 2-column at >=900px; article cards 2–3 columns; one column on narrow screens.
- Scale in 8px multiples: 8/16/24/32/48/64/80; reserve generous vertical white space.
- Delineate with thin rules, not giant rounded boxes and shadows. Card radius <=4px, no neumorphism, no generic marketing gradients.
- Header: restrained top utility row, wordmark, clear persistent categories. On mobile no overlap or horizontal scroll.

## Images
- For top stories, use one distinctive topical photograph or clearly labeled synthetic editorial photorealism. Keep alt text honest and never misrepresent a product test or client outcome.
- Max hero ratio around 1.7:1–2.3:1 on desktop, adaptable crop 1.25:1–1.6:1 on mobile. Card image 3:2 or 16:10 with consistent crop.
- Filename/rights/source/usage date recorded; prefer compressed WebP/AVIF with exact width/height. Photograph selection must directly convey article subject.
- Do not repeat identical stock photos on unrelated cards, create fake UI screenshots or use giant low-information infographics.

## Home template
Masthead -> lead analysis with visually relevant hero -> latest 4–8 stories -> buyer guides/case-specific tools -> topic navigation -> methodology/trust -> disclosure and footer. Never show fake dates, article counts, awards or testimonials.

## Article template (semantic headings)
1. Category / title / dek / authoring identity accurately stated / published+updated / disclosure.
2. Hero visual with provenance caption.
3. Plain-English answer and 3–5 key takeaways.
4. Optional internal contents links for genuinely long articles.
5. Buyer problem and decision criteria with verifiable product evidence.
6. Realistic options/tradeoffs, source-by-claim links, relevant tables.
7. Original utility/checklist/calculator when it benefits user.
8. Limitations, update date, sources, FAQ only when real questions.
9. Related guides, meaningful commercial CTA only when affiliate approval/terms allow.
Readers must understand what was *researched from documents* versus actually *tested*.

## Acceptance
At 390px and 1280px: headings not clipped, body comfortably legible, no whole-page horizontal scroll, controls keyboard-usable, links and images load, tables horizontally scroll in their own region, proper captions and mobile art direction. Test at 768 and 1440 when possible.
Lighthouse/performance numbers only if measured. Static code lint not a visual test. QA can reject generic look, shallow content, repeated imagery, fake media authority or missing provenance.