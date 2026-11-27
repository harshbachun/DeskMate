"""Makes the README's 3D buttons: docs/images/download-button.svg and docs/images/badge-*.svg.

Style after uiverse.io/Voxybuns/lucky-fireant-71: the coloured top face sits 0.2em above a darker
base, lifts to 0.33em on hover and drops flat while pressed. GitHub shows README SVGs as plain
images, which can't react to the mouse, so each button also plays that lift-and-press by itself
every 5 s, staggered so they take turns (hover/press still work when an SVG is opened on its own).

Each button has two halves: a grey label (Verdana bold) and a coloured value in JetBrains Mono Bold.
The value font is embedded as a small subset, because an SVG shown as an image can't load fonts.

Usage:  python tools/make_badges.py      (set RELEASE first when a new version ships)
Needs:  Google Chrome (to measure the label text), `pip install fonttools`, and JetBrains Mono
        installed (the variable TTF from jetbrains.com/lp/mono or Google Fonts).
"""
import base64, html, io, json, os, pathlib, re, subprocess, tempfile
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools import subset

RELEASE = 'v1.0.2'
LABEL_BG = '#555'
LABEL_FONT = 'Verdana, Geneva, "DejaVu Sans", sans-serif'
MONO_ADVANCE = 0.6  # JetBrains Mono: every glyph is 600/1000 em wide
R = 10.5            # corner radius, the same on every button

# Sizes: font px, face height, inner padding, outer padding (extra room past the rounded corner)
BADGE = dict(f=13, h=30, pad=9, outer=13)
DOWNLOAD = dict(f=15, h=44, pad=14, outer=18)

BUTTONS = [  # file, label, value, value colour, base/outline colour, size, arrow icon
    ('download-button', 'Download', 'DeskmateAgent.exe', '#2563eb', '#1e3a8a', DOWNLOAD, True),
    ('badge-release', 'release', RELEASE, '#22c55e', '#14532d', BADGE, False),
    ('badge-pc', 'PC', 'Windows 10/11', '#0078d4', '#0b3a66', BADGE, False),
    ('badge-phone', 'phone', 'Android 5+', '#3ddc84', '#14532d', BADGE, False),
    ('badge-license', 'license', 'MIT', '#9f9f9f', '#3f3f46', BADGE, False),
]

CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
MONO_TTF = [os.path.expandvars(r'%LOCALAPPDATA%\Microsoft\Windows\Fonts\JetBrainsMono-VariableFont_wght.ttf'),
            r'C:\Windows\Fonts\JetBrainsMono-VariableFont_wght.ttf']


def measure_labels(items):
    """Width in px of each (text, font size) in Verdana bold, measured in headless Chrome."""
    body = ''.join(f'<text style="{html.escape(f"font:bold {f}px {LABEL_FONT}")}">{html.escape(t)}</text>' for t, f in items)
    page = ('<svg xmlns="http://www.w3.org/2000/svg">' + body + '</svg><script>document.title=JSON.stringify('
            '[...document.querySelectorAll("text")].map(t=>t.getComputedTextLength()))</script>')
    p = pathlib.Path(tempfile.gettempdir(), 'measure-badges.html')
    p.write_text(page, encoding='utf-8')
    out = subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--dump-dom', p.as_uri()],
                         capture_output=True, text=True, encoding='utf-8').stdout
    return json.loads(html.unescape(re.search(r'<title>(.*?)</title>', out).group(1)))


def mono_bold():
    path = next(p for p in MONO_TTF if os.path.exists(p))
    return instancer.instantiateVariableFont(TTFont(path), {'wght': 700})


def mono_subset_b64(font, text):
    f = TTFont(io.BytesIO(_save(font)))
    opts = subset.Options(); opts.flavor = 'woff'; opts.name_IDs = ['*']; opts.notdef_outline = True
    s = subset.Subsetter(opts); s.populate(text=text); s.subset(f)
    return base64.b64encode(_save(f, 'woff')).decode()


def _save(font, flavor=None):
    font.flavor = flavor
    b = io.BytesIO(); font.save(b); return b.getvalue()


