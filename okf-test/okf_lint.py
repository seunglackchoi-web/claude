#!/usr/bin/env python3
"""A minimal OKF consumer: conformance check + practical lint + schema-drift detector.

Implements the v0.1 spec's THREE hard conformance rules, then layers on the
"soft" checks the spec explicitly says a consumer MUST NOT reject on — because
those are exactly the things that bite you in production.
"""
import json, re, sys
from pathlib import Path

BUNDLE = Path(__file__).parent / "bundle"
RESERVED = {"index.md", "log.md"}
RECOMMENDED = ["title", "description", "resource", "tags", "timestamp"]

def parse_frontmatter(text):
    """Return (frontmatter_dict_or_None, parse_ok). Tiny YAML-ish parser."""
    if not text.startswith("---"):
        return None, True  # no frontmatter block at all
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        return None, False  # opened a block but never closed it -> unparseable
    fm = {}
    for line in m.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            return None, False
        k, v = line.split(":", 1)
        v = v.strip()
        if v.startswith("[") and v.endswith("]"):
            v = [x.strip() for x in v[1:-1].split(",") if x.strip()]
        fm[k.strip()] = v
    return fm, True

def all_md():
    return sorted(BUNDLE.rglob("*.md"))

def rel(p):
    return "/" + str(p.relative_to(BUNDLE))

# ---- 1. Hard conformance (the only things that make a bundle non-conformant) ----
def conformance():
    errors = []
    for p in all_md():
        text = p.read_text()
        fm, ok = parse_frontmatter(text)
        if p.name in RESERVED:
            if fm is not None:
                errors.append(f"[CONFORMANCE] {rel(p)}: reserved file must NOT have frontmatter")
            continue
        if not ok:
            errors.append(f"[CONFORMANCE] {rel(p)}: unparseable frontmatter")
        elif fm is None:
            errors.append(f"[CONFORMANCE] {rel(p)}: missing required frontmatter block")
        elif not fm.get("type"):
            errors.append(f"[CONFORMANCE] {rel(p)}: missing required non-empty `type`")
    return errors

# ---- 2. Soft lint (spec says consumers MUST NOT reject on these) ----
LINK_RE = re.compile(r"\]\((/[^)]+\.md)\)")

def lint():
    warns = []
    existing = {rel(p) for p in all_md()}
    for p in all_md():
        text = p.read_text()
        fm, ok = parse_frontmatter(text)
        # broken bundle-relative links
        for target in LINK_RE.findall(text):
            if target not in existing:
                warns.append(f"[BROKEN LINK] {rel(p)} -> {target} (target not in bundle)")
        if p.name in RESERVED or not fm:
            continue
        for field in RECOMMENDED:
            if field not in fm:
                warns.append(f"[MISSING FIELD] {rel(p)}: no `{field}`")
    return warns

# ---- 3. Drift: documented schema vs live warehouse ----
SCHEMA_ROW = re.compile(r"^\|\s*([A-Za-z_][A-Za-z0-9_]*)\s*\|\s*([A-Z0-9_]+)\s*\|")

def documented_schema(text):
    cols = {}
    for line in text.splitlines():
        m = SCHEMA_ROW.match(line)
        if m and m.group(1).lower() not in ("column",):
            cols[m.group(1)] = m.group(2)
    return cols

def drift():
    live = json.loads((Path(__file__).parent / "live_schema.json").read_text())
    out = []
    for p in all_md():
        text = p.read_text()
        fm, _ = parse_frontmatter(text)
        if not fm or fm.get("type") != "BigQuery Table":
            continue
        res = fm.get("resource", "")
        qp = re.search(r"p=(\w+)&d=(\w+)&t=(\w+)", res)
        if not qp:
            continue
        key = f"{qp.group(1)}.{qp.group(2)}.{qp.group(3)}"
        if key not in live:
            out.append(f"[DRIFT] {rel(p)}: table {key} not found live")
            continue
        doc = documented_schema(text)
        livecols = live[key]
        for c, t in doc.items():
            if c not in livecols:
                out.append(f"[DRIFT] {rel(p)}: documents `{c}` but it no longer exists live")
            elif livecols[c] != t:
                out.append(f"[DRIFT] {rel(p)}: `{c}` doc={t} live={livecols[c]} (type changed)")
        for c in livecols:
            if c not in doc:
                out.append(f"[DRIFT] {rel(p)}: live column `{c}` is UNDOCUMENTED")
    return out

if __name__ == "__main__":
    conf = conformance()
    print("=== 1. HARD CONFORMANCE (spec's only reject criteria) ===")
    print("  PASS — conformant bundle" if not conf else "\n".join("  " + e for e in conf))
    print("\n=== 2. SOFT LINT (spec says: do NOT reject, but you care in prod) ===")
    print("\n".join("  " + w for w in lint()) or "  clean")
    print("\n=== 3. SCHEMA DRIFT (doc vs live warehouse — format has no opinion here) ===")
    print("\n".join("  " + d for d in drift()) or "  no drift")
    sys.exit(1 if conf else 0)
