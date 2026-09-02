from pathlib import Path

files = {
    Path('index.html'): [],
    Path('.github/build-fantomons-inject.html'): [],
}

# Current Guardian investment priorities were too conservative and under-ranked
# the two T4 skills most consistently called out by current Guardian players.
old_tech = '''<div class="priorityPanel"><div class="priorityIntro"><span>Technique investment</span><strong>Build slots first</strong><p>These priorities now follow the techniques actually equipped in the Guardian builds below. Hamper Strike remains a useful taunt swap, but is no longer ranked as if it were a default slot.</p></div><ol class="priorityList"><li><b>1</b><div><strong>Valor Surge</strong><p>Equipped in both the dungeon and Dragon/Chaos support builds for party damage and cleanse utility.</p></div></li><li><b>2</b><div><strong>Heart of Challenge</strong><p>The core group-taunt slot in the default dungeon tank build.</p></div></li><li><b>3</b><div><strong>Luminous Shield</strong><p>Equipped in both the dungeon tank and reflect/solo builds and directly supports the Guardian survival loop.</p></div></li><li><b>4</b><div><strong>Lunarwater Threads</strong><p>Used in both Water/AoE and Dragon/Chaos support; the most reusable offensive/control slot across those variants.</p></div></li></ol></div>'''
new_tech = '''<div class="priorityPanel"><div class="priorityIntro"><span>Technique investment</span><strong>Swirling Blade first</strong><p>Current S2 Guardian testing consistently elevates Swirling Blade as the best T4 Technique investment because it works in the Water shell, shield builds and general PvE while still giving a shield.</p></div><ol class="priorityList"><li><b>1</b><div><strong>Swirling Blade</strong><p>The most reusable T4 damage Technique: strong single-target damage, Water synergy and a self-shield. It is also the first offensive flex into the dungeon tank bar.</p></div></li><li><b>2</b><div><strong>Valor Surge</strong><p>Long-lived party damage and cleanse utility; equipped in dungeon and Dragon/Chaos support.</p></div></li><li><b>3</b><div><strong>Heart of Challenge</strong><p>The core group-taunt slot in the default dungeon tank build.</p></div></li><li><b>4</b><div><strong>Luminous Shield</strong><p>Still central to the dungeon and reflect shells, though high-Block accounts can flex it more aggressively later.</p></div></li></ol></div>'''

old_charm = '''<div class="priorityPanel"><div class="priorityIntro"><span>Charm investment</span><strong>Iron Will is the keeper</strong><p>Community long-term rankings line up with the T4 guide: Iron Will and Holy Aegis age extremely well. Soul Protection is especially strong right now.</p></div><ol class="priorityList"><li><b>1</b><div><strong>Iron Will</strong><p>Damage reduction from taunted enemies; one of the strongest long-lasting Guardian investments.</p></div></li><li><b>2</b><div><strong>Holy Aegis</strong><p>More DEF and stronger DEF-scaling shields—directly reinforces the class core.</p></div></li><li><b>3</b><div><strong>Soul Protection</strong><p>Huge opening shield and excellent dungeon value; particularly strong during T4 progression.</p></div></li><li><b>4</b><div><strong>Oath of Vigil</strong><p>Excellent group/PvP protection. Get at least one copy; it is useful even without forcing heavy rank investment.</p></div></li></ol></div>'''
new_charm = '''<div class="priorityPanel"><div class="priorityIntro"><span>Charm investment</span><strong>Soul Protection first</strong><p>Fresh S2 Guardian feedback is unusually consistent here: Soul Protection is the standout T4 Charm and remains useful across dungeons, Arena and Nexus-style team PvP.</p></div><ol class="priorityList"><li><b>1</b><div><strong>Soul Protection</strong><p>The best T4 Guardian investment: a massive opening shield that scales the whole shield/DEF loop and works in essentially every mode.</p></div></li><li><b>2</b><div><strong>Holy Aegis</strong><p>Universal DEF plus stronger DEF-based shields; excellent wherever Guardian is actually tanking.</p></div></li><li><b>3</b><div><strong>Iron Will</strong><p>Excellent damage reduction once Taunt is active, especially in dungeon and team-PvP tank bars.</p></div></li><li><b>4</b><div><strong>Oath of Vigil</strong><p>High-value group/PvP protection. One copy is already useful, so it ranks below the more universal personal-core investments.</p></div></li></ol></div>'''

p = Path('index.html')
s = p.read_text(encoding='utf-8')
for old, new, label in [
    (old_tech, new_tech, 'Guardian technique investment'),
    (old_charm, new_charm, 'Guardian charm investment'),
]:
    if old in s:
        s = s.replace(old, new, 1)
    elif new not in s:
        raise SystemExit(f'expected {label} block not found')
s = s.replace('Research snapshot Aug 21, 2026 · <a href="https://www.prydwen.gg/sword-x-staff/guides/build-guide-guardian"', 'Research snapshot Sep 2, 2026 · <a href="https://www.prydwen.gg/sword-x-staff/guides/build-guide-guardian"', 1)
p.write_text(s, encoding='utf-8')

# Keep the enhanced Arena card aligned with the same conclusion without forcing
# Soul Protection on low-Block accounts that still need Block Awareness.
p = Path('.github/build-fantomons-inject.html')
s = p.read_text(encoding='utf-8')
old = "'If Pandarial and your ranks support it, Luminous Shield → Light Sword Array is the aggressive flex; keep Block stats high.'"
new = "'If your sheet Block is already comfortably high, Block Awareness → Soul Protection is the stronger universal survival flex. If Pandarial and your ranks support it, Luminous Shield → Light Sword Array is the aggressive Technique flex.'"
if old in s:
    s = s.replace(old, new, 1)
elif new not in s:
    raise SystemExit('expected Guardian Arena flex note not found')
p.write_text(s, encoding='utf-8')

print('Applied Sep 2 Guardian build pass')
