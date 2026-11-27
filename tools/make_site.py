"""Graphics for the website-style README: docs/images/site-*.svg (banner, feature cards, install steps). All text is JetBrains Mono, embedded as a subset,
because an SVG shown as an image on GitHub can't load fonts.
Run: python tools/make_site.py   (needs fonttools and JetBrains Mono installed)"""
import base64, html, io, os, pathlib, textwrap
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools import subset

OUT = pathlib.Path(__file__).resolve().parent.parent / 'docs' / 'images'
TTF = next(p for p in [os.path.expandvars(r'%LOCALAPPDATA%\Microsoft\Windows\Fonts\JetBrainsMono-VariableFont_wght.ttf'),
                       r'C:\Windows\Fonts\JetBrainsMono-VariableFont_wght.ttf'] if os.path.exists(p))
FONTS = {w: instancer.instantiateVariableFont(TTFont(TTF), {'wght': w}) for w in (400, 700, 800)}
ADV = 0.6  # every JetBrains Mono glyph is 0.6em wide

BG, CARD, LINE, TEXT, MUTED = '#0d1117', '#111827', '#263042', '#f0f6fc', '#9aa7b8'


def _bytes(f, flavor=None):
    f.flavor = flavor; b = io.BytesIO(); f.save(b); return b.getvalue()


def font_css(texts):
    """@font-face rules with only the glyphs used, per weight. texts: {weight: str}"""
    rules = []
    for w, t in texts.items():
        f = TTFont(io.BytesIO(_bytes(FONTS[w])))
        o = subset.Options(); o.flavor = 'woff'; o.name_IDs = ['*']; o.notdef_outline = True
        s = subset.Subsetter(o); s.populate(text=t + ' '); s.subset(f)
        b64 = base64.b64encode(_bytes(f, 'woff')).decode()
        rules.append(f'@font-face{{font-family:"JBM";font-weight:{w};src:url(data:font/woff;base64,{b64}) format("woff")}}')
    return '\n    '.join(rules)


class Doc:
    def __init__(self, w, h, title):
        self.w, self.h, self.title, self.parts, self.used = w, h, title, [], {400: '', 700: '', 800: ''}

    def text(self, x, y, s, size, weight=400, fill=TEXT, anchor='start', extra=''):
        self.used[weight] += s
        self.parts.append(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
                          f'text-anchor="{anchor}" {extra}>{html.escape(s)}</text>')

    def add(self, s): self.parts.append(s)

    def save(self, name, css='', defs=''):
        body = '\n  '.join(self.parts)
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}" role="img" aria-label="{html.escape(self.title)}">
  <title>{html.escape(self.title)}</title>
  <!-- JetBrains Mono subset: SIL Open Font License 1.1, (c) The JetBrains Mono Project Authors -->
  <style>
    {font_css({w: t for w, t in self.used.items() if t})}
    text {{ font-family: "JBM", "JetBrains Mono", Consolas, monospace; }}
    @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
    {css}
  </style>
  <defs>{defs}</defs>
  {body}
