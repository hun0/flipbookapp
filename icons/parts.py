# Flipbook icon v2: warm sunset tile, a black ink brush stroke that bursts into fire at its head ("drawing an effect")
BG = '''
  <linearGradient id="bgG" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#ffc23a"/><stop offset=".5" stop-color="#ff6a2b"/><stop offset="1" stop-color="#e8236a"/>
  </linearGradient>
  <radialGradient id="bgHi" cx="30%" cy="22%" r="60%">
    <stop offset="0" stop-color="#fff3c4" stop-opacity=".55"/><stop offset="1" stop-color="#fff3c4" stop-opacity="0"/>
  </radialGradient>'''
BG_BODY = '<rect width="1024" height="1024" fill="url(#bgG)"/><rect width="1024" height="1024" fill="url(#bgHi)"/>'

FG_DEFS = '''
  <linearGradient id="inkG" x1="150" y1="860" x2="640" y2="340" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="#14070c"/><stop offset=".7" stop-color="#1c0a12"/><stop offset=".9" stop-color="#5a1208"/><stop offset="1" stop-color="#ff7a1a"/>
  </linearGradient>
  <linearGradient id="fireO" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ff3d1a"/><stop offset="1" stop-color="#ff9a1f"/></linearGradient>
  <linearGradient id="fireY" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ffb21f"/><stop offset="1" stop-color="#ffe866"/></linearGradient>
  <filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="22"/></filter>
  <filter id="shadow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="14"/></filter>'''

INK = "M130 900 C 210 580, 400 380, 650 330 C 500 440, 380 660, 130 900 Z"
# dry-brush hairs splitting off the tail
HAIRS = ''.join(f'<path d="{d}" fill="none" stroke="#14070c" stroke-width="{w}" stroke-linecap="round"/>' for d,w in [
  ("M168 864 C 240 680, 330 560, 430 480", 7), ("M200 866 C 290 700, 390 590, 480 520", 5), ("M150 840 C 190 680, 260 580, 340 510", 4)])
SPLAT = ''.join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#14070c"/>' for x,y,r in [(104,830,14),(80,880,7),(220,926,9),(296,900,5)])

FLAME_O = "M0 -62 L 92 -96 L 72 -154 L 166 -96 L 196 -132 L 210 -60 L 318 -42 L 236 -6 L 336 30 L 224 46 L 254 104 L 162 78 L 132 136 L 82 72 L 0 62 Q -34 0 0 -62 Z"
FLAME_Y = "M20 -40 C 70 -54 110 -36 140 -86 C 146 -46 168 -28 206 -30 C 182 -8 190 14 230 26 C 180 44 166 60 176 92 C 136 72 100 76 60 80 C 34 66 12 36 20 -40 Z"
FLAME_W = "M40 -16 C 70 -24 96 -12 112 -40 C 118 -16 136 -6 156 -6 C 140 10 146 24 166 36 C 130 44 118 52 120 70 C 96 58 76 60 56 60 C 40 50 30 30 40 -16 Z"
SPARKS = ''.join(f'<path transform="translate({x} {y}) rotate({a})" d="M0 -{l} L {w} 0 L 0 {l} L -{w} 0 Z" fill="{c}"/>' for x,y,a,l,w,c in [
  (930,230,60,30,8,"#fff6c8"),(860,160,20,22,6,"#ffe866"),(960,340,70,20,5,"#fff6c8"),(770,170,0,16,4,"#ffffff"),(900,440,80,14,4,"#ffe866"),(700,230,-20,12,3,"#ffffff")])

FG_BODY = f'''
  <path d="{INK}" fill="#7a0d24" opacity=".45" filter="url(#shadow)" transform="translate(14 22)"/>
  <path d="{INK}" fill="url(#inkG)"/>
  {HAIRS}{SPLAT}
  <path d="M220 800 C 300 600, 440 430, 620 344" fill="none" stroke="#ffffff" stroke-opacity=".16" stroke-width="10" stroke-linecap="round"/>
  <g transform="translate(610 352) rotate(-24) scale(1.1)">
    <path d="{FLAME_O}" fill="#ffd23f" filter="url(#soft)" opacity=".9"/>
    <path d="{FLAME_O}" fill="url(#fireO)"/>
    <path d="{FLAME_O}" fill="url(#fireY)" transform="translate(36 2) scale(.64)"/>
    <path d="{FLAME_O}" fill="#fffbe6" transform="translate(60 4) scale(.34)"/>
  </g>
  {SPARKS}
'''
def svg(defs, body, clip=True):
    c = '<clipPath id="rr"><rect width="1024" height="1024" rx="228"/></clipPath>' if clip else ''
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" width="1024" height="1024"><defs>{defs}{c}</defs><g{" clip-path=\"url(#rr)\"" if clip else ""}>{body}</g></svg>'
def fg_scaled(k):
    o = 512*(1-k); return f'<g transform="translate({o} {o}) scale({k})">{FG_BODY}</g>'
open('icon.svg','w').write(svg(BG+FG_DEFS, BG_BODY+FG_BODY))
open('icon_square.svg','w').write(svg(BG+FG_DEFS, BG_BODY+FG_BODY, clip=False))
open('android_bg.svg','w').write(svg(BG, BG_BODY, clip=False))
open('android_fg.svg','w').write(svg(FG_DEFS, fg_scaled(0.72), clip=False))
open('android_legacy.svg','w').write(svg(BG+FG_DEFS, BG_BODY+fg_scaled(0.86)))
