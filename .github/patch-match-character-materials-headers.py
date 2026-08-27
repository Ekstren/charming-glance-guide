from pathlib import Path

path = Path('index.html')
s = path.read_text(encoding='utf-8')
marker = 'MATCH_CHARACTER_MATERIALS_HEADERS_V1'
if marker in s:
    print('already applied')
    raise SystemExit(0)

needle = '''<style id="materials-header-compact-v1">
/* MATERIALS_HEADER_COMPACT_V1 */'''
if needle not in s:
    raise SystemExit('materials header style marker not found')

# The Materials card was still inheriting outer panel padding while Character explicitly
# zeroed it, which made a collapsed Materials card much taller. Normalize the shell and
# summary geometry for both cards in one final override.
insert = '''<style id="matched-character-materials-headers-v1">
/* MATCH_CHARACTER_MATERIALS_HEADERS_V1 */
#characterDetails,
#materialsDetails{padding:0!important;overflow:hidden}
#characterDetails>summary.characterSummary,
#materialsDetails>summary.materialsSummary{
  min-height:44px!important;
  padding:12px 16px!important;
  margin:0!important;
  display:flex!important;
  align-items:center!important;
  justify-content:space-between!important;
  gap:10px!important;
}
#characterDetails>summary.characterSummary>span,
#materialsDetails>summary.materialsSummary>span{
  font-size:13px!important;
  font-weight:850!important;
  color:var(--ink)!important;
  letter-spacing:-.01em!important;
}
@media(max-width:760px){
  #characterDetails>summary.characterSummary,
  #materialsDetails>summary.materialsSummary{padding:11px 14px!important}
}
</style>

'''
s = s.replace(needle, insert + needle, 1)
path.write_text(s, encoding='utf-8')
print('matched Character and Materials collapsed headers')
