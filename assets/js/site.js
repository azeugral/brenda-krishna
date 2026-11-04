(function () {
  'use strict';
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var reduz = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var LOJA = 'https://ig.me/m/ink.krishna_';

  /* tudo pronto logo de cara: imagens baixam ao abrir, sem esperar a rolagem */
  addEventListener('load', function () { $$('img[loading=lazy]').forEach(function (i) { i.loading = 'eager'; }); });

  /* ---------- hero ---------- */
  var fundo = $('#heroFundo'), hero = $('#inicio');
  function deitado() { return innerWidth / innerHeight >= 1; }
  function posArte() { return deitado() ? { cx: .68, cy: .54, alt: .94 } : { cx: .5, cy: .3, alt: .46 }; }
  function iniciaVideo() {
    var v = document.createElement('video');
    v.muted = true; v.loop = true; v.playsInline = true; v.autoplay = true; v.setAttribute('playsinline', ''); v.setAttribute('aria-hidden', 'true');
    v.src = 'assets/video/hero-' + (deitado() ? 'largo' : 'retrato') + '.mp4';
    v.poster = 'assets/img/hero-' + (deitado() ? 'largo' : 'retrato') + '.webp';
    fundo.appendChild(v);
    v.addEventListener('playing', function () { v.classList.add('on'); }, { once: true });
    new IntersectionObserver(function (e) { if (e[0].isIntersecting) { var p = v.play(); if (p) p.catch(function () {}); } else v.pause(); }).observe(hero);
  }
  function iniciaCanvas() {
    var cv = document.createElement('canvas'); cv.setAttribute('aria-hidden', 'true'); fundo.appendChild(cv);
    var a; try { a = window.Arte(cv, { cor: 'assets/img/arte-cor.webp', mapa: 'assets/img/arte-mapa.webp', papel: 'assets/img/papel.webp', pos: posArte }); } catch (e) { a = null; }
    if (!a) { cv.remove(); return iniciaVideo(); }
    function medida() { var d = Math.min(devicePixelRatio || 1, 2), r = fundo.getBoundingClientRect(); cv.width = Math.round(r.width * d); cv.height = Math.round(r.height * d); }
    medida(); addEventListener('resize', medida);
    var visivel = true, t0 = 0, lentos = 0, ult = 0;
    new IntersectionObserver(function (e) { visivel = e[0].isIntersecting; if (visivel) { ult = 0; requestAnimationFrame(q); } }).observe(hero);
    function q(ms) {
      if (!visivel) return;
      if (!t0) t0 = ms;
      if (ult && ms - ult > 34) lentos++; else if (lentos > 0) lentos -= .25;
      ult = ms;
      if (lentos > 40) { cv.remove(); return iniciaVideo(); }
      a.desenhar((ms - t0) / 1000); requestAnimationFrame(q);
    }
    a.carregou.then(function () { a.desenhar(0); cv.classList.add('on'); requestAnimationFrame(q); }, function () { cv.remove(); iniciaVideo(); });
  }
  if (!reduz) {
    if (matchMedia('(pointer: coarse)').matches || innerWidth < 900) iniciaVideo(); else iniciaCanvas();
  } else { $('#heroPoster').src = 'assets/img/hero-' + (deitado() ? 'largo' : 'retrato') + '-fim.webp'; var sp = $('#heroFundo source'); if (sp) sp.srcset = 'assets/img/hero-retrato-fim.webp'; }

  /* ---------- menu ---------- */
  var menu = $('#menu'), mb = $('#menuBtn');
  function fechaMenu() { menu.hidden = true; mb.setAttribute('aria-expanded', 'false'); mb.textContent = 'Menu'; document.documentElement.classList.remove('trava'); }
  mb.addEventListener('click', function () {
    if (menu.hidden) { menu.hidden = false; mb.setAttribute('aria-expanded', 'true'); mb.textContent = 'Fechar'; document.documentElement.classList.add('trava'); } else fechaMenu();
  });
  $$('a', menu).forEach(function (a) { a.addEventListener('click', fechaMenu); });

  /* topo muda de tom depois do hero */
  new IntersectionObserver(function (e) { $('#topo').classList.toggle('solido', !e[0].isIntersecting); }, { rootMargin: '-80px 0px 0px 0px' }).observe(hero);

  /* ---------- entrada das seções ---------- */
  if (!reduz) {
    var alvo = $$('.cab, .intro, .obra, .disp li, .proc article, .cic li, .fb blockquote, .folha, .artista-txt > p, .artista-txt blockquote, .passos li, .pedido, .q');
    alvo.forEach(function (el) { el.classList.add('sobe'); });
    var io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('foi'); io.unobserve(e.target); } }); }, { rootMargin: '0px 0px -6% 0px', threshold: .01 });
    alvo.forEach(function (el) { io.observe(el); });
  }

  /* ---------- filtro + ver mais ---------- */
  var obras = $$('.obra'), grade = $('#grade'), mais = $('#verMais'), aberto = false;
  function limite() { return innerWidth < 700 ? 8 : 12; }
  function aplica() {
    var f = ($('.filtro.on') || {dataset: {}}).dataset.f || 'todos', n = 0, lim = limite(), oculto = 0;
    obras.forEach(function (o) {
      var ok = f === 'todos' || o.dataset.cat === f;
      if (ok) { n++; if (!aberto && n > lim) { ok = false; oculto++; } }
      o.hidden = !ok; if (ok) o.classList.add('foi');
    });
    mais.parentNode.hidden = !oculto;
  }
  $$('.filtro').forEach(function (b) {
    b.addEventListener('click', function () {
      $$('.filtro').forEach(function (x) { x.classList.toggle('on', x === b); x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
      aberto = false; aplica();
    });
  });
  mais.addEventListener('click', function () { aberto = true; aplica(); });
  addEventListener('resize', function () { if (!aberto) aplica(); });
  aplica();

  /* ---------- caixa de foto ---------- */
  var cx = $('#caixa'), ci = $('#caixaImg'), cl = $('#caixaLeg'), lista = [], at = 0, volta = null;
  function mostra(i) {
    at = (i + lista.length) % lista.length; var b = lista[at];
    ci.src = b.dataset.g; ci.alt = b.dataset.leg; cl.textContent = b.dataset.leg;
  }
  function abre(b) {
    lista = obras.filter(function (o) { return !o.hidden; }).map(function (o) { return $('button', o); });
    volta = b; cx.hidden = false; document.documentElement.classList.add('trava'); mostra(lista.indexOf(b)); $('.caixa-x').focus();
  }
  function fecha() { cx.hidden = true; ci.removeAttribute('src'); document.documentElement.classList.remove('trava'); if (volta) volta.focus(); }
  grade.addEventListener('click', function (e) { var b = e.target.closest('button'); if (b) abre(b); });
  $('.caixa-x').addEventListener('click', fecha);
  $('.ant').addEventListener('click', function () { mostra(at - 1); });
  $('.prox').addEventListener('click', function () { mostra(at + 1); });
  cx.addEventListener('click', function (e) { if (e.target === cx) fecha(); });
  addEventListener('keydown', function (e) {
    if (cx.hidden) { if (e.key === 'Escape' && !menu.hidden) fechaMenu(); return; }
    if (e.key === 'Escape') fecha(); if (e.key === 'ArrowLeft') mostra(at - 1); if (e.key === 'ArrowRight') mostra(at + 1);
  });
  var xi = null;
  cx.addEventListener('touchstart', function (e) { xi = e.touches[0].clientX; }, { passive: true });
  cx.addEventListener('touchend', function (e) { if (xi === null) return; var d = e.changedTouches[0].clientX - xi; xi = null; if (Math.abs(d) > 50) mostra(at + (d < 0 ? 1 : -1)); });

  /* ---------- comparador ---------- */
  /* arraste na foto inteira (o iOS só move um range pelo polegar); o range fica para o teclado */
  var co = $('#compara'), rg = $('input', co), arrasta = false;
  function poe(v) { v = Math.max(0, Math.min(100, v)); co.style.setProperty('--p', v + '%'); rg.value = v; }
  function dedo(e) { var r = co.getBoundingClientRect(); poe((e.clientX - r.left) / r.width * 100); }
  co.addEventListener('pointerdown', function (e) { arrasta = true; co.setPointerCapture(e.pointerId); dedo(e); });
  co.addEventListener('pointermove', function (e) { if (arrasta) dedo(e); });
  ['pointerup', 'pointercancel'].forEach(function (n) { co.addEventListener(n, function () { arrasta = false; }); });
  rg.addEventListener('input', function () { poe(+rg.value); });

  /* ---------- vídeo do processo só toca visível ---------- */
  var reel = $('.reel video');
  var rb = $('#reelBtn'), parado = reduz;
  function toca() { var p = reel.play(); if (p) p.catch(function () {}); }
  function rotulo() { rb.textContent = parado ? 'Tocar vídeo' : 'Pausar vídeo'; }
  rotulo();
  rb.addEventListener('click', function () { parado = !parado; rotulo(); if (parado) reel.pause(); else toca(); });
  new IntersectionObserver(function (e) { if (e[0].isIntersecting) { if (!parado) toca(); } else reel.pause(); }, { threshold: .25 }).observe(reel);

  /* ---------- dúvidas: uma aberta por vez ---------- */
  $$('#faq button').forEach(function (b) {
    b.addEventListener('click', function () {
      var ab = b.getAttribute('aria-expanded') === 'true';
      $$('#faq button').forEach(function (x) { x.setAttribute('aria-expanded', 'false'); x.parentNode.classList.remove('ab'); });
      if (!ab) { b.setAttribute('aria-expanded', 'true'); b.parentNode.classList.add('ab'); }
    });
  });

  /* ---------- pedido copiado para a DM ---------- */
  var fm = $('#pedido'), ide = $('#ideia'), er = $('#ideiaErro'), ok = $('#pedidoOk');
  $$('.quero').forEach(function (b) {
    b.addEventListener('click', function () {
      ide.value = 'Quero o projeto disponível "' + b.dataset.t + '".'; er.hidden = true;
      $('#agendar').scrollIntoView({ behavior: reduz ? 'auto' : 'smooth' }); ide.focus({ preventScroll: true });
    });
  });
  fm.addEventListener('submit', function (e) {
    e.preventDefault();
    var v = ide.value.trim();
    if (!v) { er.hidden = false; ide.setAttribute('aria-invalid', 'true'); ide.focus(); return; }
    er.hidden = true; ide.removeAttribute('aria-invalid');
    var txt = ['Oi, Brenda! Vim pelo seu site.', 'Ideia: ' + v];
    if (fm.local.value.trim()) txt.push('Local: ' + fm.local.value.trim());
    if (fm.tam.value.trim()) txt.push('Tamanho: ' + fm.tam.value.trim());
    if (fm.ref.value.trim()) txt.push('Referência: ' + fm.ref.value.trim());
    var t = txt.join('\n');
    function abreDM() { ok.hidden = false; window.open(LOJA, '_blank', 'noopener'); }
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(t).then(abreDM, abreDM); else abreDM();
  });
})();
