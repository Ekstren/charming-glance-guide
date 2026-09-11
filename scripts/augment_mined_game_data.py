#!/usr/bin/env python3
"""Capture remaining small/public SxS game-data payloads missed by the main snapshotter.

Only structured game facts are retained. This does not mirror UI/source/assets.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

SKIP = object()
DROP_KEYS = {
    "description", "desc", "tooltip", "tooltips", "flavor", "flavour", "lore",
    "story", "stories", "recommended", "recommendation", "recommendations",
    "guide", "guides", "note", "notes", "comment", "comments", "help",
    "html", "css", "style", "styles", "markup", "template", "templates",
    "image", "images", "icon", "icons", "portrait", "portraits", "art",
    "asset", "assets", "imageurl", "image_url", "iconurl", "icon_url",
    "thumbnail", "thumbnails", "screenshot", "screenshots",
}

ASSIGNMENT_SOURCES = [
    ("sxs-loadout-builder/fantomons.js", "FANTOMON_CATALOG", "sxs-loadout-builder/fantomons.json"),
    ("sxs-primo-calculator/server-data.js", "SXS_SERVER_ROWS", "sxs-primo-calculator/server-data.json"),
    ("wardrobe-assets/catalog.js", "WARDROBE_DATA", "wardrobe-assets/catalog.json"),
]

# Standalone structured factual tables that are not wired through a window.X assignment.
JSON_SOURCES = [
    ("tools/skill-entity-links.json", "tools/skill-entity-links.json"),
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def scrub(value: Any, key: str | None = None) -> Any:
    kl = (key or "").lower()
    if kl in DROP_KEYS:
        return SKIP
    if isinstance(value, dict):
        out = {}
        for k, v in value.items():
            sv = scrub(v, str(k))
            if sv is not SKIP:
                out[str(k)] = sv
        return out
    if isinstance(value, list):
        out = []
        for v in value:
            sv = scrub(v, key)
            if sv is not SKIP:
                out.append(sv)
        return out
    if isinstance(value, str):
        return value if len(value) <= 180 else SKIP
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return SKIP


def strip_leading_comments(text: str) -> str:
    while True:
        newer = re.sub(r"^\s*(?://[^\n]*(?:\n|$)|/\*.*?\*/)", "", text, count=1, flags=re.S)
        if newer == text:
            return text.lstrip()
        text = newer


def parse_assignment(path: Path, expected: str) -> Any:
    text = strip_leading_comments(path.read_text(encoding="utf-8", errors="replace"))
    m = re.match(rf"(?:window\.)?{re.escape(expected)}\s*=\s*", text)
    if not m:
        raise ValueError(f"{path}: expected assignment to {expected}")
    rhs = text[m.end():].strip()
    if rhs.endswith(";"):
        rhs = rhs[:-1].rstrip()

    try:
        return json.loads(rhs)
    except json.JSONDecodeError:
        pass

    # Tiny hand-authored catalogs may use JS object-literal keys. Normalize only
    # that conservative syntax; do not execute arbitrary upstream JavaScript.
    normalized = re.sub(r"([\{,])\s*([A-Za-z_$][\w$]*)\s*:", r'\1"\2":', rhs)
    normalized = re.sub(r",\s*([}\]])", r"\1", normalized)
    try:
        return json.loads(normalized)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path}: unsupported non-data JavaScript literal") from exc


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n", encoding="utf-8")


def record_output(manifest: dict[str, Any], rel: str, dest: Path, src: Path, variable: str | None = None) -> None:
    manifest["skipped"] = [x for x in manifest.get("skipped", []) if x.get("source") != rel]
    manifest["outputs"] = [x for x in manifest.get("outputs", []) if x.get("source") != rel]
    row = {
        "source": rel,
        "output": str(dest),
        "source_sha256": sha256(src),
        "output_bytes": dest.stat().st_size,
    }
    if variable:
        row["variable"] = variable
    manifest["outputs"].append(row)
    print(f"captured {rel} -> {dest} ({dest.stat().st_size:,} bytes)")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--upstream", required=True, type=Path)
    ap.add_argument("--output", default="data/mined", type=Path)
    args = ap.parse_args()

    manifest_path = args.output / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    for rel, variable, out_rel in ASSIGNMENT_SOURCES:
        src = args.upstream / rel
        raw = parse_assignment(src, variable)
        clean = scrub(raw)
        if clean is SKIP:
            raise ValueError(f"{rel}: empty after scrub")
        dest = args.output / "0xnobody" / out_rel
        write_json(dest, clean)
        record_output(manifest, rel, dest, src, variable)

    for rel, out_rel in JSON_SOURCES:
        src = args.upstream / rel
        raw = json.loads(src.read_text(encoding="utf-8"))
        clean = scrub(raw)
        if clean is SKIP:
            raise ValueError(f"{rel}: empty after scrub")
        dest = args.output / "0xnobody" / out_rel
        write_json(dest, clean)
        record_output(manifest, rel, dest, src)

    manifest["outputs"] = sorted(manifest["outputs"], key=lambda x: (x.get("source", ""), x.get("output", "")))
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
