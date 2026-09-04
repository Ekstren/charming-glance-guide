import { chromium } from 'playwright';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
const errors = [];
page.on('pageerror', err => errors.push(String(err?.stack || err)));

const url = pathToFileURL(path.resolve('index.html')).href;
await page.goto(url, { waitUntil: 'load' });
await page.waitForTimeout(350);

const assert = (cond, msg) => { if (!cond) throw new Error(msg); };
const openBuild = async cls => {
  await page.locator('.sectionSwitch button[data-section="builds"]').click();
  await page.locator(`#classTabs button[data-class="${cls}"]`).click();
  await page.waitForFunction(name => {
    const active = document.querySelector('#classTabs button.active')?.dataset.class;
    const quick = document.querySelector('#buildContent .buildQuickStats');
    return active === name && quick?.querySelectorAll('.quickGearRow').length === 5 && quick?.querySelectorAll('.quickGemLine').length === 5;
  }, cls, { timeout: 4000 });
  await page.waitForTimeout(80);
};
const gemRows = async () => page.locator('#buildContent .quickGearRow').evaluateAll(rows => Object.fromEntries(rows.map(row => [
  row.querySelector(':scope > b')?.textContent.trim(),
  row.querySelector('.quickGemText')?.textContent.trim()
])));

const EXPECTED = {
  Conqueror: {
    Sword: 'Obsidian > Amethyst ≥ Ruby',
    Gauntlets: 'Obsidian > Amethyst ≥ Citrine',
    Helmet: 'Citrine > Beryl = Sapphire',
    Chest: 'Moonstone > Beryl = Sapphire',
    Boots: 'Amethyst > Citrine'
  },
  Guardian: {
    Sword: 'Obsidian > Amethyst ≥ Ruby',
    Shield: 'Moonstone > Sapphire > Citrine',
    Helmet: 'Sapphire > Citrine > Beryl',
    Chest: 'Moonstone > Beryl = Sapphire',
    Boots: 'Amethyst > Citrine'
  },
  Destroyer: {
    Staff: 'Obsidian > Amethyst',
    Codex: 'Obsidian > Amethyst > Moonstone',
    Helmet: 'Citrine > Beryl = Sapphire',
    Chest: 'Moonstone',
    Boots: 'Amethyst'
  }
};

for (const cls of Object.keys(EXPECTED)) {
  await openBuild(cls);
  const rows = await gemRows();
  for (const [slot, gems] of Object.entries(EXPECTED[cls])) {
    assert(rows[slot] === gems, `${cls} ${slot} gems wrong: ${rows[slot]}`);
  }
  const note = await page.locator('#buildContent .quickGemNote').innerText();
  assert(/2 gems per gear slot/i.test(note) && /duplicates allowed/i.test(note), `${cls} gem note missing or incomplete: ${note}`);
}

await openBuild('Dominator');
await page.locator('#buildContent button[data-dominator-mode="dps"]').click();
await page.waitForFunction(() => document.querySelector('#buildContent .buildQuickStats')?.dataset.gemPrioritySig === 'Dominator|dps');
let rows = await gemRows();
assert(rows.Staff === 'Obsidian > Amethyst > Ruby', `Dominator DPS Staff gems wrong: ${rows.Staff}`);
assert(rows.Orb === 'Obsidian > Amethyst > Ruby', `Dominator DPS Orb gems wrong: ${rows.Orb}`);
assert(rows.Helmet === 'Citrine', `Dominator DPS Helmet gems wrong: ${rows.Helmet}`);
assert(rows.Chest === 'Moonstone', `Dominator DPS Chest gems wrong: ${rows.Chest}`);
assert(rows.Boots === 'Amethyst > Ruby', `Dominator DPS Boots gems wrong: ${rows.Boots}`);

await page.locator('#buildContent button[data-dominator-mode="heals"]').click();
await page.waitForFunction(() => document.querySelector('#buildContent .buildQuickStats')?.dataset.gemPrioritySig === 'Dominator|heals');
rows = await gemRows();
assert(rows.Staff === 'Amethyst', `Dominator Heals Staff gems wrong: ${rows.Staff}`);
assert(rows.Orb === 'Amber > Citrine', `Dominator Heals Orb gems wrong: ${rows.Orb}`);
assert(rows.Helmet === 'Amber > Citrine', `Dominator Heals Helmet gems wrong: ${rows.Helmet}`);
assert(rows.Chest === 'Moonstone', `Dominator Heals Chest gems wrong: ${rows.Chest}`);
assert(rows.Boots === 'Amber > Citrine', `Dominator Heals Boots gems wrong: ${rows.Boots}`);

await page.setViewportSize({ width: 390, height: 844 });
await openBuild('Conqueror');
const mobile = await page.locator('#buildContent .quickGearRow').evaluateAll(rows => rows.map(row => {
  const rr = row.getBoundingClientRect();
  const gem = row.querySelector('.quickGemLine')?.getBoundingClientRect();
  return gem ? { rowLeft: rr.left, rowRight: rr.right, gemLeft: gem.left, gemRight: gem.right } : null;
}));
assert(mobile.every(x => x && x.gemLeft >= x.rowLeft - 1 && x.gemRight <= x.rowRight + 1), `mobile gem lines overflow their slot cards: ${JSON.stringify(mobile)}`);
const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
assert(overflow <= 3, `mobile page has ${overflow}px horizontal overflow after gem priorities`);

if (errors.length) throw new Error(`page runtime errors:\n${errors.join('\n---\n')}`);
console.log('gem priority smoke passed: all S2 classes, Dominator role switch, 390px mobile containment');
await browser.close();
