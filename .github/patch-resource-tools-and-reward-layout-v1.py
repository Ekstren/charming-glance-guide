from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='RESOURCE_TOOLS_REWARD_LAYOUT_V1'
if marker in s:
    print('already applied')
    raise SystemExit(0)

# Split long Primostar reward seasons into two vertical columns on desktop so the
# expandable section actually uses the available result-card width. Preserve order:
# first half top-to-bottom on the left, second half top-to-bottom on the right.
old="""    host.innerHTML=groups.map(group=>`<section class=\"primostarRewardSeason\"><h4>${group.title}</h4><div class=\"primostarRewardList\">${group.nodes.map((node,i)=>row(node,group.offset+i)).join('')}</div></section>`).join('');
"""
new="""    // RESOURCE_TOOLS_REWARD_LAYOUT_V1: long reward tables use two vertical columns on desktop.
    const rewardLists=(group)=>{
      if(group.nodes.length<=20) return `<div class=\"primostarRewardList\">${group.nodes.map((node,i)=>row(node,group.offset+i)).join('')}</div>`;
      const split=Math.ceil(group.nodes.length/2);
      const left=group.nodes.slice(0,split);
      const right=group.nodes.slice(split);
      return `<div class=\"primostarRewardColumns\"><div class=\"primostarRewardList\">${left.map((node,i)=>row(node,group.offset+i)).join('')}</div><div class=\"primostarRewardList\">${right.map((node,i)=>row(node,group.offset+split+i)).join('')}</div></div>`;
    };
    host.innerHTML=groups.map(group=>`<section class=\"primostarRewardSeason\"><h4>${group.title}</h4>${rewardLists(group)}</section>`).join('');
"""
if old not in s:
    raise SystemExit('Primostar reward host renderer not found')
s=s.replace(old,new,1)

css=r'''
<style id="resource-tools-reward-layout-v1">
/* RESOURCE_TOOLS_REWARD_LAYOUT_V1
   Raw material Remaining + Reserve are one logical block. Realm tools are a second
   logical block, separated by one divider, while still reading as one inset card. */
.planCosts .reserveRequirementLine{
  border-top:0!important;
  margin-top:2px!important;
  padding-top:0!important;
}

/* When a raw balance is immediately followed by a visible tool balance, visually join
   the sibling elements into one card. Keeping them as siblings is intentional: raw
   balance renderers replace their innerHTML on every calculator update. */
.planCosts small.rawRemaining:has(+ small.toolBalance:not([hidden])){
  border-bottom:0!important;
  border-radius:10px 10px 0 0!important;
  padding-bottom:8px!important;
}
.planCosts small.rawRemaining + small.toolBalance:not([hidden]){
  display:grid!important;
  gap:3px!important;
  min-height:0!important;
  margin-top:0!important;
  padding:8px 10px 9px!important;
  border:1px solid var(--line)!important;
  border-top:1px solid var(--line)!important;
  border-radius:0 0 10px 10px!important;
  background:color-mix(in srgb,var(--surface) 84%,var(--bg) 16%)!important;
  box-shadow:none!important;
}

/* Primostar rewards should use the result panel width instead of leaving a blank
   second column while only Season 1 is visible. Long season tables are then divided
   into two vertical reading columns. */
.primostarRewardSeasons{grid-template-columns:1fr!important}
.primostarRewardSeason{width:100%!important}
.primostarRewardColumns{
  display:grid;
  grid-template-columns:repeat(2,minmax(0,1fr));
}
.primostarRewardColumns>.primostarRewardList+ .primostarRewardList{
  border-left:1px solid var(--line);
}
@media(max-width:760px){
  .primostarRewardColumns{grid-template-columns:1fr}
  .primostarRewardColumns>.primostarRewardList+ .primostarRewardList{
    border-left:0;
    border-top:1px solid var(--line);
  }
  .planCosts small.rawRemaining + small.toolBalance:not([hidden]){
    padding:9px 11px 10px!important;
  }
}
</style>
'''
if '</head>' not in s:
    raise SystemExit('</head> not found')
s=s.replace('</head>',css+'\n</head>',1)

p.write_text(s,encoding='utf-8')
print('applied resource tool-card grouping and wide reward layout')
