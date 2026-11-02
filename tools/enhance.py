"""Enhance customer phone photos for Instagram.
Usage: python3 -I enhance.py SRC_DIR OUT_DIR
Outputs per photo: feed (4:5 or 1:1, 1080 wide) and story (1080x1920), JPEG q92, no EXIF.
"""
import sys, os, glob
import numpy as np, cv2
from PIL import Image, ImageOps, ImageFilter

SRC, OUT = sys.argv[1], sys.argv[2]
os.makedirs(os.path.join(OUT, 'feed'), exist_ok=True)
os.makedirs(os.path.join(OUT, 'story'), exist_ok=True)

# crop boxes as fractions (x0, y0, x1, y1) and feed aspect (w/h)
PLAN = {
    'IMG_7134': dict(crop=(0.0, 0.055, 0.95, 0.988), aspect=0.8, denoise=3, name='garam-masala-gavar-bhaji'),
    'IMG_7135': dict(crop=(0.008, 0.0, 0.993, 1.0), aspect=0.8, denoise=4, name='garam-masala-aloo-roti', warm=1.0, vib=0.22),
    'IMG_7136': dict(crop=(0.0, 0.0, 1.0, 1.0), aspect=0.8, denoise=3, name='pav-bhaji-thali', warm=0.0, vib=0.08, clahe=0.3, wb=0.5),
    'IMG_7137': dict(crop=(0.0, 0.13, 1.0, 0.985), aspect=0.8, denoise=3, name='pav-bhaji-with-pack', warm=0.5, vib=0.2),
    'IMG_7138': dict(crop=None, aspect=None, denoise=5, name='chaas-tall', clahe=0.7, clip=2.4),  # story only
    'IMG_7139': dict(crop=(0.0, 0.0, 1.0, 1.0), aspect=1.0, denoise=5, name='chaas-with-pack', clahe=0.7, clip=2.4),
}

def to_aspect(img, box, aspect):
    W, H = img.size
    x0, y0, x1, y1 = [int(round(v)) for v in (box[0]*W, box[1]*H, box[2]*W, box[3]*H)]
    w, h = x1 - x0, y1 - y0
    if w / h > aspect:   # too wide -> trim width around centre
        nw = int(round(h * aspect)); x0 += (w - nw) // 2; w = nw
    else:                # too tall -> trim height around centre
        nh = int(round(w / aspect)); y0 += (h - nh) // 2; h = nh
    return img.crop((x0, y0, x0 + w, y0 + h))

def white_balance(rgb, strength=0.75, warm=1.0):
    f = rgb.astype(np.float32) / 255.0
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV).astype(np.float32) / 255.0
    mask = (hsv[..., 1] < 0.18) & (hsv[..., 2] > 0.45) & (hsv[..., 2] < 0.97)
    if mask.mean() < 0.02:  # no neutral reference -> grey world on mid-tones
        mask = (hsv[..., 2] > 0.2) & (hsv[..., 2] < 0.9)
    mean = f[mask].mean(axis=0)
    gains = np.clip(mean.mean() / mean, 0.8, 1.25)
    gains = 1 + strength * (gains - 1)
    gains *= np.array([1 + 0.03*warm, 1.0, 1 - 0.025*warm])  # gentle warmth for food
    return np.clip(f * gains, 0, 1)

def levels(f):
    lum = 0.299 * f[..., 0] + 0.587 * f[..., 1] + 0.114 * f[..., 2]
    lo, hi = np.percentile(lum, 0.4), np.percentile(lum, 99.6)
    hi = max(hi, 0.6)
    f = np.clip((f - lo) / (hi - lo) * 0.975 + 0.01, 0, 1)
    med = np.median(0.299 * f[..., 0] + 0.587 * f[..., 1] + 0.114 * f[..., 2])
    if med < 0.46:  # lift dark shots
        g = np.clip(np.log(0.48) / np.log(max(med, 1e-3)), 0.72, 1.0)
        f = f ** g
    return f