</svg>
'''
        (OUT / f'{name}.svg').write_text(svg, encoding='utf-8')
        print(name, f'{len(svg) // 1024} KB')


def tw(s, size): return len(s) * ADV * size


# ---------- icons (24x24 line icons, drawn at scale) ----------
ICONS = {
    'pulse': 'M3 12h4l3-8 4 16 3-8h4',
    'bars': 'M4 7h12M4 12h16M4 17h8',
    'mic': 'M12 3a3 3 0 0 0-3 3v6a3 3 0 0 0 6 0V6a3 3 0 0 0-3-3zM5 11a7 7 0 0 0 14 0M12 18v3',
    'crosshair': 'M12 3v5M12 16v5M3 12h5M16 12h5M12 12h.01M12 6.5a5.5 5.5 0 1 0 0 11 5.5 5.5 0 0 0 0-11z',
    'note': 'M9 18V6l11-2v12M9 18a3 3 0 1 1-6 0 3 3 0 0 1 6 0zM20 16a3 3 0 1 1-6 0 3 3 0 0 1 6 0z',
    'plug': 'M9 2v6M15 2v6M6 8h12v3a6 6 0 0 1-12 0zM12 17v5',
    'download': 'M12 4v11M7 10l5 5 5-5M5 20h14',
    'phone': 'M8 2h8a2 2 0 0 1 2 2v16a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2zM11 18h2',
    'usb': 'M12 2v14M9 5l3-3 3 3M7 9v3l5 3 5-3V8M7 9h.01M17 8h.01M12 16a2 2 0 1 0 0 4 2 2 0 0 0 0-4z',
}


FILLED = {'valorant': ([0.0, 0.0, 32.0, 32.0], ['M19.8,26.1h-0.2c-2.4,0-4.8,0-7.2,0c-0.3,0-0.5-0.1-0.6-0.3c-2.5-3.2-5.1-6.3-7.6-9.5C4.1,16.1,4,16,4,15.8 c0-3.1,0-6.1,0-9.2c0-0.1,0-0.2,0.1-0.2h0.1c5.2,6.5,10.4,13,15.5,19.5c0,0,0,0.1,0.1,0.1L19.8,26.1L19.8,26.1z', 'M27.8,16.3c-0.7,0.9-1.5,1.8-2.2,2.8c-0.2,0.2-0.4,0.3-0.6,0.3c-2.4,0-4.8,0-7.1,0c0,0-0.1,0-0.1,0c-0.1,0-0.2-0.1-0.1-0.2 c0,0,0-0.1,0.1-0.1c2.4-3,4.7-5.9,7.1-8.9c1-1.2,2-2.5,2.9-3.7c0-0.1,0.1-0.1,0.2-0.1c0,0,0.1,0,0.1,0c0,0.1,0,0.1,0,0.2 c0,3,0,6.1,0,9.1C28,16,27.9,16.2,27.8,16.3L27.8,16.3z']), 'musicnote': ([0.0, 0.0, 24.0, 24.0], ['M3.18,19.83Q2,18.65 2,17t1.18-2.83T6,13q0.58,0 1.06,0.14T8,13.55V5L20,3V15q0,1.65-1.18,2.82T16,19t-2.82-1.18T12,15t1.18-2.83T16,11q0.57,0 1.06,0.14T18,11.55V7.43L10,9v8q0,1.65-1.17,2.82T6,21T3.18,19.83Z']), 'discord': ([0.0, -28.5, 256.0, 256.0], ['M216.856339,16.5966031 C200.285002,8.84328665 182.566144,3.2084988 164.041564,0 C161.766523,4.11318106 159.108624,9.64549908 157.276099,14.0464379 C137.583995,11.0849896 118.072967,11.0849896 98.7430163,14.0464379 C96.9108417,9.64549908 94.1925838,4.11318106 91.8971895,0 C73.3526068,3.2084988 55.6133949,8.86399117 39.0420583,16.6376612 C5.61752293,67.146514 -3.4433191,116.400813 1.08711069,164.955721 C23.2560196,181.510915 44.7403634,191.567697 65.8621325,198.148576 C71.0772151,190.971126 75.7283628,183.341335 79.7352139,175.300261 C72.104019,172.400575 64.7949724,168.822202 57.8887866,164.667963 C59.7209612,163.310589 61.5131304,161.891452 63.2445898,160.431257 C105.36741,180.133187 151.134928,180.133187 192.754523,160.431257 C194.506336,161.891452 196.298154,163.310589 198.110326,164.667963 C191.183787,168.842556 183.854737,172.420929 176.223542,175.320965 C180.230393,183.341335 184.861538,190.991831 190.096624,198.16893 C211.238746,191.588051 232.743023,181.531619 254.911949,164.955721 C260.227747,108.668201 245.831087,59.8662432 216.856339,16.5966031 Z M85.4738752,135.09489 C72.8290281,135.09489 62.4592217,123.290155 62.4592217,108.914901 C62.4592217,94.5396472 72.607595,82.7145587 85.4738752,82.7145587 C98.3405064,82.7145587 108.709962,94.5189427 108.488529,108.914901 C108.508531,123.290155 98.3405064,135.09489 85.4738752,135.09489 Z M170.525237,135.09489 C157.88039,135.09489 147.510584,123.290155 147.510584,108.914901 C147.510584,94.5396472 157.658606,82.7145587 170.525237,82.7145587 C183.391518,82.7145587 193.761324,94.5189427 193.539891,108.914901 C193.539891,123.290155 183.391518,135.09489 170.525237,135.09489 Z']), 'dl': ([0.0, 0.0, 24.0, 24.0], ['M12,16L7,11L8.4,9.55l2.6,2.6V4h2v8.15l2.6-2.6L17,11l-5,5ZM6,20q-0.82,0-1.41-0.59T4,18V15H6v3H18V15h2v3q0,0.82-0.59,1.41T18,20H6Z'])}


def icon(doc, name, x, y, color, box=64):
    if name in FILLED:
        (mx, my, vw, vh), ps = FILLED[name]
        doc.add(f'<rect x="{x}" y="{y}" width="{box}" height="{box}" rx="14" fill="{color}" fill-opacity=".14" stroke="{color}" stroke-opacity=".45"/>')
        k = box * 0.6 / max(vw, vh)
        tx, ty = x + (box - vw * k) / 2 - mx * k, y + (box - vh * k) / 2 - my * k
        for d_ in ps:
            doc.add(f'<path d="{d_}" transform="translate({tx:.2f} {ty:.2f}) scale({k:.4f})" fill="{color}"/>')
        return
    s = box * 0.58 / 24
    doc.add(f'<rect x="{x}" y="{y}" width="{box}" height="{box}" rx="14" fill="{color}" fill-opacity=".14" stroke="{color}" stroke-opacity=".45"/>')
    doc.add(f'<path d="{ICONS[name]}" transform="translate({x + box * 0.21} {y + box * 0.21}) scale({s})" fill="none" '
            f'stroke="{color}" stroke-width="{2 / s * s * 2 / 2:.1f}" stroke-linecap="round" stroke-linejoin="round" '
            f'vector-effect="non-scaling-stroke" style="stroke-width:2.6px"/>')


# ---------- banner ----------
def banner():
    W, H = 1280, 330
    d = Doc(W, H, 'DeskMate: turn an old Android phone into a desk panel for your Windows PC')
    defs = f'''
    <linearGradient id="title" x1="0" x2="1"><stop offset="0" stop-color="#ffffff"/><stop offset=".55" stop-color="#bfdbfe"/><stop offset="1" stop-color="#86efac"/></linearGradient>
    <radialGradient id="orbA"><stop offset="0" stop-color="#2563eb" stop-opacity=".55"/><stop offset="1" stop-color="#2563eb" stop-opacity="0"/></radialGradient>
    <radialGradient id="orbB"><stop offset="0" stop-color="#22c55e" stop-opacity=".35"/><stop offset="1" stop-color="#22c55e" stop-opacity="0"/></radialGradient>
    <radialGradient id="orbC"><stop offset="0" stop-color="#ff4655" stop-opacity=".25"/><stop offset="1" stop-color="#ff4655" stop-opacity="0"/></radialGradient>
    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="#ffffff" stroke-opacity=".045"/></pattern>
    <clipPath id="card"><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="28"/></clipPath>'''
    css = '''
    .a { animation: driftA 14s ease-in-out infinite alternate; }
    .b { animation: driftB 18s ease-in-out infinite alternate; }
    .c { animation: driftC 16s ease-in-out infinite alternate; }
    @keyframes driftA { to { transform: translate(140px, 40px); } }
    @keyframes driftB { to { transform: translate(-160px, -30px); } }
    @keyframes driftC { to { transform: translate(-80px, 50px); } }
    .dot { animation: blink 2.4s ease-in-out infinite; }
    @keyframes blink { 50% { opacity: .25; } }'''
    d.add(f'<g clip-path="url(#card)"><rect width="{W}" height="{H}" fill="{BG}"/>'
          f'<circle class="a" cx="260" cy="90" r="330" fill="url(#orbA)"/>'
          f'<circle class="b" cx="1060" cy="330" r="320" fill="url(#orbB)"/>'
          f'<circle class="c" cx="980" cy="40" r="240" fill="url(#orbC)"/>'
          f'<rect width="{W}" height="{H}" fill="url(#grid)"/></g>')
    d.add(f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="28" fill="none" stroke="{LINE}" stroke-width="2"/>')
    # eyebrow chip
    chip = 'Windows PC  +  Android phone'
    cw = tw(chip, 17) + 64
    d.add(f'<rect x="{(W - cw) / 2}" y="62" width="{cw}" height="38" rx="19" fill="#ffffff" fill-opacity=".05" stroke="#ffffff" stroke-opacity=".14"/>')
    d.add(f'<circle class="dot" cx="{(W - cw) / 2 + 24}" cy="81" r="5" fill="#22c55e"/>')
    d.text((W - cw) / 2 + 42, 87, chip, 17, 400, '#c9d4e2')
    d.text(W / 2, 205, 'DeskMate', 104, 800, 'url(#title)', 'middle')
    d.text(W / 2, 258, 'Turn an old Android phone into a desk panel for your PC.', 24, 400, '#c9d4e2', 'middle')
    d.save('site-banner', css, defs)


# ---------- cards ----------
def card_grid(name, title, items, cols=3, numbered=False):
    W, gap, pad, TS, BS, LH = 1280, 20, 32, 30, 22, 32
    cw = (W - gap * (cols - 1)) / cols
    chars = int((cw - 2 - 2 * pad) // (ADV * BS))
    for it in items:
        it['lines'] = textwrap.wrap(it['desc'], chars)
    top = 150 if numbered else 140
    card_h = top + 18 + max(len(it['lines']) for it in items) * LH + pad
    rows = (len(items) + cols - 1) // cols
    H = rows * card_h + (rows - 1) * gap + 4
    d = Doc(W, round(H), title)
    css = '.glow { animation: glow 6s ease-in-out infinite; opacity: 0; } @keyframes glow { 0%, 70%, 100% { opacity: 0; } 80% { opacity: 1; } }'
    defs = ''
    for i, it in enumerate(items):
        r, c = divmod(i, cols)
        x, y = c * (cw + gap) + 1, r * (card_h + gap) + 1
        col = it['color']
        defs += (f'<linearGradient id="g{i}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{col}" stop-opacity=".16"/>'
                 f'<stop offset=".6" stop-color="{col}" stop-opacity="0"/></linearGradient>')
        for extra in (f'fill="{CARD}"', f'fill="url(#g{i})"', f'fill="none" stroke="{LINE}" stroke-width="1.5"'):
            d.add(f'<rect x="{x}" y="{y}" width="{cw - 2}" height="{card_h - 2}" rx="24" {extra}/>')
        d.add(f'<rect class="glow" style="animation-delay:{i * 0.5}s" x="{x}" y="{y}" width="{cw - 2}" height="{card_h - 2}" rx="24" fill="none" stroke="{col}" stroke-opacity=".7" stroke-width="2"/>')
        if numbered:
            d.text(x + pad, y + 78, f'{i + 1:02d}', 56, 800, col)
            icon(d, it['icon'], x + cw - 2 - pad - 64, y + pad, col)
        else:
            icon(d, it['icon'], x + pad, y + pad, col)
        ty = y + top
        d.text(x + pad, ty, it['title'], TS, 700, TEXT)
        for j, line in enumerate(it['lines']):
            d.text(x + pad, ty + 18 + LH * (j + 1) - 4, line, BS, 400, MUTED)
    d.save(name, css, defs)


FEATURES = [
    dict(icon='pulse', color='#38bdf8', title='Live PC stats', desc='CPU, GPU, RAM, network and temperatures, plus the apps using the most.'),
    dict(icon='bars', color='#a78bfa', title='AI usage limits', desc='Claude and Codex quotas as bars, with reset times.'),
    dict(icon='discord', color='#818cf8', title='Discord voice', desc="Mute, deafen and hang up, see who's talking, jump between your favourite servers."),
    dict(icon='valorant', color='#ce3a46', title='VALORANT page', desc='Opens when the game starts: the match, save clip, hold to talk and your stats.'),
    dict(icon='musicnote', color='#22c55e', title='Media and shortcuts', desc='Control any music player, launch apps or lock the PC with one tap.'),
    dict(icon='dl', color='#f59e0b', title='One download', desc='The phone app, the USB tool and the temperature driver are built in.'),
]
STEPS = [
    dict(icon='dl', color='#2563eb', title='Download', desc='Open DeskmateAgent.exe. It installs itself and starts with Windows.'),
    dict(icon='phone', color='#a78bfa', title='USB debugging', desc='Tap Build number 7 times, then turn on USB debugging in Developer options.'),
    dict(icon='usb', color='#22c55e', title='Plug it in', desc='Allow USB debugging on the phone. DeskMate installs the app and opens the panel.'),
]

if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    banner()
    card_grid('site-features', 'Features: live PC stats, AI usage limits, Discord voice, VALORANT page, media and shortcuts, one download', FEATURES)
    card_grid('site-steps', 'Install in 3 steps: download, turn on USB debugging, plug in the phone', STEPS, numbered=True)
