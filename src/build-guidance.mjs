// Season 3 / T5 priorities from the linked author-published class guides.
// Affix Preview numeric maxima below are retained verbatim from the user-confirmed baseline.
export const BUILD_STAT_PROFILES={
  "Ravager": {
    "rule": "The T5 source prioritizes Elemental Mastery on offensive secondaries. Crit remains the premium reroll target; special conversion or debuff-damage affixes depend on the rest of your gear.",
    "rows": [
      [
        "Sword",
        "Elemental Mastery > ATK > SPD"
      ],
      [
        "Gauntlets",
        "Elemental Mastery > ATK > SPD"
      ],
      [
        "Helmet",
        "DEF ≥ Physical RES = Elemental RES > HP"
      ],
      [
        "Chest",
        "DEF ≥ Physical RES = Elemental RES > HP"
      ],
      [
        "Boots",
        "Elemental Mastery > ATK > SPD"
      ]
    ],
    "substats": "Crit Rate / Crit DMG > Elemental Mastery / Accuracy > HP or SPD → ATK conversion / SPD / debuff-target Technique DMG > ATK / ATK%"
  },
  "Magister": {
    "rule": "T5 prioritizes Elemental Mastery on Staff, Codex and Boots. The source values S3 Wind Shield, damage-evasion and paired Crit affixes; defensive power and gear-score gates can outweigh a close offensive comparison.",
    "rows": [
      [
        "Staff",
        "Elemental Mastery > Crit > ATK > SPD > Effect Hit Rate"
      ],
      [
        "Codex",
        "Elemental Mastery > Crit > ATK > SPD > Effect Hit Rate"
      ],
      [
        "Helmet",
        "DEF ≥ Physical RES = Elemental RES > HP > Effect RES"
      ],
      [
        "Chest",
        "DEF ≥ Physical RES = Elemental RES > HP"
      ],
      [
        "Boots",
        "Elemental Mastery > SPD > ATK"
      ]
    ],
    "substats": "Wind Shield / damage evasion / Lightning-on-movement / paired Crit + Accuracy or Crit DMG > Elemental Mastery / Crit Rate / Accuracy / Crit DMG; PvP damage/resistance for PvP"
  },
  "Templar": {
    "tank": {
      "label": "Tank",
      "rule": "Prioritize paired Block Rate + Block Efficiency and the Season 3 weapon Auto-protect affix. SPD drives buff and Taunt timing; choose enough Block for the opponent’s Accuracy rather than a fixed universal target.",
      "rows": [
        [
          "Sword",
          "SPD > ATK > Elemental Mastery > Physical Mastery"
        ],
        [
          "Shield",
          "Block > DEF > HP > Physical RES = Elemental RES"
        ],
        [
          "Helmet",
          "DEF ≥ Physical RES = Elemental RES > HP > Effect RES"
        ],
        [
          "Chest",
          "DEF ≥ Physical RES = Elemental RES > HP"
        ],
        [
          "Boots",
          "SPD > ATK = Elemental Mastery > Physical Mastery / Effect Hit Rate"
        ]
      ],
      "substats": "Block Rate + Block Efficiency / weapon Auto-protect > Block Rate / paired Block + Crit RES > paired Crit / PvP damage and resistance; defensive stats as needed"
    },
    "dps": {
      "label": "DPS",
      "rule": "The offensive T5 bars still use the source’s SPD-first gear priorities. Keep Block for the matchup, then compare paired Crit and offensive affixes against the defensive utility you would lose.",
      "rows": [
        [
          "Sword",
          "SPD > ATK > Elemental Mastery > Physical Mastery"
        ],
        [
          "Shield",
          "Block > DEF > HP > Physical RES = Elemental RES"
        ],
        [
          "Helmet",
          "DEF ≥ Physical RES = Elemental RES > HP > Effect RES"
        ],
        [
          "Chest",
          "DEF ≥ Physical RES = Elemental RES > HP"
        ],
        [
          "Boots",
          "SPD > ATK = Elemental Mastery > Physical Mastery / Effect Hit Rate"
        ]
      ],
      "substats": "Block Rate + Block Efficiency / weapon Auto-protect > paired Crit Rate + Crit DMG or Accuracy > matchup Block / PvP damage and resistance > flat stats / Mastery"
    }
  },
  "Prophet": {
    "dps": {
      "label": "DPS",
      "rule": "T5 direct damage still needs reliable debuffs. Get enough Effect Hit Rate for the encounter, then favor paired Crit or damage against debuffed targets; do not treat Effect Hit Rate as an unlimited stacking goal.",
      "rows": [
        [
          "Staff",
          "Effect Hit Rate ≥ Elemental Mastery ≥ ATK > SPD"
        ],
        [
          "Orb",
          "Effect Hit Rate ≥ Elemental Mastery ≥ ATK > SPD"
        ],
        [
          "Helmet",
          "DEF ≥ Physical RES = Elemental RES > HP > Effect RES"
        ],
        [
          "Chest",
          "DEF ≥ Physical RES = Elemental RES > HP"
        ],
        [
          "Boots",
          "Elemental Mastery > ATK > SPD"
        ]
      ],
      "substats": "Paired Crit + Accuracy / Crit DMG and debuffed-target damage > Effect Hit Rate as needed / stat-to-ATK conversion / Crit / Elemental Mastery; PvP or monster bonuses by content"
    },
    "heals": {
      "label": "Heals",
      "rule": "Healer Prophet retains SPD-first offensive slots and HP-first armor. Healing Boost and paired Block are premium survival/support rolls; the source favors broadly useful DPS rolls when a setup also plays damage.",
      "rows": [
        [
          "Staff",
          "SPD > Effect Hit Rate > Elemental Mastery > ATK"
        ],
        [
          "Orb",
          "SPD > Effect Hit Rate > Elemental Mastery > ATK"
        ],
        [
          "Helmet",
          "HP > DEF ≥ Physical RES = Elemental RES > Effect RES"
        ],
        [
          "Chest",
          "HP > DEF ≥ Physical RES = Elemental RES"
        ],
        [
          "Boots",
          "SPD > Elemental Mastery > ATK"
        ]
      ],
      "substats": "Block Rate + Block Efficiency / Healing Boost > damage evasion / paired Block + Crit RES / SPD / SPD% / HP / HP% / paired DMG RES + Healing Boost"
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
  "Ravager": [
    "crit",
    "critdmg",
    "critpair",
    "acc",
    "critacc",
    "em",
    "spd",
    "spdpct",
    "atk",
    "atkpct"
  ],
  "Magister": [
    "crit",
    "critdmg",
    "critpair",
    "critacc",
    "em",
    "acc",
    "spd",
    "atk"
  ],
  "Templar": {
    "tank": [
      "block",
      "blockpair",
      "def",
      "spd",
      "hp",
      "defpct",
      "spdpct",
      "hppct"
    ],
    "dps": [
      "block",
      "blockpair",
      "crit",
      "critdmg",
      "critpair",
      "critacc",
      "spd",
      "atk",
      "em"
    ]
  },
  "Prophet": {
    "dps": [
      "ehr",
      "crit",
      "critdmg",
      "critpair",
      "critacc",
      "em",
      "atk",
      "atkpct",
      "spd",
      "spdpct"
    ],
    "heals": [
      "heal",
      "healpair",
      "block",
      "blockpair",
      "spd",
      "spdpct",
      "hp",
      "hppct",
      "dmgres"
    ]
  }
};

export const FANTOMON_GUIDANCE={
  "Ravager": [
    [
      "Damage lead",
      "Nyxarchon",
      "The T5 guide favors its damage and DEF reduction, especially in longer fights."
    ],
    [
      "Opening tempo",
      "Pandarial",
      "Opening cooldown reduction supports burst; compare it with Nyx for the fight’s length."
    ],
    [
      "PvP / alternatives",
      "Aegiswing · Sylvaerie · Zeioletus",
      "Aegiswing supplies survival. Compare the non-Mythic damage options with your own stats."
    ]
  ],
  "Magister": [
    [
      "General lead",
      "Pandarial",
      "The T5 source’s usual pick: opening cooldown reduction lets the published bars omit Rapid Cast, with healing utility."
    ],
    [
      "Damage alternative",
      "Nyxarchon",
      "DEF reduction and personal damage remain useful when longer-fight output wins over opening tempo."
    ],
    [
      "PvP / later S3",
      "Aegiswing · Prismora",
      "Aegiswing is a defensive option. Prismora is a later-season healing option, but the source gives it low Mage priority."
    ]
  ],
  "Templar": [
    [
      "Tank lead",
      "Aegiswing",
      "Taunt, debuffs and survival remain the source’s priority tank investment."
    ],
    [
      "Published dungeon bar",
      "Pandarial",
      "The Generic Dungeon/4vs4 preset assumes its opening cooldown reduction; it also supports offensive bars."
    ],
    [
      "Team support",
      "Kels · Nyxarchon",
      "Kels supplies Dispel and potential DEF reduction; Nyx adds damage and debuffs."
    ],
    [
      "Later S3 PvP",
      "Prismora",
      "A later Aethyris unlock offering Purity and a revive. Its one-debuff cleanse is not a blanket answer to double Taunt."
    ]
  ],
  "Prophet": [
    [
      "Damage / healing lead",
      "Pandarial",
      "The T5 guide favors opening cooldown reduction and Fragility for burst damage and early healing."
    ],
    [
      "Damage / PvP alternatives",
      "Nyxarchon · Aegiswing",
      "Nyx adds damage and DEF reduction; Aegiswing is the high-end PvP survival option."
    ],
    [
      "Before a Mythic",
      "Zeioletus · Sylvaerie · Mandragora",
      "Compare Zeioletus and Sylvaerie for damage; Mandragora is the healing-focused alternative."
    ],
    [
      "Later S3 support",
      "Prismora",
      "A later Aethyris unlock for dedicated healing, immunity and revival; it gives up Pandarial’s opening cooldown reduction."
    ]
  ]
};
