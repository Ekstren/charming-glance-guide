"""CI static validation for the Charming Glance guide site (one-shot).

Checks, in order:
  1. index.html: referenced local asset paths exist on disk; no dangling `defer`
     scripts (the shell captures document.currentScript for versioned chunk URLs).
  2. Every assets/*.js file passes Node's `--check` syntax validation (skipped
     with a clear warning if Node is not on PATH, e.g. running in a Python-only
     environment — CI always has Node and this check is mandatory there).
  3. Every assets/*.css file has balanced braces (outside strings/comments).
  4. data/*.json files parse as JSON.
  5. T5 source-build renderer contract: src/builds.mjs exports the section
     initializer and renders the four current classes from linked source guides;
     its generated bundle contains no removed build augmentation hooks.

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

    print("== Season 3 / T5 source-build renderer contract ==")
    builds_source = (ROOT / "src/builds.mjs").read_text(encoding="utf-8", errors="replace")
    expected_classes = ["Magister", "Prophet", "Ravager", "Templar"]
    source_match = re.search(r"const T5_SOURCE_BUILDS=(\{[\s\S]*?\n\});", builds_source)
    current_builds = {}
    if source_match:
        try:
            current_builds = json.loads(source_match.group(1))
        except json.JSONDecodeError as exc:
            print(f"       T5 source data is not valid JSON: {exc}")
    source_classes = list(current_builds)
    check(source_classes == expected_classes, f"builds.mjs defines current T5 classes in order ({source_classes})")
    expected_counts = {"Magister": 4, "Prophet": 4, "Ravager": 3, "Templar": 4}
    for cls, count in expected_counts.items():
        entry = current_builds.get(cls, {})
        check(len(entry.get("builds", [])) == count, f"{cls}: {count} published presets")
        check(entry.get("url") == f"https://www.prydwen.gg/sword-x-staff/guides/build-guide-{cls.lower()}", f"{cls}: current author-published source")
    check("export function initialize()" in builds_source, "builds.mjs exports the lazy-section initializer")
    check("Current T5 loadouts from published guides" in builds_source, "builds.mjs labels the source-published T5 presets")
    check("sourceBuildCard" in builds_source and "buildSourceLink" in builds_source, "builds.mjs renders linked source cards")
    check("gearAdvicePanel" in builds_source and "fantomonAdvicePanel" in builds_source, "builds.mjs retains gear and Fantomon guidance")
    check("communityBuildCard" in builds_source and "More source notes" in builds_source, "builds.mjs separates community presets from partial source notes")
    check("legacyBuildArchive" in builds_source and "legacyBuildCard" in builds_source and "T4_SOURCE_BUILDS" in builds_source, "builds.mjs preserves previous-tier presets in a labeled archive")
    check("metaBuildTabs" not in builds_source and "data-meta-mode" not in builds_source, "builds.mjs does not invent activity selector mappings")
    check("__applyBuild" not in builds_source, "builds.mjs does not depend on removed augmentation hooks")
    generated_builds = (ROOT / "assets/builds-section.js").read_text(encoding="utf-8", errors="replace")
    check("sourceBuildCard" in generated_builds and "buildSourceLink" in generated_builds, "generated Builds bundle includes linked source cards")
    check("__applyBuild" not in generated_builds, "generated Builds bundle contains no removed augmentation hooks")

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
