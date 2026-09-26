"""Rebuild the profile cards from the website's homepage hero images.

Run from this folder:  python3 build_cards.py
Crop matches the site's homepage cards: 16:9, centered (object-fit: cover).
"""
import base64, io, html
from PIL import Image

SITE = '../patrickknguyen.github.io/assets/Home/'
CARDS = [
    ('vigor',   'vigor-hero.png',   'ViGOR',               'Computer Vision & Natural Language · 2026'),
    ('clustr',  'clustr-hero.png',  'Clustr',              'Computer Vision & UX Prototyping · 2026'),
    ('zipvote', 'zipvote-hero.png', 'ZipVote',             'Information & Web Design · 2026'),
    ('summit',  'summit-hero2.png', 'Summit Media Center', 'Design Thinking & UX Prototyping · 2020'),
]
THEMES = {'light': ('#1f2328', '#59636e', '#d1d9e0'),
          'dark':  ('#f0f6fc', '#9198a1', '#3d444d')}
W, IH = 400, 225          # image area, 16:9
GUTTER_R, GUTTER_B = 40, 48   # breathing room baked into each card
TEXT_H = 64
FONT = '-apple-system, BlinkMacSystemFont, &quot;Helvetica Neue&quot;, Helvetica, Arial, sans-serif'

def crop_16_9(im):
    w, h = im.size
    if w / h > 16 / 9:
        nw = round(h * 16 / 9); l = (w - nw) // 2
        return im.crop((l, 0, l + nw, h))
    nh = round(w * 9 / 16); t = (h - nh) // 2
    return im.crop((0, t, w, t + nh))

for key, img, title, meta in CARDS:
    im = crop_16_9(Image.open(SITE + img).convert('RGB')).resize((W * 2, IH * 2), Image.LANCZOS)
    buf = io.BytesIO(); im.save(buf, 'JPEG', quality=84, optimize=True, progressive=True)
    data = base64.b64encode(buf.getvalue()).decode()
    VW, VH = W + GUTTER_R, IH + TEXT_H + GUTTER_B
    for theme, (fg, fg2, stroke) in THEMES.items():
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{VW}" height="{VH}" viewBox="0 0 {VW} {VH}" role="img" aria-label="{html.escape(title)}">
<defs><clipPath id="r"><rect width="{W}" height="{IH}" rx="6"/></clipPath></defs>
<image width="{W}" height="{IH}" clip-path="url(#r)" preserveAspectRatio="xMidYMid slice" href="data:image/jpeg;base64,{data}" xlink:href="data:image/jpeg;base64,{data}"/>
<rect x="0.5" y="0.5" width="{W-1}" height="{IH-1}" rx="5.5" fill="none" stroke="{stroke}" stroke-opacity="0.8"/>
<g font-family='{FONT}'>
<text x="0" y="{IH+30}" font-size="20" font-weight="600" fill="{fg}">{html.escape(title)}</text>
<text x="0" y="{IH+54}" font-size="17" fill="{fg2}">{html.escape(meta)}</text>
</g></svg>'''
        open(f'cards/{key}-{theme}.svg', 'w').write(svg)
print('Built', len(CARDS) * 2, 'cards')
