from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
needle="    const planStars=historical+cfg.starBase+Math.floor(plan.score/cfg.scorePerStar);\n"
count=s.count(needle)
if count>1:
    first=s.find(needle)
    second=s.find(needle,first+len(needle))
    s=s[:second]+s[second+len(needle):]
    p.write_text(s,encoding='utf-8')
    print('Removed duplicate Smart Balance planStars declaration.')
elif count==1:
    print('Smart Balance planStars declaration already singular.')
else:
    raise SystemExit('Smart Balance planStars declaration missing')
