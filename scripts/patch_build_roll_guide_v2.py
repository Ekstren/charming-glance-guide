from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

payload = r'''
<style id="build-roll-guide-v1">
/* BUILD_ROLL_GUIDE_V2
   Compact, class-specific early-S2 refine roll reference under Builds > Substats. */
.rollGuide{border-top:1px solid color-mix(in srgb,var(--line) 72%,transparent);padding-top:7px;margin-top:0}
.rollGuide>summary{list-style:none;cursor:pointer;display:flex;align-items:center;gap:9px;color:var(--body-text);font-size:9px;font-weight:850;letter-spacing:.04em;user-select:none}
.rollGuide>summary::-webkit-details-marker{display:none}
.rollGuide>summary small{color:var(--muted);font-size:8px;font-weight:750;letter-spacing:0;margin-left:auto}
.rollGuide>summary:after{content:'+';color:var(--green);font-size:13px;font-weight:900;line-height:1}
.rollGuide[open]>summary:after{content:'−'}
.rollGuideBody{margin-top:7px;border:1px solid var(--line);border-radius:9px;background:var(--bg);overflow:visible}
.rollGuideNote{padding:5px 7px;border-bottom:1px solid var(--line);color:var(--muted);font-size:7.5px;line-height:1.3}
.rollGuideGrid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:4px;padding:6px}
.rollGuideRow{min-width:0;display:grid;grid-template-columns:minmax(0,1fr) auto;align-items:center;gap:7px;padding:5px 6px;border:1px solid color-mix(in srgb,var(--line) 76%,transparent);border-radius:6px;background:var(--surface)}
.rollGuideName{min-width:0;color:var(--body-text);font-size:8px;font-weight:760;line-height:1.2}
.rollGuideValue{color:var(--ink);font-size:8.5px;font-weight:850;line-height:1.15;text-align:right;white-space:nowrap}
.rollGuideValue.rollScaling{color:var(--secondary-text);font-size:7.5px}
.rollHelp{appearance:none;border:0;background:none;padding:0;margin:0 0 0 3px;color:var(--green);font:inherit;font-size:8.5px;font-weight:900;line-height:1;cursor:help;text-decoration:underline;text-underline-offset:2px;position:relative;display:inline;vertical-align:baseline;outline:none}
.rollHelp:hover,.rollHelp:focus{color:var(--ink)}
.rollHelp:hover:after,.rollHelp:focus:after{content:attr(data-tip);position:absolute;z-index:100;left:0;bottom:calc(100% + 6px);width:min(245px,72vw);padding:7px 8px;border:1px solid var(--line);border-radius:8px;background:var(--surface);color:var(--body-text);font-size:8.5px;font-weight:650;line-height:1.35;text-align:left;white-space:normal;box-shadow:0 8px 22px #0004;text-decoration:none}
.rollGuideSources{padding:5px 7px;color:var(--muted);font-size:7px;line-height:1.3;border-top:1px solid var(--line)}
@media(max-width:620px){
  .rollGuideGrid{grid-template-columns:1fr;gap:4px;padding:5px}
  .rollGuideRow{padding:6px 7px}
  .rollGuideName{font-size:8.5px}.rollGuideValue{font-size:9px}
  .rollHelp:hover:after,.rollHelp:focus:after{left:-6px;width:min(235px,78vw)}
}
</style>
<script id="build-roll-guide-v1-script">
(()=>{
  const R={
    atk:['ATK','Gear-level scaling',1,'No single season-wide cap. Flat ATK scales with the receiving gear level; the exact current English-client early-S2 maximum still needs a direct Affix Preview capture.',1],
    def:['DEF','Gear-level scaling',1,'No single season-wide cap. Flat DEF scales with the receiving gear level; the exact current English-client early-S2 maximum still needs a direct Affix Preview capture.',1],
    hp:['HP','Gear-level scaling',1,'No single season-wide cap. Flat HP scales with the receiving gear level; the exact current English-client early-S2 maximum still needs a direct Affix Preview capture.',1],
    spd:['SPD','Gear-level scaling',1,'No single season-wide cap. Flat SPD scales with the receiving gear level; the exact current English-client early-S2 maximum still needs a direct Affix Preview capture.',1],
    crit:['Crit Rate','5.00%',0,'',0],
    critdmg:['Crit DMG','≈ 7.50%',1,'Approximate standalone early-S2 Crit DMG cap. The paired Crit Rate + Crit DMG affix is confirmed, but this standalone maximum has not been directly confirmed on the English client.',0],
    block:['Block Rate','≈ 5.00%',1,'Approximate early-S2 standalone Block Rate cap inferred from the same pre-160 affix tier. Needs direct English-client Affix Preview confirmation.',0],
    acc:['Accuracy','≈ 5.00%',1,'Approximate early-S2 standalone Accuracy cap inferred from the same pre-160 affix tier. Needs direct English-client Affix Preview confirmation.',0],
    em:['Elemental Mastery','?',1,'The affix is recommended for this class, but I could not confirm a trustworthy current pre-160 English-client maximum yet.',0],
    ehr:['Effect Hit Rate','?',1,'The affix is recommended for DPS Dominator, but I could not confirm a trustworthy current pre-160 English-client maximum yet.',0],
    dmgres:['DMG RES','?',1,'The affix is recommended for healer Dominator, but I could not confirm a trustworthy current pre-160 standalone maximum yet.',0],
    heal:['Healing Boost','≈ 10.00%',1,'Approximate standalone early-S2 Healing Boost cap. The paired DMG RES + Healing Boost affix is confirmed, but this standalone maximum has not been directly confirmed.',0],
    critpair:['Crit Rate + Crit DMG','5.12% + 7.68%',0,'',0],
    critacc:['Crit Rate + Accuracy','5.12% + 5.12%',0,'',0],
    blockpair:['Block Rate + Block Efficiency','5.12% + 7.68%',0,'',0],
    healpair:['DMG RES + Healing Boost','2.56% + 10.24%',0,'',0]
  };
  const PROFILES={
    Conqueror:['crit','critdmg','critpair','acc','critacc','em','spd','atk'],
    Guardian:['block','blockpair','def','spd','hp'],
    Destroyer:['crit','critdmg','critpair','atk','em','acc','critacc','spd'],
    Dominator:{
      dps:['ehr','crit','critdmg','critpair','em','atk','spd'],
      heals:['heal','healpair','spd','hp','dmgres']
    }
  };
  const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const activeClass=()=>document.querySelector('#classTabs button.active')?.dataset.class||'Conqueror';
  const role=()=>{try{return localStorage.getItem('sxs-build-dominator-mode')==='heals'?'heals':'dps'}catch(_){return 'dps'}};
  const rowsFor=(cls,mode)=>{
    const keys=cls==='Dominator'?PROFILES.Dominator[mode]:PROFILES[cls];
    return (keys||PROFILES.Conqueror).map(k=>R[k]);
  };
  const help=tip=>`<button type="button" class="rollHelp" aria-label="Approximate or unconfirmed value" data-tip="${esc(tip)}">?</button>`;
  const guideHtml=(cls,mode)=>{
    const rows=rowsFor(cls,mode);
    const label=cls==='Dominator'?`${cls} · ${mode==='heals'?'Heals':'DPS'}`:cls;
    return `<details class="rollGuide" data-roll-sig="${esc(cls+'|'+mode)}"><summary><span>Roll guide</span><small>${esc(label)} · Early S2 &lt;160</small></summary><div class="rollGuideBody"><div class="rollGuideNote">Only substats recommended above are shown. <b>?</b> = approximate/unconfirmed.</div><div class="rollGuideGrid">${rows.map(([name,val,approx,tip,scaling])=>`<div class="rollGuideRow"><span class="rollGuideName">${esc(name)}${approx?help(tip):''}</span><span class="rollGuideValue${scaling?' rollScaling':''}">${esc(val)}</span></div>`).join('')}</div><div class="rollGuideSources">Pre-160 S2 reference. Confirmed special dual-stat caps use older-server S2 scaling cross-checked against the current refine pool; Lv160+ changes these values.</div></div></details>`;
  };
  let queued=false;
  function apply(){
    queued=false;
    const cls=activeClass(),mode=cls==='Dominator'?role():'dps',sig=cls+'|'+mode;
    document.querySelectorAll('#buildContent .buildQuickStats').forEach(quick=>{
      const existing=quick.querySelector(':scope > .rollGuide');
      if(existing?.dataset.rollSig===sig) return;
      const html=guideHtml(cls,mode);
      if(existing) existing.outerHTML=html;
      else quick.querySelector(':scope > .quickSubstats')?.insertAdjacentHTML('afterend',html);
    });
  }
  function queue(){if(queued)return;queued=true;requestAnimationFrame(()=>setTimeout(apply,0))}
  document.addEventListener('DOMContentLoaded',()=>{
    const host=document.getElementById('buildContent');
    if(host) new MutationObserver(queue).observe(host,{subtree:true,childList:true});
    document.getElementById('classTabs')?.addEventListener('click',queue);
    host?.addEventListener('click',e=>{if(e.target.closest?.('[data-dominator-mode]'))setTimeout(queue,0)});
    queue();
  });
  window.addEventListener('load',queue);
})();
</script>
'''

pattern = re.compile(r'<style id="build-roll-guide-v1">.*?</style>\s*<script id="build-roll-guide-v1-script">.*?</script>', re.S)
if pattern.search(s):
    s = pattern.sub(payload.strip(), s, count=1)
else:
    if '</body>' not in s:
        raise SystemExit('index.html has no </body>')
    s = s.replace('</body>', payload + '\n</body>', 1)

p.write_text(s, encoding='utf-8')
print('Installed compact class-specific Build roll guide v2')
