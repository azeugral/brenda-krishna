"""Gera as imagens do site a partir de _ref. Uso: python tools/processar.py
OBRAS: (post, foco_y 0..1, categoria, legenda). DISP: (post, foco_y, título, nota)."""
import os
from PIL import Image, ImageOps
AQUI = os.path.dirname(os.path.abspath(__file__)); SITE = os.path.dirname(AQUI)
REF = os.path.join(SITE, '..', '_ref'); IG = os.path.join(REF, 'ig', 'fotos'); IMG = os.path.join(SITE, 'assets', 'img')
OBRAS = [
    ('014_0', .45, 'asas', 'Asas nas costas'), ('019_0', .4, 'asas', 'Filigrana em lilás nas costas'), ('016_2', .4, 'asas', 'Asa no ombro e no braço'),
    ('012_0', .5, 'asas', 'Asa no braço, primeira sessão'), ('009_0', .5, 'asas', 'Asas rosa, segunda sessão'), ('029_0', .5, 'natureza', 'Flores encantadas nas costas'),
    ('010_0', .5, 'asas', 'Espinhos na costela, no free hand'), ('028_0', .5, 'asas', 'Ornamento na perna'), ('026_0', .5, 'asas', 'Antebraço com olho e chamas'),
    ('006_0', .4, 'personagens', 'Hannya, a mulher por trás da máscara'), ('002_0', .5, 'personagens', 'Menina e polvo'), ('043_1', .5, 'personagens', 'Câncer, regido pela Lua'),
    ('036_0', .5, 'natureza', 'Mariposa, cobertura'), ('037_0', .5, 'natureza', 'Fragmentos de um jardim particular'), ('004_0', .5, 'natureza', 'Carcará com sombra vermelha'),
    ('005_1', .5, 'natureza', 'Lírio no antebraço'), ('109_0', .5, 'natureza', 'Borboleta'), ('086_0', .55, 'natureza', 'Mariposa e lua'),
    ('017_0', .5, 'natureza', 'Aranha no free hand'), ('053_0', .5, 'natureza', 'Tartaruga'), ('005_2', .5, 'delicadas', 'Sol de traço fino'),
    ('005_6', .5, 'delicadas', 'Vaso e ramos no punho'), ('005_5', .5, 'delicadas', 'Ramo no antebraço'), ('068_0', .5, 'delicadas', 'O sol pediu a lua em casamento'),
    ('092_0', .5, 'delicadas', 'Fases da lua'), ('082_0', .5, 'delicadas', 'Rosa no punho'), ('113_0', .5, 'personagens', 'Morgana, mestra das lâminas'),
    ('057_1', .4, 'personagens', 'Arcanjo Miguel'), ('076_0', .5, 'personagens', 'Dragão na costela'), ('056_0', .5, 'personagens', 'Polvo no braço'),
    ('045_0', .5, 'personagens', 'Ratinho da Coraline, cicatrizada'), ('100_0', .5, 'personagens', 'Serzinho místico'), ('000_0', .5, 'cor', 'Boca recortada, em cor'),
    ('115_0', .5, 'cor', 'Noite estrelada de Van Gogh'), ('098_0', .4, 'cor', 'Personagem em cor'), ('051_0', .35, 'cor', 'Ghostface em cor'), ('034_0', .5, 'cor', 'Hello Kitty em rosa'), ('050_0', .5, 'cor', 'My Melody'),
]
DISP = [
    ('001_1', .5, 'Asas para as costas', 'Arte autoral'), ('024_1', .5, 'Três estrelas', 'Em conjunto ou separadas'), ('039_0', .5, 'Tridente e tentáculos', 'Arte autoral'),
    ('038_0', .5, 'Estrela e fumaça', 'Arte autoral'), ('021_0', .5, 'Fada e cristal', 'Arte autoral'), ('023_0', .55, 'Casa no cogumelo', 'Em cor'),
    ('030_0', .5, 'Sol e bússola', 'Arte autoral'), ('042_0', .5, 'Cat potion', 'Mínimo de 13 cm'), ('011_0', .5, 'Gato e coração', 'Em cor'),
]


def corte(im, ar, fy=.5):
    w, h = im.size
    if w / h > ar:
        nw = int(h * ar); x = (w - nw) // 2; return im.crop((x, 0, x + nw, h))
    nh = int(w / ar); y = int((h - nh) * fy); return im.crop((0, y, w, y + nh))


