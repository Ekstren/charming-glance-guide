from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')
marker = 'TARGET_MESSAGE_LINES_V1'
if marker in text:
    print('Target message line breaks already applied.')
    raise SystemExit(0)

old_caution = """        const route=dailySuggested.changed
          ? ` Recommended refreshes/day: Ore ${dailySuggested.ore} · Essence ${dailySuggested.essence} · Sand ${dailySuggested.sand}.`
          : '';
        $('targetMessage').textContent=`⚠ Goal is achievable, but your current Material Realm refresh plan is too low.${route}`;
"""
new_caution = """        // TARGET_MESSAGE_LINES_V1: keep the status sentence and recommendation on separate lines.
        const route=dailySuggested.changed
          ? `<span class=\"targetMessageDetail\">Recommended refreshes/day: Ore ${dailySuggested.ore} · Essence ${dailySuggested.essence} · Sand ${dailySuggested.sand}.</span>`
          : '';
        $('targetMessage').innerHTML=`⚠ Goal is achievable, but your current Material Realm refresh plan is too low.${route}`;
"""

old_danger = """      $('targetMessage').hidden=false;$('targetMessage').classList.add('warning','danger');
      $('targetMessage').textContent=`⚠ Goal not achievable with remaining Realm capacity. Short at max 20 refreshes/day: ${shortageBits.join(' · ')||'resources'}.`;
"""
new_danger = """      $('targetMessage').hidden=false;$('targetMessage').classList.add('warning','danger');
      $('targetMessage').innerHTML=`⚠ Goal not achievable with remaining Realm capacity.<span class=\"targetMessageDetail\">Short at max 20 refreshes/day: ${shortageBits.join(' · ')||'resources'}.</span>`;
"""

if text.count(old_caution) != 1:
    raise SystemExit(f'Expected one caution block, found {text.count(old_caution)}')
if text.count(old_danger) != 1:
    raise SystemExit(f'Expected one danger block, found {text.count(old_danger)}')

text = text.replace(old_caution, new_caution, 1)
text = text.replace(old_danger, new_danger, 1)

anchor = '</head>'
css = '''\n<style id="target-message-lines-v1">\n/* TARGET_MESSAGE_LINES_V1 */\n#targetMessage .targetMessageDetail{display:block;margin-top:3px}\n</style>\n'''
if anchor not in text:
    raise SystemExit('head close not found')
text = text.replace(anchor, css + '\n' + anchor, 1)

path.write_text(text, encoding='utf-8')
print('Applied target message line breaks.')
