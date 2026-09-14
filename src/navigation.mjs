export function setupNavigation({ $, setSection, saveState, updateThemeButton }){
    const clearCalculatorFragment=()=>{
      if(['#calcResults','#characterDetails'].includes(location.hash))
        history.replaceState(history.state,'',location.pathname+location.search);
    };
    clearCalculatorFragment();
    document.querySelectorAll('.calculatorJumpNav a').forEach(link=>link.addEventListener('click',e=>{
      if(e.ctrlKey||e.metaKey||e.shiftKey||e.altKey) return;
      const target=document.querySelector(link.getAttribute('href'));
      if(!target) return;
      e.preventDefault();
      clearCalculatorFragment();
      target.setAttribute('tabindex','-1');
      target.focus({preventScroll:true});
      target.scrollIntoView({block:'start',behavior:'instant'});
    }));
    document.querySelector('.sectionSwitch').addEventListener('click',e=>{const b=e.target.closest('button[data-section]');if(b)setSection(b.dataset.section);});
    document.querySelectorAll('[data-open-section]').forEach(b=>b.addEventListener('click',()=>setSection(b.dataset.openSection)));
    $('themeToggle').addEventListener('click',()=>{document.documentElement.dataset.theme=document.documentElement.dataset.theme==='dark'?'light':'dark';updateThemeButton();saveState();});
    updateThemeButton();
  }
