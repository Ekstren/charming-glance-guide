from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

if 'JOINT_HOURS_ACTIVE_SET_V9' in s:
    print('Primostar joint-hours active-set optimizer already applied.')
    raise SystemExit(0)

old="""    /* JOINT_HOURS_NO_CLOSURE_V2
       This helper used to be allocated inside every jointHoursFast() call. Keeping it once
       per optimizer search removes hot-loop closure churn without changing arithmetic. */
    const nodesAtFast=(hours,ore,essence,sand)=>{
      let total=0,rem=0;
      rem=Math.max(0,ore-acqCartOre*hours);if(rem>0){if(acqNodeOre<=0)return Infinity;total+=rem/acqNodeOre;}
      rem=Math.max(0,essence-acqCartEssence*hours);if(rem>0){if(acqNodeEssence<=0)return Infinity;total+=rem/acqNodeEssence;}
      rem=Math.max(0,sand-acqCartSand*hours);if(rem>0){if(acqNodeSand<=0)return Infinity;total+=rem/acqNodeSand;}
      return total;
    };
    const jointHoursFast=(oreRaw,essRaw,sandRaw,treatRaw)=>{
      const ore=Math.max(0,Number(oreRaw)||0);
      const essence=Math.max(0,Number(essRaw)||0);
      const sand=Math.max(0,Number(sandRaw)||0);
      const treat=Math.max(0,Number(treatRaw)||0);
      let floor=0;
      if(treat>0){
        if(acqCartTreat<=0) return 1e9;
        floor=Math.max(floor,treat/acqCartTreat);
      }
      if(ore>0&&acqNodeOre<=0){if(acqCartOre<=0)return 1e9;floor=Math.max(floor,ore/acqCartOre);}
      if(essence>0&&acqNodeEssence<=0){if(acqCartEssence<=0)return 1e9;floor=Math.max(floor,essence/acqCartEssence);}
      if(sand>0&&acqNodeSand<=0){if(acqCartSand<=0)return 1e9;floor=Math.max(floor,sand/acqCartSand);}
      if(nodesAtFast(floor,ore,essence,sand)<=floor+1e-9) return floor;
      let mask=0;
      if(ore>acqCartOre*floor+1e-9&&acqNodeOre>0) mask|=1;
      if(essence>acqCartEssence*floor+1e-9&&acqNodeEssence>0) mask|=2;
      if(sand>acqCartSand*floor+1e-9&&acqNodeSand>0) mask|=4;
      let hours=floor;
      for(let pass=0;pass<4;pass++){
        let numerator=0,denominator=1;
        if(mask&1){numerator+=ore/acqNodeOre;denominator+=acqCartOre/acqNodeOre;}
        if(mask&2){numerator+=essence/acqNodeEssence;denominator+=acqCartEssence/acqNodeEssence;}
        if(mask&4){numerator+=sand/acqNodeSand;denominator+=acqCartSand/acqNodeSand;}
        hours=Math.max(floor,numerator/denominator);
        let next=0;
        if((mask&1)&&ore>acqCartOre*hours+1e-9) next|=1;
        if((mask&2)&&essence>acqCartEssence*hours+1e-9) next|=2;
        if((mask&4)&&sand>acqCartSand*hours+1e-9) next|=4;
        if(next===mask){
          if(nodesAtFast(hours,ore,essence,sand)<=hours+1e-7) return hours;
          break;
        }
        mask=next;
        if(!mask) return floor;
      }
      let lo=floor,hi=Math.max(1,hours,floor);
      while(nodesAtFast(hi,ore,essence,sand)>hi+1e-9&&hi<1e9) hi*=2;
      if(hi>=1e9&&nodesAtFast(hi,ore,essence,sand)>hi+1e-9) return 1e9;
      for(let i=0;i<48;i++){
        const mid=(lo+hi)/2;
        if(nodesAtFast(mid,ore,essence,sand)<=mid) hi=mid; else lo=mid;
      }
      return hi;
    };
"""

