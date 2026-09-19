#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, html, io, urllib.request
from pathlib import Path

THEMES={
 "dark":{"bg":"#0b0b0c","panel":"#111113","line":"#2a2a2e","text":"#f3f2ed","muted":"#8b8b91","soft":"#171719","accent":"#ff3b30","dot":"#dddcd6"},
 "light":{"bg":"#f5f3ed","panel":"#fffefa","line":"#d8d4ca","text":"#171719","muted":"#6e6b65","soft":"#f0ede6","accent":"#d92d24","dot":"#2d2d30"}}
ROWS=[("ROLE","AI Engineer"),("BASE","Cairo, Egypt"),("FOCUS","Computer Vision · ML Systems"),("EXPLORING","RAG · Agents · Multimodal"),("TOOLCHAIN","Python · Git · Docker · Linux"),("MODE","Build · Test · Ship")]

def avatar(user):
    req=urllib.request.Request(f'https://github.com/{user}.png?size=512',headers={'User-Agent':'profile-hero'})
    with urllib.request.urlopen(req,timeout=20) as r:return r.read()

def runs_from_avatar(data,theme):
    from PIL import Image,ImageEnhance,ImageFilter,ImageOps
    im=Image.open(io.BytesIO(data)).convert('RGB'); side=min(im.size); x=(im.width-side)//2; y=(im.height-side)//2
    im=im.crop((x,y,x+side,y+side)).resize((82,82)); g=ImageOps.grayscale(im); g=ImageEnhance.Contrast(g).enhance(1.35); g=g.filter(ImageFilter.UnsharpMask(radius=1,percent=150,threshold=2)); p=g.load(); pts=set()
    for yy in range(82):
        for xx in range(82):
            keep=p[xx,yy]>=112 if theme=='dark' else p[xx,yy]<150
            if keep and (xx*7+yy*11)%5: pts.add((xx,yy))
    return to_runs(pts)

def to_runs(pts):
    out=[]
    for y in range(82):
        xs=sorted(x for x,py in pts if py==y); i=0
        while i<len(xs):
            x0=xs[i]; x1=x0; i+=1
            while i<len(xs) and xs[i]<=x1+1:x1=xs[i];i+=1
            out.append((x0,x1,y))
    return out

def fallback(user):
    seed=hashlib.sha256(user.encode()).digest(); pts=set()
    for y in range(82):
        for x in range(82):
            h=(16<=x<=23) or (56<=x<=63) or (34<=y<=42 and 16<=x<=63); m=(24<=x<=30) or (51<=x<=57)
            if (h or m) and seed[(x+y)%len(seed)]%7: pts.add((x,y))
    return to_runs(pts)

def render(theme,user,runs):
    c=THEMES[theme]; scale=3.15; px,py=72,132
    d=''.join(f'M{px+x0*scale:.1f} {py+y*scale:.1f}h{max(1.3,(x1-x0+1)*scale-.8):.1f}' for x0,x1,y in runs)
    rows=[]; y=150
    for label,value in ROWS:
        rows.append(f'<text x="515" y="{y}" fill="{c["muted"]}" font-size="11" letter-spacing="1.8">{html.escape(label)}</text><line x1="610" y1="{y-4}" x2="738" y2="{y-4}" stroke="{c["line"]}" stroke-dasharray="2 7"/><text x="1110" y="{y}" text-anchor="end" fill="{c["text"]}" font-size="15">{html.escape(value)}</text>'); y+=44
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="500" viewBox="0 0 1180 500" role="img" aria-label="Hesham Mohamed profile"><defs><clipPath id="p"><rect x="58" y="116" width="286" height="286"/></clipPath><clipPath id="r"><rect x="58" y="116" width="286" height="0"><animate attributeName="height" from="0" to="286" dur="1.6s" fill="freeze"/></rect></clipPath></defs><rect width="1180" height="500" rx="18" fill="{c['bg']}"/><rect x="14" y="14" width="1152" height="472" rx="14" fill="{c['panel']}" stroke="{c['line']}"/><line x1="14" y1="70" x2="1166" y2="70" stroke="{c['line']}"/><circle cx="42" cy="42" r="5" fill="{c['accent']}"/><circle cx="61" cy="42" r="5" fill="{c['muted']}" opacity=".45"/><circle cx="80" cy="42" r="5" fill="{c['muted']}" opacity=".25"/><text x="102" y="47" fill="{c['muted']}" font-family="ui-monospace,Consolas,monospace" font-size="12">hesham.profile / live</text><circle cx="1030" cy="42" r="4" fill="{c['accent']}"><animate attributeName="opacity" values="1;.25;1" dur="2.6s" repeatCount="indefinite"/></circle><text x="1044" y="47" fill="{c['muted']}" font-family="ui-monospace,Consolas,monospace" font-size="11">CAIRO · UTC+03</text><rect x="48" y="102" width="306" height="326" rx="8" fill="{c['soft']}" stroke="{c['line']}"/><text x="64" y="126" fill="{c['muted']}" font-family="ui-monospace,Consolas,monospace" font-size="10">PORTRAIT / MONO</text><g clip-path="url(#p)"><path d="{d}" fill="none" stroke="{c['dot']}" stroke-width="2.15" clip-path="url(#r)" opacity=".92"/><line x1="58" y1="120" x2="344" y2="120" stroke="{c['accent']}" opacity=".7"><animate attributeName="y1" values="120;400;120" dur="6.5s" repeatCount="indefinite"/><animate attributeName="y2" values="120;400;120" dur="6.5s" repeatCount="indefinite"/><animate attributeName="opacity" values="0;.7;0" dur="6.5s" repeatCount="indefinite"/></line></g><text x="64" y="414" fill="{c['muted']}" font-family="ui-monospace,Consolas,monospace" font-size="9.5">PUBLIC AVATAR · GENERATED LOCALLY</text><text x="514" y="110" fill="{c['muted']}" font-family="ui-monospace,Consolas,monospace" font-size="10">PROFILE.NOTES</text>{''.join(rows)}<line x1="500" y1="418" x2="1110" y2="418" stroke="{c['line']}"/><text x="500" y="446" fill="{c['accent']}" font-family="ui-monospace,Consolas,monospace" font-size="11">● BUILDING IN PUBLIC</text><text x="1110" y="446" text-anchor="end" fill="{c['muted']}" font-family="ui-monospace,Consolas,monospace" font-size="11">@{html.escape(user)}</text></svg>'''

def main():
    p=argparse.ArgumentParser();p.add_argument('--user',default='hishammohamed445');p.add_argument('--out',default='assets');a=p.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    try:data=avatar(a.user)
    except Exception as e:print('avatar fallback:',e);data=None
    for theme in THEMES:
        try:runs=runs_from_avatar(data,theme) if data else fallback(a.user)
        except Exception:runs=fallback(a.user)
        (out/f'hero-{theme}.svg').write_text(render(theme,a.user,runs),encoding='utf-8')
if __name__=='__main__':main()
