from pathlib import Path
import re

START='<!-- BUILD_FANTOMON_PAIRS_START -->'
END='<!-- BUILD_FANTOMON_PAIRS_END -->'
TARGETS=[Path('index.html'),Path('.github/build-fantomons-inject.html')]


def patch_build_block(block: str) -> str:
    original=block
    block=block.replace("const META_MODES=['Dungeon','Crucible / Conquest','Fantasia Ascent','Arena','Tournament'];",
                        "const META_MODES=['Dungeon','Crucible / Conquest','Arena','Tournament'];")
    block=block.replace('grid-template-columns:repeat(5,minmax(0,1fr))',
                        'grid-template-columns:repeat(4,minmax(0,1fr))')

    # Remove every Fantasia role preset from the current S2 build data. They are kept
    # out entirely rather than merely hidden so future UI refactors cannot surface them.
    block,n_roles=re.subn(r"^[ \t]*role\('Fantasia Ascent[^\n]*\),?\n",'',block,flags=re.M)

    # Remove dedicated Technique/Charm swap maps for the removed scenario.
    swap_pat=re.compile(r"^    'Fantasia Ascent[^\n]*':\[\n(?:^      .*\n)*?^    \],?\n",re.M)
    block,n_swaps=swap_pat.subn('',block)

    # Remove Ascent-only Fantomon overrides; normal mode-specific pools remain.
    block,n_fanto=re.subn(
        r"\n    const ascent=String\(title\|\|''\)\.startsWith\('Fantasia Ascent'\);.*?(?=\n    if\(role==='Arena'\)\{)",
        '',block,flags=re.S)

    if "Fantasia Ascent" in block:
        raise SystemExit('Fantasia Ascent still present in maintained build block after patch')
    if "const META_MODES=['Dungeon','Crucible / Conquest','Arena','Tournament'];" not in block:
        raise SystemExit('four-mode META_MODES patch missing')
    if n_roles < 6:
        raise SystemExit(f'expected at least 6 Fantasia role rows, removed {n_roles}')
    if n_swaps < 6:
        raise SystemExit(f'expected at least 6 Fantasia swap blocks, removed {n_swaps}')
    if n_fanto < 1:
        raise SystemExit('Ascent Fantomon override block was not removed')
    if block==original:
        raise SystemExit('build patch made no changes')
    return block


for path in TARGETS:
    text=path.read_text(encoding='utf-8')
    if path.name=='index.html':
        a=text.find(START); b=text.find(END)
        if a<0 or b<0 or b<=a:
            raise SystemExit('index.html build injection markers missing')
        b+=len(END)
        patched=patch_build_block(text[a:b])
        text=text[:a]+patched+text[b:]
    else:
        text=patch_build_block(text)
    path.write_text(text,encoding='utf-8')
    print(f'{path}: removed Fantasia Ascent from Builds')

# Remove Fantasia-only browser assertions and replace them with the four-mode contract.
smoke=Path('scripts/site_smoke_test.mjs')
text=smoke.read_text(encoding='utf-8')
start=text.find('// Fantasia Ascent is a first-class solo-push mode for every current S2 class.')
end=text.find('// Tournament size controls live inside the Tournament scenario tab and are interactive.')
if start<0 or end<0 or end<=start:
    raise SystemExit('site smoke Fantasia assertion block not found')
replacement="""// Builds intentionally expose only the four scenarios with stable recommendations.\nawait waitBuild('Conqueror');\nconst scenarioOrder=await page.locator('#buildContent .metaBuildTabs [data-meta-mode]').evaluateAll(xs=>xs.map(x=>x.dataset.metaMode));\nassert(JSON.stringify(scenarioOrder)===JSON.stringify(['Dungeon','Crucible / Conquest','Arena','Tournament']), `activity order wrong: ${scenarioOrder.join(' | ')}`);\nassert(await page.locator('#buildContent .metaBuildTabs [data-meta-mode=\"Fantasia Ascent\"]').count()===0, 'Fantasia Ascent still appears in Builds');\nassert(await page.locator('#buildContent .buildCard[data-role^=\"Fantasia Ascent\"]').count()===0, 'Fantasia Ascent build cards still render');\n\n"""
text=text[:start]+replacement+text[end:]
smoke.write_text(text,encoding='utf-8')
print('scripts/site_smoke_test.mjs: replaced Fantasia assertions with four-mode contract')
