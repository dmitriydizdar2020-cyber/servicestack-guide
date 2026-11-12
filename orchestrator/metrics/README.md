# AffiliateOS measurement — evidence-first, local-only

Use `python3 scripts/owner_scorecard.py --date YYYY-MM-DD` to read current canonical GitHub task state. **No CSV provided = search and earnings UNKNOWN, not zero.** Never commit client exports, IDs, payment receipts, customer data or access tokens to this PUBLIC repository.

## Search Console data

Google Search Console is verified for the owner, but this repository has no authorized live GSC API access. Open Performance > Search results > Pages; choose a known date range; export the Pages CSV. Then run locally:

```bash
python3 scripts/owner_scorecard.py --date 2026-11-12 --gsc-pages ~/Downloads/Pages.csv --output /tmp/affiliateos-scorecard.md
```

The parser expects a **Pages** export with `Page` (or `Top pages`), `Clicks`, and `Impressions` columns. It sums only the supplied CSV's rows. CSV is user-supplied evidence, **not independently verified by the script**. Index coverage requires separate Search Console inspection.

## Affiliate evidence ledger (optional)

Prepare a private CSV using `merchant_events_TEMPLATE.csv` headers: `event_id,date,merchant,kind,amount,currency,evidence`.

Allowed kinds: `outbound_click`, `approved_sale`, `commission_approved`, `commission_paid`, `commission_reversed`. Events require unique IDs and nonempty evidence references. Money is grouped by **original currency**, not converted. Revenue is called independently confirmed only after checking actual merchant/bank evidence. For a click record, amount = 0.00. Never store payout, email or banking data in this public repo.

```bash
python3 scripts/owner_scorecard.py --date 2026-11-12 --merchant-events /private/merchant-events.csv
```

The tool makes no network requests and never writes inputs back to the repo. If neither export exists, it still provides a QA/publishing summary using recorded task evidence.

## Leading indicators

Track weekly: indexed pages, search impressions, organic clicks, click-through by guide, disclosed referral clicks, **merchant-approved** sales, reversed commissions, **actually paid** cash by currency, and time/cost spent. Add source, reporting window and evidence every time. Do not count draft articles or QA-stage URLs as indexed pages. Do not promise rankings or income.
