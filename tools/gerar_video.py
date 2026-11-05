"""Grava o hero (assets/js/arte.js) e gera MP4 + pôsteres.
Pôsteres: hero-*.webp (quadro 0, lápis) e hero-*-fim.webp (arte pronta, movimento reduzido).
Uso: python tools/gerar_video.py [--teste]   (--teste grava só 4 quadros em _ref/hero)"""
import base64, functools, http.server, io, os, subprocess, sys, threading
from PIL import Image
from playwright.sync_api import sync_playwright
AQUI = os.path.dirname(os.path.abspath(__file__)); SITE = os.path.dirname(AQUI)
VID = os.path.join(SITE, 'assets', 'video'); IMG = os.path.join(SITE, 'assets', 'img'); CONF = os.path.join(SITE, '..', '_ref', 'hero')
FPS = 24
VERS = {'largo': (1920, 1080, '{cx:.68,cy:.54,alt:.94}'), 'retrato': (1080, 1920, '{cx:.5,cy:.3,alt:.46}')}
HTML = '<!doctype html><body style="margin:0"><canvas id=c></canvas><script src="/assets/js/arte.js"></script>'


class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        if self.path == '/g':
            b = HTML.encode(); self.send_response(200); self.send_header('Content-Type', 'text/html'); self.send_header('Content-Length', str(len(b))); self.end_headers(); self.wfile.write(b)
        else:
            super().do_GET()


s = http.server.ThreadingHTTPServer(('127.0.0.1', 8931), functools.partial(H, directory=SITE))
threading.Thread(target=s.serve_forever, daemon=True).start()
os.makedirs(VID, exist_ok=True); os.makedirs(CONF, exist_ok=True)
teste = '--teste' in sys.argv
with sync_playwright() as p:
    b = p.chromium.launch(args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
    for nome, (w, h, pos) in VERS.items():
        g = b.new_page(viewport={'width': w, 'height': h}); g.goto('http://127.0.0.1:8931/g')
        g.evaluate(f"""async()=>{{const c=document.getElementById('c');c.width={w};c.height={h};
          window.a=Arte(c,{{gravar:true,cor:'/assets/img/arte-cor.webp',mapa:'/assets/img/arte-mapa.webp',papel:'/assets/img/papel.webp',pos:()=>({pos})}});await a.carregou;
          window.q=(t)=>{{a.desenhar(t);return c.toDataURL('image/jpeg',.97).split(',')[1]}};window.qf=()=>{{a.final();return c.toDataURL('image/jpeg',.97).split(',')[1]}};}}""")
        pega = lambda js: Image.open(io.BytesIO(base64.b64decode(g.evaluate(js)))).convert('RGB')
        pega('q(0)').save(os.path.join(IMG, f'hero-{nome}.webp'), quality=84, method=6)
        pega('qf()').save(os.path.join(IMG, f'hero-{nome}-fim.webp'), quality=84, method=6)
        if nome == 'largo':
            # só o papel: é o que aparece antes do desenho, para o tamanho da arte nunca mudar na troca de camada
            g.evaluate("""async()=>{const c=document.createElement('canvas');c.width=1920;c.height=1080;
              window.p=Arte(c,{gravar:true,cor:'/assets/img/arte-cor.webp',mapa:'/assets/img/arte-mapa.webp',papel:'/assets/img/papel.webp',pos:()=>({cx:-5,cy:.54,alt:.94})});await p.carregou;window.pf=()=>{p.final();return c.toDataURL('image/jpeg',.97).split(',')[1]}}""")
            pega('pf()').save(os.path.join(IMG, 'hero-papel.webp'), quality=84, method=6)
        if teste:
            for t in (2, 4, 6):
                pega(f'q({t})').save(os.path.join(CONF, f'{nome}-{t}.jpg'), quality=88)
            g.close(); continue
        n = 16 * FPS
        ff = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'image2pipe', '-c:v', 'mjpeg', '-r', str(FPS), '-i', '-', '-vf', 'scale=in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p', '-c:v', 'libx264', '-preset', 'slow', '-crf', '23', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv', '-movflags', '+faststart', '-an', os.path.join(VID, f'hero-{nome}.mp4')], stdin=subprocess.PIPE)
        for i in range(n):
            ff.stdin.write(base64.b64decode(g.evaluate(f'q({i / FPS})')))
            if i % 120 == 0:
                print(nome, i, n, flush=True)
        ff.stdin.close(); ff.wait(); g.close()
        print(nome, round(os.path.getsize(os.path.join(VID, f'hero-{nome}.mp4')) / 1e6, 2), 'MB', flush=True)
    b.close()
