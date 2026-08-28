from pathlib import Path
import re

FILES=[Path('index.html'),Path('.github/build-fantomons-inject.html')]
MARK='ARENA_TOURNAMENT_RESTORE_V2'

CARDS={
'Berserker':[
'''      role('Arena','Solo PvP burst / mobility',['Darkness Descends','Lion Combo','Eclipse Slash','Sunset Sword'],['Insightful Eye','Blade of Judgment','Frame of Battles','Indomitable Will'],'This is the published solo-PvP core: mobility, multi-hit pressure and cheat-death.','Keep Indomitable Will. Into reflect/block tanks, reduce multi-hit exposure with the Flash Dash / Heavy Impact / Doom Blade / Darkness Descends anti-tank shell.','Prydwen Arena')''',
'''      role('Tournament','Team PvP grouping / area pressure',["Hunter's Judgment",'Flame Aura','Eclipse Slash','Sunset Sword'],['Insightful Eye','Blade of Judgment','Frame of Battles','Indomitable Will'],'Hunter’s Judgment groups targets for teammates while Flame Aura adds team-fight pressure; if your comp already controls targets, Hunter’s Judgment → Lion Combo.','Keep Indomitable Will; the team build should not greed away its survival layer.','Multi-guide team PvP')'''],
'Paladin':[
'''      role('Arena','Solo reflect / block bruiser',['Luminous Shield','Leap Attack','Star Shattering Slash','Valor Surge'],['Rebound','Block Mastery','Block Awareness','Stone Skin'],'Arena is about surviving the burst window and letting Block/Rebound punish repeated hits before Star Shattering Slash comes online.','If the opponent cannot pressure you, Stone Skin can flex to a damage charm; do not sacrifice Block consistency just for sheet power.','Community Arena')''',
'''      role('Tournament','Team protection / frontline',['Valor Surge','Heart of Challenge','Luminous Shield','Desperate Protection'],['Iron Fortress','Block Mastery','Block Awareness','Stone Skin'],'Use the full tank shell in team PvP: buff, hold aggro/control space and keep allies alive instead of chasing solo damage.','If the team is already safe, Luminous Shield can flex to Lunarwater Threads for pull pressure.','Guide-derived team PvP')'''],
'Archmage':[
'''      role('Arena','Fast solo burst without Divine Wrath RNG',['Tempest Sphere','Howling Hurricane','Meteoric Flames',"Wind's Delight"],['Rapid Cast','Void Bubble','Mana Surge','Radiant Sear'],'Prydwen specifically recommends the single-target shell without Divine Wrath for PvP; Tempest Sphere is more reliable on player-sized targets.','Keep Void Bubble; Mana Surge → Repelling Wind when melee pressure is the matchup problem.','Prydwen Arena')''',
'''      role('Tournament','Team AoE pressure',['Tempest Sphere','Howling Hurricane','Meteoric Flames','Lightning Chain'],['Rapid Cast','Void Bubble','Mana Surge','Radiant Sear'],'Tournament rewards wider coverage more than solo Arena, so keep the reliable PvP core but trade the single-target finisher for Lightning Chain.','Keep Void Bubble. Do not force Divine Wrath into small-player targeting just because it is strong on bosses.','Guide-derived team PvP')'''],
'Arcanist':[
'''      role('Arena','Solo Dark burst / Erosion cash-out',['Mana Blast','Dark Bullet','Abyssal Hand','Shadow of Termination'],['Shadow Vengeance',"Night's Blessing",'Shadow Erosion','Linked Misfortune'],'Solo Arena favors actually killing the target: build Erosion, cash it out with Shadow of Termination and let Shadow Vengeance buy the finishing turn.','Do not default to the healer bar in solo PvP; PvP healing is reduced and needs real Healing Boost/SPD investment to justify it.','Guide-derived Arena')''',
'''      role('Tournament','Hybrid team pressure / revive utility',['Mana Blast','Abyssal Hand','Radiant Restoration','Frenzy Totem'],['Resurrection','Shadow Vengeance','Shadow Erosion','Linked Misfortune'],'Tournament should not default to full healing: Mana Blast + Abyssal Hand provide Dark pressure, Erosion and Slow while Frenzy Totem buffs the team and Radiant Restoration gives one efficient group-heal slot.','PvP healing is heavily reduced. Only move toward the dedicated Healing card when your Healing Boost/SPD are genuinely built for it; otherwise keep Resurrection + damage/debuff utility.','Community hybrid PvP')'''],
'Conqueror':[
'''      role('Arena','Solo PvP / anti-Guardian pressure',['Darkness Descends','Doom Blade','Flickering Blade','Blade Storm'],['Piercing Assault','Tactical Adaptation','Soul Breaker','Indomitable Will'],'Current community Arena testing leans into Dispel, DEF reduction and fewer reflection-triggering hits against Guardians. If Crit is still low, Soul Breaker → Insightful Eye.','Accuracy is a premium PvP roll into high-Block Guardians; keep Indomitable Will even when you outpower the opponent.','Community Arena')''',
'''      role('Tournament','Team PvP mobility / reach',['Flash Fire','Darkness Descends','Flickering Blade','Blade Storm'],['Insightful Eye','Piercing Assault','Tactical Adaptation','Indomitable Will'],'Use the safer Prydwen PvP core for team fights: Flash Fire keeps reach while Darkness Descends gives mobility and Dispel. High Crit: Insightful Eye → Soul Breaker.','Keep Indomitable Will; coordinated team focus punishes greedier Dragon-style charm bars.','Prydwen team PvP')'''],
'Guardian':[
'''      role('Arena','Solo block / reflect wall',['Luminous Shield','Forceful Charge','Star Shattering Slash','Desperate Protection'],['Rebound','Holy Aegis','Block Mastery','Block Awareness'],'Solo Arena does not benefit from ally-protection charms, so stay self-focused: Block, shields, Rebound and enough threat to punish attackers.','If Pandarial and your ranks support it, Luminous Shield → Light Sword Array is the aggressive flex; keep Block stats high.','Guide-derived Arena')''',
'''      role('Tournament','Taunt / ally protection',['Hamper Strike','Heart of Challenge','Luminous Shield','Desperate Protection'],['Iron Will','Holy Aegis','Iron Fortress','Oath of Vigil'],'This is where Oath of Vigil belongs: Hamper Strike and Heart of Challenge control targeting while Oath protects the ally most likely to be bursted.','Iron Fortress and Oath of Vigil are explicitly group-PvP oriented; do not use the Arena reflect bar when your job is protecting a carry.','Prydwen team PvP')'''],
'Destroyer':[
'''      role('Arena','Wind control / solo tempo',['Tempest Sphere','Wind Blade Spiral',"Wind's Delight",'Howling Hurricane'],['Cyclone Lament','Repelling Wind',"Wind's Shadow",'Void Bubble'],'Wind is the cleanest solo-PvP identity: movement pressure, knockback/delay and Laceration while Void Bubble buys the extra turn a squishy Destroyer needs.','Repelling Wind is specifically valuable in PvP; keep enough Effect Hit Rate for the control/debuff package to matter.','Guide + community Arena')''',
'''      role('Tournament','Team AoE / Formation Breaker',['Formation Breaker','Howling Hurricane','Meteoric Flames','Wind Blade Spiral'],['Rapid Cast','Void Bubble','Cyclone Lament','Radiant Sear'],'Formation Breaker matters much more in team PvP because it can buff and advance allies; the rest of the bar keeps broad AoE pressure.','Keep Void Bubble. If your team already supplies tempo buffs, Formation Breaker can flex to another damaging/control Technique.','Guide-derived team PvP')'''],
'Dominator':[
'''      role('Arena','Solo Arena burst / utility',['Abyssal Hand','Dark Starburst','Dark Bullet','Shadow of Termination'],['Linked Misfortune','Shadow Erosion','Mantra of Blessings','Shadow Vengeance'],'This follows the published Loot & Waifus Solo PvP shell: reliable Dark pressure plus Mantra utility instead of forcing a full healer bar.','A healing hybrid is possible, but pure sustain has a much higher gear requirement in solo PvP.','Loot & Waifus Arena')''',
'''      role('Tournament','Hybrid support / anti-tank pressure',['Decoy Clone','Frenzy Totem','Dark Starburst','Abyssal Hand'],['Mantra of Blessings','Resurrection','Shadow Vengeance',"Night's Blessing"],'Use Dominator as a support/sub-DPS, not a pure healer: Decoy Clone pressures shield-heavy tanks, Frenzy Totem + Mantra amplify the carry, and Dark Starburst/Abyssal Hand keep meaningful direct pressure and Slow utility.','If your team truly needs healing, Abyssal Hand → Radiant Restoration. Full healing should be reserved for unusually high Healing Boost/SPD setups because PvP cuts healing effectiveness.','Community hybrid PvP')''']
}

