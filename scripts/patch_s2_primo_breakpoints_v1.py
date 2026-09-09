from pathlib import Path

PATH = Path("index.html")

OLD = '''          <div class="s2TargetPresets" id="s2TargetPresets" hidden aria-label="Season 2 common planning targets"><span>S2 planning targets</span><div><button type="button" data-s2-target="680" title="QY: Basic">680 · Basic</button><button type="button" data-s2-target="800" title="QY: F2P / Light">800 · F2P/Light</button><button type="button" data-s2-target="920" title="QY: Light / Mid spender">920 · Light/Mid</button><button type="button" data-s2-target="1060" title="QY: Stop point">1060 · Stop</button></div><small>QY recommendation tiers · any total still works.</small></div>'''

NEW = '''          <div class="s2TargetPresets" id="s2TargetPresets" hidden aria-label="Season 2 Primostar breakpoints"><span>S2 breakpoints</span><div><button type="button" data-s2-target="680">680</button><button type="button" data-s2-target="800">800</button><button type="button" data-s2-target="920">920</button><button type="button" data-s2-target="990">990</button><button type="button" data-s2-target="1060">1060</button><button type="button" data-s2-target="1200">1200</button><button type="button" data-s2-target="1280">1280</button></div><small>S2 breakpoint shortcuts · any total still works.</small></div>'''

EXPECTED_TARGETS = (680, 800, 920, 990, 1060, 1200, 1280)


def validate(text: str) -> None:
    if NEW not in text:
        raise SystemExit("S2 breakpoint block did not match expected output")
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
    if NEW in text:
        validate(text)
        print("S2 Primostar breakpoints already current")
        return
    if OLD not in text:
        raise SystemExit("Could not find the existing S2 planning-target block; refusing a blind edit")
    text = text.replace(OLD, NEW, 1)
    validate(text)
    PATH.write_text(text, encoding="utf-8")
    print("Updated S2 Primostar breakpoints to numeric-only shortcuts")


if __name__ == "__main__":
    main()
