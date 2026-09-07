from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
changed=False

def replace_once(old,new,label):
    global s,changed
    if new in s:
        return
    if old not in s:
        raise SystemExit(f'{label}: expected anchor not found')
    s=s.replace(old,new,1)
    changed=True

old="""    // Within a tool-using stage, consume the fewest actual Realm entries before comparing
    // acquisition economics. Reserve-aware topups still enforce any protected carry reserve.
    if(cStage>=1){
      const toolCmp=betterToolBurden(candidate,best);
      if(toolCmp!==null) return toolCmp;
    }

    // Same-stage economics: compare the marginal time-equivalent burden of the resources
    // consumed by each score-capable route. This now applies to both S1 and S2.
    const effortCmp=compareAcquisitionEffort(candidate,best);
    if(effortCmp!==null) return effortCmp;
"""
new="""    /* TOOL_MATERIAL_WEIGHTS_V1
       Once both candidates are in the SAME sourcing tier, value Realm-tool-backed
       progression with the SAME material acquisition weights used for raw Ore/Essence/Sand.
       This prevents an unweighted 'fewest tools' rule from exhausting scarce Hammers/Ore
       while abundant Knuckles/Essence are left idle. Source priority remains strict:
       raw-only still beats any tool route, and projected tools still beat extra purchases. */
    const effortCmp=compareAcquisitionEffort(candidate,best);
    if(effortCmp!==null) return effortCmp;

    // If the weighted material burden is genuinely tied, preserve the route that consumes
    // fewer actual Realm entries. Reserve-aware topups still enforce protected carry reserve.
    if(cStage>=1){
      const toolCmp=betterToolBurden(candidate,best);
      if(toolCmp!==null) return toolCmp;
    }
"""
replace_once(old,new,'weighted tools within source tier')

# Keep the comment above betterToolBurden aligned with its now-secondary role.
old="""  /* REALM_TOOL_TIEBREAK_V1
     Acquisition effort is the primary route metric. Realm stage, Dawnium and actual tool
     burden are consulted only when acquisition effort is effectively tied, so sourcing
     details cannot override a materially better progression route. */
"""
new="""  /* REALM_TOOL_TIEBREAK_V2
     Source tier is a hard priority. Inside the same tier, material acquisition weighting
     ranks the route first; literal Realm-tool counts only break a weighted-material tie. */
"""
replace_once(old,new,'tool tie-break comment')

if changed:
    p.write_text(s,encoding='utf-8')
    print('Applied material-weighted Realm tool selection.')
else:
    print('Material-weighted Realm tool selection already current.')
