import { chromium } from 'playwright';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1100, height: 1000 } });
const errors = [];
page.on('pageerror', err => errors.push(String(err?.stack || err)));

await page.goto(pathToFileURL(path.resolve('index.html')).href, { waitUntil: 'load' });
await page.waitForTimeout(250);

const assert = (cond, msg) => { if (!cond) throw new Error(msg); };
await page.locator('.sectionSwitch button[data-section="calculator"]').click();
await page.waitForTimeout(100);

// Run state changes in the page's own classic-script world so the calculator's global
// lexical bindings (snapshotSeason, gearLocked, updateCalculator, etc.) are available.
await page.addScriptTag({ content: `
(() => {
  const set = (id, value) => {
    const el = document.getElementById(id);
    if (!el) throw new Error('missing input ' + id);
    el.value = String(value);
  };

  snapshotSeason = 's2';
  snapshotStateLoaded = true;
  snapshotAtMs = Date.now();
  snapshotCarry = { ore: 0, essence: 0, sand: 0, treat: 0, exp: 0 };
  gearLocked = false;

  set('charLevel', 120);
  set('charExp', 0);
  set('bedExp', 0);
  set('historicalStars', 253);
  set('targetStars', 800);
  set('skillLevel', 121);
  set('relicLevel', 13);
  set('fantomonLevel', 130);
  for (const id of ['gearWeapon','gearOffhand','gearHelmet','gearArmor','gearBoots']) set(id, 130);

  set('oreCurrent', 100000000);
  set('essenceCurrent', 100000000);
  set('sandCurrent', 100000000);
  set('sandBlueCurrent', 0);
  set('treatCurrent', 100000000);
  set('treatPremiumCurrent', 0);
  set('treatDeluxeCurrent', 0);
  set('oreRate', 0);
  set('essenceRate', 0);
  set('sandRate', 0);
  set('treatRate', 0);
  set('shopRefreshesDaily', 0);
  set('hammerCurrent', 0);
  set('knucklesCurrent', 0);
  set('shovelCurrent', 0);
  set('realmDailyOre', 0);
  set('realmDailyEssence', 0);
  set('realmDailySand', 0);
  set('refinedOreCurrent', 0);
  set('exactSkillLevels', '');
  set('exactRelicLevels', '');
  set('exactFantoLevels', '');

  updateCalculator();
})();
` });
await page.waitForTimeout(350);

const state = await page.evaluate(() => {
  const ore = document.getElementById('oreBalance');
  const oreTool = document.getElementById('oreToolBalance');
  const ess = document.getElementById('essenceBalance');
  const oreRect = ore?.getBoundingClientRect();
  const essRect = ess?.getBoundingClientRect();
  const oreTile = ore?.closest('.planCosts > span');
  return {
    targetStatus: document.getElementById('targetStatus')?.textContent?.trim() || '',
    targetMessage: document.getElementById('targetMessage')?.textContent || '',
    explain: document.getElementById('currentBreakdownExplain')?.textContent || '',
    rules: document.getElementById('seasonRulesHint')?.textContent || '',
    headline: document.getElementById('currentStars')?.textContent?.trim() || '',
    oreText: ore?.textContent?.trim() || '',
    oreTileText: oreTile?.innerText?.trim() || '',
    oreHidden: !!ore?.hidden,
    oreToolHidden: !!oreTool?.hidden,
    oreToolText: oreTool?.textContent?.trim() || '',
    oreTop: oreRect?.top ?? 0,
    essTop: essRect?.top ?? 0,
  };
});

assert(/Lv\.131/i.test(state.explain + ' ' + state.rules), `Lv.120 planner does not expose the Lv.131 unlock preview: ${state.explain}`);
assert(state.targetStatus !== 'cap', `Lv.120 preview is still structurally capped with abundant resources: ${state.targetMessage}`);
assert(!state.oreHidden, 'Ore result inset is hidden');
assert(state.oreText.length > 3 && state.oreText !== '—', `Ore inset collapsed to a placeholder: ${state.oreText}`);
assert(!/^RAW ORE\s+\S+\s+—$/im.test(state.oreTileText), `Ore tile still contains only a dash placeholder: ${state.oreTileText}`);
assert(state.oreToolHidden, `unused Ore tool placeholder is still visible: ${state.oreToolText}`);
assert(Math.abs(state.oreTop - state.essTop) <= 4, `Ore inset top does not align with Essence: ${state.oreTop} vs ${state.essTop}`);

assert(errors.length === 0, `page runtime errors:\n${errors.join('\n---\n')}`);
await browser.close();
console.log('pre-season Primostar preview + Ore card regression smoke passed');
