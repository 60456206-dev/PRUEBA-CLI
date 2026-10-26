"""Frontal vector gears, constant angular acceleration per four-second cycle."""
from pathlib import Path
from math import sin, cos, pi
p = Path(__file__).resolve().parent

def rotation(angle):
    return f'<animateTransform attributeName="transform" type="rotate" values="0;{angle}" dur="4s" repeatCount="indefinite" calcMode="spline" keyTimes="0;1" keySplines=".333333 0 .666667 .333333"/>'

def gear(x,y,r,n,color,angle):
    points=[]
    for i in range(n):
        for f,rr in [(0,r*.90),(.18,r*.90),(.28,r),(.66,r),(.78,r*.90)]:
            a=2*pi*(i+f)/n
            points.append(f'{rr*cos(a):.2f},{rr*sin(a):.2f}')
    out=f'<g transform="translate({x} {y})"><g class="rotor">{rotation(angle)}'
    out+=f'<polygon points="{" ".join(points)}" fill="url(#{color})" stroke="url(#{color}Edge)" stroke-width="5" stroke-linejoin="round"/>'
    for radius,width,opacity in [(.83,3,.9),(.76,14,.35),(.69,3,.8),(.42,8,.6),(.32,3,1)]:
        out+=f'<circle r="{r*radius}" fill="none" stroke="url(#{color}Edge)" stroke-width="{width}" opacity="{opacity}"/>'
    for i in range(8):
        out+=f'<g transform="rotate({i*45})"><path d="M {r*.45} -18 L {r*.67} -27 L {r*.70} 13 L {r*.46} 25 Z" fill="#000" stroke="url(#{color}Edge)" stroke-width="2"/><path d="M {r*.48} -28 L {r*.70} -36" stroke="url(#{color}Edge)" stroke-width="5" opacity=".8"/></g>'
    out+=f'<circle r="{r*.26}" fill="#01040a" stroke="url(#{color}Edge)" stroke-width="12"/><circle r="{r*.20}" fill="#000" stroke="url(#{color}Edge)" stroke-width="2"/>'
    if color=='ice':
        for i in range(20):
            out+=f'<path transform="rotate({i*18})" d="M 95 -20 L 150 -46 L 177 -16 L 224 -33 L 248 -5 M 150 -46 L 159 -72" fill="none" stroke="#b4f6ff" stroke-width="1.8" opacity=".55"/>'
    out+='</g></g>'
    return out

s='''<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" style="width:100%;height:100%" viewBox="0 0 1080 1920" role="img" aria-labelledby="title desc">
<title id="title">Engranajes frontales · hielo y ámbar</title><desc id="desc">Dos ruedas frontales con aceleración angular constante en ciclos de cuatro segundos y estelas de vapor que giran y se dispersan. Diseño vectorial estilizado.</desc>
<defs>
<radialGradient id="ice"><stop stop-color="#08202d"/><stop offset=".44" stop-color="#195476"/><stop offset=".64" stop-color="#051426"/><stop offset=".83" stop-color="#296a89"/><stop offset="1" stop-color="#071621"/></radialGradient>
<linearGradient id="iceEdge" x2=".8" y2="1"><stop stop-color="#fff"/><stop offset=".3" stop-color="#70e9ff"/><stop offset=".55" stop-color="#3269a2"/><stop offset=".8" stop-color="#b2f5ff"/><stop offset="1" stop-color="#26a8dc"/></linearGradient>
<radialGradient id="amber"><stop stop-color="#3a1e08"/><stop offset=".45" stop-color="#925018"/><stop offset=".64" stop-color="#160d07"/><stop offset=".84" stop-color="#633a14"/><stop offset="1" stop-color="#160b03"/></radialGradient>
<linearGradient id="amberEdge" x2=".7" y2="1"><stop stop-color="#ffedbb"/><stop offset=".25" stop-color="#f99522"/><stop offset=".55" stop-color="#663813"/><stop offset=".8" stop-color="#ffd886"/><stop offset="1" stop-color="#c46c16"/></linearGradient>
<filter id="mist" x="-70%" y="-70%" width="240%" height="240%"><feTurbulence type="fractalNoise" baseFrequency=".012 .022" numOctaves="3" seed="9" result="noise"/><feDisplacementMap in="SourceGraphic" in2="noise" scale="65"/><feGaussianBlur stdDeviation="7"/></filter>
<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="32"/></filter>
</defs>
<style>@media(prefers-reduced-motion:reduce){.rotor,.drift,.camera{transform:none}.animatedMist{display:none}}</style>
<rect width="1080" height="1920" fill="#000"/>
<g transform="translate(540 960)"><g class="camera"><animateTransform attributeName="transform" type="scale" values="1;1.04;1" dur="12s" repeatCount="indefinite" calcMode="spline" keyTimes="0;.5;1" keySplines=".42 0 .58 1;.42 0 .58 1"/><g transform="translate(-540 -960)">
<g filter="url(#glow)" opacity=".24"><circle cx="365" cy="800" r="260" fill="#1485bf"/><circle cx="795" cy="1080" r="208" fill="#bc650e"/></g>
'''
# Pitch radii 270/216, centers separated by 486: same tooth pitch.
s+=gear(350,800,285,20,'ice',360)
s+=gear(757,1066,228,16,'amber',-450)
for x,y,r,c,angle in [(350,800,285,'#84dfff',360),(757,1066,228,'#dab785',-450)]:
    s+=f'<g class="animatedMist" transform="translate({x} {y})"><g class="rotor">{rotation(angle)}'
    for j in range(3):
        s+=f'<g transform="rotate({j*120})"><g class="drift"><animateTransform attributeName="transform" type="translate" values="0 0;35 -45;0 0" dur="3s" repeatCount="indefinite"/><path d="M {r*.65} {-r*.45} C {r*1.3} {-r*.9}, {r*1.2} {r*.65}, {r*.8} {r} S {r*1.6} {r*1.3}, {r*1.4} {r*1.65}" fill="none" stroke="{c}" stroke-width="32" opacity=".23" filter="url(#mist)"><animate attributeName="opacity" values=".12;.32;.12" dur="3s" repeatCount="indefinite"/></path></g></g>'
    s+='</g></g>'
s+='</g></g></g></svg>'
(p/'ENGRANAJES_INTRO_V3.svg').write_text(s)
