# Lunch Break · 오늘 점심, 고민은 짧게

짧은 점심시간에 메뉴를 빠르게 정하는 한영 추천 앱입니다. 파스텔 민트·라벤더·피치 화면에 한국어와 영어를 함께 표시합니다. `DAY1-DAY8/Codex.md`의 구현 규칙을 사용하고, 목적은 이번 요청에 따라 점심 추천으로 바꿨습니다.

## 현재 AI4에서 실행

```powershell
cd C:\AI4\DAY1-DAY8\lunch
.\run.cmd
```

- 화면: <http://127.0.0.1:8010>
- API: <http://127.0.0.1:8010/docs>
- 상태: <http://127.0.0.1:8010/health>
- 종료: 실행한 터미널에서 Ctrl+C

실행 파일은 이 폴더의 `.venv`를 먼저 찾고, 없으면 기존 `DAY7/sync_async_shop/.runtime/python`을 사용합니다. 기존 루트 `.venv`를 수정하거나 새 라이브러리를 설치하지 않았습니다.

## 사용 흐름

1. 남은 시간(20/30/45/60분), 예산(8,000/12,000/16,000/20,000원)을 선택합니다.
2. 음식 종류, 채식 취향, 매운맛 선호를 선택합니다.
3. **빠르게 추천받기 / Quick picks**로 빠른 후보 3개를 보거나 **Surprise me!**로 하나를 뽑습니다.
4. **이걸로 할래요 / Choose this**를 누르면 결정한 메뉴와 한국어 주문 문장을 봅니다.
5. **식당 검색 / Find restaurants**로 외부 Google Maps 검색을 열 수 있습니다. 위치 권한이나 API 키는 요구하지 않습니다.

기본 계산은 **식사 예상 시간 + 왕복 이동 10분 + 대기 5분**입니다. `이동·대기 시간 조정 / Travel & wait`에서 값을 바꿀 수 있습니다. 전부 더한 시간이 남은 점심시간 안에 들어오는 후보만 보여 줍니다.

가격·시간·재료는 교육용 참고값입니다. 실제 식당의 메뉴·가격·영업시간·대기를 조회하는 서비스가 아닙니다. 채식 메뉴는 지정한 재료·소스로 준비해 달라고 주문하는 선택지이며, 육수·소스·알레르기 재료는 식당에 확인해야 합니다.

다시 뽑을 때 조건을 유지하고, 다른 후보가 있으면 직전 메뉴를 제외합니다. 후보가 하나면 같은 메뉴가 나올 수 있습니다. 맞는 후보가 없으면 조건을 바꾸라는 안내를 표시합니다.

## 기술과 학습 자료

| AI4 자료 | 활용 |
|---|---|
| Day1 `python_basics_practice.py` | 함수·조건문·반복문·f-string·random |
| Day2 사전·리스트 실습 | 메뉴 데이터, 조건별 후보 처리 |
| DAY3 클래스·타입 힌트 | 입력 모델과 함수 분리 |
| DAY4 리스트 컴프리헨션 실습 | DB 행을 목록으로 변환 |
| DAY6 `ch08_project/models.py` | Pydantic 모델과 검증 |
| DAY7 `sync_async_shop/app.py` | FastAPI, StaticFiles, 일반 def 경로 |
| Day8 `lesson_02_parameters`, 응답 모델·검증 실습 | Query/Depends, 타입·허용값 검증, API 문서, TestClient |

현재 AI4에는 Day5 폴더가 없습니다. 기존 실습 파일을 직접 import하지 않고 배운 문법을 적용했습니다. 새로운 추천 알고리즘 대신 SQL 조건 필터링·시간/가격 정렬과 기존 Day1의 `random.choice`를 사용합니다.

- 화면: HTML + CSS, 추가 JavaScript 없음.
- 서버: 기존 FastAPI·Pydantic·Uvicorn 버전 유지.
- DB: Python 내장 SQLite, `menus` 테이블 하나, 외래 키 없음.
- 외부 유료 API·프런트엔드 빌드·이미지 업로드 없음.
- 메뉴 18개를 첫 실행에 넣고 중복 초기화를 방지합니다.
- 사용자의 개인 정보와 선택 이력은 수집하지 않습니다.

## 파일

```text
lunch/
├── main.py                 # 필터, 추천, HTML, API, SQLite
├── menu_data.py            # 한영 메뉴 18개와 참고값
├── templates/index.html    # 한영 화면
├── static/style.css        # 파스텔·반응형 디자인
├── run.cmd                 # 현재 AI4 실행
├── requirements.txt        # 기존 서버 패키지
├── test_app.py             # 12개 기능 검사
├── README.md
├── DEPLOY.md
├── VERIFICATION.md
├── lunch-deploy.zip        # 배포용 파일 묶음
└── data/lunch.db           # 최초 실행 생성, Git 제외
```

DB 파일 위치는 `LUNCH_DB_PATH`로 지정할 수 있습니다. 상대 경로는 이 앱 폴더 기준입니다. SQLite는 방명록의 DB와 별개 파일을 사용합니다.

## 다른 PC에서 설치

Python 3.13 설치 후 PowerShell에서 실행합니다.

```powershell
cd C:\AI4\DAY1-DAY8\lunch
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\run.cmd
```

## 검사

현재 AI4에서는 기존 Day7의 Python으로 검사합니다.

```powershell
..\..\DAY7\sync_async_shop\.runtime\python\python.exe test_app.py
```

다른 환경에서는 기존 Day8에서 사용하는 `httpx==0.28.1`을 개발 환경에 설치한 뒤 `python test_app.py`를 실행합니다. unittest는 Python 내장 모듈입니다. 테스트는 임시 DB를 사용합니다. [검증 결과](VERIFICATION.md) · [무료 배포 안내](DEPLOY.md)
