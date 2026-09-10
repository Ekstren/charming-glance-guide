from pathlib import Path

p=Path('index.html')
asset=Path('assets/build-layout-icons-v1.js')
s=p.read_text(encoding='utf-8')
a=asset.read_text(encoding='utf-8')
MARK='BUILD_VISUAL_STABILITY_V2'
if MARK in s and 'window.__applyBuildHeroNow=apply' in a:
    print('Build visual stability v2 already applied.')
    raise SystemExit(0)
if 'BUILD_SWITCH_NO_FLICKER_V1' not in s:
    raise SystemExit('Expected BUILD_SWITCH_NO_FLICKER_V1 baseline not found')


def patch_script(script_id, transform):
    global s
    start_tag=f'<script id="{script_id}">'
    pos=s.find(start_tag)
    if pos < 0:
        raise SystemExit(f'{script_id}: script start not found')
    body_start=pos+len(start_tag)
    end=s.find('</script>',body_start)
    if end < 0:
        raise SystemExit(f'{script_id}: script end not found')
    body=s[body_start:end]
    new_body=transform(body)
    if new_body==body:
        raise SystemExit(f'{script_id}: expected transform anchor not found')
    s=s[:body_start]+new_body+s[end:]


def expose_rich(body):
    old='''  function queue(){\n    if(queued) return;\n    queued=true;\n    requestAnimationFrame(()=>setTimeout(apply,0));\n  }'''
    new='''  // BUILD_VISUAL_STABILITY_V2: class switching calls the rich-layout transformer\n  // in the same click task, before the browser paints the newly mounted class.\n  window.__applyBuildRichNow=apply;\n  function queue(){\n    if(queued) return;\n    queued=true;\n    requestAnimationFrame(()=>setTimeout(apply,0));\n  }'''
    if old not in body:
        return body
    return body.replace(old,new,1)


def expose_roll(body):
    old='''  function queue(){if(queued)return;queued=true;requestAnimationFrame(()=>setTimeout(apply,0))}'''
    new='''  // BUILD_VISUAL_STABILITY_V2: Roll Guide is part of the finished class layout,\n  // so make it available to the synchronous Builds render pipeline.\n  window.__applyBuildRollNow=apply;\n  function queue(){if(queued)return;queued=true;requestAnimationFrame(()=>setTimeout(apply,0))}'''
    if old not in body:
        return body
    return body.replace(old,new,1)

patch_script('restore-rich-builds-v1-script',expose_rich)
patch_script('build-roll-guide-v1-script',expose_roll)

# BUILD_HERO_LAYOUT_V2 is an external deferred asset. It was the remaining second paint in the
# user's recording: it moves the compact stats into the final hero grid and clones the Roll Guide
# into the right column. Expose its idempotent apply() so the class renderer can complete that
# reflow before returning to the browser.
hero_old='''  let queued=false;\n  function apply(){\n    queued=false;\n    document.querySelectorAll('#buildContent .guideSummary.buildSummaryCompact').forEach(enhanceGuide);\n  }\n  function queue(){'''
hero_new='''  let queued=false;\n  function apply(){\n    queued=false;\n    document.querySelectorAll('#buildContent .guideSummary.buildSummaryCompact').forEach(enhanceGuide);\n  }\n  // BUILD_VISUAL_STABILITY_V2: finish the hero reflow in the originating class-click task.\n  window.__applyBuildHeroNow=apply;\n  function queue(){'''
if 'window.__applyBuildHeroNow=apply' not in a:
    if hero_old not in a:
        raise SystemExit('Hero layout apply/queue anchor not found')
    a=a.replace(hero_old,hero_new,1)

old_hook='''    host.replaceChildren(template.content.cloneNode(true));\n    applyDominatorBuildMode();\n    // The META script is loaded after this main runtime. On initial parse it will enhance at\n    // DOMContentLoaded; on every later class click this hook exists and completes before paint.\n    if(typeof window.__applyBuildMetaNow==='function') window.__applyBuildMetaNow();\n    warmBuildTemplates(list);'''
new_hook='''    host.replaceChildren(template.content.cloneNode(true));\n    applyDominatorBuildMode();\n    /* BUILD_VISUAL_STABILITY_V2\n       The recording exposed three post-render stages after a class click: Rich stat/priority\n       layout, Roll Guide insertion, then BUILD_HERO_LAYOUT_V2 reflow. Run the whole dependency\n       chain synchronously so the browser only receives the finished class. META creates the final\n       activity cards first; Rich fingerprints those headings and creates buildQuickStats; Roll\n       populates that stats panel; Hero performs the final two-column summary/reflow last. */\n    if(typeof window.__applyBuildMetaNow==='function') window.__applyBuildMetaNow();\n    if(typeof window.__applyBuildRichNow==='function') window.__applyBuildRichNow();\n    if(typeof window.__applyBuildRollNow==='function') window.__applyBuildRollNow();\n    if(typeof window.__applyBuildHeroNow==='function') window.__applyBuildHeroNow();\n    warmBuildTemplates(list);'''
if old_hook not in s:
    raise SystemExit('Build render enhancement hook not found')
s=s.replace(old_hook,new_hook,1)

# The selected class fill also lagged behind the content because the generic class-tab rule animates
# background/color/border for 160 ms. Companion tabs already feel good, so scope this only to Builds.
style='''\n<style id="build-visual-stability-v2">\n/* BUILD_VISUAL_STABILITY_V2: selected class state must change in the same paint as its content. */\n#buildsSection #classTabs button{transition:none!important}\n</style>\n'''
if MARK not in s:
    if '</head>' not in s:
        raise SystemExit('head close not found')
    s=s.replace('</head>',style+'\n</head>',1)

p.write_text(s,encoding='utf-8')
asset.write_text(a,encoding='utf-8')
print('Applied synchronous META + Rich + Roll + Hero Builds rendering and removed Builds-only class-tab transition.')
