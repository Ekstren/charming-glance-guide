import pathlib, re
path = pathlib.Path(r'C:\Users\ekstren\Documents\Local AI Projects\GUI Projects\charming-glance-guide\index.html')
text = path.read_text(encoding='utf-8')
# find start of script block
start = text.find('<script>\n// Navigation tabs')
end = text.find('</script>', start) + len('</script>')
# new block
new_block = '''<script>\n\ndocument.addEventListener('DOMContentLoaded', () => {\n  const nav = document.querySelector('.sectionSwitch');\n  const buttons = nav.querySelectorAll('button');\n  const sections = document.querySelectorAll('.siteSection');\n\n  function showSection(target) {\n    const targetId = target + 'Section';\n    sections.forEach(sec => {\n      sec.style.display = sec.id === targetId ? 'block' : 'none';\n    });\n  }\n\n  buttons.forEach(btn => {\n    btn.addEventListener('click', () => {\n      buttons.forEach(b => b.classList.remove('active'));\n      btn.classList.add('active');\n      showSection(btn.dataset.section);\n    });\n  });\n\n  const firstBtn = buttons[0];\n  if (firstBtn) {\n    showSection(firstBtn.dataset.section);\n  }\n});\n</script>'''
new_text = text[:start] + new_block + text[end:]
path.write_text(new_text, encoding='utf-8')
print('script replaced')
