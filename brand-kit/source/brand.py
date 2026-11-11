from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np, cv2, os, math

ROOT = '/home/claude/libala'
S = 3  # upscale factor for master
GREEN = (18, 58, 40)
DEEP = (12, 38, 27)
GOLD = (198, 160, 82)
GOLD_L = (226, 196, 120)
CREAM = (250, 247, 238)
INK = (28, 36, 31)
F = ROOT + '/fonts/'


def font(name, size, wght=None):
    f = ImageFont.truetype(F + name, size)
    if wght:
        f.set_variation_by_axes([wght])
    return f


def mont(size, w=600): return font('Montserrat[wght].ttf', size, w)
def cinzel(size, w=700): return font('Cinzel[wght].ttf', size, w)
def cdec(size, bold=True): return font('CinzelDecorative-Bold.ttf' if bold else 'CinzelDecorative-Regular.ttf', size)


def text_w(txt, f, track=0):
    return sum(f.getlength(c) for c in txt) + track * (len(txt) - 1)


def draw_text(d, xy, txt, f, fill, track=0, anchor='l'):
    x, y = xy
    w = text_w(txt, f, track)
    if anchor == 'm': x -= w / 2
    if anchor == 'r': x -= w
    for c in txt:
        d.text((x, y), c, font=f, fill=fill)
        x += f.getlength(c) + track
    return w


def build_master():
    src = Image.open(ROOT + '/src/logo-source.png').convert('RGB')
    W, H = src.size
    big = src.resize((W * S, H * S), Image.LANCZOS)
    a = np.asarray(big).astype(float)
    bg = np.array([251., 252., 248.])
    d = (bg - a).max(2)
    alpha = np.clip((d - 14) / 32, 0, 1)
    al = alpha[..., None]
    col = np.clip(np.where(al > 0, (a - (1 - al) * bg) / np.maximum(al, 1e-3), a), 0, 255)
    rgba = np.dstack([col, alpha * 255]).astype('uint8')
    # letter mask from 1x components
    a1 = np.asarray(src).astype(float)
    m1 = (((bg - a1).max(2) - 14) / 32 > .25).astype('uint8')
    n, lab, st, cen = cv2.connectedComponentsWithStats(m1[:545], 8)
    letters = np.zeros(m1.shape, 'uint8')
    for i in range(1, n):
        x, y, w, h, ar = st[i]
        if ar > 5000 and ar < 40000:
            letters[:545][lab == i] = 1
    embm = np.zeros(m1.shape, 'uint8')
    for i in range(1, n):
        x, y, w, h, ar = st[i]
        if ar >= 40000 or (1500 < ar <= 5000):
            embm[:545][lab == i] = 1
    letters = cv2.dilate(letters, np.ones((9, 9), 'uint8'))
    embm = cv2.dilate(embm, np.ones((7, 7), 'uint8')) & (1 - letters)
    up = lambda m: cv2.resize(m, (W * S, H * S), interpolation=cv2.INTER_NEAREST).astype(bool)
    return rgba, up(letters), up(embm)


def crop_alpha(arr, pad=0):
    ys, xs = np.where(arr[..., 3] > 20)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    out = arr[y0:y1, x0:x1]
    if pad:
        out = np.pad(out, ((pad, pad), (pad, pad), (0, 0)))
    return out


def mono(arr, color):
    out = arr.copy()
    out[..., :3] = color
    return out


def reversed_(arr, keep=None):
    """Dark greens -> cream so lettering reads on dark backgrounds. `keep` = mask left in colour."""
    a = arr.astype(float)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    lum = (0.3 * r + 0.59 * g + 0.11 * b) / 255
    greenish = (g >= r - 6) & (lum < 0.62)
    t = np.clip(lum / 0.45, 0, 1)[..., None]
    light = np.array(CREAM, float)
    sage = np.array([150., 190., 150.])
    new = light * (1 - t) + sage * t
    out = a.copy()
    if keep is not None:
        greenish = greenish & ~keep
    out[..., :3] = np.where(greenish[..., None], new, a[..., :3])
    return out.astype('uint8')


