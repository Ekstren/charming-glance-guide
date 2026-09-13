import re,sys,os
path='C:\\Users\\ekstren\\Documents\\Local AI Projects\\GUI Projects\\charming-glance-guide\\index.html'
text=open(path,'r',encoding='utf-8').read()
# find the script block
start=text.find('<script>\n// Navigation tabs')
if start==-1:
    print('start not found')
    sys.exit(1)
end=text.find('</script>',start)+len('</script>')
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
new_text=text[:start]+new_block+text[end:]
open(path,'w',encoding='utf-8').write(new_text)
print('script replaced')
