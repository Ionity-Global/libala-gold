import sys; sys.path.insert(0, '/home/claude/libala')
from brand import *

OUT = ROOT + '/kit'
L = OUT + '/logos/'
rgba, letters, embm = build_master()
H3 = rgba.shape[0]

full = crop_alpha(rgba, 30)
top = rgba.copy(); top[545 * S:] = 0           # arc name + emblem
crest = crop_alpha(top, 30)
emb = rgba.copy(); emb[~embm] = 0
emblem = crop_alpha(emb, 20)
tag = rgba.copy(); tag[:650 * S] = 0
tagline = crop_alpha(tag, 10)

rev = reversed_(rgba, embm)
full_r = crop_alpha(rev, 30)
t2 = rev.copy(); t2[545 * S:] = 0; crest_r = crop_alpha(t2, 30)
REV = {'logo-full': full_r, 'logo-crest': crest_r, 'emblem': emblem}
sets = {'logo-full': full, 'logo-crest': crest, 'emblem': emblem}
for name, arr in sets.items():
    save(img(arr), f'{L}transparent/libala-gold-{name}-colour.png')
    if name != 'emblem': save(img(REV[name]), f'{L}transparent/libala-gold-{name}-reversed-for-dark.png')
    save(img(mono(arr, (255, 255, 255))), f'{L}transparent/libala-gold-{name}-white.png')
    save(img(mono(arr, GOLD)), f'{L}transparent/libala-gold-{name}-gold.png')
    save(img(mono(arr, GREEN)), f'{L}transparent/libala-gold-{name}-green.png')
    save(img(mono(arr, (0, 0, 0))), f'{L}transparent/libala-gold-{name}-black.png')
    # web-size copies
    for w in (1200, 600, 300):
        save(fit(img(arr), w=w), f'{L}web/libala-gold-{name}-colour-{w}w.png', optimize=True)
    # on backgrounds
    for bgname, bgc, a2 in (('white', (255, 255, 255), arr), ('cream', CREAM, arr), ('green', GREEN, REV[name])):
        fg = img(a2); m = round(max(fg.size) * .08)
        c = canvas(fg.width + 2 * m, fg.height + 2 * m, bgc); c.alpha_composite(fg, (m, m))
        save(c, f'{L}on-background/libala-gold-{name}-on-{bgname}.jpg', quality=93)

save(img(tagline), f'{L}transparent/libala-gold-tagline-gold.png')

# horizontal lockups
E = img(emblem)
for dark in (False, True):
    lk = lockup(E, 900, dark)
    n = 'reversed-for-dark' if dark else 'colour'
    save(lk, f'{L}transparent/libala-gold-horizontal-{n}.png')
    save(fit(lk, h=160), f'{L}web/libala-gold-horizontal-{n}-160h.png', optimize=True)
    c = canvas(lk.width + 200, lk.height + 200, GREEN if dark else (255, 255, 255)); c.alpha_composite(lk, (100, 100))
    save(c, f'{L}on-background/libala-gold-horizontal-on-{"green" if dark else "white"}.jpg', quality=93)

# ---------- icons ----------
I = OUT + '/favicons/'
def icon(size, pad=.13, bg='green', rounded=0):
    ss = 4 if size < 256 else 2
    n = size * ss
    c = green_bg(n, n) if bg == 'green' else canvas(n, n, CREAM)
    if bg == 'green':
        # hide river lines on icons
        c = Image.fromarray(np.asarray(green_bg(64, 64).resize((n, n))), 'RGBA')
        yy, xx = np.mgrid[0:n, 0:n]; t = np.clip(np.hypot((xx - n / 2) / n, (yy - n / 2) / n) * 1.5, 0, 1)[..., None]
        c = Image.fromarray(np.dstack([np.array([30, 84, 58.]) * (1 - t) + np.array(DEEP, float) * t, np.full((n, n), 255.)]).astype('uint8'), 'RGBA')
    e = fit(E, w=n * (1 - 2 * pad), h=n * (1 - 2 * pad))
    paste_c(c, e, n / 2, n / 2)
    if rounded:
        m = Image.new('L', (n, n), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, n - 1, n - 1], n * rounded, fill=255)
        c.putalpha(m)
    return c.resize((size, size), Image.LANCZOS)

# tight head crop for tiny sizes
x0, y0 = (545 - 469 + 0), 0
head = E.crop((round(E.width * .14), round(E.height * .02), round(E.width * .86), round(E.height * .98)))
def tiny(size):
    n = size * 8
    yy, xx = np.mgrid[0:n, 0:n]
    c = canvas(n, n, (22, 66, 45))
    e = fit(head, w=n * .96, h=n * .96); paste_c(c, e, n / 2, n / 2)
    m = Image.new('L', (n, n), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, n - 1, n - 1], n * .2, fill=255)
    c.putalpha(m)
    return c.resize((size, size), Image.LANCZOS)

