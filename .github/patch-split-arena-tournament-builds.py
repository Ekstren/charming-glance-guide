from pathlib import Path

FILES=[Path('index.html'),Path('.github/build-fantomons-inject.html')]
MARK='BUILD_ARENA_TOURNAMENT_SPLIT_V1'

REPLS={
"      role('PvP','Mobility, burst and cheat-death',['Darkness Descends','Lion Combo','Eclipse Slash','Sunset Sword'],['Insightful Eye','Blade of Judgment','Frame of Battles','Indomitable Will'],'For 2v2/4v4, Lion Combo → Hunter’s Judgment when grouping is more valuable.','Keep Indomitable Will for PvP.','Prydwen PvP')":
"      role('Arena','Solo PvP burst / mobility',['Darkness Descends','Lion Combo','Eclipse Slash','Sunset Sword'],['Insightful Eye','Blade of Judgment','Frame of Battles','Indomitable Will'],'This is the published solo-PvP core: mobility, multi-hit pressure and cheat-death.','Keep Indomitable Will. Into reflect/block tanks, reduce multi-hit exposure with the Flash Dash / Heavy Impact / Doom Blade / Darkness Descends anti-tank shell.','Prydwen Arena'),\n      role('Tournament','Team PvP grouping / area pressure',[\"Hunter's Judgment\",'Flame Aura','Eclipse Slash','Sunset Sword'],['Insightful Eye','Blade of Judgment','Frame of Battles','Indomitable Will'],'Hunter’s Judgment groups targets for teammates while Flame Aura adds team-fight pressure; if your comp already controls targets, Hunter’s Judgment → Lion Combo.','Keep Indomitable Will; the team build should not greed away its survival layer.','Multi-guide team PvP')",

"      role('PvP','Reflect / block pressure with team protection',['Luminous Shield','Leap Attack','Star Shattering Slash','Heart of Challenge'],['Iron Fortress','Rebound','Block Mastery','Block Awareness'],'Star Shattering Slash gives real kill pressure while Leap Attack/Heart of Challenge keep control and Rebound converts DEF into return damage.','For 4v4 or heavy enemy burst, Star Shattering Slash → Desperate Protection; Stone Skin is the first defensive charm flex.','Multi-guide PvP')":
"      role('Arena','Solo reflect / block bruiser',['Luminous Shield','Leap Attack','Star Shattering Slash','Valor Surge'],['Rebound','Block Mastery','Block Awareness','Stone Skin'],'Arena is about surviving the burst window and letting Block/Rebound punish repeated hits before Star Shattering Slash comes online.','If the opponent cannot pressure you, Stone Skin can flex to a damage charm; do not sacrifice Block consistency just for sheet power.','Community Arena'),\n      role('Tournament','Team protection / frontline',['Valor Surge','Heart of Challenge','Luminous Shield','Desperate Protection'],['Iron Fortress','Block Mastery','Block Awareness','Stone Skin'],'Use the full tank shell in team PvP: buff, hold aggro/control space and keep allies alive instead of chasing solo damage.','If the team is already safe, Luminous Shield can flex to Lunarwater Threads for pull pressure.','Guide-derived team PvP')",

"      role('PvP','Fast elemental burst without Divine Wrath targeting RNG',['Tempest Sphere','Howling Hurricane','Meteoric Flames',\"Wind's Delight\"],['Rapid Cast','Void Bubble','Mana Surge','Radiant Sear'],'This is Prydwen’s single-target shell with Divine Wrath removed for PvP reliability.','Keep Void Bubble; Mana Surge → Repelling Wind if control/survival is more valuable than greed.','Prydwen PvP')":
"      role('Arena','Fast solo burst without Divine Wrath RNG',['Tempest Sphere','Howling Hurricane','Meteoric Flames',\"Wind's Delight\"],['Rapid Cast','Void Bubble','Mana Surge','Radiant Sear'],'Prydwen specifically recommends the single-target shell without Divine Wrath for PvP; Tempest Sphere is more reliable on player-sized targets.','Keep Void Bubble; Mana Surge → Repelling Wind when melee pressure is the matchup problem.','Prydwen Arena'),\n      role('Tournament','Team AoE pressure',['Tempest Sphere','Howling Hurricane','Meteoric Flames','Lightning Chain'],['Rapid Cast','Void Bubble','Mana Surge','Radiant Sear'],'Tournament rewards wider coverage more than solo Arena, so keep the reliable PvP core but trade the single-target finisher for Lightning Chain.','Keep Void Bubble. Do not force Divine Wrath into small-player targeting just because it is strong on bosses.','Guide-derived team PvP')",

"      role('PvP','4v4 sustain / support shell',['Void Blessing','Waterling Summon','Radiant Restoration','Frenzy Totem'],['Resurrection','Healing Mastery','Overhealing','Shadow Vengeance'],'Use the healer shell when your team benefits more from sustain than another damage dealer; Shadow Vengeance keeps you relevant through focus fire.','Healing is less efficient in PvP, so if your Healing Boost/SPD are weak, switch to the Single Target DPS shell instead of forcing sustain.','Community PvP')":
"      role('Arena','Solo Dark burst / Erosion cash-out',['Mana Blast','Dark Bullet','Abyssal Hand','Shadow of Termination'],['Shadow Vengeance',\"Night's Blessing\",'Shadow Erosion','Linked Misfortune'],'Solo Arena favors actually killing the target: build Erosion, cash it out with Shadow of Termination and let Shadow Vengeance buy the finishing turn.','Do not default to the healer bar in solo PvP; PvP healing is reduced and needs real Healing Boost/SPD investment to justify it.','Guide-derived Arena'),\n      role('Tournament','Team sustain / revive support',['Void Blessing','Waterling Summon','Radiant Restoration','Frenzy Totem'],['Resurrection','Healing Mastery','Overhealing','Shadow Vengeance'],'Team PvP is where the healer shell makes sense: sustain, revive value and Shadow Vengeance to survive focus.','If your Healing Boost/SPD are weak, use the AoE DPS card instead of forcing a low-output healer build.','Community team PvP')",

"      role('PvP','Mobility, dispel and durable elemental pressure',['Flash Fire','Darkness Descends','Flickering Blade','Blade Storm'],['Insightful Eye','Piercing Assault','Tactical Adaptation','Indomitable Will'],'Darkness Descends replaces Flame Aura for mobility and Dispel. High Crit: Insightful Eye → Soul Breaker.','Always keep Indomitable Will in PvP; against high-block tanks, Accuracy becomes much more important than another small damage roll.','Prydwen PvP')":
"      role('Arena','Solo PvP / anti-Guardian pressure',['Darkness Descends','Doom Blade','Flickering Blade','Blade Storm'],['Piercing Assault','Tactical Adaptation','Soul Breaker','Indomitable Will'],'Current community Arena testing leans into Dispel, DEF reduction and fewer reflection-triggering hits against Guardians. If Crit is still low, Soul Breaker → Insightful Eye.','Accuracy is a premium PvP roll into high-Block Guardians; keep Indomitable Will even when you outpower the opponent.','Community Arena'),\n      role('Tournament','Team PvP mobility / reach',['Flash Fire','Darkness Descends','Flickering Blade','Blade Storm'],['Insightful Eye','Piercing Assault','Tactical Adaptation','Indomitable Will'],'Use the safer Prydwen PvP core for team fights: Flash Fire keeps reach while Darkness Descends gives mobility and Dispel. High Crit: Insightful Eye → Soul Breaker.','Keep Indomitable Will; coordinated team focus punishes greedier Dragon-style charm bars.','Prydwen team PvP')",

"      role('PvP','Taunt, reflection and ally protection',['Hamper Strike','Heart of Challenge','Luminous Shield','Desperate Protection'],['Iron Will','Holy Aegis','Iron Fortress','Oath of Vigil'],'Hamper Strike gives reliable Taunt while Oath of Vigil protects the ally most likely to get bursted.','Iron Fortress and Oath of Vigil are explicitly PvP-oriented; keep the defense-first shell unless your team already has another Guardian.','Prydwen-derived PvP')":
"      role('Arena','Solo block / reflect wall',['Luminous Shield','Forceful Charge','Star Shattering Slash','Desperate Protection'],['Rebound','Holy Aegis','Block Mastery','Block Awareness'],'Solo Arena does not benefit from ally-protection charms, so stay self-focused: Block, shields, Rebound and enough threat to punish attackers.','If Pandarial and your ranks support it, Luminous Shield → Light Sword Array is the aggressive flex; keep Block stats high.','Guide-derived Arena'),\n      role('Tournament','Taunt / ally protection',['Hamper Strike','Heart of Challenge','Luminous Shield','Desperate Protection'],['Iron Will','Holy Aegis','Iron Fortress','Oath of Vigil'],'This is where Oath of Vigil belongs: Hamper Strike and Heart of Challenge control targeting while Oath protects the ally most likely to be bursted.','Iron Fortress and Oath of Vigil are explicitly group-PvP oriented; do not use the Arena reflect bar when your job is protecting a carry.','Prydwen team PvP')",

"      role('PvP','Wind pressure / action-tempo burst',['Formation Breaker','Howling Hurricane','Meteoric Flames','Wind Blade Spiral'],['Rapid Cast','Void Bubble','Cyclone Lament','Radiant Sear'],'Community T4 testing consistently favors Wind in PvP; this uses the published Wind-heavy core rather than inventing a separate untested bar. Stack enough Effect Hit Rate for Laceration to matter.','Keep Void Bubble unless you are reliably deleting targets before they act; PvP Accuracy rolls are valuable into Block-heavy Guardians.','Community consensus')":
"      role('Arena','Wind control / solo tempo',['Tempest Sphere','Wind Blade Spiral',\"Wind's Delight\",'Howling Hurricane'],['Cyclone Lament','Repelling Wind',\"Wind's Shadow\",'Void Bubble'],'Wind is the cleanest solo-PvP identity: movement pressure, knockback/delay and Laceration while Void Bubble buys the extra turn a squishy Destroyer needs.','Repelling Wind is specifically valuable in PvP; keep enough Effect Hit Rate for the control/debuff package to matter.','Guide + community Arena'),\n      role('Tournament','Team AoE / Formation Breaker',['Formation Breaker','Howling Hurricane','Meteoric Flames','Wind Blade Spiral'],['Rapid Cast','Void Bubble','Cyclone Lament','Radiant Sear'],'Formation Breaker matters much more in team PvP because it can buff and advance allies; the rest of the bar keeps broad AoE pressure.','Keep Void Bubble. If your team already supplies tempo buffs, Formation Breaker can flex to another damaging/control Technique.','Guide-derived team PvP')",

"      role('PvP','Solo Arena burst / utility',['Abyssal Hand','Dark Starburst','Dark Bullet','Shadow of Termination'],['Linked Misfortune','Shadow Erosion','Mantra of Blessings','Shadow Vengeance'],'This follows the published Loot & Waifus Solo PvP shell: reliable Dark pressure plus Mantra utility instead of forcing a full healer bar.','For coordinated 4v4, pivot toward Decoy Clone / Waterling / Mantra / Resurrection support if your team already has the damage carry.','Loot & Waifus PvP')":
"      role('Arena','Solo Arena burst / utility',['Abyssal Hand','Dark Starburst','Dark Bullet','Shadow of Termination'],['Linked Misfortune','Shadow Erosion','Mantra of Blessings','Shadow Vengeance'],'This follows the published Loot & Waifus Solo PvP shell: reliable Dark pressure plus Mantra utility instead of forcing a full healer bar.','A healing hybrid is possible, but pure sustain has a much higher gear requirement in solo PvP.','Loot & Waifus Arena'),\n      role('Tournament','Team support / carry protection',['Decoy Clone','Waterling Summon','Radiant Restoration','Rejuvenating Rain'],['Phantom Light','Mantra of Blessings','Resurrection','Shadow Vengeance'],'Team PvP changes the job: Decoy Clone/Mantra support the carry while healing and Resurrection add real squad value.','If your healing stats are not developed, use the AoE Erosion card and consider Aberrancy instead; Loot & Waifus specifically flags Aberrancy as more useful in AoE/Tournament than Arena.','Multi-guide team PvP')"
}

