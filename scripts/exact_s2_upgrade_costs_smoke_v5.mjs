import { chromium } from 'playwright';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const browser=await chromium.launch({headless:true});
const page=await browser.newPage({viewport:{width:1440,height:1100}});
const errors=[];
page.on('pageerror',e=>errors.push(String(e?.stack||e)));

await page.addInitScript(()=>{
  const fixed=Date.parse('2026-09-07T12:00:00-07:00');
  const RealDate=Date;
  class FixedDate extends RealDate{
    constructor(...args){super(...(args.length?args:[fixed]));}
    static now(){return fixed;}
  }
  Object.setPrototypeOf(FixedDate,RealDate);
  window.Date=FixedDate;
});

await page.goto(pathToFileURL(path.resolve('index.html')).href,{waitUntil:'load'});
const probeReady=await page.evaluate(()=>typeof window.__sxsExactCostProbeV5==='function');
if(!probeReady) throw new Error('Exact S2 internal cost probe missing');
const got=await page.evaluate(()=>window.__sxsExactCostProbeV5());
const dom=await page.evaluate(()=>({
  marker:document.documentElement.innerHTML.includes('EXACT_S2_UPGRADE_COSTS_V5'),
  secondaryStyle:document.getElementById('secondaryCostNote')?.getAttribute('style')||'',
  methodText:document.querySelector('.methodPanel')?.innerText||''
}));

const eq=(key,expected,tol=1e-9)=>{
  const actual=got[key];
  if(!Number.isFinite(actual)||Math.abs(actual-expected)>tol) throw new Error(`${key}: expected ${expected}, got ${actual}`);
};

if(!dom.marker) throw new Error('Exact S2 marker missing');
if(got.charLen!==158) throw new Error(`Expected 158 extracted S2 Character EXP rows, got ${got.charLen}`);
if(got.fantoLen!==150) throw new Error(`Expected 150 extracted S2 Fantomon EXP rows, got ${got.fantoLen}`);
eq('gear130',16630);
eq('gear131',16795);
eq('gear160',21620);
eq('gear188',26275);
eq('skill130',12025);
eq('skill140',13230);
eq('skill160',15635);
eq('skill180',18040);
eq('relic13',33750);
eq('relic18',50625);
eq('relic27',81000);
eq('fanto130',57370/50);
eq('fanto160',91790/50);
eq('xp130',6342809);
eq('xp210',13478732);
eq('xp281',13478732);
eq('xp287',13478732);
if(Number.isFinite(got.xp288)) throw new Error(`xp288 should stop outside extracted range, got ${got.xp288}`);
eq('refined134',510);
eq('refined139',510);
eq('refined135',0);
// Pre-floor catch-up math intentionally remains unchanged.
eq('preGear121',14630);
eq('preSkill121',10265);
if(/display\s*:\s*none\s*!important/i.test(dom.secondaryStyle)) throw new Error('Secondary exact Gear costs are still force-hidden');
if(!dom.methodText.includes('1,350 Purple Sand')||!dom.methodText.includes('510 Refined Ore')||!dom.methodText.includes('Rolla is 2× Gear Ore')){
  throw new Error('Exact S2 method/source note is incomplete');
}
if(errors.length) throw new Error('Runtime errors:\n'+errors.join('\n---\n'));

console.log('Exact S2 upgrade-cost smoke passed.',{...got,methodNote:true});
await browser.close();
