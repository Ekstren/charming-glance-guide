"""Minify assets/*.js with esbuild (transform-only, no bundling).
Backs up originals first, verifies syntax, reports size savings."""
import os, shutil, subprocess, sys

base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
assets = os.path.join(base, 'assets')
backup = r"C:\Users\ekstren\Documents\Local AI Projects\GUI Projects\_js_backup_20260913"
node_dir = r"C:\Users\ekstren\Documents\Local AI Projects\GUI Projects\node\node-v24.21.0-win-x64"
env = dict(os.environ, PATH=node_dir + os.pathsep + os.environ.get('PATH', ''))

os.makedirs(backup, exist_ok=True)
files = sorted(f for f in os.listdir(assets) if f.endswith('.js'))
total_before = total_after = 0
failures = []

for f in files:
    path = os.path.join(assets, f)
    orig = os.path.join(backup, f)
    if not os.path.exists(orig):
        shutil.copy2(path, orig)
    before = os.path.getsize(path)
    tmp = path + '.tmpmin.js'
    esbuild_exe = os.path.join(base, 'node_modules', '@esbuild', 'win32-x64', 'esbuild.exe')
    r = subprocess.run(
        [esbuild_exe, path, '--minify', '--target=es2017', '--charset=utf8', '--outfile=' + tmp],
        cwd=base, env=env, capture_output=True, text=True)
    if r.returncode != 0:
        failures.append((f, r.stderr))
        print(f'  [FAIL] {f}: {r.stderr[:300]}')
        continue
    # syntax check minified
    chk = subprocess.run([os.path.join(node_dir, 'node.exe'), '--check', tmp], env=env, capture_output=True, text=True)
    if chk.returncode != 0:
        failures.append((f, 'node --check failed: ' + chk.stderr[:300]))
        print(f'  [FAIL] {f} failed node --check')
        continue
    os.replace(tmp, path)
    after = os.path.getsize(path)
    total_before += before
    total_after += after
    print(f'  {f:30s} {before/1024:8.1f} KB -> {after/1024:8.1f} KB  (saved {(before-after)/1024:.1f} KB, {(1-after/before)*100:.0f}%)')

print()
print(f'TOTAL JS: {total_before/1024:.1f} KB -> {total_after/1024:.1f} KB (saved {(total_before-total_after)/1024:.1f} KB)')
if failures:
    print('FAILURES:', failures)
    sys.exit(1)
print('All minified OK. Backups in', backup)
