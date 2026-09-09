from pathlib import Path

PATH = Path("index.html")

OLD = '''          <div class="s2TargetPresets" id="s2TargetPresets" hidden aria-label="Season 2 common planning targets"><span>S2 planning targets</span><div><button type="button" data-s2-target="680" title="QY: Basic">680 · Basic</button><button type="button" data-s2-target="800" title="QY: F2P / Light">800 · F2P/Light</button><button type="button" data-s2-target="920" title="QY: Light / Mid spender">920 · Light/Mid</button><button type="button" data-s2-target="1060" title="QY: Stop point">1060 · Stop</button></div><small>QY recommendation tiers · any total still works.</small></div>'''

NEW = '''          <div class="s2TargetPresets" id="s2TargetPresets" hidden aria-label="Season 2 Primostar breakpoints"><span>S2 breakpoints</span><div><button type="button" data-s2-target="680">680</button><button type="button" data-s2-target="800">800</button><button type="button" data-s2-target="920">920</button><button type="button" data-s2-target="990">990</button><button type="button" data-s2-target="1060">1060</button><button type="button" data-s2-target="1200">1200</button><button type="button" data-s2-target="1280">1280</button></div><small>S2 breakpoint shortcuts · any total still works.</small></div>'''

STYLE_OLD = '''.s2TargetPresets{grid-column:1/-1;border:1px solid var(--line);background:var(--filter-bg);border-radius:10px;padding:9px 10px;display:grid;grid-template-columns:auto 1fr auto;align-items:center;gap:8px 10px}
.s2TargetPresets[hidden],.s2ProgressionGates[hidden]{display:none!important}
.s2TargetPresets>span{color:var(--green);font-size:9px;font-weight:850;letter-spacing:.06em;text-transform:uppercase}
.s2TargetPresets>div{display:flex;gap:5px;flex-wrap:wrap}
.s2TargetPresets button{border:1px solid var(--line);background:var(--surface);color:var(--body-text);border-radius:8px;min-height:32px;padding:6px 9px;font-size:10px;font-weight:850;cursor:pointer}
.s2TargetPresets button:hover,.s2TargetPresets button.active{border-color:var(--green);color:var(--green);background:var(--green-soft)}
.s2TargetPresets small{color:var(--muted);font-size:8px;line-height:1.35;text-align:right}
.s2ProgressionGates{margin-top:8px;display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:6px}
.s2ProgressionGates span{border:1px solid var(--line);background:var(--filter-bg);color:var(--secondary-text);border-radius:9px;padding:7px 6px;text-align:center;font-size:8px;line-height:1.25;font-weight:750}
.s2ProgressionGates b{display:block;color:var(--green);font-size:12px;line-height:1.1;margin-bottom:2px}
@media(max-width:760px){.s2TargetPresets{grid-template-columns:1fr}.s2TargetPresets small{text-align:left}.s2ProgressionGates{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media(max-width:520px){.s2ProgressionGates{grid-template-columns:repeat(2,minmax(0,1fr))}}'''

STYLE_NEW = '''.s2TargetPresets{grid-column:1/-1;border:1px solid var(--line);background:var(--ui-subpanel,var(--filter-bg));border-radius:10px;padding:10px 11px;display:grid;grid-template-columns:auto 1fr auto;align-items:center;gap:8px 10px}
.s2TargetPresets[hidden],.s2ProgressionGates[hidden]{display:none!important}
.s2TargetPresets>span{color:var(--muted);font-size:10px;font-weight:850;letter-spacing:.06em;text-transform:uppercase}
.s2TargetPresets>div{display:flex;gap:6px;flex-wrap:wrap}
.s2TargetPresets button{border:1px solid var(--line);background:var(--ui-inset,var(--surface));color:var(--ink);border-radius:8px;min-height:36px;padding:7px 10px;font-size:11px;line-height:1.2;font-weight:850;cursor:pointer;transition:background .16s,color .16s,border-color .16s}
.s2TargetPresets button:hover{border-color:var(--green);color:var(--green);background:var(--ui-hover,var(--green-soft))}
.s2TargetPresets button.active{border-color:var(--green);color:var(--green);background:var(--calc-accent-soft,var(--green-soft));box-shadow:0 0 0 1px color-mix(in srgb,var(--green) 12%,transparent)}
.s2TargetPresets small{color:var(--secondary-text);font-size:9px;line-height:1.4;text-align:right}
.s2ProgressionGates{margin-top:8px;display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:6px}
.s2ProgressionGates span{border:1px solid var(--line);background:var(--ui-subpanel,var(--filter-bg));color:var(--secondary-text);border-radius:9px;padding:8px 6px;text-align:center;font-size:9px;line-height:1.3;font-weight:750}
.s2ProgressionGates b{display:block;color:var(--green);font-size:13px;line-height:1.1;margin-bottom:2px}
@media(max-width:760px){.s2TargetPresets{grid-template-columns:1fr}.s2TargetPresets small{text-align:left}.s2TargetPresets button{min-height:40px}.s2ProgressionGates{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media(max-width:520px){.s2ProgressionGates{grid-template-columns:repeat(2,minmax(0,1fr))}}'''

EXPECTED_TARGETS = (680, 800, 920, 990, 1060, 1200, 1280)


def validate(text: str) -> None:
    if NEW not in text:
        raise SystemExit("S2 breakpoint block did not match expected output")
    if STYLE_NEW not in text:
        raise SystemExit("S2 breakpoint styling did not match expected output")
    for target in EXPECTED_TARGETS:
        needle = f'data-s2-target="{target}">{target}</button>'
        if needle not in text:
            raise SystemExit(f"Missing numeric-only S2 breakpoint {target}")
    forbidden = (
        "680 · Basic",
        "800 · F2P/Light",
        "920 · Light/Mid",
        "1060 · Stop",
        'title="QY: Basic"',
        'title="QY: F2P / Light"',
        'title="QY: Light / Mid spender"',
        'title="QY: Stop point"',
    )
    for value in forbidden:
        if value in text:
            raise SystemExit(f"Old named breakpoint text is still present: {value}")


def main() -> None:
    text = PATH.read_text(encoding="utf-8")
    changed = False

    if NEW not in text:
        if OLD not in text:
            raise SystemExit("Could not find the existing S2 planning-target block; refusing a blind edit")
        text = text.replace(OLD, NEW, 1)
        changed = True

    if STYLE_NEW not in text:
        if STYLE_OLD not in text:
            raise SystemExit("Could not find the existing S2 shortcut style block; refusing a blind edit")
        text = text.replace(STYLE_OLD, STYLE_NEW, 1)
        changed = True

    validate(text)
    if changed:
        PATH.write_text(text, encoding="utf-8")
        print("Updated S2 Primostar shortcut typography and color consistency")
    else:
        print("S2 Primostar shortcuts already current")


if __name__ == "__main__":
    main()
