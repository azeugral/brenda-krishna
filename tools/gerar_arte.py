"""Separa a filigrana do post 019_3 do papel, como transmitância (aquarela multiplicada sobre o papel), e gera os mapas do hero.
assets/img/arte-cor.webp  : RGB = transmitância (1 = papel limpo). Base: original denoised; traços escuros: ampliação x4.
assets/img/arte-mapa.webp : R = lápis, G = chegada da tinta (geodésica a partir da estrela central), B = halo molhado
assets/img/papel.webp     : trama real do papel dela, ladrilho sem emenda, gerado
Uso: python tools/gerar_arte.py"""
import os
import cv2, numpy as np
from PIL import Image
from skimage.graph import MCP_Geometric
AQUI = os.path.dirname(os.path.abspath(__file__)); SITE = os.path.dirname(AQUI)
REF = os.path.join(SITE, '..', '_ref'); IMG = os.path.join(SITE, 'assets', 'img')
E = 2  # trabalha em 2160x2880
orig = cv2.imread(os.path.join(REF, 'ig', 'fotos', '019_3.jpg'))
limpo = cv2.fastNlMeansDenoisingColored(orig, None, 4, 8, 5, 15)
W0, H0 = 2160, 2880
base = cv2.resize(limpo, (W0, H0), interpolation=cv2.INTER_LANCZOS4).astype(np.float32)
base = cv2.GaussianBlur(base, (0, 0), sigmaX=.4, sigmaY=2.2)  # a trama do papel deixa riscas horizontais
crisp = cv2.resize(cv2.imread(os.path.join(REF, 'up', '019_3-x4.png')), (W0, H0), interpolation=cv2.INTER_AREA).astype(np.float32)
peq = cv2.resize(base, (W0 // 8, H0 // 8), interpolation=cv2.INTER_AREA).astype(np.uint8)
pap = cv2.GaussianBlur(cv2.resize(cv2.medianBlur(peq, 61), (W0, H0), interpolation=cv2.INTER_CUBIC).astype(np.float32), (0, 0), 30)
T = np.clip(base / pap, 0, 1)
Tc = np.clip(crisp / pap, 0, 1)
esc = np.clip((.55 - Tc.mean(2)) / .25, 0, 1)[..., None]  # só traço escuro vem do x4
T = T * (1 - esc) + np.minimum(T, Tc) * esc
# cobertura: desvio do papel, generosa, para não perder aguada nem lápis
dev = 1 - T.min(2)
cob = np.clip((cv2.GaussianBlur(dev, (0, 0), 2.2) - .035) / .07, 0, 1)
mask = np.ones(cob.shape, np.float32)
for x0, y0, x1, y1 in [(0, 0, 540, 225), (0, 0, 70, 1440), (860, 0, 1080, 110), (0, 1000, 430, 1440), (670, 1130, 1080, 1440), (980, 1090, 1080, 1440), (1036, 0, 1080, 1440), (0, 0, 1080, 62), (0, 1345, 1080, 1440)]:
    mask[y0 * E:y1 * E, x0 * E:x1 * E] = 0
mask = cv2.GaussianBlur(mask, (0, 0), 6)
cob = (cob * mask).astype(np.float32)
b = (cob > .4).astype(np.uint8)
n, lb, st, _ = cv2.connectedComponentsWithStats(cv2.dilate(b, np.ones((9, 9), np.uint8)), connectivity=8)
keep = np.zeros(n, bool); keep[1:] = st[1:, cv2.CC_STAT_AREA] > 500
cob *= cv2.GaussianBlur(keep[lb].astype(np.float32), (0, 0), 3)
ys, xs = np.where(cob > .3); M = 24
x0, x1, y0, y1 = max(xs.min() - M, 0), min(xs.max() + M, W0), max(ys.min() - M, 0), min(ys.max() + M, H0)
print('caixa', x0 / E, x1 / E, y0 / E, y1 / E)
T2 = 1 - (1 - T[y0:y1, x0:x1]) * cob[y0:y1, x0:x1, None]
c2 = cob[y0:y1, x0:x1]
hs = 1800; ws = int(round(c2.shape[1] * hs / c2.shape[0]))
T3 = cv2.resize(T2, (ws, hs), interpolation=cv2.INTER_AREA); c3 = cv2.resize(c2, (ws, hs), interpolation=cv2.INTER_AREA)
Image.fromarray((T3[..., ::-1] * 255).astype(np.uint8), 'RGB').save(os.path.join(IMG, 'arte-cor.webp'), quality=90, method=5)
L = T3.mean(2).astype(np.float32)
bh = cv2.morphologyEx(L, cv2.MORPH_BLACKHAT, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (13, 13)))
lap = np.clip(bh / .22, 0, 1) * np.clip(c3 * 2, 0, 1)
p = 3; ap = cv2.resize(c3, (ws // p, hs // p), interpolation=cv2.INTER_AREA)
custo = 1 + 14 * (1 - np.clip(ap * 2, 0, 1))
cx = int(((551 * E - x0) / (x1 - x0)) * ap.shape[1]); cy = int(((590 * E - y0) / (y1 - y0)) * ap.shape[0])
dist, _ = MCP_Geometric(custo).find_costs([(cy, cx)])
dist = np.nan_to_num(dist, posinf=dist[np.isfinite(dist)].max())
c = np.quantile(dist[ap > .3], np.linspace(0, 1, 256))
t = .6 * np.interp(dist, c, np.linspace(0, 1, 256)) + .4 * np.clip(dist / c[-1], 0, 1)
t = cv2.GaussianBlur(cv2.resize(t.astype(np.float32), (ws, hs), interpolation=cv2.INTER_CUBIC), (0, 0), 2)
halo = cv2.GaussianBlur(c3, (0, 0), 16); halo = np.clip(halo * 1.4, 0, 1)
mapa = np.dstack([lap * 255, np.clip(t, 0, 1) * 255, halo * 255]).astype(np.uint8)
Image.fromarray(mapa, 'RGB').save(os.path.join(IMG, 'arte-mapa.webp'), quality=92, method=5)
# fibra do papel: ruído filtrado por FFT, por isso o ladrilho emenda sozinho. Sem marcas de foto.
def fibra(sem, tam=600):
    r = np.random.default_rng(sem); n = r.standard_normal((tam, tam)); fy = np.fft.fftfreq(tam)[:, None]; fx = np.fft.fftfreq(tam)[None, :]
    def banda(ex, ey, a, b):
        d = np.sqrt((fx * ex) ** 2 + (fy * ey) ** 2) + 1e-6
        return np.real(np.fft.ifft2(np.fft.fft2(n) * np.exp(-(d / b) ** 2) * (1 - np.exp(-(d / a) ** 2))))
    u = lambda v: v / v.std()
    return .62 * u(banda(4, 1, .05, .26)) + .5 * u(banda(1, 1, .09, .4)) + .4 * u(banda(1, 1, .006, .03))
for nome, cor, k in (('papel', (238, 232, 221), 2.6), ('caderno', (240, 224, 168), 2.8)):
    v = fibra(7 if nome == 'papel' else 11)[..., None] * k
    Image.fromarray(np.clip(np.array(cor, np.float32) + v * np.array((1, 1.02, 1.08)), 0, 255).astype(np.uint8)).save(os.path.join(IMG, nome + '.webp'), quality=86, method=6)
print('ok', ws, hs, {f: round(os.path.getsize(os.path.join(IMG, f)) / 1e6, 2) for f in ('arte-cor.webp', 'arte-mapa.webp', 'papel.webp')})
pv = np.array([221, 232, 238], np.float32) * T3
cv2.imwrite(os.path.join(REF, 'folhas', 'arte-previa.jpg'), pv.astype(np.uint8)[300:1300, 150:1150], [cv2.IMWRITE_JPEG_QUALITY, 88])