for s in (16, 32, 48):
    save(tiny(s), f'{I}favicon-{s}x{s}.png')
tiny(256).save(I + 'favicon.ico', sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
save(icon(180, .11), I + 'apple-touch-icon.png', rgb=True)
save(icon(192, .11, rounded=.2), I + 'android-chrome-192x192.png')
save(icon(512, .11, rounded=.2), I + 'android-chrome-512x512.png')
save(icon(512, .22), I + 'maskable-icon-512x512.png', rgb=True)
save(icon(150, .16), I + 'mstile-150x150.png', rgb=True)
open(I + 'site.webmanifest', 'w').write('''{
  "name": "Libala Gold Agribusiness Limited",
  "short_name": "Libala Gold",
  "icons": [
    {"src": "android-chrome-192x192.png", "sizes": "192x192", "type": "image/png"},
    {"src": "android-chrome-512x512.png", "sizes": "512x512", "type": "image/png"},
    {"src": "maskable-icon-512x512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}
  ],
  "theme_color": "#123a28",
  "background_color": "#faf7ee",
  "display": "standalone"
}
''')

# ---------- social ----------
So = OUT + '/social/'
Erev = E  # colour emblem reads well on green
crest_rev = img(crest_r)
full_rev = img(full_r)
TAG = 'FROM THE PLAINS OF SESHEKE TO THE NATIONS'

def profile(size, bg):
    c = icon(size, .12, bg)
    return c
for bg in ('green', 'cream'):
    save(profile(1080, bg), f'{So}profile/profile-{bg}-1080.png', rgb=True)
    save(profile(640, bg), f'{So}profile/profile-{bg}-640-whatsapp.png', rgb=True)
    c = canvas(1080, 1080, CREAM) if bg == 'cream' else green_bg(1080, 1080)
    paste_c(c, fit(img(crest) if bg == 'cream' else crest_rev, w=880, h=880), 540, 540)
    save(c, f'{So}profile/profile-crest-{bg}-1080.png', rgb=True)

def banner(w, h, safe_w=None, safe_h=None, name=''):
    c = green_bg(w, h)
    d = ImageDraw.Draw(c)
    sw, sh = safe_w or w * .86, safe_h or h * .78
    lh = round(min(sh * .46, sw * .17))
    lk = lockup(E, lh * 3, dark=True); lk = fit(lk, h=lh)
    if lk.width > sw: lk = fit(lk, w=round(sw)); lh = lk.height
    fs = round(lh * .2)
    f = cdec(fs)
    while text_w(TAG, f, fs * .08) > sw * .98:
        fs -= 1; f = cdec(fs)
    block = lh + lh * .32 + fs * 1.3
    y = h / 2 - block / 2
    paste_c(c, lk, w / 2, y + lh / 2)
    ry = y + lh + lh * .17
    rule(d, w / 2, ry, min(sw * .7, lk.width * .9), GOLD, max(2, lh * .022))
    draw_text(d, (w / 2, ry + lh * .14), TAG, f, GOLD_L, fs * .08, 'm')
    save(c, So + name, rgb=True, quality=94)

banner(1640, 624, 1200, 500, 'facebook-cover-1640x624.jpg')
banner(1584, 396, 1100, 330, 'linkedin-personal-banner-1584x396.jpg')
banner(1128, 191, 900, 170, 'linkedin-company-cover-1128x191.jpg')
banner(1500, 500, 1100, 380, 'x-twitter-header-1500x500.jpg')
banner(2560, 1440, 1546, 423, 'youtube-banner-2560x1440.jpg')
banner(1200, 630, 1000, 480, 'og-share-image-1200x630.jpg')
banner(1920, 1080, 1500, 800, 'presentation-title-1920x1080.jpg')

def post(w, h, name, dark=True):
    c = green_bg(w, h) if dark else canvas(w, h, CREAM)
    d = ImageDraw.Draw(c)
    fg = full_rev if dark else img(full)
    paste_c(c, fit(fg, w=w * .86, h=h * .66), w / 2, h * .47)
    m = round(w * .045)
    d.rectangle([m, m, w - m, h - m], outline=GOLD, width=max(2, round(w * .003)))
    save(c, So + name, rgb=True, quality=94)
post(1080, 1080, 'instagram-post-1080x1080-green.jpg')
post(1080, 1080, 'instagram-post-1080x1080-cream.jpg', False)
post(1080, 1350, 'instagram-portrait-1080x1350.jpg')
post(1080, 1920, 'story-1080x1920.jpg')

# email signature logo
save(fit(lockup(E, 900), h=96), OUT + '/email-signature/libala-gold-signature-logo.png', optimize=True)
print('done')
