"""Lunch Break: 기존 Python/FastAPI + HTML/CSS + 단일 SQLite 테이블."""

from contextlib import asynccontextmanager, closing
from html import escape
from pathlib import Path
import os
import random
import sqlite3
from string import Template
from typing import Annotated, Literal
from urllib.parse import urlencode

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ValidationError

from menu_data import MENUS

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get('LUNCH_DB_PATH', str(BASE_DIR / 'data' / 'lunch.db')))
if not DB_PATH.is_absolute():
    DB_PATH = BASE_DIR / DB_PATH
TEMPLATE = Template((BASE_DIR / 'templates' / 'index.html').read_text(encoding='utf-8'))
CUISINES = {'all': '모두 · All', 'korean': '한식 · Korean', 'japanese': '일식 · Japanese', 'western': '양식 · Western', 'asian': '아시안 · Asian'}
DIETS = {'any': '모두 괜찮아요 · Any', 'vegetarian': '채식 (달걀·유제품 가능) · Vegetarian', 'vegan': '완전 채식 요청 · Plant-based'}


class Preferences(BaseModel):
    minutes: Literal[20, 30, 45, 60] = 30
    budget: Literal[8000, 12000, 16000, 20000] = 12000
    cuisine: Literal['all', 'korean', 'japanese', 'western', 'asian'] = 'all'
    diet: Literal['any', 'vegetarian', 'vegan'] = 'any'
    mild: bool = False
    travel: Literal[0, 10, 20] = 10
    wait: Literal[0, 5, 10, 15] = 5


class MenuOut(BaseModel):
    id: int
    ko: str
    en: str
    cuisine: str
    meal_minutes: int
    price: int
    diet: str
    spicy: bool
    emoji: str
    description_ko: str
    description_en: str


def preferences(
    minutes: Annotated[int, Query(ge=20, le=60)] = 30,
    budget: Annotated[int, Query(ge=8000, le=20000)] = 12000,
    cuisine: Literal['all', 'korean', 'japanese', 'western', 'asian'] = 'all',
    diet: Literal['any', 'vegetarian', 'vegan'] = 'any', mild: bool = False,
    travel: Annotated[int, Query(ge=0, le=20)] = 10,
    wait: Annotated[int, Query(ge=0, le=15)] = 5,
) -> Preferences:
    values = locals()
    try:
        return Preferences(**values)
    except ValidationError as exc:
        raise HTTPException(422, detail=exc.errors()) from None


def connect():
    connection = sqlite3.connect(DB_PATH, timeout=5)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with closing(connect()) as db, db:
        db.execute('''CREATE TABLE IF NOT EXISTS menus (
            id INTEGER PRIMARY KEY, ko TEXT NOT NULL, en TEXT NOT NULL,
            cuisine TEXT NOT NULL, meal_minutes INTEGER NOT NULL,
            price INTEGER NOT NULL, diet TEXT NOT NULL, spicy INTEGER NOT NULL,
            emoji TEXT NOT NULL, description_ko TEXT NOT NULL, description_en TEXT NOT NULL
        )''')
        db.executemany('INSERT OR IGNORE INTO menus VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', MENUS)


def candidates(p: Preferences):
    # Day2의 조건과 Day8의 검증: 모든 조건을 먼저 만족한 뒤 추천합니다.
    sql = 'SELECT * FROM menus WHERE price <= ? AND meal_minutes + ? + ? <= ?'
    args = [p.budget, p.travel, p.wait, p.minutes]
    if p.cuisine != 'all':
        sql += ' AND cuisine = ?'
        args.append(p.cuisine)
    if p.diet == 'vegetarian':
        sql += " AND diet IN ('vegetarian', 'vegan')"
    elif p.diet == 'vegan':
        sql += " AND diet = 'vegan'"
    if p.mild:
        sql += ' AND spicy = 0'
    sql += ' ORDER BY meal_minutes, price, id'
    with closing(connect()) as db:
        return [dict(row) for row in db.execute(sql, args).fetchall()]


def select_menus(p, mode, avoid=0):
    pool = candidates(p)
    if mode == 'draw' and pool:
        # Day1에서 사용한 random. 직전 메뉴는 다른 후보가 있을 때 제외합니다.
        fresh = [menu for menu in pool if menu['id'] != avoid]
        return [random.choice(fresh or pool)], len(pool)
    return pool[:3], len(pool)


def options(values, selected):
    return ''.join(f'<option value="{escape(str(key))}" {"selected" if key == selected else ""}>{escape(str(label))}</option>' for key, label in values.items())


