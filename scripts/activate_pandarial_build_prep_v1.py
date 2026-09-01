from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data' / 'pandarial-build-prep-v1.json'
TARGETS = [ROOT / 'index.html', ROOT / '.github' / 'build-fantomons-inject.html']
MARK = 'PANDARIAL_RELEASE_V1'

REPLS = [
    (
        "      Solo:[pick('Nyxarchon','Main current S2 pick: Prydwen still rates its damage + DEF shred as BIS for generic content.'),pick('Aegiswing','Excellent high-push alternative when survival is the limiter.'),pick('Sylvaerie','Permanent ATK + SPD is the best currently available general damage alternative.'),pick('Zeioletus','Extra recurring burst if your stats make it outperform Sylvaerie.')],",
        "      Solo:[pick('Nyxarchon','Main all-content lead: DEF shred remains Conqueror’s strongest long-fight/raw-DPS option.'),pick('Pandarial','Burst/front-load alt: starts every fight with -1 Technique CD plus a battle-long DMG Boost; Adult form also adds Fragility and healing.'),pick('Aegiswing','High-push survival alternative when staying alive is the limiter.'),pick('Sylvaerie','Permanent ATK + SPD remains a strong non-Mythic general option.')],"
    ),
    (
        "      Boss:[pick('Nyxarchon','Main long-fight choice: DEF shred remains extremely valuable on hard bosses.'),pick('Sylvaerie','Permanent ATK + SPD scales the full boss rotation.'),pick('Zeioletus','Reliable extra damage if it tests better on your account.'),pick('Aegiswing','Defensive fallback for bosses where dying is the actual DPS loss.')],",
        "      Boss:[pick('Nyxarchon','Main long-fight choice: repeated DEF shred remains more valuable than opening burst on hard bosses.'),pick('Pandarial','Front-load alt for shorter boss fights or faster first rotations; Adult Fragility adds another damage-amplification window.'),pick('Sylvaerie','Permanent ATK + SPD scales the full boss rotation.'),pick('Aegiswing','Defensive fallback when dying is the actual DPS loss.')],"
    ),
    (
        "      PvP:[pick('Aegiswing','Main PvP choice: extra survival plus its S2 Materialization utility is more valuable here than pure damage.'),pick('Nyxarchon','Greedy damage/DEF-shred alternative.'),pick('Sylvaerie','SPD can help win action tempo while still boosting ATK.'),pick('Zeioletus','Pure damage alternative when survivability is already covered.')]",
        "      PvP:[pick('Aegiswing','Main PvP choice: extra survival and S2 control utility remain the safer Conqueror default.'),pick('Pandarial','Burst-tempo alt: -1 opening Technique CD can front-load pressure before longer-fight DEF shred catches up.'),pick('Nyxarchon','Greedy damage/DEF-shred alternative.'),pick('Sylvaerie','SPD can help win action tempo while still boosting ATK.')]"
    ),
    (
        "      Solo:[pick('Aegiswing','Main Guardian investment: Prydwen calls it the priority Mythic for the class, with survival and Taunt synergy.'),pick('Nyxarchon','Best offensive support alternative when you need more damage and debuffs.'),pick('Kels','Useful dispel/DEF-down utility when the stage benefits from it.'),pick('Boaro','Budget defensive option with shielding and S2 knockback utility.')],",
        "      Solo:[pick('Pandarial','Main aggressive Guardian lead: opening CD reduction enables faster high-CD offense, while Adult healing + Fragility add sustain and team damage.'),pick('Aegiswing','Safer tank/bruiser alt with the class’s strongest Taunt and survival synergy.'),pick('Nyxarchon','Offensive support alternative when repeated DEF shred matters more than opening tempo.'),pick('Kels','Dispel/DEF-down utility when the stage benefits from it.')],"
    ),
    (
        "      Dungeon:[pick('Aegiswing','Main tank lead: survival, extra Taunt and reduced damage from taunted enemies fit the dungeon job perfectly.'),pick('Kels','Strong party utility through dispel and Materialized DEF Down.'),pick('Nyxarchon','Offensive support option when your team wants faster kills.'),pick('Terragon','ATK/DMG reduction utility when enemy damage is the bigger problem.')],",
        "      Dungeon:[pick('Aegiswing','Main tank lead: survival, extra Taunt and reduced damage from taunted enemies still fit the dungeon job best.'),pick('Pandarial','Aggressive/support alt: opening CD reduction, Adult healing and Fragility improve tempo when raw tankiness is already sufficient.'),pick('Kels','Strong party utility through dispel and Materialized DEF Down.'),pick('Terragon','ATK/DMG reduction utility when enemy damage is the bigger problem.')],"
    ),
    (
        "      Boss:[pick('Kels','Main boss-support pick: Prydwen specifically highlights its dispel + Materialized DEF Down for team support.'),pick('Nyxarchon','Amplifies team damage with reliable debuffs and its own damage.'),pick('Terragon','Great when the raid needs enemy ATK/DMG reduction more than another damage debuff.'),pick('Aegiswing','Use when your personal survival or Taunt uptime is the limiting factor.')],",
        "      Boss:[pick('Kels','Main boss-support pick when dispel + repeatable DEF Down are valuable to the team.'),pick('Pandarial','Hybrid alt: faster opening cooldowns plus Adult Fragility/healing give strong early team value.'),pick('Nyxarchon','Repeated damage/DEF-shred alternative for longer fights.'),pick('Terragon','Use when reducing boss ATK/pressure matters more than another damage amp.')],"
    ),
    (
        "      PvP:[pick('Aegiswing','Main PvP Guardian pet: extra Taunt, survival and anti-Taunt damage reduction match the class role.'),pick('Kels','Utility alternative for dispelling buffs and adding DEF Down.'),pick('Nyxarchon','Greedy pressure option when your team already has enough protection.'),pick('Boaro','Budget control/survival alternative with shielding and knockback utility.')]",
        "      PvP:[pick('Aegiswing','Main PvP Guardian pet: extra Taunt, survival and anti-Taunt damage reduction remain the safest class fit.'),pick('Pandarial','Aggressive PvP alt: -1 opening Technique CD lets Guardian bring high-CD pressure online earlier.'),pick('Kels','Utility alternative for dispelling buffs and adding DEF Down.'),pick('Nyxarchon','Greedy pressure option when your team already has enough protection.')]"
    ),
    (
        "      Tournament:[pick('Nyxarchon','Main hybrid Tournament pick: adds real damage and DEF shred while the Dominator handles buffs and utility.'),pick('Terragon','Alt team-utility pick when reducing enemy ATK/pressure matters more than personal damage.')],",
        "      Tournament:[pick('Pandarial','Main hybrid Tournament lead: opening CD reduction accelerates support/burst tools and Adult healing + Fragility contribute on both sides of the fight.'),pick('Nyxarchon','Damage-focused alt when repeated Dark damage and DEF shred matter more than opening support tempo.')],"
    ),
    (
        "      Solo:[pick('Nyxarchon','Main DPS choice: Prydwen calls Nyx Dominator’s BIS thanks to Dark AoE damage and its supportive effect.'),pick('Zeioletus','Best straightforward F2P damage stopgap.'),pick('Sylvaerie','ATK + SPD can outperform Zei on some accounts.'),pick('Aegiswing','Use when surviving solo progression is more important than max damage.')],",
        "      Solo:[pick('Nyxarchon','Main pure-DPS lead: Dark AoE damage and repeated DEF shred remain Dominator’s strongest damage-first package.'),pick('Pandarial','Hybrid/burst alt: opening CD reduction front-loads Techniques and Adult form adds healing + Fragility.'),pick('Zeioletus','Straightforward F2P damage stopgap.'),pick('Sylvaerie','ATK + SPD can outperform Zei on some accounts.')],"
    ),
    (
        "      Dungeon:[pick('Mandragora','Main pure-healing pick: directly adds healing whenever you use ally-targeted Techniques.'),pick('Herbote','Strong S2 healing alternative once Materialized because it can extend its healing to allies.'),pick('Sylvaerie','SPD gives you more actions to heal/support.'),pick('Terragon','Support alternative when reducing enemy ATK/DMG helps the whole party more than extra healing.')],",
        "      Dungeon:[pick('Pandarial','Main healer/hybrid lead: -1 opening Technique CD enables Turn-1 healing and Adult Emerald Dew adds recurring AoE healing.'),pick('Mandragora','Pure-healing alt when you value extra ally-targeted healing over Pandarial’s burst/support package.'),pick('Herbote','Strong healing alternative once Materialized because it can extend healing to allies.'),pick('Sylvaerie','SPD gives you more actions to heal/support.')],"
    ),
    (
        "      Boss:[pick('Nyxarchon','Main DPS lead for single-target Dark builds and team damage support.'),pick('Zeioletus','Direct damage alternative before or instead of Nyx.'),pick('Sylvaerie','Permanent SPD + ATK scales the whole boss rotation.'),pick('Terragon','Useful support option when lowering the boss’s ATK matters.')],",
        "      Boss:[pick('Nyxarchon','Main DPS lead for single-target Dark builds and repeated team damage support.'),pick('Pandarial','Hybrid/front-load alt when the opening cooldown reduction and Adult Fragility/healing outweigh longer-fight Nyx value.'),pick('Zeioletus','Direct damage alternative before or instead of a Mythic.'),pick('Sylvaerie','Permanent SPD + ATK scales the whole boss rotation.')],"
    ),
    (
        "      PvP:[pick('Mandragora','Main support/healing pick when your job is keeping teammates alive.'),pick('Aegiswing','Survival-first alternative when you are being focused.'),pick('Terragon','Debuffing option that can reduce enemy pressure while you support.'),pick('Sylvaerie','SPD improves support tempo when raw healing is already sufficient.')]",
        "      PvP:[pick('Nyxarchon','Main solo-Arena DPS lead: the Arena card is damage/utility rather than a pure-healing bar.'),pick('Pandarial','Burst/hybrid alt: opening cooldown reduction speeds pressure and Adult form still adds support value.'),pick('Aegiswing','Survival-first alternative when you are being focused.'),pick('Mandragora','Use only when you deliberately pivot the PvP bar toward healing/support.')]"
    ),
    (
        "If Pandarial and your ranks support it, Luminous Shield → Light Sword Array is the aggressive flex; keep Block stats high.",
        "With Pandarial, Luminous Shield → Light Sword Array is the aggressive flex because the opening CD reduction brings the higher-CD pressure online sooner; keep Block stats high."
    ),
]


