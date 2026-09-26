"""Rebuild the profile README cards from the website's homepage hero images.

Run from this folder:  python3 build_cards.py
- Crop matches the site's homepage cards: 16:9, centered (object-fit: cover).
- Writes cards/*.svg (light + dark) and README.md.
- Bump VERSION whenever cards change, or GitHub keeps showing cached images.
"""
import base64, io, html, textwrap
from PIL import Image

VERSION = 5
SITE = '../patrickknguyen.github.io/assets/Home/'
BASE = 'https://patrickknguyen.github.io/'
# key, hero file, title, description, (unused), alt text
CARDS = [
    ('vigor',   'vigor-hero.png',   'ViGOR',               'Drafts operative notes from surgical video, with a review interface for Stanford surgeons.', '',
     'ViGOR: drafts operative notes from robotic surgery video, with a review interface for Stanford surgeons'),
    ('clustr',  'clustr-hero.png',  'Clustr',              'Sorts a moodboard into labeled groups, blending grouping by subject with grouping by look.', '',
     'Clustr: sorts a moodboard into labeled groups, blending grouping by subject with grouping by look'),
    ('zipvote', 'zipvote-hero.png', 'ZipVote',             'Matches first-time voters with local candidates through a short policy survey. In progress.', '',
     'ZipVote: matches first-time voters with local candidates through a short policy survey'),
    ('summit',  'summit-hero2.png', 'Summit Media Center', 'Field research and prototyping that reimagine how K-12 students learn and create.', '',
     'Summit Media Center: field research and prototyping that reimagine how K-12 students learn and create'),
]
THEMES = {'light': ('#1f2328', '#59636e', '#d1d9e0'),
          'dark':  ('#f0f6fc', '#9198a1', '#3d444d')}
W, IH = 400, 225            # image area, 16:9
GUTTER = 28                 # space to the right of each card
WRAP = 32                   # characters per description line
LINE = 36                   # description line height
MAX_LINES = max(len(textwrap.wrap(c[3], WRAP)) for c in CARDS)
TEXT_H = 64 + MAX_LINES * LINE + 16   # title block + description + bottom padding
FONT = '-apple-system, BlinkMacSystemFont, &quot;Helvetica Neue&quot;, Helvetica, Arial, sans-serif'

def crop_16_9(im):
    w, h = im.size
    if w / h > 16 / 9:
        nw = round(h * 16 / 9); l = (w - nw) // 2
        return im.crop((l, 0, l + nw, h))
    nh = round(w * 9 / 16); t = (h - nh) // 2
    return im.crop((0, t, w, t + nh))

VW, VH = W + GUTTER, IH + TEXT_H
for key, img, title, desc, _, alt in CARDS:
    im = crop_16_9(Image.open(SITE + img).convert('RGB')).resize((W * 2, IH * 2), Image.LANCZOS)
    buf = io.BytesIO(); im.save(buf, 'JPEG', quality=84, optimize=True, progressive=True)
    data = base64.b64encode(buf.getvalue()).decode()
    for theme, (fg, fg2, stroke) in THEMES.items():
        desc_lines = '\n'.join(
            f'<text x="0" y="{IH + 90 + i * LINE}" font-size="24" fill="{fg2}">{html.escape(line)}</text>'
            for i, line in enumerate(textwrap.wrap(desc, WRAP)))
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{VW}" height="{VH}" viewBox="0 0 {VW} {VH}" role="img" aria-label="{html.escape(title)}">
<defs><clipPath id="r"><rect width="{W}" height="{IH}" rx="6"/></clipPath></defs>
<image width="{W}" height="{IH}" clip-path="url(#r)" preserveAspectRatio="xMidYMid slice" href="data:image/jpeg;base64,{data}" xlink:href="data:image/jpeg;base64,{data}"/>
<rect x="0.5" y="0.5" width="{W-1}" height="{IH-1}" rx="5.5" fill="none" stroke="{stroke}" stroke-opacity="0.8"/>
<g font-family='{FONT}'>
<text x="0" y="{IH+50}" font-size="27" font-weight="600" fill="{fg}">{html.escape(title)}</text>
{desc_lines}
</g></svg>'''
        open(f'cards/{key}-{theme}.svg', 'w').write(svg)

cells = ''.join(
    f'<a href="{BASE}{k}/"><picture>'
    f'<source media="(prefers-color-scheme: dark)" srcset="cards/{k}-dark.svg?v={VERSION}">'
    f'<img src="cards/{k}-light.svg?v={VERSION}" width="25%" alt="{alt}"></picture></a>'
    for k, _, _, _, _, alt in CARDS)
open('README.md', 'w').write('### Selected work\n\n<p>' + cells + '</p>\n')
print('Built', len(CARDS) * 2, 'cards and README.md, version', VERSION)
