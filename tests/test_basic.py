import unittest
from app import create_app, db
from app.models import Team, Match, Prediction
from flask import url_for

class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_home(self):
        print("Running test_home...")
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        print("test_home passed.")

    def test_get_teams_empty(self):
        print("Running test_get_teams_empty...")
        resp = self.client.get('/api/v1/teams')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('teams', resp.get_json())
        self.assertEqual(len(resp.get_json()['teams']), 0)
        print("test_get_teams_empty passed.")

    def test_add_and_search_team(self):
        print("Running test_add_and_search_team...")
        with self.app.app_context():
            team = Team(name="Chelsea", logo_url="logo.png", stadium="Stamford Bridge")
            db.session.add(team)
            db.session.commit()
        resp = self.client.get('/api/v1/teams?search=Chelsea')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(any(t['name'] == 'Chelsea' for t in data['teams']))
        print("test_add_and_search_team passed.")

    def test_add_team_search_api(self):
        print("Running test_add_team_search_api...")
        resp = self.client.post('/api/v1/teams/search', json={'team_name': 'Chelsea'})
        self.assertIn(resp.status_code, [200, 409, 404, 400])
        print("test_add_team_search_api passed.")

    def test_toggle_favourite(self):
        print("Running test_toggle_favourite...")
        with self.app.app_context():
            team = Team(name="TestTeam")
            db.session.add(team)
            db.session.commit()
            team_id = team.id
        resp = self.client.post(f'/api/v1/teams/{team_id}/favourite')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('favourite', resp.get_json())
        resp2 = self.client.post(f'/api/v1/teams/{team_id}/favourite')
        self.assertEqual(resp2.status_code, 200)
        self.assertNotEqual(resp.get_json()['favourite'], resp2.get_json()['favourite'])
        print("test_toggle_favourite passed.")

    def test_get_matches_empty(self):
        print("Running test_get_matches_empty...")
        resp = self.client.get('/api/v1/matches')
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.get_json(), list)
        self.assertEqual(len(resp.get_json()), 0)
        print("test_get_matches_empty passed.")

    def test_add_and_get_match(self):
        print("Running test_add_and_get_match...")
        with self.app.app_context():
            t1 = Team(name="A")
            t2 = Team(name="B")
            db.session.add_all([t1, t2])
            db.session.commit()
            match = Match(home_team_id=t1.id, away_team_id=t2.id, date="2025-01-01")
            db.session.add(match)
            db.session.commit()
            match_id = match.id
        resp = self.client.get('/api/v1/matches')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(any(m['id'] == match_id for m in resp.get_json()))
        print("test_add_and_get_match passed.")

    def test_team_matches_endpoint(self):
        print("Running test_team_matches_endpoint...")
        with self.app.app_context():
            t1 = Team(name="C")
            t2 = Team(name="D")
            db.session.add_all([t1, t2])
            db.session.commit()
            match = Match(home_team_id=t1.id, away_team_id=t2.id, date="2025-01-02")
            db.session.add(match)
            db.session.commit()
            t1_id = t1.id  # Store id before leaving context
        resp = self.client.get(f'/api/v1/teams/{t1_id}/matches')
        self.assertEqual(resp.status_code, 200)
        matches = resp.get_json()
        self.assertTrue(any(m['home_team'] == 'C' for m in matches))
        print("test_team_matches_endpoint passed.")

    def test_add_prediction_and_get(self):
        print("Running test_add_prediction_and_get...")
        with self.app.app_context():
            t1 = Team(name="E")
            t2 = Team(name="F")
            db.session.add_all([t1, t2])
            db.session.commit()
            match = Match(home_team_id=t1.id, away_team_id=t2.id, date="2025-01-03")
            db.session.add(match)
            db.session.commit()
            match_id = match.id
        resp = self.client.post('/api/v1/predictions', json={'match_id': match_id, 'home_score': 2, 'away_score': 1})
        self.assertEqual(resp.status_code, 200)
        self.assertIn('success', resp.get_json())
        resp2 = self.client.get('/api/v1/predictions')
        self.assertEqual(resp2.status_code, 200)
        preds = resp2.get_json()
        self.assertTrue(any(p['match_id'] == match_id for p in preds))
        for p in preds:
            self.assertIn('home_team', p)
            self.assertIn('away_team', p)
            self.assertIn('date', p)
            self.assertIn('predicted_result', p)
            self.assertIn('actual_result', p)
            self.assertIn('correct', p)
        print("test_add_prediction_and_get passed.")

    def test_relevant_matches(self):
        print("Running test_relevant_matches...")
        with self.app.app_context():
            t1 = Team(name="G")
            t2 = Team(name="H")
            db.session.add_all([t1, t2])
            db.session.commit()
            match = Match(home_team_id=t1.id, away_team_id=t2.id, date="2025-01-04")
            db.session.add(match)
            db.session.commit()
        resp = self.client.get('/api/v1/matches/relevant')
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.get_json(), list)
        print("test_relevant_matches passed.")

    def test_add_team_search_missing_name(self):
        print("Running test_add_team_search_missing_name...")
        resp = self.client.post('/api/v1/teams/search', json={})
        self.assertEqual(resp.status_code, 400)
        self.assertIn('error', resp.get_json())
        print("test_add_team_search_missing_name passed.")

    def test_add_prediction_invalid_match(self):
        print("Running test_add_prediction_invalid_match...")
        resp = self.client.post('/api/v1/predictions', json={'match_id': 9999, 'home_score': 1, 'away_score': 1})
        self.assertEqual(resp.status_code, 400)
        print("test_add_prediction_invalid_match passed.")

    def test_scrape_matches_invalid_team(self):
        print("Running test_scrape_matches_invalid_team...")
        resp = self.client.post('/api/v1/matches/scrape', json={'team_name': 'NonExistentTeamXYZ'})
        self.assertIn(resp.status_code, [200, 400, 404])
        print("test_scrape_matches_invalid_team passed.")

if __name__ == '__main__':
    unittest.main() 