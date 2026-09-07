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

// Drive the calculator through its actual form events rather than reaching into lexical JS state.
const set = async (id, value) => {
  const loc = page.locator(`#${id}`);
  assert(await loc.count() === 1, `missing input ${id}`);
  await loc.evaluate((el, next) => {
    el.value = String(next);
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
  }, value);
};

await set('charLevel', 120);
await set('charExp', 0);
await set('bedExp', 0);
await set('historicalStars', 253);
await set('targetStars', 800);
await set('skillLevel', 121);
await set('relicLevel', 13);
await set('fantomonLevel', 130);
for (const id of ['gearWeapon','gearOffhand','gearHelmet','gearArmor','gearBoots']) await set(id, 130);

await set('oreCurrent', 100000000);
await set('essenceCurrent', 100000000);
await set('sandCurrent', 100000000);
await set('sandBlueCurrent', 0);
await set('treatCurrent', 100000000);
await set('treatPremiumCurrent', 0);
await set('treatDeluxeCurrent', 0);
await set('oreRate', 0);
await set('essenceRate', 0);
await set('sandRate', 0);
await set('treatRate', 0);
await set('shopRefreshesDaily', 0);
await set('hammerCurrent', 0);
await set('knucklesCurrent', 0);
await set('shovelCurrent', 0);
await set('realmDailyOre', 0);
await set('realmDailyEssence', 0);
await set('realmDailySand', 0);
await set('refinedOreCurrent', 0);
await set('exactSkillLevels', '');
await set('exactRelicLevels', '');
await set('exactFantoLevels', '');

await page.waitForTimeout(650);
const confirm = page.locator('#confirmSeasonSnapshot');
if (await confirm.count() && await confirm.isVisible()) {
  await confirm.click();
  await page.waitForTimeout(650);
}

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

assert(/Lv\.131/i.test(state.explain + ' ' + state.rules), `Lv.120 planner does not expose the Lv.131 unlock preview: ${state.explain} / ${state.rules}`);
assert(state.targetStatus !== 'cap', `Lv.120 preview is still structurally capped: ${state.targetMessage}`);
assert(!state.oreHidden, 'Ore result inset is hidden');
assert(state.oreText.length > 3 && state.oreText !== '—', `Ore inset collapsed to a placeholder: ${state.oreText}`);
assert(!/^RAW ORE\s+\S+\s+—$/im.test(state.oreTileText), `Ore tile still contains only a dash placeholder: ${state.oreTileText}`);
assert(state.oreToolHidden, `unused Ore tool placeholder is still visible: ${state.oreToolText}`);
assert(Math.abs(state.oreTop - state.essTop) <= 4, `Ore inset top does not align with Essence: ${state.oreTop} vs ${state.essTop}`);
assert(errors.length === 0, `page runtime errors:\n${errors.join('\n---\n')}`);

await browser.close();
console.log('pre-season Primostar preview + Ore card regression smoke passed');
