#!/usr/bin/env python3
"""AffiliateOS evidence-first scorecard: repository state + optional owner CSV exports.

No external API requests, tracking cookies, persisted visitor data or costs.
Missing metrics always remain UNKNOWN, never silently zero.
"""
from __future__ import annotations
import argparse
import csv
from collections import Counter, defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / 'orchestrator/state/tasks.json'
EVENT_KINDS = {'outbound_click', 'approved_sale', 'commission_approved', 'commission_paid', 'commission_reversed'}

def parse_nonnegative_int(value: str, *, field: str) -> int:
    raw = str(value).strip().replace(',', '')
    if not raw.isdigit():
        raise ValueError(f'{field} must be a nonnegative integer; received {value!r}')
    return int(raw)

def load_gsc(path: Path | None):
    if path is None:
        return None
    with path.open(newline='', encoding='utf-8-sig') as stream:
        rows = csv.DictReader(stream)
        fields = set(rows.fieldnames or [])
        if not {'Clicks', 'Impressions'}.issubset(fields) or not (fields & {'Page', 'Top pages', 'Landing page'}):
            raise ValueError('GSC export must be the Pages table with Page/Top pages, Clicks and Impressions columns')
        result = {'rows': 0, 'clicks': 0, 'impressions': 0, 'source': path.name}
        for row in rows:
            if not any(str(v or '').strip() for v in row.values()):
                continue
            result['clicks'] += parse_nonnegative_int(row['Clicks'], field='GSC Clicks')
            result['impressions'] += parse_nonnegative_int(row['Impressions'], field='GSC Impressions')
            result['rows'] += 1
    result['ctr_pct'] = round(100 * result['clicks'] / result['impressions'], 2) if result['impressions'] else None
    return result

def load_merchant_events(path: Path | None):
    if path is None:
        return None
    with path.open(newline='', encoding='utf-8-sig') as stream:
        rows = csv.DictReader(stream)
        required = {'event_id', 'date', 'merchant', 'kind', 'amount', 'currency', 'evidence'}
        if not required.issubset(rows.fieldnames or []):
            raise ValueError('Merchant ledger must contain: ' + ', '.join(sorted(required)))
        seen = set()
        counts = Counter()
        paid = defaultdict(Decimal)
        approved = defaultdict(Decimal)
        for line, row in enumerate(rows, start=2):
            eid = (row.get('event_id') or '').strip()
            if not eid or eid in seen:
                raise ValueError(f'Ledger line {line}: event_id must be unique and nonempty')
            seen.add(eid)
            date.fromisoformat((row.get('date') or '').strip())
            if not (row.get('merchant') or '').strip():
                raise ValueError(f'Ledger line {line}: merchant required')
            kind = (row.get('kind') or '').strip()
            if kind not in EVENT_KINDS:
                raise ValueError(f'Ledger line {line}: unsupported kind {kind}')
            evidence = (row.get('evidence') or '').strip()
            if not evidence:
                raise ValueError(f'Ledger line {line}: evidence reference required')
            currency = (row.get('currency') or '').strip().upper()
            if len(currency) != 3 or not currency.isalpha():
                raise ValueError(f'Ledger line {line}: use an ISO-like 3-letter currency')
            try:
                amount = Decimal((row.get('amount') or '').strip())
            except InvalidOperation as exc:
                raise ValueError(f'Ledger line {line}: invalid amount') from exc
            if not amount.is_finite() or amount < 0:
                raise ValueError(f'Ledger line {line}: amount must be finite and >= 0')
            counts[kind] += 1
            if kind == 'commission_paid':
                paid[currency] += amount
            if kind == 'commission_approved':
                approved[currency] += amount
    return {'events': len(seen), 'counts': dict(counts),
            'reported_paid_by_currency': {k: str(v) for k, v in sorted(paid.items())},
            'reported_approved_by_currency': {k: str(v) for k, v in sorted(approved.items())},
            'source': path.name}

def score_tasks(state: dict, day: str) -> dict:
    tasks = state.get('tasks')
    if not isinstance(tasks, list):
        raise ValueError('Canonical state requires a tasks array')
    published, release_today, pending, rework = [], [], [], []
    for task in tasks:
        item_id = task.get('id', '')
        artifact = task.get('artifact_path') or ''
        if not artifact.startswith('articles/') or not artifact.endswith('.html'):
            continue
        status = task.get('status')
        qa = task.get('qa') or {}
        if status == 'published':
            if qa.get('decision') != 'PASS' or qa.get('reviewer_role') != 'QAD-01' or not qa.get('evidence'):
                raise ValueError(f'{item_id}: published article lacks documented independent QA PASS')
            published.append(item_id)
            if (task.get('deployment_proof') or {}).get('checked_on') == day:
                release_today.append(item_id)
        elif status == 'awaiting_qa':
            pending.append(item_id)
        elif status == 'rework':
            rework.append(item_id)
    return {'published_approved_articles': len(published), 'published_ids': published,
            'release_proof_dated_today': len(release_today), 'release_ids_today': release_today,
            'awaiting_qa': pending, 'rework': rework, 'daily_release_target': 5,
            'release_shortfall': max(0, 5 - len(release_today)),
            'release_count_limitation': 'Based on deployment_proof.checked_on, NOT verified first-publication timestamps'}

