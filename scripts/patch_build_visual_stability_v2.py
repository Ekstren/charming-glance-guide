from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
MARK='BUILD_VISUAL_STABILITY_V2'
if MARK in s:
    print('Build visual stability v2 already applied.')
    raise SystemExit(0)
if 'BUILD_SWITCH_NO_FLICKER_V1' not in s:
    raise SystemExit('Expected BUILD_SWITCH_NO_FLICKER_V1 baseline not found')


def patch_script(script_id, transform):
    global s
    start_tag=f'<script id="{script_id}">'
    a=s.find(start_tag)
    if a < 0:
        raise SystemExit(f'{script_id}: script start not found')
    body_start=a+len(start_tag)
    b=s.find('</script>',body_start)
    if b < 0:
        raise SystemExit(f'{script_id}: script end not found')
    body=s[body_start:b]
    new_body=transform(body)
    if new_body==body:
        raise SystemExit(f'{script_id}: expected transform anchor not found')
    s=s[:body_start]+new_body+s[b:]


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

old_hook='''    host.replaceChildren(template.content.cloneNode(true));\n    applyDominatorBuildMode();\n    // The META script is loaded after this main runtime. On initial parse it will enhance at\n    // DOMContentLoaded; on every later class click this hook exists and completes before paint.\n    if(typeof window.__applyBuildMetaNow==='function') window.__applyBuildMetaNow();\n    warmBuildTemplates(list);'''
new_hook='''    host.replaceChildren(template.content.cloneNode(true));\n    applyDominatorBuildMode();\n    /* BUILD_VISUAL_STABILITY_V2\n       The video-visible flash was not the class template itself being slow. The rich stat/priority\n       layout and Roll Guide were intentionally queued for a later animation frame, so the browser\n       painted the raw template first and the finished Builds layout second. Run every layout-changing\n       enhancer synchronously inside this click task. The META layer still runs between Rich and Roll\n       because it owns activity cards/Fantomons, while Roll depends on Rich creating buildQuickStats. */\n    if(typeof window.__applyBuildRichNow==='function') window.__applyBuildRichNow();\n    if(typeof window.__applyBuildMetaNow==='function') window.__applyBuildMetaNow();\n    if(typeof window.__applyBuildRollNow==='function') window.__applyBuildRollNow();\n    warmBuildTemplates(list);'''
if old_hook not in s:
    raise SystemExit('Build render enhancement hook not found')
s=s.replace(old_hook,new_hook,1)

# The active class fill also lagged behind the content because the generic class-tab rule animates
# background/color/border for 160 ms. Companion tabs already feel good, so scope this only to Builds.
style='''\n<style id="build-visual-stability-v2">\n/* BUILD_VISUAL_STABILITY_V2: selected class state must change in the same paint as its content. */\n#buildsSection #classTabs button{transition:none!important}\n</style>\n'''
if '</head>' not in s:
    raise SystemExit('head close not found')
s=s.replace('</head>',style+'\n</head>',1)

p.write_text(s,encoding='utf-8')
print('Applied synchronous Rich + META + Roll build rendering and removed Builds-only class-tab transition.')
