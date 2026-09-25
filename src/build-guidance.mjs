// Gear and Fantomon guidance retained from the existing guide and cross-checked
// against the current class pages. Published skill bars live separately in builds.mjs.
export const BUILD_STAT_PROFILES={
  Conqueror:{
    rule:'Current T4 evidence supports ATK ≥ Elemental Mastery on main secondaries. Crit Rate/Crit DMG are the premium reroll stats; Accuracy matters more in PvP and high-Block fights.',
    rows:[['Sword','ATK ≥ Elemental Mastery > SPD'],['Gauntlets','ATK ≥ Elemental Mastery > SPD'],['Helmet','DEF ≥ Physical RES = Elemental RES > HP'],['Chest','DEF ≥ Physical RES = Elemental RES > HP'],['Boots','ATK ≥ Elemental Mastery > SPD']],
    substats:'Crit Rate / Crit DMG > Accuracy > Elemental Mastery > SPD / SPD% > ATK / ATK%'
  },
  Destroyer:{
    rule:'S2 Destroyer is balance-sensitive, not permanently EM-first. Keep a healthy Elemental Mastery floor, then flat ATK can match or beat more EM on developed accounts. Crit remains premium; dummy-test close swaps.',
    rows:[['Staff','ATK ≈ Elemental Mastery > Crit > SPD'],['Codex','ATK ≈ Elemental Mastery > Crit > SPD'],['Helmet','DEF ≥ Physical RES = Elemental RES > HP > Effect RES'],['Chest','DEF ≥ Physical RES = Elemental RES > HP'],['Boots','ATK ≈ Elemental Mastery > SPD']],
    substats:'Crit Rate / Crit DMG > ATK / ATK% ≈ Elemental Mastery > Accuracy > SPD / SPD%'
  },
  Guardian:{
    tank:{
      label:'Tank',
      rule:'Tank Guardian is built around Block first. After that, DEF/DMG RES drive survival while SPD keeps Taunt, shields and buffs cycling before the enemy can act.',
      rows:[['Sword','SPD > ATK > Physical Mastery > Elemental Mastery'],['Shield','DEF > HP > Physical RES = Elemental RES'],['Helmet','DEF ≥ Physical RES = Elemental RES > HP > Effect RES'],['Chest','DEF ≥ Physical RES = Elemental RES > HP'],['Boots','SPD > ATK > Elemental Mastery = Physical Mastery']],
      substats:'Block Rate > DEF > SPD > HP > DEF% > SPD% > HP%'
    },
    dps:{
      label:'DPS',
      rule:'DPS Guardian uses the offensive Water/counter shell, but Block still matters because the class gains damage by staying active. After a healthy Block floor, Crit Rate, SPD and ATK/Mastery are the damage-quality rolls.',
      rows:[['Sword','SPD > ATK > Elemental Mastery > Physical Mastery'],['Shield','DEF > HP > Physical RES = Elemental RES'],['Helmet','DEF ≥ Physical RES = Elemental RES > HP'],['Chest','DEF ≥ Physical RES = Elemental RES > HP'],['Boots','SPD > ATK > Elemental Mastery = Physical Mastery']],
      substats:'Block Rate > Crit Rate > SPD / SPD% > ATK / ATK% > Elemental Mastery > Crit DMG'
    }
  },
  Dominator:{
    dps:{
      label:'DPS',
      rule:'Effect Hit Rate is a threshold stat: get enough to land Erosion reliably, then favor damage-quality affixes instead of blindly stacking more EHR. If Erosion is unreliable, hybrid/direct damage is safer.',
      rows:[['Staff','Effect Hit Rate ≥ Elemental Mastery ≥ ATK > SPD'],['Orb','Effect Hit Rate ≥ Elemental Mastery ≥ ATK > SPD'],['Helmet','DEF ≥ Physical RES = Elemental RES > HP > Effect RES'],['Chest','DEF ≥ Physical RES = Elemental RES > HP'],['Boots','Elemental Mastery > ATK > SPD']],
      substats:'Effect Hit Rate > Crit Rate / Crit DMG > Elemental Mastery > ATK / ATK% > SPD / SPD%'
    },
    heals:{
      label:'Heals',
      rule:'Healer Dominator is SPD-first on Staff/Orb/Boots and HP-first on Helmet/Chest. Effect Hit Rate is the second main-secondary target on Staff/Orb, but only an average healer affix when rerolling substats.',
      rows:[['Staff','SPD > Effect Hit Rate > Elemental Mastery > ATK'],['Orb','SPD > Effect Hit Rate > Elemental Mastery > ATK'],['Helmet','HP > DEF ≥ Physical RES = Elemental RES > Effect RES'],['Chest','HP > DEF ≥ Physical RES = Elemental RES'],['Boots','SPD > Elemental Mastery > ATK']],
      substats:'Healing Boost > SPD / SPD% > HP / HP% > DMG RES'
    }
  }
};