def menu_card(menu, p, index=0, decided=False):
    total = menu['meal_minutes'] + p.travel + p.wait
    remaining = p.minutes - total
    query = urlencode(p.model_dump())
    tag = '🌶 매콤해요 · Spicy' if menu['spicy'] else '순한 맛 · Mild'
    if menu['diet'] != 'any':
        tag += ' · ' + ('Plant-based option' if menu['diet'] == 'vegan' else 'Vegetarian option')
    action = (
        f'<a class="choose" href="/decision/{menu["id"]}?{query}#results">이걸로 할래요 <span>Choose this ↗</span></a>'
        if not decided else '<div class="decided-label">✓ 오늘 점심 결정! · Lunch, sorted.</div>'
    )
    return f'''<article class="menu-card tone-{index % 3}">
      <div class="food-art"><span aria-hidden="true">{escape(menu['emoji'])}</span><span class="food-type">{escape(CUISINES[menu['cuisine']])}</span></div>
      <div class="card-body"><p class="taste">{escape(tag)}</p>
      <h3>{escape(menu['ko'])}</h3><p class="english-name" lang="en">{escape(menu['en'])}</p>
      <p class="description">{escape(menu['description_ko'])}<span lang="en">{escape(menu['description_en'])}</span></p>
      <div class="menu-facts"><span>약 <b>{total}분</b><small>Est. total</small></span><span>약 <b>₩{menu['price']:,}</b><small>Est. price</small></span></div>
      <p class="time-breakdown">식사 {menu['meal_minutes']} + 왕복 {p.travel} + 대기 {p.wait}분<br><span lang="en">Meal + round trip + wait · {remaining} min to spare</span></p>
      {action}</div></article>'''


def render(p, mode='quick', avoid=0, decision=None):
    selected, count = select_menus(p, mode, avoid)
    if decision is not None:
        selected = [menu for menu in candidates(p) if menu['id'] == decision]
        if not selected:
            raise HTTPException(404, '조건에 맞는 메뉴가 없습니다. No matching menu.')
    title = '오늘 점심, 이걸로!'
    subtitle = 'Your lunch is sorted. Enjoy your break.'
    if decision is None:
        title = '운명의 점심이 나왔어요!' if mode == 'draw' else '가볍게 골라 본 오늘의 점심'
        subtitle = 'Your lucky lunch pick.' if mode == 'draw' else 'Quick picks for your lunch break.'
    cards = ''.join(menu_card(menu, p, i, decision is not None) for i, menu in enumerate(selected))
    if not selected:
        cards = '<div class="empty"><span aria-hidden="true">🥣</span><h3>딱 맞는 메뉴를 찾지 못했어요.</h3><p lang="en">No matches for these preferences.</p><p>시간·예산을 늘리거나 식사 종류를 바꿔 보세요.<br>Try more time, a higher budget, or another cuisine.</p></div>'
    extra = ''
    if decision is not None:
        menu = selected[0]
        phrase = f'{menu["ko"]} 하나 주세요.'
        extra = f'''<aside class="order-help"><p class="eyebrow">READY TO ORDER</p><h3>이 문장을 보여 주세요 <span>Show this when ordering</span></h3><p class="order-phrase">{escape(phrase)}</p><p lang="en">One {escape(menu['en'])}, please.</p><a class="map-link" href="https://www.google.com/maps/search/?{urlencode({'api': 1, 'query': menu['ko']})}" target="_blank" rel="noopener noreferrer">식당 검색 · Find restaurants ↗</a><p class="small-note">검색 결과에서 위치·영업시간·실제 가격을 확인하세요.<br>Check location, opening hours and actual prices in search results.</p></aside>'''
    current_id = selected[0]['id'] if selected else 0
    retry = urlencode({**p.model_dump(), 'mode': 'draw', 'avoid': current_id})
    html = TEMPLATE.substitute(
        minutes=options({20:'20분 · min', 30:'30분 · min',45:'45분 · min',60:'60분 · min'}, p.minutes),
        budget=options({8000:'₩8,000',12000:'₩12,000',16000:'₩16,000',20000:'₩20,000'}, p.budget),
        cuisine=options(CUISINES, p.cuisine), diet=options(DIETS, p.diet),
        travel=options({0:'0분 · min',10:'10분 · min',20:'20분 · min'},p.travel),
        wait=options({0:'0분 · min',5:'5분 · min',10:'10분 · min',15:'15분 · min'},p.wait),
        mild='checked' if p.mild else '', title=title, subtitle=subtitle,
        cards=cards, extra=extra, count=count, retry=escape('/?' + retry + '#results'),
        result_class='single-result' if len(selected) == 1 else '',
    )
    return HTMLResponse(html, headers={'Cache-Control':'no-store','X-Content-Type-Options':'nosniff',
        'Content-Security-Policy':"default-src 'none'; style-src 'self'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'"})


@asynccontextmanager
async def lifespan(app):
    init_db()
    yield


app = FastAPI(title='Lunch Break · 오늘의 점심', version='1.0.0', lifespan=lifespan)
app.mount('/static', StaticFiles(directory=BASE_DIR / 'static'), name='static')


@app.get('/', response_class=HTMLResponse, include_in_schema=False)
def home(p: Annotated[Preferences, Depends(preferences)], mode: Literal['quick','draw']='quick', avoid: Annotated[int, Query(ge=0)]=0):
    return render(p, mode, avoid)


@app.get('/decision/{menu_id}', response_class=HTMLResponse, include_in_schema=False)
def decision(menu_id: int, p: Annotated[Preferences, Depends(preferences)]):
    return render(p, decision=menu_id)


@app.get('/api/menus', response_model=list[MenuOut], summary='조건에 맞는 전체 메뉴 · Matching menus')
def matching_menus(p: Annotated[Preferences, Depends(preferences)]):
    return candidates(p)


@app.get('/health')
def health():
    with closing(connect()) as db:
        count = db.execute('SELECT COUNT(*) FROM menus').fetchone()[0]
    return {'status':'ok', 'menus':count}
