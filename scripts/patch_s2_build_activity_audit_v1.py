from pathlib import Path

TARGETS = [
    Path('index.html'),
    Path('.github/build-fantomons-inject.html'),
    Path('scripts/patch_meta_build_modes_v1.py'),
    Path('scripts/patch_guardian_tank_dps_toggle_v1.py'),
]
TOOLTIP_TARGETS = [
    Path('index.html'),
    Path('.github/build-fantomons-inject.html'),
    Path('scripts/patch_build_skill_tooltips_v1.py'),
]

OLD_GUARDIAN = "      role('Crucible / Conquest · DPS','Personal-damage Water score build',['Swirling Blade','Lunarwater Threads','Seismic Tide','Raging Maelstrom'],['Frigid Aura','Defensive Assault','Frigid Glint','Pursuit of Victory'],'Use the Water shell when Guardian itself is the damage slot: drop the safety charm for Pursuit of Victory and lean into repeated Cold/Water pressure. If your team has a much stronger carry, Tank mode’s support bar will usually produce the better team score.','On bosses where Raging Maelstrom loses value, test a high-rank Star Shattering Slash in that flex slot rather than forcing AoE.','Prydwen Water + score logic'),"
NEW_GUARDIAN = "      role('Crucible / Conquest · DPS','Single-target Guardian score build',['Swirling Blade','Lunarwater Threads','Seismic Tide','Star Shattering Slash'],['Frigid Aura','Defensive Assault','Frigid Glint','Pursuit of Victory'],'Keep the three Water Techniques to stack Cold and preserve the Water/Frigid package, but replace Raging Maelstrom’s broad AoE with Star Shattering Slash for the actual single-target payoff. This is the personal-DPS version; if a stronger carry is present, Tank mode’s support bar can still produce more team damage.','Star Shattering Slash is the Paladin/Guardian line’s heavy single-target nuke. If your copy is badly under-ranked versus Raging Maelstrom, dummy-test the two before forcing the swap.','Prydwen ST hybrid + Global testing'),"

OLD_DESTROYER = "      role('Arena','Wind control / solo tempo',['Tempest Sphere','Wind Blade Spiral',\"Wind's Delight\",'Howling Hurricane'],['Cyclone Lament','Repelling Wind',\"Wind's Shadow\",'Void Bubble'],'Mono-Wind gives the cleanest solo-PvP identity: movement pressure, Laceration, knockback/delay and enough repeated hits to keep pressure on one target.','Keep Void Bubble unless you massively outgear the opponent; fragile casters usually need the extra turn.','Guide + community PvP'),"
NEW_DESTROYER = "      role('Arena','Wind control / solo tempo',['Formation Breaker','Tempest Sphere','Wind Blade Spiral',\"Wind's Delight\"],['Cyclone Lament','Repelling Wind',\"Wind's Shadow\",'Void Bubble'],'Arena is one target, so drop Howling Hurricane’s huge AoE. Formation Breaker stays even here: current T4/future-tier guidance treats it as a core Technique, while the other three Wind skills provide compact player-sized pressure and Laceration tempo.','Keep Void Bubble unless you massively outgear the opponent; Repelling Wind is the anti-melee control flex.','Prydwen + Global PvP'),"

OLD_STAR = "    'Star Shattering Slash':I('Heavy direct-damage Technique used as a finisher in offensive Guardian shells.','Adds real kill pressure to Block/counter PvP builds.','Direct damage'),"
NEW_STAR = "    'Star Shattering Slash':I('Heavy direct-damage Technique inherited from Paladin; it starts as one of the Knight line’s strongest single-target nukes and scales hard with rank.','Use it for Crucible/Conquest and other concentrated targets; it also adds real kill pressure to Block/counter PvP builds.','Single target · Heavy hit'),"

OLD_FB = "    'Formation Breaker':I('Support-damage Technique that buffs from your own ATK and has a 50% chance to accelerate allied actions.','Mandatory in score/team builds because advancing a stronger carry can be worth more than your own hit.','Team acceleration · Support'),"
NEW_FB = "    'Formation Breaker':I('Core Destroyer Technique that buffs from your own ATK and has a 50% chance to accelerate allied actions.','Long-lived core even in Arena; in team content the ally action advance becomes especially valuable.','ATK buff · Action advance'),"


def replace_once_or_verified(text: str, old: str, new: str, label: str) -> tuple[str, bool]:
    if new in text:
        return text, False
    if old not in text:
        raise RuntimeError(f'{label}: expected old anchor not found')
    return text.replace(old, new, 1), True

changed = []
for path in TARGETS:
    text = path.read_text(encoding='utf-8')
    text, a = replace_once_or_verified(text, OLD_GUARDIAN, NEW_GUARDIAN, f'{path} Guardian ST')
    # Guardian toggle source does not contain Destroyer; only patch Destroyer where present.
    b = False
    if 'Destroyer:[' in text:
        text, b = replace_once_or_verified(text, OLD_DESTROYER, NEW_DESTROYER, f'{path} Destroyer Arena')
    if a or b:
        path.write_text(text, encoding='utf-8')
        changed.append(str(path))

for path in TOOLTIP_TARGETS:
    text = path.read_text(encoding='utf-8')
    text, a = replace_once_or_verified(text, OLD_STAR, NEW_STAR, f'{path} Star tooltip')
    text, b = replace_once_or_verified(text, OLD_FB, NEW_FB, f'{path} Formation tooltip')
    if a or b:
        path.write_text(text, encoding='utf-8')
        if str(path) not in changed:
            changed.append(str(path))

print('S2 activity audit corrections applied:', ', '.join(changed) if changed else 'already current')
