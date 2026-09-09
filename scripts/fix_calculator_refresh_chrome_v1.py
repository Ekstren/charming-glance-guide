from pathlib import Path

PATH = Path('index.html')

STATIC_OLD = '<div class="seasonDeadline"><span id="seasonDeadlineLabel">Season 1 ends</span><b id="seasonDeadlineDate">—</b><small id="seasonRemaining">—</small></div>'
STATIC_NEW = '<div class="seasonDeadline"><span id="seasonDeadlineLabel">Season ends</span><b id="seasonDeadlineDate">—</b><small id="seasonRemaining">—</small></div>'

INIT_OLD = """  function initializeCalculatorIfNeeded(){
    if(calculatorInitialized) return;
    const status=$('optimizerSummary');
    if(status) status.textContent='Calculating your saved season plan…';
    // Let the Calculator tab paint before the expensive optimizer starts.
"""

INIT_NEW = """  function initializeCalculatorIfNeeded(){
    if(calculatorInitialized) return;
    // Paint the lightweight season-specific chrome immediately on refresh before
    // the optimizer starts. This prevents stale S1 fallback text from flashing
    // while a saved S2 plan is being restored and solved.
    renderCalculatorSeasonChrome(activeCalcConfig());
    const status=$('optimizerSummary');
    if(status) status.textContent='Calculating your saved season plan…';
    // Let the Calculator tab paint before the expensive optimizer starts.
"""


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one match, found {count}')
    return text.replace(old, new, 1)


def main() -> None:
    text = PATH.read_text(encoding='utf-8')
    changed = False

    if STATIC_OLD in text:
        text = replace_once(text, STATIC_OLD, STATIC_NEW, 'static season deadline fallback')
        changed = True
    elif STATIC_NEW not in text:
        raise SystemExit('static season deadline fallback is in an unknown state')

    if INIT_OLD in text:
        text = replace_once(text, INIT_OLD, INIT_NEW, 'calculator refresh initializer')
        changed = True
    elif INIT_NEW not in text:
        raise SystemExit('calculator refresh initializer is in an unknown state')

    if 'id="seasonDeadlineLabel">Season 1 ends<' in text:
        raise SystemExit('stale Season 1 deadline fallback remains')
    if 'renderCalculatorSeasonChrome(activeCalcConfig());' not in text:
        raise SystemExit('immediate calculator season chrome render is missing')

    if changed:
        PATH.write_text(text, encoding='utf-8')
        print('Fixed calculator refresh season chrome.')
    else:
        print('Calculator refresh season chrome already current.')


if __name__ == '__main__':
    main()
