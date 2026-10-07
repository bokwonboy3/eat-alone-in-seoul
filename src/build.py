# -*- coding: utf-8 -*-
# 빌드: page_template.html + rows_final.json + areas.json → ../site/index.html (+ ../eat-alone-in-seoul.html). 체크: 플레이스홀더, JS 문법, 중복 id
import json, re, subprocess, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
rows = json.load(open('rows_final.json', encoding='utf-8')); areas = json.load(open('areas.json', encoding='utf-8'))
assert len(rows) == len({r['id'] for r in rows}), 'duplicate ids'
for r in rows:
    if r['area'] not in areas: areas.append(r['area'])
tpl = open('page_template.html', encoding='utf-8').read()
html = tpl.replace('__DATA__', json.dumps(rows, ensure_ascii=False, separators=(',',':')).replace('</', '<\/')).replace('__AREAS__', json.dumps(areas, ensure_ascii=False))
assert '__DATA__' not in html and '__AREAS__' not in html
open('s.js','w',encoding='utf-8').write(re.search(r'<script>(.*?)</script>', html, re.S).group(1))
p = subprocess.run(['node','--check','s.js'], capture_output=True); assert p.returncode == 0, p.stderr.decode()
open('../site/index.html','w',encoding='utf-8').write(html); open('../eat-alone-in-seoul.html','w',encoding='utf-8').write(html)
print(f"BUILD OK rows {len(rows)} | areas {len(areas)} | {len(html.encode())} bytes")
