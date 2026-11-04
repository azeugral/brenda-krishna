"""Monta index.html a partir de tools/modelo.html e das listas de tools/processar.py.
Uso: python tools/montar.py   (editar o modelo, nunca o index.html da raiz)"""
import base64, html, io, os, sys, time
from PIL import Image
AQUI = os.path.dirname(os.path.abspath(__file__)); SITE = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)
import processar as P
CAT = {'asas': 'Asas e ornamentos', 'natureza': 'Natureza', 'personagens': 'Personagens', 'delicadas': 'Delicadas', 'cor': 'Em cor'}


def a(s):
    return html.escape(s, quote=True)


def lq(arq):
    im = Image.open(os.path.join(SITE, arq)).convert('RGB'); im.thumbnail((20, 25))
    b = io.BytesIO(); im.save(b, 'WEBP', quality=40)
    return 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()


def obras():
    li = []
    for i, (_p, _f, cat, leg) in enumerate(P.OBRAS):
        n = f'{i + 1:02d}'; pq = f'assets/img/obras/{n}-p.webp'; g = f'assets/img/obras/{n}.webp'
        li.append(f'''    <li class="obra" data-cat="{cat}"><button data-g="{g}" data-leg="{a(leg)}" aria-label="Ampliar: {a(leg)}"><img src="{pq}" srcset="{pq} 540w, {g} 1080w" sizes="(max-width: 700px) 47vw, (max-width: 1100px) 31vw, 23vw" alt="{a(leg)}" width="540" height="675" loading="lazy" decoding="async" draggable="false" style="background-image:url({lq(pq)})"></button><p>{a(leg)}</p></li>''')
    return '\n'.join(li)


def disp():
    return '\n'.join(f'''    <li><img src="assets/img/disp/{i + 1:02d}.webp" alt="Desenho disponível: {a(t)}" width="720" height="960" loading="lazy" decoding="async" draggable="false"><div><h3>{a(t)}</h3><p>{a(n)}</p><button class="quero" data-t="{a(t)}">Quero esta</button></div></li>''' for i, (_p, _f, t, n) in enumerate(P.DISP))


def rolo():
    return '\n'.join(f'''    <li><span class="pola"><img src="assets/img/rolo/{i + 1:02d}.webp" alt="" width="640" height="800" loading="lazy" decoding="async" draggable="false"></span></li>''' for i in range(len(P.ROLO)))


s = open(os.path.join(AQUI, 'modelo.html'), encoding='utf8').read()
s = s.replace('__OBRAS__', obras()).replace('__DISP__', disp()).replace('__ROLO__', rolo()).replace('__V__', str(int(time.time()) % 100000))
for c in ('—', '–'):
    assert c not in s, 'traço longo no HTML'
open(os.path.join(SITE, 'index.html'), 'w', encoding='utf8').write(s)
print('index', round(len(s) / 1024), 'KB')
