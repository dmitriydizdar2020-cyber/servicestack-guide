#!/usr/bin/env python3
"""Read-only, zero-dependency audit of role skill packs and QA promotion gates."""
from __future__ import annotations
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REQUIRED = ("Purpose", "Inputs", "Workflow", "Outputs", "Checks", "Handoff", "Limits")
ALLOWED_STATES = {"candidate", "approved"}


def read_frontmatter(contents: str) -> dict[str, str]:
    lines = contents.splitlines()
    if len(lines) < 4 or lines[0].strip() != "---":
        raise ValueError("Missing skill frontmatter")
    try:
        end = lines.index("---", 1)
    except ValueError as e:
        raise ValueError("Unclosed skill frontmatter") from e
    result: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip():
            continue
        if ":" not in line:
            raise ValueError(f"Invalid field: {line!r}")
        key, val = line.split(":", 1)
        key = key.strip()
        if key in result:
            raise ValueError(f"Duplicate field: {key}")
        result[key] = val.strip()
    return result


def audit(root: pathlib.Path = ROOT) -> list[str]:
    errors: list[str] = []
    try:
        registry = json.loads((root / "state/agent_registry.json").read_text(encoding="utf-8"))
        manifest = json.loads((root / "skills/manifest.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        return [f"Cannot read registry/manifest: {e}"]
    roles = [r.get("id") for r in registry.get("roles", [])]
    records = manifest.get("skills", [])
    mids = [r.get("role_id") for r in records]
    if not isinstance(records, list) or manifest.get("schema_version") != "1.0":
        errors.append("Unsupported skill manifest schema")
        return errors
    if len(roles) != len(set(roles)) or len(mids) != len(set(mids)):
        errors.append("Duplicate role IDs in registry or manifest")
    if set(roles) != set(mids):
        errors.append(f"Skill coverage mismatch: missing={sorted(set(roles)-set(mids))}, extra={sorted(set(mids)-set(roles))}")
    for item in records:
        rid = item.get("role_id", "")
        if not re.fullmatch(r"[A-Z]{3}-\d{2}", rid):
            errors.append(f"Invalid role ID: {rid!r}")
            continue
        canonical = f"skills/{rid}/SKILL.md"
        if item.get("path") != canonical:
            errors.append(f"{rid}: skill path must be {canonical}")
            continue
        file_path = root / canonical
        if not file_path.is_file() or file_path.is_symlink():
            errors.append(f"{rid}: missing/unsafe skill file")
            continue
        content = file_path.read_text(encoding="utf-8")
        try:
            meta = read_frontmatter(content)
        except ValueError as e:
            errors.append(f"{rid}: {e}")
            continue
        for name in ("name", "description", "role_id", "version", "status"):
            if not meta.get(name):
                errors.append(f"{rid}: missing {name}")
        if meta.get("role_id") != rid or meta.get("status") != item.get("status"):
            errors.append(f"{rid}: frontmatter/manifest identity or status mismatch")
        if not re.fullmatch(r"\d+\.\d+\.\d+", meta.get("version", "")):
            errors.append(f"{rid}: version must be semver x.y.z")
        if item.get("status") not in ALLOWED_STATES:
            errors.append(f"{rid}: forbidden status; use candidate or approved")
        for heading in REQUIRED:
            if not re.search(r"^## " + re.escape(heading) + r"\s*$", content, flags=re.MULTILINE):
                errors.append(f"{rid}: missing section {heading}")
        if item.get("status") == "approved":
            if item.get("approved_by") != "QAD-01" or not item.get("approval_evidence"):
                errors.append(f"{rid}: approval missing independent QAD evidence")
            if item.get("evaluation_cases_passed", 0) < 5:
                errors.append(f"{rid}: independent five-case evaluation not passed")
    return errors


def main() -> int:
    errors = audit()
    if errors:
        for error in errors:
            print("FAIL", error, file=sys.stderr)
        return 1
    manifest = json.loads((ROOT / "skills/manifest.json").read_text(encoding="utf-8"))
    counts = {s: sum(k["status"] == s for k in manifest["skills"]) for s in ALLOWED_STATES}
    print(f"PASS: {len(manifest['skills'])} roles have valid skill packs; candidate={counts['candidate']} approved={counts['approved']} (no implicit LLM activation)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())