for p in FILES:
    s=p.read_text(encoding='utf-8')
    if MARK in s:
        print(p,'already patched')
        continue
    for old,new in REPLS.items():
        if old not in s:
            raise SystemExit(f'missing PvP preset in {p}: {old[:90]}')
        s=s.replace(old,new,1)
    old_role="""  function roleKey(title){
    const t=(title||'').toLowerCase();
    if(t.startsWith('pvp')) return 'PvP';"""
    new_role="""  function roleKey(title){
    const t=(title||'').toLowerCase();
    if(t.startsWith('arena')) return 'Arena';
    if(t.startsWith('tournament')) return 'Tournament';
    if(t.startsWith('pvp')) return 'PvP';"""
    if old_role not in s:
        raise SystemExit(f'roleKey anchor missing in {p}')
    s=s.replace(old_role,new_role,1)
    old_picks="""  function picksFor(cls,title){
    const role=roleKey(title);
    return (FANTO[cls]&&FANTO[cls][role])||[];
  }"""
    new_picks="""  function picksFor(cls,title){
    const role=roleKey(title);
    const pools=FANTO[cls]||{};
    if(role==='Arena') return pools.Arena||pools.PvP||[];
    if(role==='Tournament'){
      if(cls==='Arcanist'||cls==='Dominator') return pools.Tournament||pools.Dungeon||pools.PvP||[];
      return pools.Tournament||pools.PvP||[];
    }
    return pools[role]||[];
  }"""
    if old_picks not in s:
        raise SystemExit(f'picksFor anchor missing in {p}')
    s=s.replace(old_picks,new_picks,1)
    marker='/* BUILD_GUIDE_CONSENSUS_PVP_V1 */'
    if marker in s:
        s=s.replace(marker,marker+'\n/* '+MARK+' */',1)
    else:
        s=s.replace('/* BUILD_FANTOMON_PAIRS_V5_GUIDE_LOADOUTS_MAIN_ALT */','/* BUILD_FANTOMON_PAIRS_V5_GUIDE_LOADOUTS_MAIN_ALT */\n/* '+MARK+' */',1)
    p.write_text(s,encoding='utf-8')
    print('split Arena/Tournament builds in',p)
