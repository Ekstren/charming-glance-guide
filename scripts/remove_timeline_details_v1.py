from pathlib import Path
import re

path = Path('index.html')
s = path.read_text(encoding='utf-8')

pattern = re.compile(
    r"  function timelineDetailHtml\(e\)\{.*?\n  \}\n  function dedupeTimelineDetails\(\)\{",
    re.S,
)
replacement = """  // TIMELINE_SUMMARY_ONLY_V1: timeline cards never expose expandable research/details UI.\n  // Full source/research text remains in timelineData for maintenance, while cards show only the concise summary.\n  function timelineDetailHtml(e){\n    const summary=timelineSummaryText(e);\n    return `<p>${summary}</p>`;\n  }\n  function dedupeTimelineDetails(){"""

s2, n = pattern.subn(replacement, s, count=1)
if n != 1:
    raise SystemExit(f'Expected to replace timelineDetailHtml once, replaced {n}')

path.write_text(s2, encoding='utf-8')
print('Timeline cards are now summary-only; raw research remains in timelineData.')
