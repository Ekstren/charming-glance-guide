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

  updateGearLockUI();
  updateCalculator();
})();
` });
await page.waitForTimeout(300);

const preview = await page.evaluate(() => ({
  targetStatus: document.getElementById('targetStatus')?.textContent?.trim() || '',
  targetMessage: document.getElementById('targetMessage')?.textContent || '',
  explain: document.getElementById('currentBreakdownExplain')?.textContent || '',
  rules: document.getElementById('seasonRulesHint')?.textContent || '',
}));

assert(/Lv\.131/i.test(preview.explain + ' ' + preview.rules), `Lv.120 planner does not expose the Lv.131 unlock preview: ${preview.explain}`);
assert(preview.targetStatus !== 'cap', `Lv.120 preview is still structurally capped with abundant resources: ${preview.targetMessage}`);

// Force the genuine structural-cap branch with Gear locked. This reproduces the screenshot
// edge case and verifies that the header shows the actual requested target (800), while the
// Ore card renders a normal raw Remaining row and hides the empty Realm-tool placeholder.
await page.addScriptTag({ content: `
(() => {
  gearLocked = true;
  updateGearLockUI();
  updateCalculator();
})();
` });
await page.waitForFunction(() => document.getElementById('targetStatus')?.textContent?.trim() === 'cap', null, { timeout: 5000 });
await page.waitForTimeout(80);

const capState = await page.evaluate(() => {
  const ore = document.getElementById('oreBalance');
  const oreTool = document.getElementById('oreToolBalance');
  const ess = document.getElementById('essenceBalance');
  const oreRect = ore?.getBoundingClientRect();
  const essRect = ess?.getBoundingClientRect();
  return {
    eyebrow: document.getElementById('resultEyebrow')?.textContent?.trim() || '',
    headline: document.getElementById('currentStars')?.textContent?.trim() || '',
    status: document.getElementById('targetStatus')?.textContent?.trim() || '',
    oreText: ore?.textContent?.trim() || '',
    oreHidden: !!ore?.hidden,
    oreToolHidden: !!oreTool?.hidden,
    oreToolText: oreTool?.textContent?.trim() || '',
    oreTop: oreRect?.top ?? 0,
    essTop: essRect?.top ?? 0,
    oreHeight: oreRect?.height ?? 0,
    essHeight: essRect?.height ?? 0,
  };
});

assert(capState.status === 'cap', `locked regression scenario did not enter cap branch: ${capState.status}`);
assert(/Requested target/i.test(capState.eyebrow), `cap branch eyebrow wrong: ${capState.eyebrow}`);
assert(capState.headline === '800', `cap branch mislabeled baseline as requested target: ${capState.headline}`);
assert(!capState.oreHidden && /Remaining:/i.test(capState.oreText), `Ore card did not render normal Remaining row: ${capState.oreText}`);
assert(capState.oreToolHidden, `empty Ore tool row is still visible: ${capState.oreToolText}`);
assert(Math.abs(capState.oreTop - capState.essTop) < 3, `Ore inset top does not align with Essence: ${capState.oreTop} vs ${capState.essTop}`);
assert(Math.abs(capState.oreHeight - capState.essHeight) < 3, `Ore inset height does not match Essence: ${capState.oreHeight} vs ${capState.essHeight}`);

assert(errors.length === 0, `page runtime errors:\n${errors.join('\n---\n')}`);
await browser.close();
console.log('pre-season Primostar preview + Ore card regression smoke passed');
