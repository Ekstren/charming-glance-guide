from pathlib import Path

p = Path('.github/patch-optimizer-system-audit-v4.py')
t = p.read_text(encoding='utf-8')
old = """def sub_once(pattern, repl, label, flags=re.S):
    global s
    ns, count = re.subn(pattern, lambda m: repl, s, count=1, flags=flags)
    if count != 1:
        raise SystemExit(f'expected one match for {label}, got {count}')
    s = ns
"""
new = """def sub_once(pattern, repl, label, flags=re.S):
    global s
    ns, count = re.subn(pattern, lambda m: repl, s, count=1, flags=flags)
    if count != 1 and label == 'acquisition hot path':
        start = s.find('  function acquisitionEffortFor(costs,resources,cfg=activeCalcConfig()){')
        header = '  function makePlanCandidate(go,so,ro,fo,score,desired,resources,realms){'
        end = s.find(header, start + 1)
        if start >= 0 and end >= 0:
            ns = s[:start] + repl + s[end + len(header):]
            count = 1
    if count != 1:
        raise SystemExit(f'expected one match for {label}, got {count}')
    s = ns
"""
if old not in t:
    raise SystemExit('sub_once helper anchor not found')
p.write_text(t.replace(old, new, 1), encoding='utf-8')
print('optimizer audit acquisition anchor shim applied')
