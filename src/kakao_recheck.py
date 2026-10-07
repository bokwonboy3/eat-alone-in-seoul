# -*- coding: utf-8 -*-
# 폐업 재점검 (카카오맵 검색, 무료·차단 없음): 각 행의 한글명으로 검색 → 이름 유사도 + 좌표 300m 이내 매칭 → openoff_status != 'Y' 면 기록.
# 출력 closed_recheck.json. 재개 가능. 사용: python kakao_recheck.py
import json, re, subprocess, time, random, urllib.parse, sys, io, os, difflib, math
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36"
def search(q):
    r = subprocess.run(["curl","-s","--max-time","15","-A",UA,"-H","Referer: https://map.kakao.com/","https://search.map.kakao.com/mapsearch/map.daum?q="+urllib.parse.quote(q)+"&msFlag=A&sort=0"], capture_output=True)
    try: return json.loads(r.stdout.decode('utf-8','replace'))
    except: return None
def core(n): return re.sub(r'\s*(본점|직영점|\d호점|[가-힣A-Za-z0-9]+점)\s*$', '', n).replace(' ','')
def sim(a, b): return difflib.SequenceMatcher(None, core(a), core(b)).ratio()
def km(lat1, lng1, lat2, lng2): return math.hypot((lat1-lat2)*111, (lng1-lng2)*88)
rows = json.load(open('rows_final.json', encoding='utf-8'))
R = json.load(open('closed_recheck.json', encoding='utf-8')) if os.path.exists('closed_recheck.json') else {}
n = 0; t0 = time.time()
for r in rows:
    if r['id'] in R: continue
    j = search(r.get('q') or r['ko']); n += 1
    hit = None
    for p in ((j or {}).get('place') or [])[:8]:
        try: plat, plng = float(p.get('lat') or 0), float(p.get('lon') or p.get('lng') or 0)
        except: plat = plng = 0
        near = bool(r.get('lat')) and plat and km(r['lat'], r['lng'], plat, plng) <= 0.3
        s = sim(r['ko'], p.get('name') or '')
        if (near and s >= 0.5) or (not r.get('lat') and s >= 0.8): hit = p; break
    R[r['id']] = {"ko": r['ko'], "kname": hit.get('name') if hit else None, "status": hit.get('openoff_status') if hit else None, "sim": round(sim(r['ko'], hit.get('name')), 2) if hit else None}
    if hit and hit.get('openoff_status') not in ('Y', None): print(f"NOT OPEN  {r['ko']} → {hit.get('name')} status={hit.get('openoff_status')}", flush=True)
    if n % 50 == 0:
        json.dump(R, open('closed_recheck.json','w',encoding='utf-8'), ensure_ascii=False); print(f"... {n} ({int(time.time()-t0)}s)", flush=True)
    time.sleep(random.uniform(0.7, 1.2))
json.dump(R, open('closed_recheck.json','w',encoding='utf-8'), ensure_ascii=False)
closed = [v for v in R.values() if v['status'] not in ('Y', None)]
print(f"RECHECK DONE: {len(R)} rows | matched {sum(1 for v in R.values() if v['kname'])} | not open {len(closed)}", flush=True)
for v in closed: print("  -", v['ko'], '→', v['kname'], v['status'])
