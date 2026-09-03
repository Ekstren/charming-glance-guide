from pathlib import Path
import subprocess

subprocess.run(['python','.github/patch-fantasia-ascent-builds-v1.py'],check=True)

for path in [Path('index.html'),Path('.github/build-fantomons-inject.html')]:
    text=path.read_text(encoding='utf-8')
    old="""    const base=pools[role]||[];
    if(guardianDps){
"""
    new="""    if(role==='Solo'&&cls==='Dominator'&&typeof dominatorBuildMode==='function'&&dominatorBuildMode()==='heals') return pools.Dungeon||pools.Solo||[];
    const base=pools[role]||[];
    if(guardianDps){
"""
    if text.count(old)!=1:
        raise SystemExit(f'{path}: Dominator solo-heals Fantomon anchor count={text.count(old)}')
    text=text.replace(old,new,1)
    path.write_text(text,encoding='utf-8')

smoke=Path('scripts/site_smoke_test.mjs')
text=smoke.read_text(encoding='utf-8')
old=r'''await waitBuild('Dominator');
await page.locator('#buildContent .metaBuildTabs button[data-meta-mode="Fantasia Ascent"]').click();
await page.locator('#buildContent button[data-dominator-mode="dps"]').click();
await page.waitForTimeout(80);
fantasiaTitles=await buildTitles();
assert(fantasiaTitles.length===1 && /^Fantasia Ascent/i.test(fantasiaTitles[0]||''), `Dominator DPS Fantasia build missing: ${fantasiaTitles.join(' | ')}`);
await page.locator('#buildContent button[data-dominator-mode="heals"]').click();
await page.waitForTimeout(80);
fantasiaTitles=await buildTitles();
assert(fantasiaTitles.length===1 && /^Fantasia Ascent/i.test(fantasiaTitles[0]||''), `Dominator Heals Fantasia build missing: ${fantasiaTitles.join(' | ')}`);
// Restore the existing Dominator smoke assumptions.
await page.locator('#buildContent .metaBuildTabs button[data-meta-mode="Dungeon"]').click();
await page.locator('#buildContent button[data-dominator-mode="dps"]').click();
await page.waitForTimeout(80);
'''
new=r'''await page.evaluate(()=>{
  localStorage.setItem('sxs-build-meta-mode','Fantasia Ascent');
  localStorage.setItem('sxs-build-dominator-mode','dps');
});
await waitBuild('Dominator');
await page.waitForFunction(()=>[...document.querySelectorAll('#buildContent .buildGrid .buildCard')].some(x=>x.dataset.role==='Fantasia Ascent'&&x.dataset.buildRole==='dps'&&!x.hidden&&getComputedStyle(x).display!=='none'),null,{timeout:3000});
fantasiaTitles=await buildTitles();
assert(fantasiaTitles.length===1 && /^Fantasia Ascent/i.test(fantasiaTitles[0]||''), `Dominator DPS Fantasia build missing: ${fantasiaTitles.join(' | ')}`);
await page.locator('#buildContent button[data-dominator-mode="heals"]').click();
await page.waitForFunction(()=>[...document.querySelectorAll('#buildContent .buildGrid .buildCard')].some(x=>x.dataset.role==='Fantasia Ascent'&&x.dataset.buildRole==='heals'&&!x.hidden&&getComputedStyle(x).display!=='none'),null,{timeout:3000});
fantasiaTitles=await buildTitles();
assert(fantasiaTitles.length===1 && /^Fantasia Ascent/i.test(fantasiaTitles[0]||''), `Dominator Heals Fantasia build missing: ${fantasiaTitles.join(' | ')}`);
const domFantasiaFantos=await page.locator('#buildContent .buildCard:visible .fantomonPick b').allTextContents();
assert(domFantasiaFantos.some(x=>/Mandragora|Herbote/i.test(x)), `Dominator Heals Fantasia did not switch to healing-oriented Fantomons: ${domFantasiaFantos.join(' | ')}`);
// Restore the existing Dominator smoke assumptions.
await page.locator('#buildContent .metaBuildTabs button[data-meta-mode="Dungeon"]').click();
await page.locator('#buildContent button[data-dominator-mode="dps"]').click();
await page.waitForFunction(()=>[...document.querySelectorAll('#buildContent .buildGrid .buildCard')].some(x=>x.dataset.role==='Dungeon'&&x.dataset.buildRole==='dps'&&!x.hidden&&getComputedStyle(x).display!=='none'),null,{timeout:3000});
'''
if text.count(old)!=1:
    raise SystemExit(f'smoke Dominator Fantasia block count={text.count(old)}')
text=text.replace(old,new,1)
smoke.write_text(text,encoding='utf-8')

print('fixed Dominator Fantasia browser validation and healer Fantomons')
