from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
MARK='ACQUISITION_KERNEL_V1'
if MARK in s:
    print('acquisition kernel already applied')
    raise SystemExit(0)

old='''    const acquisitionFor=(go,so,ro,fo)=>acquisitionEffortFor(
      {ore:go.oreCost,essence:so.cost,sand:ro.cost,treat:fo.cost},resources,cfg
    );
    let best=null,bestDiagnostic=null;
'''
if old not in s:
    raise SystemExit('searchPlans acquisitionFor anchor not found')

new=r'''    /* ACQUISITION_KERNEL_V1
       This metric is evaluated in the hottest optimizer loop. Precompute each category's
       marginal weighted spend once per resource state, read Cart/map rates once, and run
       the same joint-reacquisition equation with scalar locals. This removes repeated DOM
       reads, logarithms, temporary objects and arrays from millions of candidate comparisons
       without changing the acquisition formula or any tie-break rule. */
    for(const so of cats.skillOptions) so.__acqEssenceV1=marginalWeightedSpend(so.cost,'essence',resources);
    for(const ro of cats.relicOptions) ro.__acqSandV1=marginalWeightedSpend(ro.cost,'sand',resources);
    for(const fo of cats.fantoOptions) fo.__acqTreatV1=marginalWeightedSpend(fo.cost,'treat',resources);
    const acqMap=resources?.yields?.map||cfg.map||{};
    const acqCartOre=Math.max(0,n('oreRate'));
    const acqCartEssence=Math.max(0,n('essenceRate'));
    const acqCartSand=Math.max(0,n('sandRate'));
    const acqCartTreat=Math.max(0,n('treatRate'));
    const acqNodeOre=Math.max(0,Number(acqMap.ore)||0);
    const acqNodeEssence=Math.max(0,Number(acqMap.essence)||0);
    const acqNodeSand=Math.max(0,Number(acqMap.sand)||0);
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
      const nodesAt=hours=>{
        let total=0,rem=0;
        rem=Math.max(0,ore-acqCartOre*hours);if(rem>0){if(acqNodeOre<=0)return Infinity;total+=rem/acqNodeOre;}
        rem=Math.max(0,essence-acqCartEssence*hours);if(rem>0){if(acqNodeEssence<=0)return Infinity;total+=rem/acqNodeEssence;}
        rem=Math.max(0,sand-acqCartSand*hours);if(rem>0){if(acqNodeSand<=0)return Infinity;total+=rem/acqNodeSand;}
        return total;
      };
      if(nodesAt(floor)<=floor+1e-9) return floor;
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
          if(nodesAt(hours)<=hours+1e-7) return hours;
          break;
        }
        mask=next;
        if(!mask) return floor;
      }
      let lo=floor,hi=Math.max(1,hours,floor);
      while(nodesAt(hi)>hi+1e-9&&hi<1e9) hi*=2;
      if(hi>=1e9&&nodesAt(hi)>hi+1e-9) return 1e9;
      for(let i=0;i<48;i++){
        const mid=(lo+hi)/2;
        if(nodesAt(mid)<=mid) hi=mid; else lo=mid;
      }
      return hi;
    };
    const acquisitionFor=(go,so,ro,fo)=>({hours:jointHoursFast(go.oreCost,so.__acqEssenceV1,ro.__acqSandV1,fo.__acqTreatV1)});
    let best=null,bestDiagnostic=null;
'''
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
print('added exact allocation-free acquisition scoring kernel')
