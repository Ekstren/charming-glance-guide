from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')

marker = 'HIDE_TOOL_ROWS_UNTIL_USED_V2'
if marker in text:
    print('Patch already applied.')
    raise SystemExit(0)

old = """    // TOOL_DAILY_GAP_V13 · TOOLS_FIRST_S2_RESERVES_V1 · HIDE_RESERVE_TOOLS_WHEN_RAW_REMAINS_V1
    // Result cards are about what the S1 upgrade plan actually needs. If raw material still
    // remains and no Realm tool is required for the S1 spend, hide reserve-only tool counts;
    // the Material Realm panel remains the place to inspect the carried S2 tool reserve.
    // If a tool was genuinely needed to bridge a raw shortage, keep showing Use/Need even
    // when the final Realm conversion leaves a small raw overage from whole-tool rounding.
    const visibleRawRemaining=Math.max(0,Number(rawRemaining)||0);
    if(planRuns<=0 && missing<=0 && (reserveRuns<=0 || visibleRawRemaining>0.5)){ el.innerHTML=''; el.hidden=true; return; }
"""
new = """    // TOOL_DAILY_GAP_V13 · TOOLS_FIRST_S2_RESERVES_V1 · HIDE_TOOL_ROWS_UNTIL_USED_V2
    // Result cards only show Material Realm tools when the S1 plan actually consumes/needs
    // them. Reserve-only and merely-carried tool counts stay hidden here regardless of the
    // raw balance; the Material Realm panel remains the place to inspect saved S2 tools.
    if(planRuns<=0 && missing<=0){ el.innerHTML=''; el.hidden=true; return; }
"""

if old not in text:
    raise SystemExit('Expected tool-display block not found; refusing to patch.')

text = text.replace(old, new, 1)
path.write_text(text, encoding='utf-8')
print('Applied hide-until-used tool-row patch.')
