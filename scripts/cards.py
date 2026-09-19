#!/usr/bin/env python3
from __future__ import annotations
import argparse, html, json, os, urllib.request
from collections import Counter
from pathlib import Path

THEMES={
 "dark":{"bg":"#111113","line":"#303034","text":"#f3f2ed","muted":"#8b8b91","accent":"#ff3b30"},
 "light":{"bg":"#fffefa","line":"#d8d4ca","text":"#171719","muted":"#6e6b65","accent":"#d92d24"}}

def esc(x):return html.escape(str(x),quote=True)
def api(url,token=None):
    h={'User-Agent':'profile-cards'}
    if token:h['Authorization']=f'Bearer {token}'
    with urllib.request.urlopen(urllib.request.Request(url,headers=h),timeout=20) as r:return json.loads(r.read().decode())
def frame(body,theme,label,w=460,h=160):
    c=THEMES[theme];return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}"><rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="12" fill="{c["bg"]}" stroke="{c["line"]}"/>{body}</svg>'
def project(repo,item,theme):
    c=THEMES[theme];desc=item['description'];words=desc.split();lines=[];cur=''
    for word in words:
        test=(cur+' '+word).strip()
        if len(test)<=62:cur=test
        else:lines.append(cur);cur=word
    if cur:lines.append(cur)
    body=f'<text x="22" y="31" fill="{c["accent"]}" font-family="ui-sans-serif,Segoe UI,Arial" font-size="15" font-weight="700">{esc(repo["name"])}</text><text x="438" y="31" text-anchor="end" fill="{c["muted"]}" font-family="ui-monospace,Consolas,monospace" font-size="9">{esc(item["status"])}</text><line x1="22" y1="46" x2="438" y2="46" stroke="{c["line"]}"/>'
    for i,line in enumerate(lines[:3]):body+=f'<text x="22" y="{70+i*17}" fill="{c["text"]}" font-family="ui-sans-serif,Segoe UI,Arial" font-size="11.5">{esc(line)}</text>'
    body+=f'<text x="22" y="143" fill="{c["muted"]}" font-family="ui-monospace,Consolas,monospace" font-size="9.5">{esc(repo.get("language") or "—")} · ★ {repo.get("stargazers_count",0)} · forks {repo.get("forks_count",0)}</text>'
    return frame(body,theme,repo['name'])
def languages(repos,theme):
    c=THEMES[theme];counts=Counter(r.get('language') for r in repos if r.get('language'));total=sum(counts.values()) or 1
    body=f'<text x="22" y="31" fill="{c["text"]}" font-family="ui-sans-serif,Segoe UI,Arial" font-size="16" font-weight="700">Language signal</text><text x="438" y="31" text-anchor="end" fill="{c["muted"]}" font-family="ui-monospace,Consolas,monospace" font-size="9">SELECTED WORK</text><line x1="22" y1="46" x2="438" y2="46" stroke="{c["line"]}"/>';y=78
    for lang,n in counts.most_common(5):
        pct=n/total;body+=f'<text x="22" y="{y}" fill="{c["muted"]}" font-family="ui-sans-serif,Segoe UI,Arial" font-size="11">{esc(lang)}</text><rect x="118" y="{y-9}" width="285" height="7" rx="3.5" fill="{c["line"]}"/><rect x="118" y="{y-9}" width="{285*pct:.1f}" height="7" rx="3.5" fill="{c["accent"]}"/><text x="438" y="{y}" text-anchor="end" fill="{c["muted"]}" font-family="ui-monospace,Consolas,monospace" font-size="9.5">{n}</text>';y+=22
    return frame(body,theme,'Selected work language signal',h=170)
def summary(repos,items,theme):
    c=THEMES[theme];ci=sum(1 for x in items if x.get('ci'));mit=sum(1 for r in repos if (r.get('license') or {}).get('spdx_id')=='MIT');vals=[('SYSTEMS',len(items)),('WITH CI',ci),('MIT LICENSED',mit)]
    body=f'<text x="22" y="31" fill="{c["text"]}" font-family="ui-sans-serif,Segoe UI,Arial" font-size="16" font-weight="700">Portfolio snapshot</text><text x="438" y="31" text-anchor="end" fill="{c["muted"]}" font-family="ui-monospace,Consolas,monospace" font-size="9">VERIFIED SELECTED WORK</text><line x1="22" y1="46" x2="438" y2="46" stroke="{c["line"]}"/>'
    for i,(lab,val) in enumerate(vals):
        x=22+i*142;body+=f'<text x="{x}" y="94" fill="{c["text"]}" font-family="ui-sans-serif,Segoe UI,Arial" font-size="27" font-weight="700">{val}</text><text x="{x}" y="116" fill="{c["muted"]}" font-family="ui-monospace,Consolas,monospace" font-size="9.5">{lab}</text>'
    body+=f'<text x="22" y="143" fill="{c["accent"]}" font-family="ui-monospace,Consolas,monospace" font-size="10">SELF-HOSTED · NO PUBLIC CARD SERVICE</text>';return frame(body,theme,'Portfolio snapshot')
def main():
    p=argparse.ArgumentParser();p.add_argument('--user',default='hishammohamed445');p.add_argument('--projects',default='assets/projects.json');p.add_argument('--out',default='assets');a=p.parse_args();items=json.loads(Path(a.projects).read_text())['projects'];token=os.environ.get('GITHUB_TOKEN');repos=[]
    for item in items:
        cached={'name':item['repo'],'language':item.get('language'),'stargazers_count':item.get('stars',0),'forks_count':item.get('forks',0),'license':({'spdx_id':item['license']} if item.get('license') else None)}
        try:repo=api(f'https://api.github.com/repos/{a.user}/{item["repo"]}',token)
        except Exception as e:print('cached metadata:',item['repo'],e);repo=cached
        repos.append(repo)
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    for theme in THEMES:
        (out/f'card-summary-{theme}.svg').write_text(summary(repos,items,theme),encoding='utf-8');(out/f'card-languages-{theme}.svg').write_text(languages(repos,theme),encoding='utf-8')
        for repo,item in zip(repos,items):(out/f'card-{item["slug"]}-{theme}.svg').write_text(project(repo,item,theme),encoding='utf-8')
if __name__=='__main__':main()
