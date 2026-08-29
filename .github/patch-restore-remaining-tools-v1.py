from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='REMAINING_REALM_TOOLS_VISIBLE_V1'
if marker in s:
    print('already applied')
    raise SystemExit(0)

fn_start=s.find('  function setToolBalance(')
if fn_start<0:
    raise SystemExit('setToolBalance not found')
fn_end=s.find('\n  function ',fn_start+10)
if fn_end<0:
    raise SystemExit('setToolBalance end not found')
fn=s[fn_start:fn_end]

# The old hide-until-used cleanup removed useful inventory context. Keep zero-use rows
# hidden, but do not hide actual remaining Hammers/Knuckles/Shovels.
old_hide="""    // TOOL_DAILY_GAP_V13 · TOOLS_FIRST_S2_RESERVES_V1 · HIDE_TOOL_ROWS_UNTIL_USED_V2
    // Result cards only show Material Realm tools when the S1 plan actually consumes/needs
    // them. Reserve-only and merely-carried tool counts stay hidden here regardless of the
    // raw balance; the Material Realm panel remains the place to inspect saved S2 tools.
    if(planRuns<=0){ el.innerHTML=''; el.hidden=true; return; }
"""
new_hide="""    // REMAINING_REALM_TOOLS_VISIBLE_V1
    // Keep the cards compact: never print Use: 0, but always preserve useful inventory context
    // by showing remaining Hammers/Knuckles/Shovels when any are still available.
"""
if old_hide not in fn:
    raise SystemExit('current hide-until-used block not found')
fn=fn.replace(old_hide,new_hide,1)

block_start=fn.find('    const lines=[];')
block_end=fn.find('    el.hidden=false;',block_start)
if block_start<0 or block_end<0:
    raise SystemExit('tool line renderer block not found')

new_lines=r'''    const lines=[];
    const planToolLabel=planRuns===1?toolSingular:label;
    const remainingToolLabel=remainingTools===1?toolSingular:label;
    if(planRuns>0){
      lines.push(`<div class="toolSimpleLine toolUseLine"><i>Use:</i><b>${fmt(planRuns)} ${planToolLabel}${planGained>0?` <em>≈ ${fmtCompact(planGained)} ${materialName}</em>`:''}</b></div>`);
      if(dailyGapRuns>0){
        lines.push(`<div class="toolSimpleLine toolNeedLine"><i>Need:</i><b>${fmt(dailyGapRuns)} ${toolNeedLabel}${dailyGapValue>0?` <em>≈ ${fmtCompact(dailyGapValue)} ${materialName}</em>`:''}</b></div>`);
      }
    }
    if(remainingTools>0){
      lines.push(`<div class="toolSimpleLine toolRemainingLine"><i>Remaining:</i><b>${fmt(remainingTools)} ${remainingToolLabel}${reserveRuns>0?` <em>(${fmt(reserveRuns)} reserved)</em>`:''}</b></div>`);
    }
    // Hard/recoverable material shortages are already communicated by the resource card above.
    // Do not resurrect the old duplicate "Still short" tool footer.
    if(!lines.length){ el.innerHTML=''; el.hidden=true; return; }
'''
fn=fn[:block_start]+new_lines+fn[block_end:]
s=s[:fn_start]+fn+s[fn_end:]

# Regression guard comment beside the result assignment. The previous reward-reference pass threw
# before these fields were populated, leaving the header as "253 / — / —" despite a valid target plan.
score_anchor="""    $('currentStars').textContent=fmt(resourceBlocked?targetStars:planStars);$('summaryOptimizedScore').textContent=fmt(plan.score);
"""
score_new="""    // TARGET_PLAN_HEADER_COMPLETE_V1: reward-reference rendering must never prevent the target-plan score/status from populating.
    $('currentStars').textContent=fmt(resourceBlocked?targetStars:planStars);$('summaryOptimizedScore').textContent=fmt(plan.score);
"""
if score_anchor not in s:
    raise SystemExit('target-plan header assignment not found')
s=s.replace(score_anchor,score_new,1)

p.write_text(s,encoding='utf-8')
print('restored remaining Realm tools and target-header guard')