def local_contrast(f, clip=1.8, blend=0.5):
    u8 = (f * 255).astype(np.uint8)
    lab = cv2.cvtColor(u8, cv2.COLOR_RGB2LAB)
    L = lab[..., 0]
    L2 = cv2.createCLAHE(clipLimit=clip, tileGridSize=(8, 8)).apply(L)
    lab[..., 0] = cv2.addWeighted(L, 1 - blend, L2, blend, 0)
    return cv2.cvtColor(lab, cv2.COLOR_LAB2RGB).astype(np.float32) / 255.0

def vibrance(f, k=0.32):
    u8 = (f * 255).astype(np.uint8)
    hsv = cv2.cvtColor(u8, cv2.COLOR_RGB2HSV).astype(np.float32)
    s = hsv[..., 1] / 255.0
    s = np.clip(s + k * s * (1 - s), 0, 1)
    hsv[..., 1] = s * 255
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB).astype(np.float32) / 255.0

def vignette(f, strength=0.10):
    h, w = f.shape[:2]
    y, x = np.ogrid[:h, :w]
    r = np.sqrt(((x - w / 2) / (w / 2)) ** 2 + ((y - h / 2) / (h / 2)) ** 2) / np.sqrt(2)
    m = 1 - strength * np.clip(r - 0.35, 0, 1) ** 1.6 / 0.65 ** 1.6
    return f * m[..., None]

def enhance(img, denoise, cfg):
    rgb = np.array(img)
    if denoise:
        rgb = cv2.fastNlMeansDenoisingColored(rgb, None, denoise, denoise, 7, 21)
    f = white_balance(rgb, cfg.get('wb', 0.75), cfg.get('warm', 1.0))
    f = levels(f)
    f = local_contrast(f, cfg.get('clip', 1.8), cfg.get('clahe', 0.5))
    f = vibrance(f, cfg.get('vib', 0.32))
    f = vignette(f)
    return Image.fromarray((np.clip(f, 0, 1) * 255).astype(np.uint8))

def sharpen_resize(img, size):
    img = img.resize(size, Image.LANCZOS)
    return img.filter(ImageFilter.UnsharpMask(radius=1.3, percent=70, threshold=3))

def story(img):
    W, H = 1080, 1920
    bg = img.copy()
    s = max(W / bg.width, H / bg.height)
    bg = bg.resize((int(bg.width * s) + 1, int(bg.height * s) + 1), Image.LANCZOS)
    bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2, (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))
    bg = bg.filter(ImageFilter.GaussianBlur(38))
    bg = Image.fromarray((np.array(bg).astype(np.float32) * 0.62).astype(np.uint8))
    s = min(W / img.width, H / img.height)
    fg = sharpen_resize(img, (int(img.width * s), int(img.height * s)))
    bg.paste(fg, ((W - fg.width) // 2, (H - fg.height) // 2))
    return bg

for p in sorted(glob.glob(os.path.join(SRC, 'IMG_71*.JPG'))):
    key = os.path.basename(p)[:8]
    if key not in PLAN:
        continue
    cfg = PLAN[key]
    raw = ImageOps.exif_transpose(Image.open(p)).convert('RGB')
    base = enhance(raw, cfg['denoise'], cfg)
    tag = f"{key}_{cfg['name']}"
    if cfg['aspect']:
        c = to_aspect(base, cfg['crop'], cfg['aspect'])
        size = (1080, int(round(1080 / cfg['aspect'])))
        feed = sharpen_resize(c, size)
        feed.save(os.path.join(OUT, 'feed', f'{tag}_feed.jpg'), quality=92, optimize=True)
        story(c).save(os.path.join(OUT, 'story', f'{tag}_story.jpg'), quality=92, optimize=True)
        src_for_cmp = to_aspect(raw, cfg['crop'], cfg['aspect'])
        print(tag, 'feed', size, 'upscale x%.2f' % (size[0] / c.width))
    else:
        story(base).save(os.path.join(OUT, 'story', f'{tag}_story.jpg'), quality=92, optimize=True)
        print(tag, 'story only, upscale x%.2f' % (1920 / base.height))
