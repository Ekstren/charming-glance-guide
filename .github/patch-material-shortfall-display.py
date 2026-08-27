from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')
marker = 'RAW_MATERIAL_SHORTFALL_DISPLAY_V1'
if marker in text:
    print('Raw material shortfall display already applied.')
    raise SystemExit(0)

old_comment = """    // TOOL_COUNT_LABELS_V15: these rows are Material Realm TOOL counts, not raw materials.\n    // Always name the tool on Use / Need / Remaining / Still short so the resource card cannot\n    // be misread as mixing another raw-material balance into the lower helper section.\n"""
new_comment = """    // TOOL_COUNT_LABELS_V15: Use / Need / Remaining are Material Realm TOOL counts.\n    // RAW_MATERIAL_SHORTFALL_DISPLAY_V1: once Realm capacity is exhausted, stop expressing\n    // the unresolved gap as a tool count. Show the exact raw material still missing instead.\n"""
if text.count(old_comment) != 1:
    raise SystemExit(f'Expected one tool-count comment, found {text.count(old_comment)}')
text = text.replace(old_comment, new_comment, 1)

old_line = """    if(missing>0){\n      lines.push(`<div class=\"toolSimpleLine toolNeedLine\"><i>Still short:</i><b>${fmt(missing)} ${missingToolLabel}</b></div>`);\n    }\n"""
new_line = """    if(missing>0){\n      const rawStillShort=Math.max(0,Math.ceil(Number(hardShort)||0));\n      lines.push(`<div class=\"toolSimpleLine toolNeedLine\"><i>Still short:</i><b>${fmt(rawStillShort)} ${materialName}</b></div>`);\n    }\n"""
if text.count(old_line) != 1:
    raise SystemExit(f'Expected one Still short tool line, found {text.count(old_line)}')
text = text.replace(old_line, new_line, 1)

path.write_text(text, encoding='utf-8')
print('Changed hard shortfalls to exact raw material amounts.')
