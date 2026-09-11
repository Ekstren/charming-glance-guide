#!/usr/bin/env python3
"""Snapshot structured Sword x Staff game data from public datamine-backed tools.

This importer intentionally DOES NOT mirror site UI/source/assets. It extracts only
structured data payloads and pure-data constants, removes presentation/editorial
fields and long prose strings, and writes normalized JSON under data/mined/.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

SKIP = object()

# Presentation/editorial/copyright-heavy prose fields are intentionally excluded.
DROP_KEYS = {
    "description", "desc", "tooltip", "tooltips", "flavor", "flavour", "lore",
    "story", "stories", "recommended", "recommendation", "recommendations",
    "guide", "guides", "note", "notes", "comment", "comments", "help",
    "html", "css", "style", "styles", "markup", "template", "templates",
    "image", "images", "icon", "icons", "portrait", "portraits", "art",
    "asset", "assets", "imageurl", "image_url", "iconurl", "icon_url",
    "thumbnail", "thumbnails", "screenshot", "screenshots",
}

# Data-bearing files on the public Pages repo. Generic discovery means future
# folders with the same conventions are picked up automatically.
DATA_FILENAMES = {"data.js", "combat-data.js", "fantomons.js", "server-data.js"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_head(repo: Path) -> str:
    return subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()


def scrub(value: Any, key: str | None = None) -> Any:
    """Keep factual structure/numbers/short labels; drop presentation/prose/assets."""
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
        # Preserve short game labels/names/codes. Do not bulk-copy long narrative text.
        if len(value) > 180:
            return SKIP
        return value
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return SKIP


def parse_window_assignment(text: str) -> tuple[str, Any] | None:
    """Parse files shaped like window.SOME_DATA = <JSON>; without executing code."""
    m = re.match(r"\s*(?:window\.)?([A-Za-z_$][\w$]*)\s*=\s*", text)
    if not m:
        return None
    rhs = text[m.end():].strip()
    if rhs.endswith(";"):
        rhs = rhs[:-1].rstrip()
    try:
        return m.group(1), json.loads(rhs)
    except json.JSONDecodeError:
        return None


def scan_const_expr(text: str, start: int) -> tuple[str, int] | None:
    """Return JS expression until a top-level semicolon, respecting strings/comments."""
    i = start
    n = len(text)
    par = brk = brc = 0
    quote: str | None = None
    escape = False
    line_comment = False
    block_comment = False
    while i < n:
        c = text[i]
        nxt = text[i + 1] if i + 1 < n else ""
        if line_comment:
            if c == "\n":
                line_comment = False
            i += 1
            continue
        if block_comment:
            if c == "*" and nxt == "/":
                block_comment = False
                i += 2
            else:
                i += 1
            continue
        if quote:
            if escape:
                escape = False
            elif c == "\\":
                escape = True
            elif c == quote:
                quote = None
            i += 1
            continue
        if c == "/" and nxt == "/":
            line_comment = True
            i += 2
            continue
        if c == "/" and nxt == "*":
            block_comment = True
            i += 2
            continue
        if c in ("'", '"', "`"):
            quote = c
            i += 1
            continue
        if c == "(": par += 1
        elif c == ")": par = max(0, par - 1)
        elif c == "[": brk += 1
        elif c == "]": brk = max(0, brk - 1)
        elif c == "{": brc += 1
        elif c == "}": brc = max(0, brc - 1)
        elif c == ";" and par == 0 and brk == 0 and brc == 0:
            return text[start:i].strip(), i + 1
        i += 1
    return None


def uppercase_const_defs(text: str) -> list[tuple[str, str]]:
    defs: list[tuple[str, str]] = []
    pat = re.compile(r"\bconst\s+([A-Z][A-Z0-9_]*)\s*=\s*")
    pos = 0
    while True:
        m = pat.search(text, pos)
        if not m:
            break
        scanned = scan_const_expr(text, m.end())
        if scanned:
            expr, end = scanned
            defs.append((m.group(1), expr))
            pos = end
        else:
            pos = m.end()
    return defs


def evaluate_defs(defs: list[tuple[str, str]]) -> tuple[dict[str, Any], list[str]]:
    if not defs:
        return {}, []
    with tempfile.TemporaryDirectory() as td:
        defs_path = Path(td) / "defs.json"
        defs_path.write_text(json.dumps(defs), encoding="utf-8")
        js = r'''
const fs=require('fs'), vm=require('vm');
const defs=JSON.parse(fs.readFileSync(process.argv[1],'utf8'));
const ctx=vm.createContext({console:{log(){},warn(){},error(){}},Math,JSON,Object,Array,Number,String,Boolean,BigInt,Date,Map,Set,parseInt,parseFloat,Infinity,NaN});
const out={}, failed=[];
for(const [name,expr] of defs){
  try{
    vm.runInContext(`globalThis[${JSON.stringify(name)}]=(${expr})`,ctx,{timeout:1500});
    const val=ctx[name];
    const encoded=JSON.stringify(val);
    if(encoded!==undefined){out[name]=JSON.parse(encoded)} else failed.push(name);
  }catch(e){failed.push(name)}
}
process.stdout.write(JSON.stringify({out,failed}));
'''
        proc = subprocess.run(
            ["node", "-e", js, str(defs_path)], text=True, capture_output=True, timeout=120
        )
        if proc.returncode != 0:
            return {}, [name for name, _ in defs]
        payload = json.loads(proc.stdout)
        return payload.get("out", {}), payload.get("failed", [])


def write_json(path: Path, value: Any, pretty: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if pretty:
        text = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    else:
        text = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n"
    path.write_text(text, encoding="utf-8")


def output_name_for(rel: Path) -> Path:
    # Preserve tool directory so origins remain obvious.
    stem = rel.name[:-3] if rel.name.endswith(".js") else rel.stem
    return rel.parent / f"{stem}.json"


def extract_assignment_payloads(upstream: Path, out_root: Path, manifest: dict[str, Any]) -> None:
    for path in sorted(upstream.glob("sxs-*/**/*.js")):
        if path.name not in DATA_FILENAMES:
            continue
        rel = path.relative_to(upstream)
        text = path.read_text(encoding="utf-8", errors="replace")
        parsed = parse_window_assignment(text)
        if not parsed:
            manifest["skipped"].append({"source": str(rel), "reason": "not a pure JSON assignment"})
            continue
        var_name, raw = parsed
        clean = scrub(raw)
        if clean is SKIP:
            manifest["skipped"].append({"source": str(rel), "reason": "empty after scrub"})
            continue
        dest = out_root / "0xnobody" / output_name_for(rel)
        # Large combat/companion tables stay compact to keep repo size reasonable.
        write_json(dest, clean, pretty=False)
        manifest["outputs"].append({
            "source": str(rel), "variable": var_name, "output": str(dest),
            "source_sha256": sha256(path), "output_bytes": dest.stat().st_size,
        })


def extract_pure_constants(repo: Path, out_root: Path, source_label: str, manifest: dict[str, Any]) -> None:
    roots = [p for p in repo.iterdir() if p.is_dir() and p.name.startswith("sxs-")]
    if source_label == "mystonats":
        roots = [repo]
    for root in roots:
        files = list(root.rglob("*.js")) + list(root.rglob("*.html"))
        for path in sorted(set(files)):
            # Pure assignment files are handled separately; avoid reprocessing huge payloads.
            if source_label == "0xnobody" and path.name in DATA_FILENAMES:
                continue
            if path.stat().st_size > 1_000_000:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            defs = uppercase_const_defs(text)
            if not defs:
                continue
            values, failed = evaluate_defs(defs)
            values = {k: scrub(v, k) for k, v in values.items()}
            values = {k: v for k, v in values.items() if v is not SKIP}
            if not values:
                continue
            rel = path.relative_to(repo)
            dest = out_root / source_label / "constants" / rel.with_suffix(".json")
            write_json(dest, values, pretty=False)
            manifest["outputs"].append({
                "source": str(rel), "output": str(dest), "constants": sorted(values),
                "unresolved_constants": failed, "source_sha256": sha256(path),
                "output_bytes": dest.stat().st_size,
            })


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--upstream", required=True, type=Path)
    ap.add_argument("--mystonats", required=False, type=Path)
    ap.add_argument("--output", default="data/mined", type=Path)
    args = ap.parse_args()

    if args.output.exists():
        shutil.rmtree(args.output)
    args.output.mkdir(parents=True, exist_ok=True)

    manifest: dict[str, Any] = {
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "scope": "Structured Sword x Staff game facts only; UI/code/assets and long prose excluded.",
        "sources": {
            "0xnobody": {
                "repo": "https://github.com/0xNobodyYT/0xNobodyYT.github.io",
                "commit": git_head(args.upstream),
            }
        },
        "outputs": [],
        "skipped": [],
    }
    if args.mystonats and args.mystonats.exists():
        manifest["sources"]["mystonats"] = {
            "repo": "https://github.com/Mystonats/sxs_skills",
            "commit": git_head(args.mystonats),
        }

    extract_assignment_payloads(args.upstream, args.output, manifest)
    extract_pure_constants(args.upstream, args.output, "0xnobody", manifest)
    if args.mystonats and args.mystonats.exists():
        extract_pure_constants(args.mystonats, args.output, "mystonats", manifest)

    # Manifest is intentionally human-readable.
    write_json(args.output / "manifest.json", manifest, pretty=True)
    readme = """# Mined SxS game-data snapshots\n\nThis directory contains normalized **game facts/data** extracted from public datamine-backed Sword x Staff tools. It is intentionally not a mirror of any third-party website. UI code, CSS, images/audio, editorial recommendations, and long prose/descriptions are excluded.\n\n`manifest.json` records the exact upstream commit(s), source paths, hashes, outputs, and any data-bearing files the importer could not normalize automatically.\n\nUse these snapshots as reference inputs for our own calculator/build logic. Future-season data should remain dormant until separately validated for the active Global season.\n"""
    (args.output / "README.md").write_text(readme, encoding="utf-8")

    print(f"Wrote {len(manifest['outputs'])} normalized datasets/constants files")
    if manifest["skipped"]:
        print(f"Skipped {len(manifest['skipped'])} candidate data files; see manifest.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
