# 점심 앱 무료 배포

확인일: 2026-10-23. 로컬에서 구현·검증했으며 외부 호스팅에 공개 배포하지 않았습니다.

## Render Free로 배포

이 앱은 SQLite에 고정 메뉴 18개만 저장하고 서버 시작 때 다시 채웁니다. 사용자 이력을 저장하지 않으므로 Render의 임시 파일 시스템에서도 메뉴 목록을 복원할 수 있습니다. 방명록과 저장 요구가 달라 무료 시연 배포 후보로 적합하다고 판단했습니다.

1. 자신의 GitHub 저장소에 `DAY1-DAY8/lunch`의 소스를 올립니다.
2. Render의 **New → Web Service**에서 저장소를 연결합니다.
3. **Root Directory**: `DAY1-DAY8/lunch`
4. **Build Command**: `pip install -r requirements.txt`
5. **Start Command**: `python -m uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1`
6. **Instance Type**: `Free`
7. **Health Check Path**: `/health`
8. 발급된 `onrender.com` 주소에서 추천·뽑기·주문 문장을 확인합니다.

별도 저장소에 `lunch-deploy.zip` 내용만 올렸다면 Root Directory는 비워 둡니다. 필요한 파일은 `main.py`, `menu_data.py`, `requirements.txt`, `templates`, `static`입니다.

무료 서비스는 15분 유휴 뒤 정지하며 다음 방문 시 다시 시작하는 데 시간이 걸릴 수 있습니다. 재시작·재배포 때 파일은 사라집니다. 이 앱은 시작 시 메뉴를 복원하지만 향후 사용자 기록을 추가한다면 저장 방식을 다시 검토해야 합니다. 무료 서비스 시간을 비롯한 계정 한도는 공식 문서에서 확인하세요. [FastAPI 배포](https://render.com/docs/deploy-fastapi) · [무료 플랜 제약](https://render.com/docs/free)

## alwaysdata Free에서 파일을 유지하며 배포

공식 요금표의 Free는 개인 용도 월 0유로, SSD 1GB·RAM 256MB·CPU ¼를 제공합니다. [요금표](https://www.alwaysdata.com/en/offers/)

1. Free 계정의 Python을 3.13으로 선택합니다.
2. `/home/ACCOUNT/lunch/`에 배포용 ZIP 내용을 풉니다.
3. SSH에서 `python -m venv .venv` 후 `.venv/bin/python -m pip install --no-cache-dir -r requirements.txt`를 실행합니다.
4. **Web → Sites**에서 **User program**을 선택합니다.
5. 작업 폴더는 `/home/ACCOUNT/lunch`, 환경 변수는 `LUNCH_DB_PATH=/home/ACCOUNT/lunch-data/lunch.db`로 설정합니다.
6. 실행 명령: `/home/ACCOUNT/lunch/.venv/bin/python -m uvicorn main:app --host :: --port $PORT --workers 1`
7. 기본 `ACCOUNT.alwaysdata.net` 주소와 HTTPS를 사용합니다.

`ACCOUNT`는 자신의 계정명으로 바꿉니다. [공식 Python·ASGI 안내](https://help.alwaysdata.com/en/docs/web-hosting/languages/python/configuration/)

## 무료 범위에 맞춘 구성

서버 1개, 테이블 1개, 고정 메뉴 18개, 가벼운 HTML/CSS로 구성했습니다. AI 호출·지도 API·사진 저장·자동 확장 비용이 없습니다. 식당 검색은 사용자가 여는 일반 외부 링크입니다. 각 서비스의 계정 전체 사용량과 현재 무료 약관은 가입 시 확인하세요.
