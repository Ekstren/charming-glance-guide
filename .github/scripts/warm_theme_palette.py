from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')

light_old=':root{--lightningcss-light:initial;--lightningcss-dark: ;color-scheme:light;--bg:#e9e6e0;--surface:#f4f1ec;--surface-glass:#f4f1ece0;--topbar:#efebe5ee;--ink:#292b2d;--body-text:#464b4e;--secondary-text:#686e71;--muted:#6b7074;--line:#d2cdc5;--green:#3b8c70;--green-soft:#d5e8e1;--blue:#477fa9;--gold:#b98631;--red:#b95f54;--purple:#7c62a8;--filter-bg:#f1eee8d6;--filter-text:#666b6e;--today-bg:#e1eee9;--today-border:#94c1b1;--footer:#efebe5}'
light_new=':root{--lightningcss-light:initial;--lightningcss-dark: ;color-scheme:light;--bg:#ddd5c8;--surface:#eee8de;--surface-glass:#eee8dee8;--topbar:#e6ded2ee;--ink:#302a25;--body-text:#514942;--secondary-text:#756c64;--muted:#7f756c;--line:#c8beb0;--green:#71805d;--green-soft:#d9dece;--blue:#647d91;--gold:#b28448;--red:#a96155;--purple:#806b88;--filter-bg:#e9e1d5dc;--filter-text:#625a53;--today-bg:#e1e2d4;--today-border:#aeb99a;--footer:#e6ded2;--accent-strong:#667451;--accent-deep:#4f5b40}'
dark_old=':root[data-theme=dark]{--lightningcss-light: ;--lightningcss-dark:initial;color-scheme:dark;--bg:#101513;--surface:#19201d;--surface-glass:#1a221fdb;--topbar:#111715eb;--ink:#edf3f0;--body-text:#d1dad6;--secondary-text:#9eaaa5;--muted:#98a39e;--line:#303a36;--green:#62bd99;--green-soft:#1e3a31;--blue:#73acd2;--gold:#d5a653;--red:#df8176;--purple:#a98bd5;--filter-bg:#19211ed1;--filter-text:#b4bfba;--today-bg:#162b24;--today-border:#3f7d68;--footer:#151b19}'
dark_new=':root[data-theme=dark]{--lightningcss-light: ;--lightningcss-dark:initial;color-scheme:dark;--bg:#151310;--surface:#211e1a;--surface-glass:#241f1bdc;--topbar:#181512ee;--ink:#eee7dc;--body-text:#d5cabd;--secondary-text:#aa9d8f;--muted:#9b8f82;--line:#3c352e;--green:#a1b07b;--green-soft:#2d3326;--blue:#8da2ae;--gold:#d0a15f;--red:#cf7d6a;--purple:#a28aa6;--filter-bg:#24201cda;--filter-text:#c0b5a8;--today-bg:#292c22;--today-border:#596447;--footer:#1b1815;--accent-strong:#566447;--accent-deep:#3f4b34}'
for label,old,new in [('light',light_old,light_new),('dark',dark_old,dark_new)]:
    if old not in s:
        raise SystemExit(f'{label} theme block not found')
    s=s.replace(old,new,1)

# Replace the old cool-teal hard-coded interactive accent with theme-aware warm olive variables.
s=s.replace('background:#253f37','background:var(--accent-deep)')
s=s.replace('background:#345e51','background:var(--accent-strong)')
s=s.replace('box-shadow:0 7px 18px #264a3f2e','box-shadow:0 7px 18px color-mix(in srgb,var(--accent-deep) 28%,transparent)')

# Catch any remaining exact legacy accent backgrounds used by later appended CSS.
s=s.replace('background:#345e51;', 'background:var(--accent-strong);')
s=s.replace('background:#253f37;', 'background:var(--accent-deep);')

p.write_text(s,encoding='utf-8')
print('Applied warmer earthy palettes to light and dark themes.')
