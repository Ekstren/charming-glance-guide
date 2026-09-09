from pathlib import Path

PATH = Path('index.html')
MARKER = 'HIDE_S2_PROGRESSION_HELPER_V1'
STYLE = '''
<style id="hide-s2-progression-helper-v1">
/* HIDE_S2_PROGRESSION_HELPER_V1: keep calculator focused on inputs/results; these S2 helper callouts are redundant. */
#seasonRulesHint,#s2ProgressionGates{display:none!important}
</style>
'''


def main() -> None:
    text = PATH.read_text(encoding='utf-8')
    if MARKER in text:
        print('S2 progression helper UI already hidden')
        return
    if 'id="seasonRulesHint"' not in text or 'id="s2ProgressionGates"' not in text:
        raise SystemExit('Expected S2 helper elements are missing; refusing a blind edit')
    if '</head>' not in text:
        raise SystemExit('Missing </head> insertion point')
    text = text.replace('</head>', STYLE + '\n</head>', 1)
    PATH.write_text(text, encoding='utf-8')
    print('Hid S2 scoring explainer and progression-gate row in the Primostar calculator')


if __name__ == '__main__':
    main()
