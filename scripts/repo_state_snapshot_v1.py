"""Snapshot the working-tree repo state (one-shot local diagnostics).

Writes _state_snapshot.txt in the repo root covering:
- .gitignore contents
- staged index.html diff
- site-ci.yml staged diff
- full cached diff stat

Run: python scripts/repo_state_snapshot_v1.py
"""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
out = []

def run(*args):
    p = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    return p.stdout

out.append("===== .gitignore =====")
out.append((ROOT / ".gitignore").read_text(encoding="utf-8", errors="replace"))
out.append("===== git diff --cached -- index.html =====")
out.append(run("diff", "--cached", "--", "index.html"))
out.append("===== git diff --cached -- .github/workflows/site-ci.yml =====")
out.append(run("diff", "--cached", "--", ".github/workflows/site-ci.yml"))
out.append("===== git diff --cached --stat =====")
out.append(run("diff", "--cached", "--stat"))
out.append("===== git status --short =====")
out.append(run("status", "--short"))

(ROOT / "_state_snapshot.txt").write_text("\n".join(out), encoding="utf-8")
print(f"wrote {ROOT / '_state_snapshot.txt'}")