def img(arr): return Image.fromarray(arr, 'RGBA')


def fit(im, w=None, h=None):
    if w and h:
        s = min(w / im.width, h / im.height)
    elif w:
        s = w / im.width
    else:
        s = h / im.height
    return im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)


def canvas(w, h, color):
    return Image.new('RGBA', (w, h), tuple(color) + (255,))


def green_bg(w, h):
    """Deep green field with soft vignette and faint river lines."""
    ss = 2
    W, H = w * ss, h * ss
    yy, xx = np.mgrid[0:H, 0:W]
    dx = (xx - W * .5) / (W * .75); dy = (yy - H * .45) / (H * .9)
    t = np.clip(np.sqrt(dx * dx + dy * dy), 0, 1)[..., None]
    c0 = np.array([27, 78, 54.]); c1 = np.array(DEEP, float)
    base = c0 * (1 - t) + c1 * t
    im = Image.fromarray(np.dstack([base, np.full((H, W), 255.)]).astype('uint8'), 'RGBA')
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    m = min(W, H)
    for k in range(7):
        pts = []
        amp = m * (0.035 + 0.006 * k)
        y0 = H * 0.80 + k * m * 0.035
        for x in range(-10, W + 10, 6):
            pts.append((x, y0 + amp * math.sin(x / (m * 0.42) + k * 0.55) + amp * 0.4 * math.sin(x / (m * 0.17) + k)))
        d.line(pts, fill=GOLD + (max(10, 46 - k * 5),), width=max(2, int(m * 0.0022)))
    im.alpha_composite(ov)
    return im.resize((w, h), Image.LANCZOS)


def paste_c(bg, fg, cx, cy):
    bg.alpha_composite(fg, (round(cx - fg.width / 2), round(cy - fg.height / 2)))


def rule(d, cx, y, w, color=GOLD, t=3):
    """Gold rule with centre diamond, echoing the logo."""
    g = t * 5
    d.polygon([(cx - w / 2, y), (cx - g * 1.6, y - t / 2), (cx - g * 1.6, y + t / 2)], fill=color)
    d.polygon([(cx + w / 2, y), (cx + g * 1.6, y - t / 2), (cx + g * 1.6, y + t / 2)], fill=color)
    d.polygon([(cx - g, y), (cx, y - g * .6), (cx + g, y), (cx, y + g * .6)], fill=color)


def lockup(emblem, h, dark=False, tagline=False):
    """Horizontal lockup: emblem left, name set in type right."""
    e = fit(emblem, h=h)
    f1 = cinzel(round(h * .40), 800)
    f2 = mont(round(h * .125), 700)
    tr1 = h * .02; tr2 = h * .043
    w1 = text_w('LIBALA GOLD', f1, tr1)
    w2 = text_w('AGRIBUSINESS LIMITED', f2, tr2)
    # match second line width to first
    tr2 = (w1 - sum(f2.getlength(c) for c in 'AGRIBUSINESS LIMITED')) / 19
    gap = h * .14
    W = round(e.width + gap + w1 + 4)
    im = Image.new('RGBA', (W, h), (0, 0, 0, 0))
    im.alpha_composite(e, (0, 0))
    d = ImageDraw.Draw(im)
    x = e.width + gap
    c1 = CREAM if dark else GREEN
    c2 = GOLD_L if dark else GREEN
    draw_text(d, (x, h * .17), 'LIBALA GOLD', f1, c1, tr1)
    d.rectangle([x, h * .645, x + w1, h * .645 + max(2, h * .012)], fill=GOLD)
    draw_text(d, (x, h * .70), 'AGRIBUSINESS LIMITED', f2, c2, tr2)
    return im


def save(im, path, rgb=False, **kw):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if rgb or path.endswith('.jpg'):
        im = im.convert('RGB')
    im.save(path, **kw)