def restore_cards(s, path):
    start=s.find('  const ROLE_PRESETS={')
    end=s.find('\n\n  const FANTO={', start)
    if start < 0 or end < 0:
        raise SystemExit(f'ROLE_PRESETS block not found in {path}')
    block=s[start:end]

    for cls,cards in CARDS.items():
        pat=re.compile(rf'(    {re.escape(cls)}:\[\n)(.*?)(\n    \](?:,)?)(?=\n    [A-Za-z]+:\[|\n  \}};)', re.S)
        m=pat.search(block)
        if not m:
            raise SystemExit(f'{cls} preset block not found in {path}')
        lines=m.group(2).splitlines()
        lines=[ln for ln in lines if "role('PvP'" not in ln and "role('Arena'" not in ln and "role('Tournament'" not in ln]
        while lines and not lines[-1].strip():
            lines.pop()
        if not lines:
            raise SystemExit(f'{cls} has no base build cards in {path}')
        if not lines[-1].rstrip().endswith(','):
            lines[-1]=lines[-1].rstrip()+','
        new_body='\n'.join(lines+[cards[0]+',',cards[1]])
        block=block[:m.start(2)]+new_body+block[m.end(2):]

    s=s[:start]+block+s[end:]

    # Preserve the original Arena/Tournament Fantomon routing even if a later
    # preset rewrite left only the marker behind.
    if "if(t.startsWith('arena')) return 'Arena';" not in s:
        anchor="    if(t.startsWith('pvp')) return 'PvP';"
        if anchor not in s:
            raise SystemExit(f'roleKey PvP anchor missing in {path}')
        s=s.replace(anchor,"    if(t.startsWith('arena')) return 'Arena';\n    if(t.startsWith('tournament')) return 'Tournament';\n"+anchor,1)

    if MARK not in s:
        marker='/* SAGE_TOURNAMENT_HYBRID_V1 */'
        if marker in s:
            s=s.replace(marker,marker+'\n/* '+MARK+' */',1)
        else:
            s=s.replace('/* BUILD_ARENA_TOURNAMENT_SPLIT_V1 */','/* BUILD_ARENA_TOURNAMENT_SPLIT_V1 */\n/* '+MARK+' */',1)
    return s

for p in FILES:
    s=p.read_text(encoding='utf-8')
    s=restore_cards(s,p)
    p.write_text(s,encoding='utf-8')
    print('restored Arena/Tournament cards in',p)
