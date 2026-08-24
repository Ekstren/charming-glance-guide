from pathlib import Path
import re

path = Path("index.html")
text = path.read_text(encoding="utf-8")

panels = [
    ("Timeline coverage & source confidence", "timelineCoverageDetails"),
    ("Recurring event rotation", "recurringEventsDetails"),
    ("Season 5 · Ignis long-range reference", "ignisReferenceDetails"),
]

for title, panel_id in panels:
    # Find the <details class="timelineIntel" ...> immediately wrapping this summary.
    pattern = re.compile(
        r'<details\s+class="timelineIntel"(?:\s+id="[^"]+")?(?:\s+open)?\s*>\s*'
        r'(<summary><span>' + re.escape(title) + r'</span>)'
    )
    replacement = f'<details class="timelineIntel" id="{panel_id}">\n      \\1'
    text, count = pattern.subn(replacement, text, count=1)
    if count != 1 and f'id="{panel_id}"' not in text:
        raise SystemExit(f"Could not find timeline panel: {title}")

state_marker = "sxs-timeline-panel-coverage"
if state_marker not in text:
    setup_pattern = re.compile(r'(  function setupTimeline\(\)\{\n\s*renderLocalTimeLabels\(\);\n)')
    state_code = (
        "    const timelinePanelState=[\n"
        "      ['timelineCoverageDetails','sxs-timeline-panel-coverage'],\n"
        "      ['recurringEventsDetails','sxs-timeline-panel-events'],\n"
        "      ['ignisReferenceDetails','sxs-timeline-panel-ignis']\n"
        "    ];\n"
        "    timelinePanelState.forEach(([id,key])=>{\n"
        "      const panel=$(id);\n"
        "      if(!panel) return;\n"
        "      let saved=null;\n"
        "      try{ saved=localStorage.getItem(key); }catch(_){}\n"
        "      panel.open=saved==='1';\n"
        "      panel.addEventListener('toggle',()=>{try{localStorage.setItem(key,panel.open?'1':'0');}catch(_){}});\n"
        "    });\n"
    )
    text, count = setup_pattern.subn(r"\1" + state_code, text, count=1)
    if count != 1:
        raise SystemExit("Could not find setupTimeline() insertion point")

path.write_text(text, encoding="utf-8")
