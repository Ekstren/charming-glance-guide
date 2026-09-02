from pathlib import Path

paths=[Path('index.html'),Path('.github/build-fantomons-inject.html')]

old_arena="""      role('Arena','Solo block / reflect wall',['Luminous Shield','Forceful Charge','Star Shattering Slash','Desperate Protection'],['Rebound','Holy Aegis','Block Mastery','Block Awareness'],'Solo Arena does not benefit from ally-protection charms, so stay self-focused: Block, shields, Rebound and enough threat to punish attackers.','If your sheet Block is already comfortably high, Block Awareness → Soul Protection is the stronger universal survival flex. If Pandarial and your ranks support it, Luminous Shield → Light Sword Array is the aggressive Technique flex.','Guide-derived Arena'),"""
new_arena="""      role('Arena','Solo block / reflect wall',['Luminous Shield','Forceful Charge','Star Shattering Slash','Desperate Protection'],['Rebound','Holy Aegis','Block Mastery','Soul Protection'],'Solo Arena does not benefit from ally-protection charms, so stay self-focused: Block, shields, Rebound and enough threat to punish attackers.','Soul Protection is the default fourth charm. If your natural Block is still low, Soul Protection → Block Awareness. If Pandarial and your ranks support it, Luminous Shield → Light Sword Array is the aggressive Technique flex.','Guide-derived Arena'),"""

old_tournament="""      role('Tournament','Taunt / ally protection',['Hamper Strike','Heart of Challenge','Luminous Shield','Desperate Protection'],['Iron Will','Holy Aegis','Iron Fortress','Oath of Vigil'],'This is where Oath of Vigil belongs: Hamper Strike and Heart of Challenge control targeting while Oath protects the ally most likely to be bursted.','Iron Fortress and Oath of Vigil are explicitly group-PvP oriented; do not use the Arena reflect bar when your job is protecting a carry.','Prydwen team PvP')"""
new_tournament="""      role('Tournament','Taunt / ally protection',['Hamper Strike','Heart of Challenge','Luminous Shield','Desperate Protection'],['Iron Will','Soul Protection','Iron Fortress','Oath of Vigil'],'This is where Oath of Vigil belongs: Hamper Strike and Heart of Challenge control targeting while Oath protects the ally most likely to be bursted. Soul Protection adds the strongest general opening survival layer.','Iron Fortress and Oath of Vigil remain the team-PvP core; Soul Protection replaces Holy Aegis here for stronger immediate effective HP under coordinated focus.','Prydwen + current Guardian PvP')"""

changed=[]
for path in paths:
    s=path.read_text(encoding='utf-8')
    before=s
    if old_arena in s:
        s=s.replace(old_arena,new_arena,1)
    elif new_arena not in s:
        raise SystemExit(f'Guardian Arena role not found in {path}')
    if old_tournament in s:
        s=s.replace(old_tournament,new_tournament,1)
    elif new_tournament not in s:
        raise SystemExit(f'Guardian Tournament role not found in {path}')
    if s!=before:
        path.write_text(s,encoding='utf-8')
        changed.append(str(path))

print('Updated:', ', '.join(changed) if changed else 'already current')