def render(day: str, task_metrics: dict, gsc, merchant) -> str:
    t = task_metrics
    release_ids = ', '.join(t['release_ids_today']) or 'none recorded'
    lines = [f'# AffiliateOS owner scorecard — {day}', '',
             'Source: canonical GitHub task state; optional owner-provided CSV exports.',
             'This document does not independently confirm search indexing, traffic, merchant events or bank settlement.', '',
             '## Production and editorial QA',
             f"- Independently QA-approved published articles in repository: **{t['published_approved_articles']}** ({', '.join(t['published_ids']) or 'none'}).",
             f"- Published releases with deployment proof dated {day}: **{t['release_proof_dated_today']}** ({release_ids}).",
             f"- Target: **{t['daily_release_target']}** new releases/day; date-stamped proof shortfall: **{t['release_shortfall']}**. Do not treat proof date as conclusive first-publication date.",
             f"- Awaiting independent QA: **{', '.join(t['awaiting_qa']) or 'none'}**; rework: **{', '.join(t['rework']) or 'none'}**.", '',
             '## Search performance (Google Search Console)']
    if gsc is None:
        lines.append('- Clicks, impressions, CTR, indexed URL count and positions: **UNKNOWN** — no current GSC Pages CSV was supplied.')
    else:
        ctr = f"{gsc['ctr_pct']}%" if gsc['ctr_pct'] is not None else 'not defined (no impressions)'
        lines.append(f"- **User-exported**, not independently verified: {gsc['clicks']} clicks, {gsc['impressions']} impressions, CTR {ctr}, across {gsc['rows']} page rows from {gsc['source']}.")
        lines.append('- Export period, indexed URLs and ranking changes must be checked in GSC separately; no ranking inference from the file alone.')
    lines.extend(['', '## Affiliate measurement'])
    if merchant is None:
        lines.append('- Merchant outbound clicks, approved commissions, paid cash and reversals: **UNKNOWN** — no merchant export supplied.')
    else:
        counts = merchant['counts']
        lines.append(f"- **User-reported, not independently verified:** {counts.get('outbound_click', 0)} merchant click events; {counts.get('approved_sale', 0)} approved sale events; {counts.get('commission_reversed', 0)} reversals.")
        lines.append(f"- Approved commissions: **{merchant['reported_approved_by_currency'] or 'none entered'}**; paid commissions: **{merchant['reported_paid_by_currency'] or 'none entered'}** from {merchant['source']}.")
        lines.append('- Values require independent merchant/bank readback before calling them verified revenue. Never combine currencies without a documented exchange rate.')
    lines += ['', '## Next evidence gate',
              '1. Preserve separate QAD-01 PASS and release proofs; do not remove noindex for pending pages.',
              '2. Export GSC > Performance > Search results > Pages as CSV for a known date range and review indexing in Search Console.',
              '3. Record only evidence-backed affiliate events; never infer commissions from clicks.',
              '4. Pursue original useful buyer tools, sources and internal links, not mass-produced keyword variants.', '']
    return '\n'.join(lines)

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--date', default=date.today().isoformat())
    ap.add_argument('--state', type=Path, default=STATE)
    ap.add_argument('--gsc-pages', type=Path)
    ap.add_argument('--merchant-events', type=Path)
    ap.add_argument('--output', type=Path)
    args = ap.parse_args(argv)
    try:
        date.fromisoformat(args.date)
        data = json.loads(args.state.read_text(encoding='utf-8'))
        task_metrics = score_tasks(data, args.date)
        gsc = load_gsc(args.gsc_pages)
        merchant = load_merchant_events(args.merchant_events)
        doc = render(args.date, task_metrics, gsc, merchant)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(doc, encoding='utf-8')
            print(f'Owner scorecard written: {args.output}')
        else:
            print(doc)
        return 0
    except (ValueError, FileNotFoundError, json.JSONDecodeError) as exc:
        print(f'Scorecard input error: {exc}', file=sys.stderr)
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
