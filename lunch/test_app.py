from contextlib import closing
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fastapi.testclient import TestClient
import main


class LunchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / 'lunch.db'
        self.db_patch = patch.object(main, 'DB_PATH', self.path)
        self.db_patch.start()
        self.client = TestClient(main.app)
        self.client.__enter__()

    def tearDown(self):
        self.client.__exit__(None, None, None)
        self.db_patch.stop()
        self.temp.cleanup()

    def test_bilingual_page_without_javascript(self):
        r = self.client.get('/')
        self.assertEqual(r.status_code, 200)
        self.assertIn('오늘 점심,', r.text)
        self.assertIn('Less deciding. More lunching.', r.text)
        self.assertNotIn('<script', r.text)
        self.assertEqual(self.client.get('/static/style.css').status_code, 200)

    def test_all_constraints_are_respected_together(self):
        r = self.client.get('/api/menus?minutes=30&budget=12000&cuisine=western&diet=vegetarian&mild=true&travel=10&wait=5')
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json())
        for menu in r.json():
            self.assertLessEqual(menu['meal_minutes'] + 15, 30)
            self.assertLessEqual(menu['price'], 12000)
            self.assertEqual(menu['cuisine'], 'western')
            self.assertIn(menu['diet'], ['vegan', 'vegetarian'])
            self.assertFalse(menu['spicy'])

    def test_short_break_has_fast_options(self):
        menus = self.client.get('/api/menus?minutes=20&budget=8000').json()
        self.assertTrue(menus)
        self.assertTrue(all(m['meal_minutes'] + 15 <= 20 for m in menus))

    def test_vegan_filter_excludes_egg_and_dairy_options(self):
        menus = self.client.get('/api/menus?diet=vegan').json()
        self.assertTrue(menus)
        self.assertTrue(all(m['diet'] == 'vegan' for m in menus))

    def test_wait_and_round_trip_reduce_available_options(self):
        fast = self.client.get('/api/menus?travel=0&wait=0').json()
        slow = self.client.get('/api/menus?travel=20&wait=15').json()
        self.assertGreater(len(fast), len(slow))
        self.assertEqual(slow, [])

    def test_no_match_keeps_constraints_and_explains(self):
        r = self.client.get('/?minutes=20&travel=20&wait=15&mode=draw')
        self.assertEqual(r.status_code, 200)
        self.assertIn('No matches', r.text)
        self.assertNotIn('class="menu-card', r.text)

    def test_random_draw_matches_filters_and_avoids_previous_when_possible(self):
        prefs = main.Preferences(diet='vegan')
        pool = main.candidates(prefs)
        for _ in range(12):
            selected, count = main.select_menus(prefs, 'draw', pool[0]['id'])
            self.assertEqual(len(selected), 1)
            self.assertEqual(count, len(pool))
            self.assertIn(selected[0], pool)
            self.assertNotEqual(selected[0]['id'], pool[0]['id'])

    def test_random_draw_handles_single_candidate(self):
        prefs = main.Preferences(minutes=20, diet='vegan')
        pool = main.candidates(prefs)
        self.assertEqual(len(pool), 1)
        selected, count = main.select_menus(prefs, 'draw', pool[0]['id'])
        self.assertEqual(selected, pool)

    def test_draw_and_decision_preserve_preferences(self):
        r = self.client.get('/?minutes=20&budget=8000&diet=vegan&mild=true&mode=draw')
        self.assertEqual(r.status_code, 200)
        self.assertIn('운명의 점심', r.text)
        self.assertIn('diet=vegan', r.text)
        self.assertIn('minutes=20', r.text)
        r = self.client.get('/decision/17?minutes=20&budget=8000&diet=vegan')
        self.assertEqual(r.status_code, 200)
        self.assertIn('채소 랩 하나 주세요.', r.text)
        self.assertIn('One Plant-based veggie wrap, please.', r.text)
        self.assertIn('google.com/maps/search/', r.text)

    def test_decision_cannot_bypass_filters(self):
        self.assertEqual(self.client.get('/decision/9?diet=vegan').status_code, 404)
        self.assertEqual(self.client.get('/decision/999').status_code, 404)

    def test_invalid_query_values_return_422(self):
        for query in ['minutes=-1', 'minutes=25', 'minutes=abc', 'budget=10000', 'cuisine=invalid', 'diet=invalid', 'travel=5', 'wait=3', 'mode=invalid', 'avoid=-1']:
            with self.subTest(query=query):
                self.assertEqual(self.client.get('/?' + query).status_code, 422)

    def test_catalog_survives_restart_without_duplicate_tables_or_rows(self):
        main.init_db()
        main.init_db()
        with closing(sqlite3.connect(self.path)) as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM menus').fetchone()[0], 18)
            self.assertEqual(db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall(), [('menus',)])
            self.assertEqual(db.execute('PRAGMA foreign_key_list(menus)').fetchall(), [])
        self.assertEqual(self.client.get('/health').json(), {'status':'ok', 'menus':18})
        self.assertEqual(self.client.get('/docs').status_code, 200)


if __name__ == '__main__':
    unittest.main(verbosity=2)
