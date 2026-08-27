from pathlib import Path
p=Path('index.html')
s=p.read_text()
old='''? `<button type="button" class="applyRealmRecommendation" data-ore="${dailySuggested.ore}" data-essence="${dailySuggested.essence}" data-sand="${dailySuggested.sand}" onclick="applyRecommendedRealmRefreshes(this)">Apply refreshes</button>`'''
new='''? `<button type="button" class="applyRealmRecommendation" data-ore="${dailySuggested.ore}" data-essence="${dailySuggested.essence}" data-sand="${dailySuggested.sand}">Apply refreshes</button>`'''
if old not in s:
    raise SystemExit('inline apply button anchor not found')
s=s.replace(old,new,1)
anchor="    $('findMaxStars')?.addEventListener('click',findMaxAchievableStars);\n"
insert=anchor+"    $('targetMessage')?.addEventListener('click',e=>{\n      const btn=e.target.closest?.('.applyRealmRecommendation');\n      if(btn) applyRecommendedRealmRefreshes(btn);\n    });\n"
if anchor not in s:
    raise SystemExit('event listener anchor not found')
s=s.replace(anchor,insert,1)
marker='/* APPLY_REALM_REFRESH_BUTTON_DELEGATION_V2 */'
css='''\n<style id="apply-realm-refresh-button-delegation-v2">\n/* APPLY_REALM_REFRESH_BUTTON_DELEGATION_V2 */\n.applyRealmRecommendation{pointer-events:auto!important}\n</style>\n'''
if marker not in s:
    s=s.replace('</head>',css+'</head>',1)
p.write_text(s)
