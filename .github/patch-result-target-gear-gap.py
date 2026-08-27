from pathlib import Path

path=Path('index.html')
text=path.read_text(encoding='utf-8')
marker='result-target-gear-gap-v1'
if marker in text:
    print('RESULT_TARGET_GEAR_GAP_V1 already applied')
    raise SystemExit(0)
style='''\n<style id="result-target-gear-gap-v1">\n/* RESULT_TARGET_GEAR_GAP_V1: give the Fantomon/target row clear breathing room above Gear slot labels. */\n.optimizerTargets{margin-bottom:14px!important}\n</style>\n'''
if '</head>' not in text:
    raise SystemExit('missing </head>')
text=text.replace('</head>',style+'</head>',1)
path.write_text(text,encoding='utf-8')
print('Applied RESULT_TARGET_GEAR_GAP_V1')
