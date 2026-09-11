from pathlib import Path

path = Path('assets/site.css')
css = path.read_text(encoding='utf-8')
marker = '/* PROJECTED_LEVEL_GEOMETRY_MATCH_V1 */'
if marker in css:
    print('Projected level geometry patch already present.')
    raise SystemExit(0)

css += r'''

/* PROJECTED_LEVEL_GEOMETRY_MATCH_V1
   Keep the projected level's accent colors, but remove the readonly focus halo so its
   visible geometry matches the other Character inputs exactly. */
.projectionField #projectedCharacter,
.projectionField #projectedCharacter:focus,
.projectionField #projectedCharacter:focus-visible{
  box-shadow:none!important;
  outline:0!important;
}
'''

path.write_text(css, encoding='utf-8')
print('Projected level geometry now matches sibling inputs while retaining accent colors.')
