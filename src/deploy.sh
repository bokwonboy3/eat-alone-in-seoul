#!/bin/bash
# 사용: bash deploy.sh "message"  (build.py 먼저 실행됨)
set -e
cd "$(dirname "$0")"
python build.py
mkdir -p ../site/src && cp page_template.html rows_final.json areas.json build.py deploy.sh kakao_recheck.py ../site/src/ 2>/dev/null || true
cd ../site
git add -A
git -c user.name="bokwonboy3" -c user.email="jbk092000@gmail.com" commit -m "${1:-update}

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" || echo "nothing to commit"
git push origin HEAD
echo "DEPLOYED: $(git log --oneline -1)"
