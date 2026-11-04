/* Hero: a filigrana da Brenda sobre o papel, à luz de abajur.
   Ciclo de 26 s: lápis, a aquarela corre a partir da estrela central pelos caminhos do desenho, repousa e volta ao lápis.
   O quadro 0 é igual ao último, então o MP4 do celular não tem emenda. */
window.Arte = function (cv, op) {
  var gl = cv.getContext('webgl', { antialias: false, alpha: false, preserveDrawingBuffer: !!op.gravar, powerPreference: 'low-power' });
  if (!gl) return null;
  var vs = 'attribute vec2 p;void main(){gl_Position=vec4(p,0.,1.);}';
  var fs = [
    'precision highp float;',
    'uniform sampler2D A,M,P;uniform vec2 R;uniform vec3 C;uniform float asp,prog,cor,luz,t;',
    'float h(vec2 p){return fract(sin(dot(p,vec2(41.3,289.1)))*43758.5453);}',
    'float n(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(h(i),h(i+vec2(1,0)),f.x),mix(h(i+vec2(0,1)),h(i+vec2(1,1)),f.x),f.y);}',
    'float fbm(vec2 p){float v=0.,a=.5;for(int i=0;i<4;i++){v+=a*n(p);p=p*2.03+7.1;a*=.5;}return v;}',
    'void main(){',
    ' vec2 px=vec2(gl_FragCoord.x,R.y-gl_FragCoord.y);',
    ' vec2 q=(px-C.xy)/C.z;vec2 uv=vec2(q.x/asp+.5,q.y+.5);',
    ' float dentro=step(0.,uv.x)*step(uv.x,1.)*step(0.,uv.y)*step(uv.y,1.);',
    ' vec2 tp=px/(R.y>R.x?620.:760.)*vec2(1.,1.);',
    ' float trama=texture2D(P,tp).r-.933;',
    ' vec3 pap=vec3(.945,.915,.855)+trama*1.1;',
    ' pap*=1.+(fbm(px/R.y*2.6+3.)-.5)*.045;',
    ' vec3 c=pap;',
    ' if(dentro>.5){',
    '  vec4 m=texture2D(M,uv);vec3 T=texture2D(A,uv).rgb;',
    '  float w=fbm(uv*vec2(9.,12.)+t*.012);',
    '  float f=prog*1.2-m.g+(w-.5)*.1;',
    '  float rev=smoothstep(.0,.045,f);',
    '  float molh=smoothstep(.0,.05,f)*(1.-smoothstep(.05,.3,f))*m.b;',
    '  float lap=m.r*(1.-rev)*.62;',
    '  c*=mix(vec3(1.),vec3(.5,.44,.56),lap);',
    '  c*=mix(vec3(1.),T,rev*cor);',
    '  c*=mix(vec3(1.),vec3(.88,.78,.93),molh*.6*cor);',
    ' }',
    ' vec2 v=px/R;float d=length((v-vec2(.52+.012*sin(t*.7),.3))*vec2(R.x/R.y,1.)*vec2(.78,1.));',
    ' float abajur=1.-smoothstep(.2,1.25,d);',
    ' vec3 l=mix(vec3(.60,.42,.28),vec3(.985,.95,.885),abajur);',
    ' l*=1.+luz*.018;',
    ' c*=l;',
    ' float g=h(px+fract(t)*91.)-.5;c+=g*.006;',
    ' gl_FragColor=vec4(c,1.);',
    '}'].join('\n');
  function sh(tp, src) { var s = gl.createShader(tp); gl.shaderSource(s, src); gl.compileShader(s); if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw gl.getShaderInfoLog(s); return s; }
  var pr = gl.createProgram(); gl.attachShader(pr, sh(gl.VERTEX_SHADER, vs)); gl.attachShader(pr, sh(gl.FRAGMENT_SHADER, fs)); gl.linkProgram(pr); gl.useProgram(pr);
  var b = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, b); gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
  var lp = gl.getAttribLocation(pr, 'p'); gl.enableVertexAttribArray(lp); gl.vertexAttribPointer(lp, 2, gl.FLOAT, false, 0, 0);
  var U = {}; ['A', 'M', 'P', 'R', 'C', 'asp', 'prog', 'cor', 'luz', 't'].forEach(function (n) { U[n] = gl.getUniformLocation(pr, n); });
  gl.uniform1i(U.A, 0); gl.uniform1i(U.M, 1); gl.uniform1i(U.P, 2);
  var asp = 1, pronto = false, ciclo = 26;
  function tex(un, img, rep) {
    var t = gl.createTexture(); gl.activeTexture(gl.TEXTURE0 + un); gl.bindTexture(gl.TEXTURE_2D, t);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGB, gl.RGB, gl.UNSIGNED_BYTE, img);
    var pot = !(img.width & (img.width - 1)) && !(img.height & (img.height - 1));
    if (pot) gl.generateMipmap(gl.TEXTURE_2D);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, pot ? gl.LINEAR_MIPMAP_LINEAR : gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    var w = rep ? gl.REPEAT : gl.CLAMP_TO_EDGE; gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, w); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, w);
  }
  function carrega(src) { return new Promise(function (ok, no) { var i = new Image(); i.onload = function () { ok(i); }; i.onerror = no; i.src = src; }); }
  function pot(i) { var s = 512, c = document.createElement('canvas'); c.width = c.height = s; c.getContext('2d').drawImage(i, 0, 0, s, s); return c; }
  var carregou = Promise.all([carrega(op.cor), carrega(op.mapa), carrega(op.papel)]).then(function (r) {
    tex(0, r[0]); tex(1, r[1]); tex(2, pot(r[2]), true); asp = r[0].width / r[0].height; gl.uniform1f(U.asp, asp); pronto = true;
  });
  function pos() {
    var W = cv.width, H = cv.height, a = op.pos();
    gl.viewport(0, 0, W, H); gl.uniform2f(U.R, W, H); gl.uniform3f(U.C, W * a.cx, H * a.cy, a.alt * H);
  }
  function suave(a, b, x) { var t = Math.max(0, Math.min(1, (x - a) / (b - a))); return t * t * (3 - 2 * t); }
  function tremor(t) { return Math.sin(t * 2 * Math.PI / 13) * .6 + Math.sin(t * 2 * Math.PI / 2.6) * .25 + Math.sin(t * 2 * Math.PI / 1.3) * .15; }
  function pinta(p, c, t) {
    if (!pronto) return; pos();
    gl.uniform1f(U.prog, p); gl.uniform1f(U.cor, c); gl.uniform1f(U.luz, tremor(t)); gl.uniform1f(U.t, t);
    gl.drawArrays(gl.TRIANGLES, 0, 3);
  }
  return {
    ciclo: ciclo, carregou: carregou, medir: pos,
    desenhar: function (t) {
      t = t % ciclo;
      var i = suave(1, 13, t), lin = Math.max(0, Math.min(1, (t - 1) / 12));
      pinta(.5 * i + .5 * lin, 1 - suave(21.5, 25.6, t), t);
    },
    final: function () { pinta(1, 1, 0); }
  };
};