def load_data() -> dict:
    return json.loads(DATA.read_text(encoding='utf-8'))


def gate_time(data: dict) -> datetime:
    raw = data['release_gate_utc'].replace('Z', '+00:00')
    return datetime.fromisoformat(raw).astimezone(timezone.utc)


def release_due(data: dict, now: datetime | None = None) -> bool:
    if os.getenv('PANDARIAL_FORCE_ACTIVATE') == '1':
        return True
    now = now or datetime.now(timezone.utc)
    return now >= gate_time(data)


def patch_text(text: str) -> tuple[str, int]:
    if MARK in text:
        return text, 0
    changed = 0
    out = text
    for old, new in REPLS:
        if old in out:
            out = out.replace(old, new)
            changed += 1
    if changed < 12:
        raise SystemExit(f'Pandarial prep found only {changed}/{len(REPLS)} expected anchors; refusing partial activation')
    anchor = "  const FANTO={"
    if anchor not in out:
        raise SystemExit('Could not find FANTO anchor for Pandarial activation marker')
    out = out.replace(anchor, f"  // {MARK}\n{anchor}", 1)
    return out, changed


def main() -> int:
    data = load_data()
    if not release_due(data):
        print(f"Pandarial gate not live yet; waiting until {data['release_gate_utc']}")
        return 0

    total = 0
    for path in TARGETS:
        text = path.read_text(encoding='utf-8')
        patched, changed = patch_text(text)
        if changed:
            path.write_text(patched, encoding='utf-8')
            print(f'{path.relative_to(ROOT)}: activated Pandarial recommendations ({changed} anchors)')
            total += changed
        else:
            print(f'{path.relative_to(ROOT)}: Pandarial recommendations already active')
    print(f'Pandarial activation complete; {total} replacements')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
