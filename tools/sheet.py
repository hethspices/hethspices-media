import sys, os, glob
from PIL import Image, ImageDraw, ImageOps, ImageFont
files = sys.argv[3:]; out = sys.argv[1]; cell = int(sys.argv[2])
cols = 4; rows = (len(files)+cols-1)//cols
W = cols*cell; H = rows*(cell+28)
sheet = Image.new('RGB', (W, H), 'white'); d = ImageDraw.Draw(sheet)
try: f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
except: f = ImageFont.load_default()
for i, p in enumerate(files):
    im = ImageOps.exif_transpose(Image.open(p)).convert('RGB')
    print(os.path.basename(p), im.size)
    im.thumbnail((cell-8, cell-8))
    x = (i%cols)*cell; y = (i//cols)*(cell+28)
    sheet.paste(im, (x+(cell-im.width)//2, y+(cell-im.height)//2))
    d.text((x+4, y+cell+4), f"{i+1}. {os.path.basename(p)[:34]}", fill='black', font=f)
sheet.save(out, quality=85)
