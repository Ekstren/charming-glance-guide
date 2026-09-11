from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
index_path = ROOT / 'index.html'
runtime_path = ROOT / 'assets' / 'runtime.js'
css_path = ROOT / 'assets' / 'site.css'

index = index_path.read_text(encoding='utf-8')
runtime = runtime_path.read_text(encoding='utf-8')
css = css_path.read_text(encoding='utf-8')

# Restore the previously working Finish Early markup exactly.
new_control = '<div class="finishEarlyCard" title="Stop counting Character score and projected resources this many days before season end"><span>Finish early</span><input id="finishEarlyDays" type="number" min="0" step="0.5" value="0" inputmode="decimal" aria-label="Finish early days"><em>days</em><button id="finishEarlyMax" class="finishEarlyMax" type="button" title="Find the maximum half-day finish-early value that still reaches the selected Primostar target">Max</button></div>'
old_control = '<label class="finishEarlyCard" title="Stop counting Character score and projected resources this many days before season end"><span>Finish early</span><input id="finishEarlyDays" type="number" min="0" step="0.5" value="0" inputmode="decimal"><em>days</em></label>'
index = index.replace(new_control, old_control)

# Remove the Max helper/function block only.
start = runtime.find('  /* FINISH_EARLY_MAX_V1')
end = runtime.find('  /* SMART_BALANCE_RAW_CEILING_V1', start if start >= 0 else 0)
if start >= 0 and end > start:
    runtime = runtime[:start] + runtime[end:]
runtime = runtime.replace("    $('finishEarlyMax')?.addEventListener('click',findMaxFinishEarly);\n", '')

# Remove Max-only CSS appended after the working half-day styles.
marker = '/* FINISH_EARLY_MAX_V1_STYLE */'
pos = css.find(marker)
if pos >= 0:
    css = css[:pos].rstrip() + '\n'

index_path.write_text(index, encoding='utf-8')
runtime_path.write_text(runtime, encoding='utf-8')
css_path.write_text(css, encoding='utf-8')
