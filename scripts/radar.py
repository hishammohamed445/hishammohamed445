#!/usr/bin/env python3
from __future__ import annotations
import argparse, html, json, math
from pathlib import Path

THEMES={
 "dark":{"bg":"#111113","line":"#303034","text":"#f3f2ed","muted":"#8b8b91","accent":"#ff3b30"},
 "light":{"bg":"#fffefa","line":"#d8d4ca","text":"#171719","muted":"#6e6b65","accent":"#d92d24"}}

def pt(cx,cy,r,a):
    a=math.radians(a-90); return cx+math.cos(a)*r,cy+math.sin(a)*r

def render(data,theme):
    c=THEMES[theme]; W,H,cx,cy,R=430,300,215,158,92; axes=data["axes"]; n=len(axes)
    out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{html.escape(data["title"])}">',f'<rect x=".5" y=".5" width="429" height="299" rx="12" fill="{c["bg"]}" stroke="{c["line"]}"/>',f'<text x="20" y="30" fill="{c["text"]}" font-family="ui-sans-serif,Segoe UI,Arial" font-size="15" font-weight="700">{html.escape(data["title"])}</text>',f'<text x="410" y="30" text-anchor="end" fill="{c["muted"]}" font-family="ui-monospace,Consolas,monospace" font-size="9.5">CURRENT FOCUS · NOT PROFICIENCY</text>']
    for frac in (.25,.5,.75,1):
        points=' '.join(f'{x:.1f},{y:.1f}' for x,y in [pt(cx,cy,R*frac,i*360/n) for i in range(n)])
        out.append(f'<polygon points="{points}" fill="none" stroke="{c["line"]}"/>')
    values=[]
    for i,item in enumerate(axes):
        x,y=pt(cx,cy,R,i*360/n); out.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="{c["line"]}"/>')
        values.append(pt(cx,cy,R*item["value"]/100,i*360/n))
        x,y=pt(cx,cy,R+30,i*360/n); anchor='middle' if abs(x-cx)<10 else ('end' if x<cx else 'start')
        out.append(f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" dominant-baseline="middle" fill="{c["muted"]}" font-family="ui-sans-serif,Segoe UI,Arial" font-size="10.5">{html.escape(item["label"])}</text>')
    poly=' '.join(f'{x:.1f},{y:.1f}' for x,y in values); out.append(f'<polygon points="{poly}" fill="{c["accent"]}" fill-opacity=".10" stroke="{c["accent"]}" stroke-width="1.7"/>')
    out.extend(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{c["accent"]}"/>' for x,y in values); out.append('</svg>'); return ''.join(out)

def main():
    p=argparse.ArgumentParser(); p.add_argument('--data',required=True); p.add_argument('--out',required=True); a=p.parse_args(); data=json.loads(Path(a.data).read_text())
    for theme in THEMES: Path(f'{a.out}-{theme}.svg').write_text(render(data,theme),encoding='utf-8')
if __name__=='__main__': main()