def salva(im, nome, q=82):
    os.makedirs(os.path.dirname(os.path.join(IMG, nome)) or IMG, exist_ok=True)
    im.save(os.path.join(IMG, nome), quality=q, method=6)


def foto(p):
    return ImageOps.exif_transpose(Image.open(os.path.join(IG, p + '.jpg'))).convert('RGB')


def alinha():
    import cv2, numpy as np
    a = cv2.imread(os.path.join(IG, '014_2.jpg')); b = cv2.imread(os.path.join(IG, '014_0.jpg'))
    ga, gb = cv2.cvtColor(a, cv2.COLOR_BGR2GRAY), cv2.cvtColor(b, cv2.COLOR_BGR2GRAY)
    o = cv2.SIFT_create(6000); ka, da = o.detectAndCompute(ga, None); kb, db = o.detectAndCompute(gb, None)
    m = [x for x, y in cv2.BFMatcher().knnMatch(da, db, k=2) if x.distance < .75 * y.distance]
    print('pontos', len(m))
    H, ok = cv2.findHomography(np.float32([ka[x.queryIdx].pt for x in m]), np.float32([kb[x.trainIdx].pt for x in m]), cv2.RANSAC, 6)
    print('inliers', int(ok.sum()))
    w = cv2.warpPerspective(a, H, (b.shape[1], b.shape[0]), borderMode=cv2.BORDER_REPLICATE)
    # só a área comum às duas fotos: a homografia deixa borda esticada à direita e embaixo
    cx = (40, 30, 820, 1005)
    salva(corte(Image.fromarray(w[..., ::-1]), 4 / 5).resize((900, 1125), Image.LANCZOS).crop(cx).resize((900, 1125), Image.LANCZOS), 'marcacao.webp', 80)
    salva(corte(foto('014_0'), 4 / 5).resize((900, 1125), Image.LANCZOS).crop(cx).resize((900, 1125), Image.LANCZOS), 'pronta.webp', 80)


def main():
    for i, (p, fy, _c, _l) in enumerate(OBRAS):
        im = corte(foto(p), 4 / 5, fy); n = f'{i + 1:02d}'
        salva(im.resize((1080, 1350), Image.LANCZOS), f'obras/{n}.webp', 80)
        salva(im.resize((540, 675), Image.LANCZOS), f'obras/{n}-p.webp', 78)
    for i, (p, fy, _t, _n) in enumerate(DISP):
        salva(corte(foto(p), 3 / 4, fy).resize((720, 960), Image.LANCZOS), f'disp/{i + 1:02d}.webp', 80)
    salva(corte(foto('061_0'), 4 / 5).resize((1440, 1800), Image.LANCZOS), 'retrato.webp', 84)
    salva(corte(foto('061_0'), 4 / 5).resize((720, 900), Image.LANCZOS), 'retrato-p.webp', 80)
    for nome, p in (('proc-1', '018_9'), ('proc-2', '014_2'), ('proc-3', '032_13'), ('proc-4', '004_1'), ('marcacao', '014_2'), ('pronta', '014_0')):
        salva(corte(foto(p), 4 / 5).resize((900, 1125), Image.LANCZOS), nome + '.webp', 80)
    for i, (d, n, fy) in enumerate((('Cicatrizadas', '02', .4), ('Cicatrizadas', '13', .55), ('Cicatrizadas', '12', .5), ('Cicatrizadas', '11', .5))):
        im = corte(Image.open(os.path.join(REF, 'hl', d, n + '.jpg')).convert('RGB'), 4 / 5, fy); salva(im.resize((640, 800), Image.LANCZOS), f'cic-{i + 1}.webp', 80)
    alinha()
    # recortes reais da mesa dela
    cut = os.path.join(REF, 'tmp', 'cut')
    fl = Image.open(os.path.join(cut, 'flor.png')).convert('RGBA').crop((155, 20, 410, 230))
    # tira a borda preta do espelho que o recorte trouxe
    px = fl.load()
    for y in range(fl.height):
        for x in range(fl.width):
            r, g, b, _a = px[x, y]
            if r + g + b < 170: px[x, y] = (r, g, b, 0)
    fl = fl.crop(fl.getbbox()); fl.save(os.path.join(IMG, 'flor.webp'), quality=85, method=6)


if __name__ == '__main__':
    main(); print('ok')
