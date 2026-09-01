from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

MARK = 'BUILD_ROLL_GUIDE_V1'
if MARK in s:
    print('Build roll guide already installed')
    raise SystemExit(0)

payload = r'''
<style id="build-roll-guide-v1">
/* BUILD_ROLL_GUIDE_V1
   Compact early-S2 refine roll reference under Builds > Substats. */
.rollGuide{border-top:1px solid color-mix(in srgb,var(--line) 72%,transparent);padding-top:7px;margin-top:0}
.rollGuide>summary{list-style:none;cursor:pointer;display:flex;align-items:center;justify-content:space-between;gap:10px;color:var(--body-text);font-size:9px;font-weight:850;letter-spacing:.04em;user-select:none}
.rollGuide>summary::-webkit-details-marker{display:none}
.rollGuide>summary:after{content:'+';color:var(--green);font-size:13px;font-weight:900;line-height:1}
.rollGuide[open]>summary:after{content:'−'}
.rollGuide>summary small{color:var(--muted);font-size:8px;font-weight:750;letter-spacing:0}
.rollGuideBody{margin-top:8px;border:1px solid var(--line);border-radius:10px;overflow:visible;background:var(--bg)}
.rollGuideNote{padding:8px 10px;border-bottom:1px solid var(--line);color:var(--muted);font-size:8px;line-height:1.45}
.rollGuideGrid{display:grid;grid-template-columns:minmax(145px,1fr) minmax(115px,.72fr)}
.rollGuideRow{display:contents}
.rollGuideRow>span{min-width:0;padding:7px 9px;border-bottom:1px solid color-mix(in srgb,var(--line) 72%,transparent);font-size:8px;line-height:1.35}
.rollGuideRow>span:first-child{color:var(--body-text);font-weight:750}
.rollGuideRow>span:last-child{color:var(--ink);font-weight:850;text-align:right;border-left:1px solid color-mix(in srgb,var(--line) 72%,transparent)}
.rollGuideRow:last-child>span{border-bottom:0}
.rollHelp{position:relative;display:inline-grid;place-items:center;width:14px;height:14px;margin-left:4px;border:1px solid var(--gold);border-radius:50%;color:var(--gold);font-size:8px;font-weight:900;line-height:1;vertical-align:middle;cursor:help;outline:0}
.rollHelp:hover:after,.rollHelp:focus:after{content:attr(data-tip);position:absolute;z-index:100;right:-2px;bottom:calc(100% + 7px);width:min(255px,72vw);padding:8px 9px;border:1px solid var(--line);border-radius:8px;background:var(--surface);color:var(--body-text);font-size:9px;font-weight:650;line-height:1.4;text-align:left;white-space:normal;box-shadow:0 8px 22px #0004}
.rollGuideSources{padding:8px 10px;color:var(--muted);font-size:8px;line-height:1.4;border-top:1px solid var(--line)}
@media(max-width:620px){.rollGuideGrid{grid-template-columns:minmax(0,1fr) minmax(105px,.72fr)}.rollGuideRow>span{font-size:9px;padding:8px}.rollHelp:hover:after,.rollHelp:focus:after{right:-8px}}
</style>
<script id="build-roll-guide-v1-script">
(()=>{
  const MARK='BUILD_ROLL_GUIDE_V1';
  const rows=[
    ['ATK','Scales with gear level',1,'No single season-wide cap. Flat ATK affixes scale with the receiving gear level; current English-client early-S2 maximum still needs a direct Affix Preview capture.'],
    ['DEF','Scales with gear level',1,'No single season-wide cap. Flat DEF affixes scale with gear level; exact current early-S2 maximum has not been directly confirmed on the English client.'],
    ['HP','Scales with gear level',1,'No single season-wide cap. Flat HP affixes scale with gear level; exact current early-S2 maximum has not been directly confirmed on the English client.'],
    ['SPD','Scales with gear level',1,'No single season-wide cap. Flat SPD affixes scale with gear level; exact current early-S2 maximum has not been directly confirmed on the English client.'],
    ['Crit Rate','5.00%',0,''],
    ['Block Rate','≈ 5.00%',1,'Approximate early-S2 single-stat cap inferred from the same pre-160 affix tier. Needs direct English-client Affix Preview confirmation.'],
    ['Crit RES','≈ 5.00%',1,'Approximate early-S2 single-stat cap inferred from the same pre-160 affix tier. Needs direct English-client Affix Preview confirmation.'],
    ['Accuracy','≈ 5.00%',1,'Approximate early-S2 single-stat cap inferred from the same pre-160 affix tier. Needs direct English-client Affix Preview confirmation.'],
    ['Crit Rate + Crit DMG','5.12% + 7.68%',0,''],
    ['Block Rate + Block Efficiency','5.12% + 7.68%',0,''],
    ['Crit Rate + Accuracy','5.12% + 5.12%',0,''],
    ['Crit RES + Block Rate','5.12% + 5.12%',0,''],
    ['DMG RES + Healing Boost','2.56% + 10.24%',0,''],
    ['PvP Bonus DMG + PvP DMG RES','5.12% + 5.12%',0,''],
    ['PvE Bonus DMG + PvE DMG RES','5.12% + 5.12%',0,''],
    ['Crit DMG (single)','≈ 7.50%',1,'Approximate only. Current gamefile tables clearly expose Crit DMG in the paired Crit Rate + Crit DMG affix; a standalone early-S2 Crit DMG cap has not been directly confirmed.'],
    ['Healing Boost (single)','≈ 10.00%',1,'Approximate only. Current gamefile tables clearly expose Healing Boost in the paired DMG RES + Healing Boost affix; a standalone early-S2 Healing Boost cap has not been directly confirmed.']
  ];
  const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const help=tip=>`<span class="rollHelp" tabindex="0" role="note" aria-label="Approximate; not confirmed" title="Approximate; not confirmed" data-tip="${esc(tip)}">?</span>`;
  const html=()=>`<details class="rollGuide"><summary><span>Roll guide</span><small>Early S2 · gear &lt;160</small></summary><div class="rollGuideBody"><div class="rollGuideNote">Current pre-160 refine caps. <b>?</b> means approximate or not yet directly confirmed on the English client.</div><div class="rollGuideGrid">${rows.map(([name,val,approx,tip])=>`<div class="rollGuideRow"><span>${esc(name)}${approx?help(tip):''}</span><span>${esc(val)}</span></div>`).join('')}</div><div class="rollGuideSources">Special dual-stat caps use older-server S2 scaling cross-checked against the current refine affix pool. Lv160+ inheritance changes these values, so this table is intentionally early-S2 only.</div></div></details>`;
  let queued=false;
  function apply(){
    queued=false;
    document.querySelectorAll('#buildContent .buildQuickStats').forEach(quick=>{
      if(quick.querySelector(':scope > .rollGuide')) return;
      const sub=quick.querySelector(':scope > .quickSubstats');
      if(sub) sub.insertAdjacentHTML('afterend',html());
    });
  }
  function queue(){if(queued)return;queued=true;requestAnimationFrame(apply)}
  document.addEventListener('DOMContentLoaded',()=>{
    const host=document.getElementById('buildContent');
    if(host) new MutationObserver(queue).observe(host,{subtree:true,childList:true});
    queue();
  });
  window.addEventListener('load',queue);
})();
</script>
'''

if '</body>' not in s:
    raise SystemExit('index.html has no </body>')
s = s.replace('</body>', payload + '\n</body>', 1)
p.write_text(s, encoding='utf-8')
print('Installed early-S2 Build roll guide')
