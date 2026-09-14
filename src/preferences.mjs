const THEME_KEY='sxs-theme';
const CALCULATOR_KEY='charmingGlanceCloneV1';
export function loadTheme(){
 let theme='dark';
 try{theme=localStorage.getItem(THEME_KEY)||JSON.parse(localStorage.getItem(CALCULATOR_KEY)||'{}').theme||theme;}catch(_){}
 document.documentElement.dataset.theme=theme==='light'?'light':'dark';
}
export function saveTheme(){
 try{localStorage.setItem(THEME_KEY,document.documentElement.dataset.theme||'dark');}catch(_){}
}
