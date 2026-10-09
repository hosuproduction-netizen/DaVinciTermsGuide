#!/usr/bin/env python3
"""다빈치 가이드 정적 사이트 빌더.

사용법: python3 scripts/build.py
배포용: SITE_URL=https://example.com/davinci-guide/ python3 scripts/build.py
"""
from __future__ import annotations
import json
import os
import html
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse
from datetime import date
from jinja2 import Environment, FileSystemLoader, select_autoescape, StrictUndefined

BASE = Path(__file__).resolve().parents[1]
DATA_FILE = BASE / 'content' / 'features.json'
ENV = Environment(loader=FileSystemLoader(str(BASE / 'templates')), autoescape=select_autoescape(['html']), undefined=StrictUndefined)
CATEGORIES=['기본 편집','영상 효과','자막·그래픽','색보정','오디오','내보내기']
SITE_URL=os.environ.get('SITE_URL','').strip()
if SITE_URL:
    parsed=urlparse(SITE_URL)
    if parsed.scheme not in ('https','http') or not parsed.netloc:
        raise SystemExit('SITE_URL은 https://도메인/경로/ 형식이어야 합니다.')
    SITE_URL = SITE_URL.rstrip('/') + '/'

raw=json.loads(DATA_FILE.read_text(encoding='utf-8'))
features=raw['features']
programs=raw['programs']
slug_map={f['slug']:f for f in features}
assert len(slug_map)==len(features),'중복 기능 slug'
assert len({p['slug'] for p in programs})==4,'프로그램 4개 필요'
for i,p in enumerate(programs,1):p['index']=i
for f in features:
    if any(p['slug'] not in f['maps'] for p in programs):
        raise ValueError(f'프로그램 대응 자료 없음: {f["slug"]}')
    if f['category'] not in CATEGORIES: raise ValueError(f'알 수 없는 카테고리: {f["category"]}')
    if len(f['steps'])<2: raise ValueError(f'단계 설명 누락: {f["slug"]}')
    if not re.fullmatch('[a-z0-9-]+',f['slug']):raise ValueError(f'URL slug 오류: {f["slug"]}')

sorted_features=sorted(features,key=lambda f: (CATEGORIES.index(f['category']),f['title']))
paths=[]
def render(output_path,template,rel_url,title,description,root,nav,body='',**kwargs):
    canonical=urljoin(SITE_URL,rel_url) if SITE_URL else None
    jsonld=None
    if canonical:
        if rel_url=='':
            jsonld={'@context':'https://schema.org','@type':'WebSite','name':'다빈치 가이드','url':canonical,'description':description,'inLanguage':'ko-KR'}
        else:
            jsonld={'@context':'https://schema.org','@type':'WebPage','name':title,'url':canonical,'description':description,'inLanguage':'ko-KR','isPartOf':{'@type':'WebSite','name':'다빈치 가이드','url':SITE_URL}}
    page=ENV.get_template(template).render(page_title=title,meta_description=description,canonical=canonical,jsonld=jsonld,root=root,active_nav=nav,body_class=body,programs=programs,feature_count=len(features),categories=CATEGORIES,**kwargs)
    dest=BASE/output_path
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(page,encoding='utf-8')
    paths.append(rel_url)
    print('  +',output_path)

popular_slugs=['zoom','adjustment-clip','auto-subtitles','color-primary','normalize-audio','retime-curve']
render('index.html','home.html','','다빈치 가이드 | 편집은 익숙하게, 다빈치는 새롭게','프리미어 프로, 캡컷, 파이널 컷 프로, 블로 사용자라면? 기존 편집 기능을 다빈치 리졸브(DaVinci Resolve)에서 바로 찾아보세요.','', 'programs',body='is-home', popular=[slug_map[s] for s in popular_slugs])
render('dictionary/index.html','dictionary.html','dictionary/','다빈치 기능 사전 | 영상 편집 기능 47개 검색 | 다빈치 가이드','다빈치 리졸브 21.1 기능별 위치와 사용법. Zoom, Text+, 색보정, 오디오 정규화 등 47개 기능을 한글·영문으로 검색하세요.','../','dictionary',body='is-dictionary',features=sorted_features)
for p in programs:
    render(f'programs/{p["slug"]}/index.html','program.html',f'programs/{p["slug"]}/',f'{p["name"]}에서 다빈치로 | 기능·용어 비교 | 다빈치 가이드',f'{p["name"]}에서 익숙한 편집 기능 47개를 다빈치 리졸브의 기능명, 메뉴 위치, 사용법과 비교하세요.','../../','programs',body=f'program-{p["slug"]}',program=p,features=sorted_features)
for f in features:
    related=[]
    for slug in f['related']:
        if slug in slug_map and slug!=f['slug'] and slug_map[slug] not in related: related.append(slug_map[slug])
    for other in sorted_features:
        if len(related)>=3: break
        if other['category']==f['category'] and other['slug']!=f['slug'] and other not in related: related.append(other)
    render(f'features/{f["slug"]}/index.html','feature.html',f'features/{f["slug"]}/',f'{f["title"]} | 다빈치 리졸브 {f["resolve"]} 사용법 | 다빈치 가이드',f'{f["title"]}: 다빈치 리졸브 {f["resolve"]} 기능의 위치는 {f["location"]}. 프리미어·캡컷·파이널컷·블로 용어 비교와 단계별 사용법.','../../','dictionary',body='is-feature',feature=f,related=related)

# 오프라인(file://)에서 검색까지 동작하도록 데이터를 JavaScript로 제공합니다.
(BASE/'assets'/'data.js').write_text('/* Generated from content/features.json */\nwindow.DG_DATA = '+json.dumps({'programs':programs,'features':features},ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
(BASE/'robots.txt').write_text('User-agent: *\nAllow: /\n'+(f'Sitemap: {urljoin(SITE_URL,"sitemap.xml")}\n' if SITE_URL else ''),encoding='utf-8')
if SITE_URL:
    lines=['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for path in paths: lines.append(f'  <url><loc>{html.escape(urljoin(SITE_URL,path),quote=False)}</loc><lastmod>{date.today().isoformat()}</lastmod></url>')
    lines.append('</urlset>')
    (BASE/'sitemap.xml').write_text('\n'.join(lines)+'\n',encoding='utf-8')
else:
    (BASE/'sitemap.xml').unlink(missing_ok=True)
print(f'\n완료: {len(paths)} 페이지 / {len(features)}개 기능 / {len(programs)}개 프로그램')
if not SITE_URL: print('검색엔진 등록 전 SITE_URL을 지정해 다시 빌드하면 sitemap.xml 및 canonical 태그가 생성됩니다.')