export const ROLL_VALUES={
  atk:['ATK','5.36K'],atkpct:['ATK%','18.7%'],def:['DEF','5.36K'],defpct:['DEF%','18.7%'],
  hp:['HP','26.8K'],hppct:['HP%','18.7%'],spd:['SPD','4.28K'],spdpct:['SPD%','18.7%'],
  crit:['Crit Rate','7.5%'],critdmg:['Crit DMG','11.2%'],block:['Block Rate','7.5%'],acc:['Accuracy','7.5%'],
  em:['Elemental Mastery','5.36K'],ehr:['Effect Hit Rate','5.36K'],dmgres:['DMG RES','Paired affix only'],
  heal:['Healing Boost','15%'],critpair:['Crit Rate + Crit DMG','15.3% + 23%'],
  critacc:['Crit Rate + Accuracy','15.3% + 15.3%'],blockpair:['Block Rate + Block Efficiency','15.3% + 23%'],
  healpair:['DMG RES + Healing Boost','7.68% + 30.7%']
};

export const ROLL_PROFILES={
  Conqueror:['crit','critdmg','critpair','acc','critacc','em','spd','spdpct','atk','atkpct'],
  Destroyer:['crit','critdmg','critpair','atk','atkpct','em','acc','critacc','spd','spdpct'],
  Guardian:{tank:['block','blockpair','def','spd','hp','defpct','spdpct','hppct'],dps:['block','blockpair','crit','critdmg','spd','spdpct','atk','atkpct','em']},
  Dominator:{dps:['ehr','crit','critdmg','critpair','em','atk','atkpct','spd','spdpct'],heals:['heal','healpair','spd','spdpct','hp','hppct','dmgres']}
};

export const FANTOMON_GUIDANCE={
  Destroyer:[
    ['Damage lead','Nyxarchon','Its damage and DEF reduction make it the guide’s main Mythic pick for this glass-cannon class.'],
    ['Before Nyx','Sylvaerie · Zeioletus','Permanent ATK + SPD or recurring burst; compare them in test mode with your stats.'],
    ['Survival option','Armopi','DEF and a personal shield can buy the extra turn you need.']
  ],
  Conqueror:[
    ['All-content lead','Nyxarchon','Damage and DEF reduction make it the class guide’s broad pick, especially in longer fights.'],
    ['Later S2 option','Pandarial','Opening cooldown reduction front-loads damage; Nyxarchon can still win longer fights. It releases later in the season.'],
    ['PvP / alternatives','Aegiswing · Sylvaerie · Zeioletus','Aegiswing is the PvP choice; Sylvaerie and Zeioletus are damage options to compare on your stats.']
  ],
  Guardian:[
    ['Priority Mythic','Aegiswing','The class guide’s top Guardian investment for extra Taunt, debuffs, and less damage from taunted enemies.'],
    ['Dispel / damage','Kels · Nyxarchon','Kels adds Dispel and DEF Down when manifested; Nyxarchon amplifies team damage with debuffs.'],
    ['Team mitigation','Terragon · Chomusuke','Prydwen suggests Terragon when a Guild Boss team needs more damage reduction; Chomusuke remains a workable option.']
  ],
  Dominator:[
    ['DPS lead','Nyxarchon','The class guide’s best-in-slot for Dark damage and its supporting effect.'],
    ['F2P damage options','Zeioletus · Sylvaerie','Zeioletus is a damage stopgap; Sylvaerie buffs ATK and SPD and can win on some stat spreads.'],
    ['Healing / support','Mandragora · Terragon','Mandragora adds healing to ally-targeted Techniques; Terragon can reduce enemy ATK.'],
    ['Later S2 support','Pandarial','Its opening cooldown reduction supports early healing. It releases later in the season, so check availability first.']
  ]
};
