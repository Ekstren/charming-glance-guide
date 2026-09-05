from pathlib import Path

SITE = Path("index.html")
text = SITE.read_text(encoding="utf-8")
original = text

old_role = "role('Tournament · 4v4 · Tank','Full-team tank: Taunt + ally protection',['Valor Surge','Heart of Challenge','Luminous Shield','Desperate Protection'],['Iron Will','Soul Protection','Iron Fortress','Oath of Vigil'],'Valor Surge buffs and cleanses the team, Heart of Challenge provides broad Taunt, and Luminous Shield + Desperate Protection cover coordinated burst.','Iron Will, Soul Protection, Iron Fortress, and Oath of Vigil maximize team protection and keep the lowest-HP ally safer.','Prydwen + Global PvP')"
new_role = "role('Tournament · 4v4 · Tank','Full-team control tank: pull + Taunt + self-survival',['Valor Surge','Heart of Challenge','Lunarwater Threads','Luminous Shield'],['Iron Will','Soul Protection','Iron Fortress','Oath of Vigil'],'Valor Surge buffs and cleanses the team, Lunarwater Threads pulls enemies into your control zone, Heart of Challenge applies broad Taunt, and Luminous Shield helps the Guardian survive the resulting focus fire.','This is the default organized 4v4 control bar. Desperate Protection is an ally-protection fallback when Taunt/control is unreliable; when the control package is working, keeping the Guardian alive is the higher-value fourth-slot job.','Current Global PvP control tank')"

if new_role not in text:
    if old_role not in text:
        raise SystemExit("Guardian 4v4 tank role anchor not found")
    text = text.replace(old_role, new_role)

old_swap = """    'Tournament · 4v4 · Tank|Valor Surge|Heart of Challenge|Luminous Shield|Desperate Protection':[
      ['Need repeatable Taunt','Heart of Challenge','Hamper Strike']
    ],"""
new_swap = """    'Tournament · 4v4 · Tank|Valor Surge|Heart of Challenge|Lunarwater Threads|Luminous Shield':[
      ['Taunt/control is unreliable','Lunarwater Threads','Desperate Protection'],
      ['Need repeatable Taunt','Heart of Challenge','Hamper Strike']
    ],"""

if new_swap not in text:
    if old_swap not in text:
        raise SystemExit("Guardian 4v4 technique swap anchor not found")
    text = text.replace(old_swap, new_swap)

old_threads = "'Lunarwater Threads':I('Water pressure and Cold-setup Technique used in offensive and support builds.','Helps accelerate the Water/Cold loop and remains useful in boss support.','Water · Cold setup')"
new_threads = "'Lunarwater Threads':I('Wide Water control Technique that pulls enemies together while contributing Cold setup and pressure.','Premium organized-4v4 control: group enemies into the Guardian’s zone, then pair it with Heart of Challenge so Taunt funnels pressure into the tank.','Water · Pull · Control · Cold setup')"
if new_threads not in text:
    if old_threads not in text:
        raise SystemExit("Lunarwater Threads tooltip anchor not found")
    text = text.replace(old_threads, new_threads)

old_desperate = "'Desperate Protection':I('Emergency defensive Technique used to keep the Guardian standing through dangerous damage windows.','Tank default; replace it with damage only when the group is already safe.','Defense')"
new_desperate = "'Desperate Protection':I('Emergency ally-protection Technique for covering a vulnerable teammate when aggro or control breaks down.','Strong in 2v2 and as a 4v4 fallback, but not the default organized 4v4 slot when Lunarwater Threads + Heart of Challenge are reliably funneling damage into the Guardian.','Ally protection · Emergency defense')"
if new_desperate not in text:
    if old_desperate not in text:
        raise SystemExit("Desperate Protection tooltip anchor not found")
    text = text.replace(old_desperate, new_desperate)

if text == original:
    print("Guardian 4v4 control-tank changes are already applied.")
else:
    SITE.write_text(text, encoding="utf-8")
    print("Applied Guardian 4v4 Lunarwater Threads control-tank changes.")
