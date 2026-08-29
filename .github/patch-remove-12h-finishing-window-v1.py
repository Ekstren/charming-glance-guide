from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
original = s

repls = {
'''          <label><input id="grace12" checked type="checkbox"> Keep a 12-hour finishing window</label>\n''': '',
'''  const CHECK_IDS = ['holdExp','grace12','reserveS2Essence','reserveS2Sand','reserveS2Treats'];''': '''  const CHECK_IDS = ['holdExp','reserveS2Essence','reserveS2Sand','reserveS2Treats'];''',
'''    const cutoff=cfg.end.getTime()-($('grace12')?.checked?12*3_600_000:0);''': '''    const cutoff=cfg.end.getTime();''',
'''    return Math.max(Date.now(),cfg.end.getTime()-($('grace12')?.checked?12*3_600_000:0));''': '''    return Math.max(Date.now(),cfg.end.getTime());''',
'''    const realmCutoffMs=cfg.end.getTime()-($('grace12')?.checked?12*3_600_000:0);''': '''    const realmCutoffMs=cfg.end.getTime();''',
'''    return cfg.end.getTime()-($('grace12')?.checked?12*3_600_000:0);''': '''    return cfg.end.getTime();''',
'''    const cutoff=cfg.end.getTime()-($('grace12').checked?12*3_600_000:0);''': '''    const cutoff=cfg.end.getTime();''',
'''    const graceHours=$('grace12').checked?12:0;\n    $('graceText').textContent=`Effective Cart/Stamina production: ${resources.cartHours.toFixed(1)}h (${resources.wallResourceHours.toFixed(1)} wall hours + ${resources.boostResets} reset boost${resources.boostResets===1?'':'s'}). Cutoff is ${graceHours}h before ${cfg.name} end.`;''': '''    $('graceText').textContent=`Effective Cart/Stamina production: ${resources.cartHours.toFixed(1)}h (${resources.wallResourceHours.toFixed(1)} wall hours + ${resources.boostResets} reset boost${resources.boostResets===1?'':'s'}). Runs through the ${cfg.name} reset.`;''',
'''      if($('grace12').checked) brief.push('final 12h excluded');\n''': '',
'''      $('holdExp').checked=true; $('grace12').checked=true; $('reserveS2Essence').checked=true; $('reserveS2Sand').checked=true; $('reserveS2Treats').checked=true;''': '''      $('holdExp').checked=true; $('reserveS2Essence').checked=true; $('reserveS2Sand').checked=true; $('reserveS2Treats').checked=true;''',
'''    // The optional 12h finishing window is a real planning cutoff: score still receives final Character EXP,\n    // but upgrades unlocked only after that cutoff are not treated as safely available.\n''': '''    // Upgrade availability now runs through the actual season reset; there is no separate finishing cutoff.\n''',
'''    const graceText=$('grace12').checked?' Final 12-hour Cart income and Stamina regen are excluded.':'';\n    const capText=cfg.key==='s1'?` S1 safe-upgrade cap uses projected Lv.${p.upgradeCapLevel??p.level}${$('grace12').checked?` at the 12h finishing cutoff (final Character projects Lv.${p.level})`:''}: Skills ${projectedCaps.skill}, Fantomons ${projectedCaps.fanto} (next 10-level band), Relics +${projectedCaps.relic}; Gear is not Character-level capped.`:''': '''    const capText=cfg.key==='s1'?` S1 safe-upgrade cap uses projected Lv.${p.upgradeCapLevel??p.level} at season reset: Skills ${projectedCaps.skill}, Fantomons ${projectedCaps.fanto} (next 10-level band), Relics +${projectedCaps.relic}; Gear is not Character-level capped.`:''',
'''<small class="seasonPlanningNote" id="graceText">Cart income and projected Stamina generation stop 12 hours before season end.</small>''': '''<small class="seasonPlanningNote" id="graceText">Cart income, Stamina generation, Realm purchase availability, and upgrade timing run through the season reset.</small>''',
'''When the 12-hour finishing window is enabled, newly unlocked Skill/Relic/Fantomon caps must be available by that cutoff; final Character EXP can still add score afterward.''': '''Skill, Relic and Fantomon upgrade availability is evaluated through the actual season reset, with no separate finishing cutoff.'''
}

for old, new in repls.items():
    if old in s:
        s = s.replace(old, new)

# Remove any duplicated legacy summary clauses left by earlier patches.
s = s.replace("      if($('grace12').checked) brief.push('final 12h excluded');\n", '')

if 'grace12' in s:
    raise SystemExit('grace12 reference still present')
if '12-hour finishing window' in s or 'final 12h excluded' in s or '12h finishing cutoff' in s:
    raise SystemExit('legacy finishing-window wording still present')
if s == original:
    raise SystemExit('no changes made')

p.write_text(s, encoding='utf-8')
print('Removed 12-hour finishing window; resource and upgrade projections now run through reset.')