def make(label, value, color, base, size, icon, label_w, font_b64, delay=0.0):
    f, h, pad, outer = size['f'], size['h'], size['pad'], size['outer']
    lift, hover = round(0.2 * f, 1), round(0.33 * f, 1)
    icon_w = f + 6 if icon else 0
    value_w = len(value) * MONO_ADVANCE * f
    a = round(outer + icon_w + label_w + pad)   # left (label) half
    b = round(pad + value_w + outer)            # right (value) half
    W, y = a + b + 2, round(hover) + 2
    H = y + h + 1
    ty = round(y + h / 2 + f * 0.36, 1)
    arrow = ''
    if icon:
        cx, s = 1 + outer + f / 2 - 1, f / 15
        top, tip = y + h / 2 - 7 * s, y + h / 2 + 3.5 * s
        arrow = (f'\n    <path d="M{cx:.1f} {top:.1f}V{tip:.1f}m-{4.5*s:.1f}-{4.5*s:.1f}l{4.5*s:.1f} {4.5*s:.1f} {4.5*s:.1f}-{4.5*s:.1f}'
                 f'M{cx-6*s:.1f} {tip+4*s:.1f}h{12*s:.1f}" fill="none" stroke="#fff" stroke-width="{2.2*s:.1f}" '
                 f'stroke-linecap="round" stroke-linejoin="round"/>')
    lx = 1 + outer + icon_w + label_w / 2
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{label} {value}">
  <title>{label} {value}</title>
  <!-- 3D button for the README, made by tools/make_badges.py. JetBrains Mono subset: SIL Open Font License 1.1, (c) The JetBrains Mono Project Authors -->
  <style>
    @font-face {{ font-family: "JBM"; font-weight: 700; src: url(data:font/woff;base64,{font_b64}) format("woff"); }}
    .top {{ transform: translateY(-{lift}px); transition: transform .1s ease;
            animation: press 5s ease-in-out {delay:.1f}s infinite; }}
    @keyframes press {{ 0%, 72% {{ transform: translateY(-{lift}px); }} 80%, 86% {{ transform: translateY(-{hover}px); }}
                        89% {{ transform: translateY(0); }} 94%, 100% {{ transform: translateY(-{lift}px); }} }}
    @media (prefers-reduced-motion: reduce) {{ .top {{ animation: none; }} }}
    svg:hover .top {{ animation: none; transform: translateY(-{hover}px); }}
    svg:active .top {{ animation: none; transform: translateY(0); }}
    svg {{ cursor: pointer; }}
    text {{ font-size: {f}px; font-weight: bold; fill: #fff; }}
    .l {{ font-family: {LABEL_FONT}; }}
    .v {{ font-family: "JBM", "JetBrains Mono", Consolas, monospace; }}
  </style>
  <defs><clipPath id="face"><rect x="1" y="{y}" width="{W - 2}" height="{h}" rx="{R}"/></clipPath></defs>
  <rect x="1" y="{y}" width="{W - 2}" height="{h}" rx="{R}" fill="{base}"/>
  <g class="top">
    <g clip-path="url(#face)">
      <rect x="1" y="{y}" width="{a}" height="{h}" fill="{LABEL_BG}"/>
      <rect x="{1 + a}" y="{y}" width="{b}" height="{h}" fill="{color}"/>
    </g>
    <rect x="2" y="{y + 1}" width="{W - 4}" height="{h - 2}" rx="{R - 1}" fill="none" stroke="{base}" stroke-width="2"/>{arrow}
    <text class="l" x="{lx:.1f}" y="{ty}" text-anchor="middle">{html.escape(label)}</text>
    <text class="v" x="{1 + a + b / 2:.1f}" y="{ty}" text-anchor="middle" textLength="{value_w:.1f}">{html.escape(value)}</text>
  </g>
</svg>
'''


repo = pathlib.Path(__file__).resolve().parent.parent
widths = measure_labels([(lbl, size['f']) for _, lbl, _, _, _, size, _ in BUTTONS])
mono = mono_bold()
for i, ((name, label, value, color, base, size, icon), lw) in enumerate(zip(BUTTONS, widths)):
    # staggered so the buttons take turns: badges left to right, then the download button
    delay = (len(BUTTONS) - 1) * 0.3 if i == 0 else (i - 1) * 0.3
    svg = make(label, value, color, base, size, icon, lw, mono_subset_b64(mono, value), delay)
    (repo / 'docs' / 'images' / f'{name}.svg').write_text(svg, encoding='utf-8')
    print(name, re.search(r'width="(\d+)" height="(\d+)"', svg).groups(), f'{len(svg)//1024} KB')
