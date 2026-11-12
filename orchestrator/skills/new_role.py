#!/usr/bin/env python3
"""Scaffold a role SKILL.md as a DRAFT only; never grants tool access or schedules it."""
from __future__ import annotations
import argparse
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]


def create_draft(role: str, name: str, purpose: str, root: pathlib.Path = ROOT) -> pathlib.Path:
    if not re.fullmatch(r"[A-Z]{3}-\d{2}", role):
        raise ValueError("Role must look like PRD-01")
    if not name.strip() or not purpose.strip() or len(name) > 90 or len(purpose) > 260:
        raise ValueError("Short name and purpose required")
    target = root / "skills" / "drafts" / role / "SKILL.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    body = f'''---
name: {name.strip()}
description: Candidate internal AffiliateOS role, not activated
role_id: {role}
version: 0.1.0
status: draft
---
# {name.strip()} — DRAFT ONLY

## Purpose
{purpose.strip()}

## Inputs
Define allowed sources with specific paths and permissions.

## Workflow
Define minimum data and one bounded, measurable task.

## Outputs
Define exact artifact and evidence trace.

## Checks
Define five-case evaluation and independent QA requirements.

## Handoff
Task ID, evidence, next owner, acceptance, cost, and unknowns.

## Limits
No external spend, owner authorization, no autonomous role activation, no QA bypass. DRAFT is not in the active skills manifest.
'''
    with target.open("x", encoding="utf-8") as f:
        f.write(body)
    return target


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--role", required=True)
    p.add_argument("--name", required=True)
    p.add_argument("--purpose", required=True)
    a = p.parse_args()
    print(create_draft(a.role, a.name, a.purpose))