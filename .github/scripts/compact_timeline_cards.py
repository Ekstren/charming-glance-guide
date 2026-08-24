from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
marker = '/* TIMELINE_COMPACT_RENDERER_V1 */'
if marker in s:
    print('Compact timeline renderer already present')
    raise SystemExit(0)

patch = r'''
<style>
/* TIMELINE_COMPACT_RENDERER_V1 */
.timelineCardDetails{margin-top:6px;border-top:1px solid var(--line)}
.timelineCardDetails>summary{cursor:pointer;list-style:none;color:var(--muted);font-size:9px;font-weight:850;padding:6px 0 2px;width:max-content}
.timelineCardDetails>summary::-webkit-details-marker{display:none}
.timelineCardDetails>summary:after{content:' +';color:var(--green)}
.timelineCardDetails[open]>summary:after{content:' −'}
.timelineCardDetailsBody{color:var(--secondary-text);font-size:11px;line-height:1.5;padding:3px 0 2px}
.timelineCardDetailsBody p{font-size:inherit!important;color:inherit!important;margin:0!important}
.timelineNowCard .timelineCardDetails{margin-top:5px}
.timelineNowCard .timelineCardDetails>summary{font-size:8px;padding-top:4px}
.timelineNowCard .timelineCardDetailsBody{font-size:8px}
.timelineNowBadge{display:inline-flex;margin-left:5px;padding:1px 5px;border-radius:999px;border:1px solid rgba(213,166,83,.45);color:var(--gold);font-size:7px;font-weight:900;letter-spacing:.05em;vertical-align:1px}
</style>
<script>
(() => {
  'use strict';
  const COMPACT_MARK='timelineCompactDone';
  const explicit = [
    [/oceanic festival/i, 'Aug 18–31. Do the daily Ice Cream Shop and Ocean Chase, then spend Festival currency on the rewards you actually need.'],
    [/bingo draw/i, 'Aug 19–26 on Charming Glance. Clear daily missions first; use Destiny Fruits only if you are pushing Bingo or overlapping Oceanic objectives.'],
    [/lucky scratch/i, 'Starts Aug 26. Save Material Realm tools now, then spend them while Lucky Scratch is active to feed its ticket missions.'],
    [/grand treasure hunt|treasure hunt/i, 'Weekly phase. Auroradrasil Energy carries over, so save it unless this phase has the Lv.5 reward or relic you want.'],
    [/gift code|4p7y2r9m/i, 'Redeem 4P7Y2R9M by Aug 25 for 2,000 Rolla + 120 Dawnium. Exact cutoff time is community-reported, so claim it early.'],
    [/season 1.*(end|final|prep)|season prep/i, 'Finish Season 1 scoring and any last upgrades before the Aug 30, 6:00 AM PT reset. Preserve the S2 materials your planner marks as reserved.'],
    [/season 2.*(start|open)|loong haven/i, 'Season 2 opens Aug 30 at the 6:00 AM PT reset. Expect Tier IV progression and a fresh seasonal-growth loop; update the planner after rollover.']
  ];

  function plain(node){ return (node?.textContent||'').replace(/\s+/g,' ').trim(); }
  function titleFor(card){
    const firstP=card.querySelector('p');
    return plain(card.querySelector('strong,h3,b'))+' '+plain(firstP);
  }
  function summaryFor(title,text){
    for(const [re,sum] of explicit) if(re.test(title+' '+text)) return sum;
    const sentences=(text.match(/[^.!?]+[.!?]+|[^.!?]+$/g)||[]).map(x=>x.trim()).filter(Boolean);
    let out=sentences.slice(0,2).join(' ');
    if(!out) out=text;
    if(out.length>190){
      out=out.slice(0,187).replace(/\s+\S*$/,'').trim()+'…';
    }
    return out;
  }
  function addDetails(afterNode, original){
    const details=document.createElement('details');
    details.className='timelineCardDetails';
    const summary=document.createElement('summary');
    summary.textContent='Details';
    const body=document.createElement('div');
    body.className='timelineCardDetailsBody';
    body.appendChild(original.cloneNode(true));
    details.append(summary,body);
    afterNode.insertAdjacentElement('afterend',details);
  }
  function compactEntry(card){
    if(card.dataset[COMPACT_MARK]) return;
    const ps=[...card.querySelectorAll('p')];
    if(ps.length<2){ card.dataset[COMPACT_MARK]='1'; return; }
    const desc=ps[ps.length-1];
    const full=plain(desc);
    const title=titleFor(card);
    if(!full){ card.dataset[COMPACT_MARK]='1'; return; }
    const short=summaryFor(title,full);
    if(short!==full || full.length>210){
      const clone=desc.cloneNode(true);
      desc.textContent=short;
      addDetails(desc,clone);
    }
    card.dataset[COMPACT_MARK]='1';
  }
  function compactNow(card){
    if(card.dataset[COMPACT_MARK]) return;
    const desc=card.querySelector('small');
    if(!desc){ card.dataset[COMPACT_MARK]='1'; return; }
    const full=plain(desc);
    const title=plain(card.querySelector('strong'));
    if(!full){ card.dataset[COMPACT_MARK]='1'; return; }
    const short=summaryFor(title,full);
    if(short!==full || full.length>150){
      const clone=desc.cloneNode(true);
      desc.textContent=short;
      addDetails(desc,clone);
    }
    card.dataset[COMPACT_MARK]='1';
  }
  function injectCodeAlert(){
    const grid=document.querySelector('#timelineNow .timelineNowGrid');
    if(!grid || grid.querySelector('[data-code-alert="4P7Y2R9M"]')) return;
    // Community sources agree on an Aug 25 expiry, but do not consistently publish the cutoff hour.
    const now=Date.now();
    const stop=new Date('2026-08-26T06:00:00-07:00').getTime();
    if(now>=stop) return;
    const card=document.createElement('div');
    card.className='timelineNowCard';
    card.dataset.codeAlert='4P7Y2R9M';
    card.innerHTML='<strong>Gift code: 4P7Y2R9M <span class="timelineNowBadge">UNCONFIRMED CUTOFF</span></strong><small>Redeem by Aug 25 for 2,000 Rolla + 120 Dawnium. Multiple current code trackers agree on the date; exact cutoff time is not official, so claim it early.</small>';
    grid.prepend(card);
  }
  function run(){
    document.querySelectorAll('.timeline .entry').forEach(compactEntry);
    document.querySelectorAll('#timelineNow .timelineNowCard').forEach(compactNow);
    injectCodeAlert();
    document.querySelectorAll('#timelineNow .timelineNowCard').forEach(compactNow);
  }
  let queued=false;
  function queue(){ if(queued) return; queued=true; requestAnimationFrame(()=>{queued=false;run();}); }
  const observer=new MutationObserver(queue);
  function start(){
    run();
    const root=document.querySelector('#timelineSection')||document.body;
    observer.observe(root,{childList:true,subtree:true});
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',start,{once:true}); else start();
})();
</script>
'''

idx = s.lower().rfind('</body>')
if idx < 0:
    raise SystemExit('Could not locate </body>')
s = s[:idx] + patch + '\n' + s[idx:]
p.write_text(s, encoding='utf-8')
print('Added compact timeline renderer and current code alert')
