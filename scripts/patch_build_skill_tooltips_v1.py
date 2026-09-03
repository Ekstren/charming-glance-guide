from pathlib import Path

INDEX = Path('index.html')
INJECT = Path('.github/build-fantomons-inject.html')
RESTORE = Path('scripts/patch_restore_rich_builds_v1.py')
MARK = 'BUILD_SKILL_TOOLTIPS_V1'
END = '<!-- BUILD_FANTOMON_PAIRS_END -->'

PAYLOAD = r'''
<style id="build-skill-tooltips-v1">
/* BUILD_SKILL_TOOLTIPS_V1 */
#buildContent .skillGroup b[data-skill-tooltip]{cursor:help;outline:none}
#buildContent .skillGroup b[data-skill-tooltip]:focus-visible{box-shadow:0 0 0 2px var(--surface),0 0 0 4px var(--green)}
.buildSkillTipLayer{position:fixed;z-index:2500;width:min(310px,calc(100vw - 20px));padding:10px 11px;border:1px solid color-mix(in srgb,var(--green) 45%,var(--line));border-radius:11px;background:color-mix(in srgb,var(--surface) 96%,var(--bg) 4%);color:var(--body-text);box-shadow:0 14px 36px #0007;pointer-events:none;opacity:0;visibility:hidden;transform:translateY(3px);transition:opacity .1s ease,transform .1s ease,visibility .1s;overflow-wrap:anywhere}
.buildSkillTipLayer.open{opacity:1;visibility:visible;transform:none}
.buildSkillTipHead{display:flex;align-items:baseline;justify-content:space-between;gap:10px;margin-bottom:6px}
.buildSkillTipHead strong{color:var(--ink);font-size:11px;line-height:1.25}
.buildSkillTipHead span{flex:0 0 auto;color:var(--green);font-size:7.5px;font-weight:900;letter-spacing:.08em;text-transform:uppercase}
.buildSkillTipMeta{display:flex;flex-wrap:wrap;gap:4px;margin:0 0 6px}
.buildSkillTipMeta:empty{display:none}
.buildSkillTipMeta i{font-style:normal;border:1px solid var(--line);border-radius:999px;padding:2px 5px;color:var(--muted);font-size:7.5px;font-weight:800}
.buildSkillTipEffect{margin:0;font-size:9px;line-height:1.45}
.buildSkillTipWhy{border-top:1px solid var(--line);margin:7px 0 0;padding-top:6px;color:var(--muted);font-size:8.5px;line-height:1.4}
.buildSkillTipWhy b{color:var(--green)}
@media(hover:none),(pointer:coarse){#buildContent .skillGroup b[data-skill-tooltip]{cursor:pointer}.buildSkillTipLayer{width:min(340px,calc(100vw - 16px));padding:11px 12px}.buildSkillTipHead strong{font-size:12px}.buildSkillTipEffect{font-size:10px}.buildSkillTipWhy{font-size:9.5px}}
</style>
<script id="build-skill-tooltips-v1-script">
(()=>{
  const I=(effect,why,meta='')=>({effect,why,meta});
  const INFO={
    // Conqueror / Duelist line
    'Flash Fire':I('Fast elemental attack with useful reach and mobility. It helps Conqueror cross space while still contributing damage.','Preferred in Dungeon and 4v4 when reach and fast target access matter.','Elemental · Mobility'),
    'Flame Aura':I('Repeating Fire damage that performs well into both single targets and groups; one of the strongest inherited elemental engines for the class.','Core PvE damage piece when Dispel or extra mobility is not required.','Fire · Repeating damage'),
    'Flickering Blade':I('Single-target Technique with no cooldown. If the target survives, it has a 60% chance to repeat, up to two extra attacks.','The repeat mechanic gives Conqueror excellent cleanup and boss pressure every turn.','0 CD · Single target · Repeat'),
    'Blade Storm':I('Hard-hitting line AoE. Positioning matters because its coverage is narrower than broad circular AoE skills.','Reliable damage across current Conqueror content, especially when enemies can be lined up.','AoE · Line'),
    'Darkness Descends':I('Mobility plus buff removal/Dispel, trading some raw PvE damage for control and access.','A premium PvP slot for stripping enemy buffs and staying on priority targets.','Mobility · Dispel'),
    'Doom Blade':I('Aggressive leap/area-pressure Technique used to close distance and add immediate burst.','Arena flex when you want harder pressure instead of the sustain offered by Soul Piercer.','Mobility · AoE pressure'),
    'Soul Piercer':I('Damage Technique with sustain utility, giving the Conqueror a safer way to keep pressure up.','Especially useful in 2v2 where losing one unit is half the team.','Damage · Sustain'),
    'Piercing Assault':I('Core T4 Charm that lets Conqueror ignore enemy DEF; the effect improves while you have buffs.','The defining damage Charm for current Conqueror and a long-term investment.','DEF ignore'),
    'Tactical Adaptation':I('Adaptive Charm that shifts between a strong offensive or defensive benefit depending on how many enemies are nearby.','Universal because it automatically changes value between bosses, packs and PvP.','Adaptive offense/defense'),
    'Soul Splash':I('Offensive follow-up/proc Charm that benefits from repeated attacks.','Pairs especially well with Flickering Blade repeats in fast PvE clears.','Follow-up damage'),
    'Insightful Eye':I('Crit-focused Charm used to stabilize Crit Rate before gear and other permanent sources solve the breakpoint.','Use early; replace with a greedier damage Charm once your effective Crit Rate is high enough.','Crit support'),
    'Soul Breaker':I('Greedy offensive Charm used after Crit Rate is already solved.','The standard upgrade over Insightful Eye in PvP or developed S2 accounts.','Offense'),
    'Indomitable Will':I('Major survival Charm with a strong safety window and self-healing.','Keep it in serious PvP; in easy PvE it is the first slot you can greed into damage.','Survival · Heal'),
    'Blazing Clash':I('Boss-oriented offensive Charm that adds sustained Fire/elemental pressure in longer fights.','Used in the greedier Crucible/Conquest score setup when survival is already handled.','Boss offense'),
    'Crit Mastery':I('Crit payoff Charm for accounts that already have enough Crit Rate without Insightful Eye.','A high-end boss flex once the Crit breakpoint is solved.','Crit payoff'),
    'Gale Dance':I('Team-tempo Technique that can provide a useful SPD advantage when coordinated with another Conqueror.','A 4v4 composition flex; normally only one Conqueror needs to carry it.','Team SPD · Utility'),

    // Guardian / Knight line
    'Valor Surge':I('Team-oriented buff Technique with cleanse utility.','Pre-cast support for Dungeon and boss teams; flex it out when you need more Taunt.','Team buff · Cleanse'),
    'Heart of Challenge':I('Core group-Taunt Technique that finally gives Guardian reliable frontline control.','Central to the Tank setup whenever you need enemies focused on you instead of allies.','Taunt · Tank'),
    'Luminous Shield':I('Reliable shield Technique that supports Guardian’s DEF/Block survival loop.','Tank staple and a useful defensive anchor in PvP bruiser builds.','Shield'),
    'Desperate Protection':I('Emergency defensive Technique used to keep the Guardian standing through dangerous damage windows.','Tank default; replace it with damage only when the group is already safe.','Defense'),
    'Hamper Strike':I('Direct Taunt option with no pre-cast and a 1-turn cooldown.','Use when the normal Tank bar needs more reliable Taunt uptime.','Taunt · 1 CD'),
    'Swirling Blade':I('Strong Water damage Technique that also grants a self-shield.','The best reusable offensive T4 Guardian investment and a core offensive Technique.','Water · Damage · Shield'),
    'Lunarwater Threads':I('Water pressure and Cold-setup Technique used in offensive and support builds.','Helps accelerate the Water/Cold loop and remains useful in boss support.','Water · Cold setup'),
    'Seismic Tide':I('Water Technique favored for steadier Cold stacking.','Used when consistency matters more than a situational utility slot.','Water · Cold stacking'),
    'Raging Maelstrom':I('Large Water/AoE payoff for the full offensive Water build.','Best when multiple enemies let DPS Guardian spread pressure and exploit Cold setup.','Water · AoE'),
    'Forceful Charge':I('Engage/mobility Technique that helps Guardian stay attached to a target and apply pressure.','Useful in Arena and 2v2 where target access matters more than broad AoE.','Mobility · Pressure'),
    'Star Shattering Slash':I('Heavy direct-damage Technique inherited from Paladin; it starts as one of the Knight line’s strongest single-target nukes and scales hard with rank.','Use it for Crucible/Conquest and other concentrated targets; it also adds real kill pressure to Block/counter PvP builds.','Single target · Heavy hit'),
    'Leap Attack':I('Mobile attack with a chance to reduce enemy DEF.','Boss-support Guardian uses it to contribute damage amplification while staying active.','Mobility · DEF down'),
    'Holy Purification':I('Purification/Dispel utility Technique for removing problematic enemy buffs or effects.','Excellent in boss support when there is actually something important to remove; otherwise it is a flex slot.','Dispel utility'),
    'Light Sword Array':I('Aggressive Light damage flex used when Guardian can afford to give up part of its shield package.','A later/Pandarial-friendly offensive swap rather than the default Tank choice.','Light · Offense'),
    'Iron Will':I('Reduces damage taken from enemies that are Taunted.','Extremely efficient in Tank builds because Guardian now has reliable Taunt access.','Taunt synergy · Mitigation'),
    'Holy Aegis':I('Raises DEF and improves DEF-based shields.','Universal Guardian durability that also strengthens the shield loop.','DEF · Shield scaling'),
    'Block Awareness':I('Improves Block consistency.','Use when your natural Block rate is not yet high enough to make the defensive loop reliable.','Block'),
    'Soul Protection':I('At battle start, converts 50% of HP into a large shield; remaining shield can restore HP at the end of the fight.','One of Guardian’s strongest universal T4 survival Charms, especially in dungeons.','Opening shield'),
    'Iron Fortress':I('Heavy team-mitigation Charm for protecting the party through dangerous windows.','Premium in hard group content and Tournament; less necessary when the team already survives comfortably.','Team mitigation'),
    'Oath of Vigil':I('Protects the lowest-HP ally with Vigil, redirecting part of their incoming damage to Guardian and reducing that redirected damage.','Especially strong in 2v2/4v4 where protecting a carry can decide the round.','Ally protection'),
    'Rebound':I('Counter/reflect-style Charm that punishes enemies for repeatedly hitting a durable Guardian.','Core Arena and small-team PvP pressure without abandoning the Block identity.','Counter · Reflect'),
    'Block Mastery':I('Turns high Block investment into a stronger defensive/counter package.','Keeps the PvP bruiser build consistent against repeated-hit attackers.','Block scaling'),
    'Frigid Aura':I('Core Water/Cold damage amplifier for offensive Guardian.','The first Charm you build around in the Water DPS build.','Water/Cold amp'),
    'Defensive Assault':I('Converts Guardian’s defensive investment into offensive pressure.','Lets DPS Guardian remain bruiser-tanky instead of becoming a fragile pseudo-DPS.','Defense → offense'),
    'Frigid Glint':I('Cold-synergy offensive Charm that rewards the Water stacking loop.','Paired with Frigid Aura in the Water DPS build.','Cold synergy'),
    'Potential Rebirth':I('Second-chance survival Charm.','The safety flex in offensive Guardian; replace it with more damage only when deaths are no longer a concern.','Cheat death'),
    'Pursuit of Victory':I('Greedy offensive Charm for situations where survival is already solved.','Used in boss-score or overgeared PvE versions of DPS Guardian.','Offense'),
    'Eye for an Eye':I('Counter-oriented offensive Charm that adds punishment while Guardian absorbs pressure.','PvP DPS flex when you can survive without another pure defensive slot.','Counter offense'),

    // Destroyer / Sorcerer line
    'Formation Breaker':I('Core Destroyer Technique that buffs from your own ATK and has a 50% chance to accelerate allied actions.','Long-lived core even in Arena; in team content the ally action advance becomes especially valuable.','ATK buff · Action advance'),
    'Fiery Star Trail':I('Fire AoE setup piece that adds Fire pressure across packs.','Dungeon Fire build uses it to generate more Fire events for the Fiery Burst package.','Fire · AoE'),
    'Fireball':I('Straightforward Fire damage Technique.','In the horde build its main job is reliable Fire triggering for the Crit/Fiery Burst engine.','Fire'),
    'Meteoric Flames':I('Strong Fire/area damage Technique that remains useful in mixed-element setups.','Excellent on packs and can outperform some boss options when target size/resistance favors it.','Fire · AoE'),
    'Divine Wrath':I('Heavy area damage whose value improves on large targets.','Boss-score option; on small bosses Meteoric Flames can test better.','AoE · Boss-size sensitive'),
    'Wind Blade Spiral':I('A smaller, faster-cooldown alternative to Howling Hurricane that produces strong sustained Wind damage.','One of Destroyer’s best repeatable damage Techniques in both PvE and PvP.','Wind · Fast cycle'),
    'Thunder of Judgment':I('Destroyer’s highest single-target Technique and it prioritizes bosses.','Ideal for Crucible/Conquest because it avoids wasting the big hit on random adds.','Single target · Boss priority'),
    "Wind's Delight":I('High-hit Wind single-target pressure that can produce excellent proc value.','A rank-dependent score/PvP flex; dummy-test it against Wind Blade Spiral or Tempest Sphere.','Wind · Multi-hit'),
    'Tempest Sphere':I('Compact Wind pressure that is more reliable on player-sized or small targets than giant-area skills.','A strong Arena/2v2 option where precise targeting matters.','Wind · Small-target'),
    'Howling Hurricane':I('Broad Wind AoE with strong multi-target coverage.','Best when you can actually hit several enemies; 4v4 gives it much more value than 1v1.','Wind · AoE'),
    'Rapid Cast':I('Front-loads the caster rotation so damage comes online faster.','Core tempo Charm for PvE score and team builds where acting quickly matters.','Tempo'),
    'Void Bubble':I('Defensive Charm that buys a fragile Mage extra survival.','Keep it until you clearly outgear the content; a dead Destroyer loses more damage than the greed slot gains.','Defense'),
    'Explosive Spirit':I('Builds Crit support as you use Fire Techniques.','One of the two core pieces of the Fire horde setup because it helps trigger Fiery Burst.','Fire · Crit support'),
    'Fiery Burst':I('Bonus Fire damage triggered from Fire crits; AoE can create separate burst instances on multiple targets.','The main payoff of the Dungeon Fire build.','Fire · Crit proc'),
    'Mana Surge':I('Greedy offensive Charm used to push damage when extra protection is unnecessary.','Boss-score flex; swap to a defensive option when survival costs attempts.','Offense'),
    'Radiant Sear':I('Major repeat-hit/proc damage Charm that rewards multi-hit elemental rotations.','A staple in mixed Wind/Light damage setups and 4v4 AoE pressure.','Proc damage'),
    'Incarnation of Light':I('Greedy Light-oriented damage slot for score content.','Used only when the encounter lets Destroyer sacrifice defensive utility for more output.','Light · Offense'),
    'Cyclone Lament':I('Wind/Laceration payoff Charm that benefits from repeated Wind Techniques.','Core mono-Wind pressure in Arena and strong when the build carries multiple Wind attacks.','Wind · Laceration'),
    'Repelling Wind':I('PvP control Charm used to create space and disrupt enemy tempo.','Excellent against melee pressure in Arena/2v2; flex to damage if your team already controls targets.','Control · Knockback'),
    "Wind's Shadow":I('Wind PvP utility slot focused on tempo/mobility rather than raw sheet damage.','Used in the dedicated solo-control shell where surviving and maintaining spacing matter.','Wind · PvP utility'),

    // Dominator / Sage line
    'Waterling Summon':I('Summons a Waterling that provides recurring healing/support.','A stable source of sustain in the dedicated Dungeon healer bar.','Summon · Healing'),
    'Rejuvenating Rain':I('Simple single-target heal that can be used every turn.','Reliable spot-healing and the first active healer Technique to prioritize.','0 CD · Single-target heal'),
    'Radiant Restoration':I('Direct party-healing Technique.','Main group-sustain button and the one healing slot retained in several hybrid support bars.','Group heal'),
    'Frenzy Totem':I('Team-support Totem that increases offensive throughput.','Used when the goal is boosting a carry rather than maximizing personal Dominator damage.','Team buff · Summon'),
    'Healing Touch':I('Additional direct-healing Technique.','Swap it in when the default healer bar needs more raw healing than Frenzy Totem provides.','Healing'),
    'Phantom Light':I('Improves healing and converts overhealing into shields.','Mandatory core Charm for a dedicated T4 healer.','Healing amp · Overheal shield'),
    'Healing Mastery':I('Universal healing-throughput Charm.','Straightforward core scaling for the healer profile.','Healing boost'),
    'Overhealing':I('Healer safety/value Charm that rewards excess healing rather than letting it go to waste.','Part of the standard sustain build in Dungeon and carry-support setups.','Healing utility'),
    'Resurrection':I('Revives a fallen ally.','Massive round-swing utility in 2v2/4v4 and valuable insurance in difficult PvE.','Revive'),
    'Mantra of Blessings':I('Strong damage buff for a carry or for yourself in solo content.','Excellent in scoring teams; in hard dungeons it loses priority to survival tools.','Damage buff'),
    'Decoy Clone':I('Position-dependent support Technique that can amplify a hypercarry’s damage.','One of the best score-support tools when your team can exploit the clone connection.','Carry amp · Positioning'),
    'Mana Blast':I('Dark/Erosion attack used to build the higher-ceiling damage-over-time plan.','Core in AoE and becomes the high-Effect-Hit-Rate single-target flex over Chaos Rune.','Dark · Erosion'),
    'Chaos Rune':I('Direct-damage Dark Technique used in the single-target hybrid so damage is less dependent on Erosion landing.','Best when Effect Hit Rate is not high enough to justify going all-in on Erosion; high EHR can flex it to Mana Blast.','Dark · Direct damage · ST'),
    'Shadow Impact':I('Broad Dark AoE payoff carried forward for T4 because Dominator receives no new dedicated AoE replacement.','The fourth Technique in the Dungeon/4v4 AoE setup where multiple targets justify its coverage.','Dark · AoE'),
    'Dark Bullet':I('Reliable Dark attack used to apply/maintain Erosion pressure.','Cheap, consistent glue for both DPS and support bars that still want debuff value.','Dark · Erosion'),
    'Dark Starburst':I('Reliable multi-hit direct Dark damage that does not require Erosion stacks to deal good damage.','Keeps Dominator functional when Effect Hit Rate or Erosion RNG is not perfect.','Dark · Multi-hit · Direct damage'),
    'Abyssal Hand':I('Dark AoE/control Technique used to spread pressure and debuffs across multiple targets.','Excellent in Arena/Tournament hybrids where broad Erosion/Slow pressure matters.','Dark · AoE · Debuff'),
    'Shadow of Termination':I('Single-target Dark finisher that cashes out the Erosion-oriented damage plan.','The kill-pressure payoff in Arena and 2v2.','Dark · Finisher'),
    'Shadow Erosion':I('Core Charm for the Erosion damage engine.','Mandatory whenever the bar is actually trying to win through Erosion rather than pure support.','Erosion'),
    'Linked Misfortune':I('Accelerates Erosion/debuff stack generation.','Pairs with Shadow Erosion to raise the ceiling of the Dark DPS build.','Erosion support'),
    'Shadow Vengeance':I('Defensive/offensive safety-window Charm that helps Dominator survive long enough to finish a damage cycle.','Very valuable in PvP where fragile Sage builds otherwise die before their setup pays off.','Survival · Damage window'),
    "Night's Blessing":I('General Dark-damage scaling Charm.','A standard selfish DPS slot in the Erosion/direct-damage build.','Dark damage'),
    'Aberrancy':I('Broad debuff-oriented Charm whose value rises when several enemies/effects are in play.','More attractive in 4v4 than solo Arena because team fights provide more debuff interactions.','Debuff utility')
  };

  const finePointer=()=>matchMedia('(hover:hover) and (pointer:fine)').matches;
  let layer=null,active=null,closeTimer=0,raf=0;
  const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  function ensureLayer(){
    if(layer) return layer;
    layer=document.createElement('div');
    layer.className='buildSkillTipLayer';
    layer.setAttribute('role','tooltip');
    layer.id='buildSkillTooltip';
    document.body.append(layer);
    return layer;
  }
  function dataFor(el){
    const name=el.textContent.trim();
    const kind=el.closest('.skillGroup')?.querySelector(':scope > span')?.textContent.trim()?.replace(/s$/,'')||'Skill';
    const info=INFO[name]||I('This skill is part of the selected loadout. Exact values and scaling depend on its rarity, level and ascension.','See the build notes for why it is equipped in this setup.');
    return {name,kind,...info};
  }
  function position(){
    if(!layer||!active||!active.isConnected) return close();
    const r=active.getBoundingClientRect(),w=layer.offsetWidth||300,h=layer.offsetHeight||120,pad=8,gap=7;
    let left=r.left+(r.width-w)/2;
    left=Math.max(pad,Math.min(left,innerWidth-w-pad));
    const roomBelow=innerHeight-r.bottom-gap;
    let top=roomBelow>=h+pad?r.bottom+gap:r.top-h-gap;
    top=Math.max(pad,Math.min(top,innerHeight-h-pad));
    layer.style.left=Math.round(left)+'px';
    layer.style.top=Math.round(top)+'px';
  }
  function open(el){
    clearTimeout(closeTimer);
    const d=dataFor(el),tip=ensureLayer();
    if(active&&active!==el) active.setAttribute('aria-expanded','false');
    active=el;
    const tags=(d.meta||'').split('·').map(x=>x.trim()).filter(Boolean);
    tip.innerHTML=`<div class="buildSkillTipHead"><strong>${esc(d.name)}</strong><span>${esc(d.kind)}</span></div><div class="buildSkillTipMeta">${tags.map(x=>`<i>${esc(x)}</i>`).join('')}</div><p class="buildSkillTipEffect">${esc(d.effect)}</p><p class="buildSkillTipWhy"><b>Why here:</b> ${esc(d.why)}</p>`;
    el.setAttribute('aria-describedby',tip.id);
    el.setAttribute('aria-expanded','true');
    tip.classList.add('open');
    requestAnimationFrame(position);
  }
  function close(){
    clearTimeout(closeTimer);
    if(active){active.setAttribute('aria-expanded','false');active.removeAttribute('aria-describedby');}
    active=null;
    layer?.classList.remove('open');
  }
  function scheduleClose(){clearTimeout(closeTimer);closeTimer=setTimeout(close,70)}
  function prep(root=document){
    root.querySelectorAll?.('#buildContent .skillGroup b:not([data-skill-tooltip])').forEach(el=>{
      el.dataset.skillTooltip='1';
      el.tabIndex=0;
      el.setAttribute('role','button');
      el.setAttribute('aria-haspopup','true');
      el.setAttribute('aria-expanded','false');
      el.addEventListener('mouseenter',()=>{if(finePointer())open(el)});
      el.addEventListener('mouseleave',()=>{if(finePointer())scheduleClose()});
      el.addEventListener('focus',()=>open(el));
      el.addEventListener('blur',()=>{if(finePointer())scheduleClose()});
      el.addEventListener('click',e=>{
        if(finePointer()) return;
        e.preventDefault();e.stopPropagation();
        active===el?close():open(el);
      });
      el.addEventListener('keydown',e=>{
        if(e.key==='Escape'){close();el.blur();return;}
        if((e.key==='Enter'||e.key===' ')&&!finePointer()){e.preventDefault();active===el?close():open(el);}
      });
    });
  }
  document.addEventListener('pointerdown',e=>{if(active&&!e.target.closest?.('#buildContent .skillGroup b[data-skill-tooltip]'))close()});
  document.addEventListener('keydown',e=>{if(e.key==='Escape')close()});
  addEventListener('resize',()=>{if(active)position()});
  document.addEventListener('scroll',()=>{if(!active||raf)return;raf=requestAnimationFrame(()=>{raf=0;position()})},true);
  document.addEventListener('DOMContentLoaded',()=>{
    const host=document.getElementById('buildContent');
    prep(document);
    if(host)new MutationObserver(()=>{if(active&&!active.isConnected)close();prep(document)}).observe(host,{subtree:true,childList:true});
  });
  addEventListener('load',()=>prep(document));
})();
</script>
'''.strip()


def install(text: str) -> str:
    # Replace in place if an older revision is already present.
    if '<style id="build-skill-tooltips-v1">' in text:
        a = text.index('<style id="build-skill-tooltips-v1">')
        b = text.find('</script>', a)
        if b < 0:
            raise RuntimeError('Skill tooltip block starts but has no closing script tag')
        b += len('</script>')
        return text[:a] + PAYLOAD + text[b:]
    if END not in text:
        raise RuntimeError('Build injection end marker missing')
    return text.replace(END, PAYLOAD + '\n' + END, 1)


for path in (INDEX, INJECT):
    original = path.read_text(encoding='utf-8')
    patched = install(original)
    path.write_text(patched, encoding='utf-8')

restore = RESTORE.read_text(encoding='utf-8')
if "'BUILD_SKILL_TOOLTIPS_V1'" not in restore:
    anchor = "    'META_BUILD_MODES_V1',\n"
    if anchor not in restore:
        raise RuntimeError('Restore required-token anchor missing')
    restore = restore.replace(anchor, anchor + "    'BUILD_SKILL_TOOLTIPS_V1',\n", 1)
    RESTORE.write_text(restore, encoding='utf-8')

print('Installed hover/focus and mobile tap tooltips for Build skills')
