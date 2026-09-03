from pathlib import Path

paths = [Path('index.html'), Path('.github/build-fantomons-inject.html')]

replacements = {
"role('Tournament · 2v2 · Tank','Duo frontline: protect one carry and still threaten',['Hamper Strike','Heart of Challenge','Luminous Shield','Desperate Protection'],['Iron Will','Rebound','Iron Fortress','Oath of Vigil'],'Hamper Strike + Heart of Challenge control targeting while Luminous Shield and Desperate Protection protect the frontline.','Oath of Vigil protects your partner; Iron Fortress and Iron Will absorb team pressure. Rebound → Soul Protection if you are being focused too hard.','Current PvP')":
"role('Tournament · 2v2 · Tank','Duo frontline: protect one carry and still threaten',['Valor Surge','Hamper Strike','Luminous Shield','Desperate Protection'],['Iron Will','Rebound','Iron Fortress','Oath of Vigil'],'Valor Surge buffs and cleanses the duo, Hamper Strike provides repeatable Taunt, and Luminous Shield + Desperate Protection absorb focus pressure.','Oath of Vigil protects your partner; Iron Fortress and Iron Will absorb team pressure. Rebound → Soul Protection if you are being focused too hard.','Current PvP')",
"role('Tournament · 4v4 · Tank','Full-team tank: Taunt + ally protection',['Hamper Strike','Heart of Challenge','Luminous Shield','Desperate Protection'],['Iron Will','Soul Protection','Iron Fortress','Oath of Vigil'],'Hamper Strike + Heart of Challenge provide reliable Taunt, with Luminous Shield and Desperate Protection covering coordinated burst.','Iron Will, Soul Protection, Iron Fortress, and Oath of Vigil maximize team protection and keep the lowest-HP ally safer.','Prydwen + Global PvP')":
"role('Tournament · 4v4 · Tank','Full-team tank: Taunt + ally protection',['Valor Surge','Heart of Challenge','Luminous Shield','Desperate Protection'],['Iron Will','Soul Protection','Iron Fortress','Oath of Vigil'],'Valor Surge buffs and cleanses the team, Heart of Challenge provides broad Taunt, and Luminous Shield + Desperate Protection cover coordinated burst.','Iron Will, Soul Protection, Iron Fortress, and Oath of Vigil maximize team protection and keep the lowest-HP ally safer.','Prydwen + Global PvP')",
}

for path in paths:
    text = path.read_text(encoding='utf-8')
    for old, new in replacements.items():
        count = text.count(old)
        if count != 1:
            raise SystemExit(f'{path}: expected exactly one match, found {count}: {old[:90]}')
        text = text.replace(old, new)
    path.write_text(text, encoding='utf-8')

print('updated Guardian Tournament Tank Valor Surge loadouts')
