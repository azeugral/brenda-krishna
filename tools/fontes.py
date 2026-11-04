"""Baixa as fontes do Google e grava self-hosted em assets/fontes + assets/css/fontes.css. Uso: python tools/fontes.py"""
import os, re, urllib.request
AQUI = os.path.dirname(os.path.abspath(__file__)); SITE = os.path.dirname(AQUI)
ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36'
fam = 'family=Oranienbaum&family=Pinyon+Script&family=Playfair+Display:ital,wght@1,400;1,500&family=Instrument+Sans:wght@400..600&display=swap'
css = urllib.request.urlopen(urllib.request.Request('https://fonts.googleapis.com/css2?' + fam, headers={'User-Agent': ua})).read().decode()
saida = []
for sub, b in re.findall(r'/\* ([a-z-]+) \*/\s*(@font-face \{.*?\})', css, re.S):
    if sub not in ('latin', 'latin-ext'):
        continue
    f = re.search(r"font-family: '([^']+)'", b).group(1).replace(' ', '')
    st = re.search(r'font-style: (\w+)', b).group(1); wg = re.search(r'font-weight: ([\d ]+)', b).group(1).strip().replace(' ', '-')
    u = re.search(r'url\((https[^)]+)\)', b).group(1)
    nome = f'{f}-{st}-{wg}-{sub}.woff2'
    urllib.request.urlretrieve(u, os.path.join(SITE, 'assets', 'fontes', nome))
    saida.append(re.sub(r'url\(https[^)]+\)', f'url(../fontes/{nome})', b))
open(os.path.join(SITE, 'assets', 'css', 'fontes.css'), 'w', encoding='utf8').write('\n'.join(saida))
print(len(saida))