new="""    /* JOINT_HOURS_NO_CLOSURE_V2 · JOINT_HOURS_ACTIVE_SET_V9
       The acquisition equation is a three-term piecewise-linear fixed point:
         sum(max(0, demand - CartRate * hours) / nodeYield) <= hours.
       Active resources can only DROP OUT as hours rises. Precompute reciprocal node yields,
       fold the floor residual check into active-set construction, then solve each active set
       directly. With only Ore/Essence/Sand, at most three active-set solves are possible.
       This removes repeated division, the stable-set verification pass and the 48-step binary
       fallback while preserving the same mathematical root and tolerance boundaries. */
    const acqInvNodeOre=acqNodeOre>0?1/acqNodeOre:0;
    const acqInvNodeEssence=acqNodeEssence>0?1/acqNodeEssence:0;
    const acqInvNodeSand=acqNodeSand>0?1/acqNodeSand:0;
    const acqCartNodeOre=acqCartOre*acqInvNodeOre;
    const acqCartNodeEssence=acqCartEssence*acqInvNodeEssence;
    const acqCartNodeSand=acqCartSand*acqInvNodeSand;
    const nodesAtFast=(hours,ore,essence,sand)=>{
      let total=0,rem=0;
      rem=ore-acqCartOre*hours;if(rem>0){if(acqInvNodeOre<=0)return Infinity;total+=rem*acqInvNodeOre;}
      rem=essence-acqCartEssence*hours;if(rem>0){if(acqInvNodeEssence<=0)return Infinity;total+=rem*acqInvNodeEssence;}
      rem=sand-acqCartSand*hours;if(rem>0){if(acqInvNodeSand<=0)return Infinity;total+=rem*acqInvNodeSand;}
      return total;
    };
    const jointHoursFast=(oreRaw,essRaw,sandRaw,treatRaw)=>{
      const ore=oreRaw>0?oreRaw:0;
      const essence=essRaw>0?essRaw:0;
      const sand=sandRaw>0?sandRaw:0;
      const treat=treatRaw>0?treatRaw:0;
      let floor=0;
      if(treat>0){
        if(acqCartTreat<=0) return 1e9;
        floor=treat/acqCartTreat;
      }
      if(ore>0&&acqInvNodeOre<=0){if(acqCartOre<=0)return 1e9;floor=Math.max(floor,ore/acqCartOre);}
      if(essence>0&&acqInvNodeEssence<=0){if(acqCartEssence<=0)return 1e9;floor=Math.max(floor,essence/acqCartEssence);}
      if(sand>0&&acqInvNodeSand<=0){if(acqCartSand<=0)return 1e9;floor=Math.max(floor,sand/acqCartSand);}

      let mask=0,floorNodes=0,rem=0;
      rem=ore-acqCartOre*floor;
      if(rem>1e-9&&acqInvNodeOre>0){mask|=1;floorNodes+=rem*acqInvNodeOre;}
      rem=essence-acqCartEssence*floor;
      if(rem>1e-9&&acqInvNodeEssence>0){mask|=2;floorNodes+=rem*acqInvNodeEssence;}
      rem=sand-acqCartSand*floor;
      if(rem>1e-9&&acqInvNodeSand>0){mask|=4;floorNodes+=rem*acqInvNodeSand;}
      if(!mask||floorNodes<=floor+1e-9) return floor;

      let hours=floor;
      for(let pass=0;pass<3;pass++){
        let numerator=0,denominator=1;
        if(mask&1){numerator+=ore*acqInvNodeOre;denominator+=acqCartNodeOre;}
        if(mask&2){numerator+=essence*acqInvNodeEssence;denominator+=acqCartNodeEssence;}
        if(mask&4){numerator+=sand*acqInvNodeSand;denominator+=acqCartNodeSand;}
        hours=Math.max(floor,numerator/denominator);
        let next=0;
        if((mask&1)&&ore>acqCartOre*hours+1e-9) next|=1;
        if((mask&2)&&essence>acqCartEssence*hours+1e-9) next|=2;
        if((mask&4)&&sand>acqCartSand*hours+1e-9) next|=4;
        if(next===mask) return hours;
        mask=next;
        if(!mask) return floor;
      }
      // Three resources means a non-empty active set must stabilize within three passes.
      return hours;
    };
"""

if old not in s:
    raise SystemExit('jointHoursFast v11 baseline anchor not found')

s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
print('Applied Primostar v12 direct three-resource active-set joint-hours solver.')
