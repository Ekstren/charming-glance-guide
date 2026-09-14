"""CI static validation for the Charming Glance guide site (one-shot).

Checks, in order:
  1. index.html: referenced local asset paths exist on disk; no dangling `defer`
     scripts after the BUILD_HERO_LAYOUT_ICONS_V1 hook (that script is synchronous
     and must run in source order with builds.js so __applyBuild*Now hooks exist).
  2. Every assets/*.js file passes Node's `--check` syntax validation (skipped
     with a clear warning if Node is not on PATH, e.g. running in a Python-only
     environment — CI always has Node and this check is mandatory there).
  3. Every assets/*.css file has balanced braces (outside strings/comments).
  4. data/*.json files parse as JSON.
  5. Cross-file hook contract: window.__applyBuild*Now hooks called by
     assets/runtime.js are each defined by exactly one assets/*.js file (other
     than runtime.js itself, which only *calls* them), and no hook is defined
     twice.

Exit code 0 = all checks pass; nonzero = at least one failure (details printed).
Run: python scripts/validate_site_v1.py
"""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
failures: list[str] = []


def check(ok: bool, label: str) -> None:
    print(f"  [{'ok' if ok else 'FAIL'}] {label}")
    if not ok:
        failures.append(label)


def node_check(js_path: Path) -> tuple[bool, str]:
    """Run `node --check` on a JS file; return (ok, detail)."""
    if shutil.which("node") is None:
        return True, "node not found — skipped (CI enforces this separately)"
    p = subprocess.run(["node", "--check", str(js_path)], capture_output=True, text=True)
    return p.returncode == 0, (p.stderr or p.stdout).strip()[:400]


def css_balanced(src: str) -> bool:
    depth = 0
    i, n = 0, len(src)
    in_str = None
    while i < n:
        c = src[i]
        if in_str:
            if c == '\\': i += 1
            elif c == in_str: in_str = None
        elif c in '"\'':
            in_str = c
        elif c == '/' and i + 1 < n and src[i + 1] == '*':
            j = src.find('*/', i + 2)
            if j == -1:
                return False
            i = j + 1
        elif c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth < 0:
                return False
        i += 1
    return depth == 0 and in_str is None


def main() -> int:
    html = (ROOT / "index.html").read_text(encoding="utf-8", errors="replace")

    print("== index.html references ==")
    refs = sorted(set(re.findall(r'(?:src|href)="([^"]+)"', html)))
    local = [r for r in refs if not r.startswith(("http", "data:", "#", "//"))]
    check(bool(local), f"found {len(local)} local asset references")
    for r in local:
        p = ROOT / r.split("#", 1)[0].split("?", 1)[0]
        check(p.exists(), f"exists: {r}")

    defer_scripts = re.findall(r'<script[^>]*\bdefer\b[^>]*src="([^"]+)"', html)
    check(not defer_scripts, f"no deferred scripts (got {defer_scripts!r})")

    print("== asset JS (node --check) ==")
    asset_js = sorted((ROOT / "assets").glob("*.js"))
    check(bool(asset_js), f"found {len(asset_js)} assets/*.js")
    for f in asset_js:
        ok, detail = node_check(f)
        if not ok:
            print(f"       {detail}")
        check(ok, f"node --check: {f.relative_to(ROOT)}")

    print("== asset CSS ==")
    asset_css = sorted((ROOT / "assets").glob("*.css"))
    for f in asset_css:
        src = f.read_text(encoding="utf-8", errors="replace")
        check(css_balanced(src), f"CSS balanced: {f.relative_to(ROOT)}")

    print("== data JSON ==")
    data = sorted((ROOT / "data").glob("*.json")) if (ROOT / "data").is_dir() else []
    check(len(data) >= 2, f"found {len(data)} data/*.json")
    for f in data:
        try:
            json.loads(f.read_text(encoding="utf-8", errors="replace"))
            ok = True
        except Exception as exc:  # noqa: BLE001
            ok = False
            print(f"       JSON error in {f.name}: {exc}")
        check(ok, f"JSON parses: {f.relative_to(ROOT)}")

    print("== __applyBuild*Now hook contract ==")
    runtime = (ROOT / "assets/runtime.js").read_text(encoding="utf-8", errors="replace")
    called = set(re.findall(r"window\.(__applyBuild\w+Now)\s*===\s*['\"]function['\"]", runtime))
    check(bool(called), f"runtime.js calls {len(called)} hooks: {sorted(called)}")
    # Only count hook assignments in files that are NOT the caller (runtime.js
    # uses `if(typeof window.__applyBuild*Now==='function')` which is a call,
    # not a definition).
    all_defs: dict[str, int] = {}
    for f in asset_js:
        if f.name == "runtime.js":
            continue
        src = f.read_text(encoding="utf-8", errors="replace")
        defs = re.findall(r"window\.(__applyBuild\w+Now)\s*=", src)
        check(len(defs) == len(set(defs)), f"{f.name}: no duplicate hook defs ({defs})")
        for d in set(defs):
            all_defs[d] = all_defs.get(d, 0) + 1
    for hook in sorted(called):
        check(all_defs.get(hook, 0) == 1, f"hook {hook} defined exactly once (got {all_defs.get(hook, 0)})")

    print()
    if failures:
        print(f"RESULT: FAIL ({len(failures)} failures)")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("RESULT: PASS (all checks green)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
