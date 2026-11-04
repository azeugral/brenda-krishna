"""og.jpg, favicon.svg e apple-touch-icon.png, feitos da própria arte do hero."""
import os
from PIL import Image, ImageDraw, ImageFont
AQUI = os.path.dirname(os.path.abspath(__file__)); SITE = os.path.dirname(AQUI); IMG = os.path.join(SITE, 'assets', 'img')
im = Image.open(os.path.join(IMG, 'hero-largo-fim.webp')).convert('RGB').resize((1200, 675), Image.LANCZOS)
o = Image.new('RGB', (1200, 630)); o.paste(im.crop((0, 22, 1200, 652)))
d = ImageDraw.Draw(o)
f = None
for c in (r'C:\Windows\Fonts\georgia.ttf', r'C:\Windows\Fonts\times.ttf'):
    if os.path.exists(c):
        f = ImageFont.truetype(c, 76); g = ImageFont.truetype(c, 30); break
d.text((58, 232), 'BRENDA', font=f, fill=(46, 31, 23)); d.text((58, 316), 'KRISHNA', font=f, fill=(46, 31, 23)); d.text((60, 410), 'Tatuadora em Sorocaba', font=g, fill=(107, 58, 107))
o.save(os.path.join(SITE, 'og.jpg'), quality=86)
# estrela de quatro pontas, o sinal das folhas dela
open(os.path.join(SITE, 'favicon.svg'), 'w', encoding='utf8').write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" fill="#2e1f17"/><path fill="#f0d9f0" d="M16 3l2.4 10.6L29 16l-10.6 2.4L16 29l-2.4-10.6L3 16l10.6-2.4z"/></svg>')
a = Image.new('RGB', (720, 720), (46, 31, 23)); ImageDraw.Draw(a).polygon([(360, 72), (414, 306), (648, 360), (414, 414), (360, 648), (306, 414), (72, 360), (306, 306)], fill=(240, 217, 240))
a.resize((180, 180), Image.LANCZOS).save(os.path.join(SITE, 'apple-touch-icon.png'))
