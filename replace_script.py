import pathlib
path=pathlib.Path('C:\\Users\\ekstren\\Documents\\Local AI Projects\\GUI Projects\\charming-glance-guide\\index.html')
text=path.read_text(encoding='utf-8')
# replace the script block
import re
pattern=re.compile(r'<script>\n// Navigation tabs.*?\n\s*</script>',re.S)
new_block='''<script>
document.addEventListener('DOMContentLoaded', () => {
  const nav = document.querySelector('.sectionSwitch');
  const buttons = nav.querySelectorAll('button');
  const sections = document.querySelectorAll('.siteSection');

  function showSection(target) {
    const targetId = target + 'Section';
    sections.forEach(sec => {
      sec.style.display = sec.id === targetId ? 'block' : 'none';
    });
  }

  buttons.forEach(btn => {
    btn.addEventListener('click', () => {
      buttons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      showSection(btn.dataset.section);
    });
  });

  const firstBtn = buttons[0];
  if (firstBtn) {
    showSection(firstBtn.dataset.section);
  }
});
</script>'''
new_text=pattern.sub(new_block,text)
path.write_text(new_text,encoding='utf-8')
print('replaced')
