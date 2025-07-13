import unittest
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, Team, Match, League
from werkzeug.security import generate_password_hash

class MatchesAPITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(testing=True)
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            self.setup_test_data()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def setup_test_data(self):
        """Setup test data for all tests"""
        # Create test user
        user = User(username='testuser', password_hash='hash')
        db.session.add(user)
        db.session.commit()
        self.user_id = user.id
        
        # Create test league
        league = League(id=1, name='Premier League')
        db.session.add(league)
        db.session.commit()
        
        # Create test teams
        teams = [
            Team(id=1, name='Chelsea', league_id=1),
            Team(id=2, name='Arsenal', league_id=1),
            Team(id=3, name='Manchester United', league_id=1),
            Team(id=4, name='Liverpool', league_id=1)
        ]
        db.session.add_all(teams)
        db.session.commit()
        
        # Create test matches
        matches = [
            Match(id=1, home_team_id=1, away_team_id=2, date='2025-01-01', result='2-1'),
            Match(id=2, home_team_id=3, away_team_id=4, date='2025-01-02', result='1-1'),
            Match(id=3, home_team_id=1, away_team_id=3, date='2025-01-03', result=None),
            Match(id=4, home_team_id=2, away_team_id=4, date='2025-01-04', result=None)
        ]
        db.session.add_all(matches)
        db.session.commit()

    def get_auth_token(self):
        """Helper method to get authentication token"""
        # Always register a user before login to ensure a valid token
        username = 'testuser_api_matches'
        password = 'password123'
        self.client.post('/api/v1/register',
            json={'username': username, 'password': password})
        response = self.client.post('/api/v1/login',
            json={'username': username, 'password': password})
        if response.status_code == 200:
            return json.loads(response.data)['token']
        return None

    def test_get_matches_success(self):
        """Test successful matches retrieval"""
        print("Running test_get_matches_success...")
        token = self.get_auth_token()
        response = self.client.get('/api/v1/matches',
            headers={'Authorization': f'Bearer {token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('matches', data)
        self.assertIn('total', data)
        self.assertIn('page', data)
        self.assertIn('per_page', data)
        self.assertIn('pages', data)
        self.assertEqual(len(data['matches']), 4)
        print("test_get_matches_success passed.")

    def test_get_matches_with_league_filter(self):
        """Test matches retrieval with league filter"""
        print("Running test_get_matches_with_league_filter...")
        token = self.get_auth_token()
        response = self.client.get('/api/v1/matches?league_id=1',
            headers={'Authorization': f'Bearer {token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['matches']), 4)
        print("test_get_matches_with_league_filter passed.")

    def test_get_matches_with_team_filter(self):
        """Test matches retrieval with team filter"""
        print("Running test_get_matches_with_team_filter...")
        token = self.get_auth_token()
        response = self.client.get('/api/v1/matches?team_id=1',
            headers={'Authorization': f'Bearer {token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        # Should return matches where Chelsea is home or away
        self.assertEqual(len(data['matches']), 2)
        print("test_get_matches_with_team_filter passed.")

    def test_get_matches_pagination(self):
        """Test matches pagination"""
        print("Running test_get_matches_pagination...")
        token = self.get_auth_token()
        response = self.client.get('/api/v1/matches?page=1&per_page=2',
            headers={'Authorization': f'Bearer {token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['matches']), 2)
        self.assertEqual(data['page'], 1)
        self.assertEqual(data['per_page'], 2)
        print("test_get_matches_pagination passed.")

    def test_get_matches_data_structure(self):
        """Test that matches have correct data structure"""
        print("Running test_get_matches_data_structure...")
        token = self.get_auth_token()
        response = self.client.get('/api/v1/matches',
            headers={'Authorization': f'Bearer {token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        match = data['matches'][0]
        
        self.assertIn('id', match)
        self.assertIn('home_team', match)
        self.assertIn('away_team', match)
        self.assertIn('date', match)
        self.assertIn('result', match)
        print("test_get_matches_data_structure passed.")

    def test_get_relevant_matches_success(self):
        """Test successful relevant matches retrieval"""
        print("Running test_get_relevant_matches_success...")
        token = self.get_auth_token()
        response = self.client.get('/api/v1/matches/relevant',
            headers={'Authorization': f'Bearer {token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        # Should return matches with no predictions yet
        self.assertEqual(len(data), 4)
        print("test_get_relevant_matches_success passed.")

    def test_get_relevant_matches_with_predictions(self):
        """Test relevant matches when some matches have predictions"""
        print("Running test_get_relevant_matches_with_predictions...")
        token = self.get_auth_token()
        
        # Add a prediction for match 1
        from app.models import Prediction
        with self.app.app_context():
            prediction = Prediction(user_id=self.user_id, match_id=1, predicted_result='2-1')
            db.session.add(prediction)
            db.session.commit()
        
        response = self.client.get('/api/v1/matches/relevant',
            headers={'Authorization': f'Bearer {token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        # Should return matches without predictions
        self.assertEqual(len(data), 3)
        print("test_get_relevant_matches_with_predictions passed.")

    def test_get_relevant_matches_data_structure(self):
        """Test that relevant matches have correct data structure"""
        print("Running test_get_relevant_matches_data_structure...")
        token = self.get_auth_token()
        response = self.client.get('/api/v1/matches/relevant',
            headers={'Authorization': f'Bearer {token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        if data:
            match = data[0]
            self.assertIn('id', match)
            self.assertIn('home_team', match)
            self.assertIn('away_team', match)
            self.assertIn('date', match)
            self.assertIn('result', match)
        print("test_get_relevant_matches_data_structure passed.")

    def test_scrape_matches_success(self):
        """Test successful match scraping"""
        print("Running test_scrape_matches_success...")
        token = self.get_auth_token()
        response = self.client.post('/api/v1/matches/scrape',
            json={'team_name': 'Chelsea'},
            headers={'Authorization': f'Bearer {token}'})
        
        # Should return 200 even if no matches found
        self.assertIn(response.status_code, [200, 400, 404])
        data = json.loads(response.data)
        self.assertIsInstance(data, dict)
        print("test_scrape_matches_success passed.")

    def test_scrape_matches_invalid_team(self):
        """Test match scraping with invalid team name"""
        print("Running test_scrape_matches_invalid_team...")
        token = self.get_auth_token()
        response = self.client.post('/api/v1/matches/scrape',
            json={'team_name': 'NonExistentTeamXYZ'},
            headers={'Authorization': f'Bearer {token}'})
        
        # Should handle gracefully
        self.assertIn(response.status_code, [200, 400, 404])
        print("test_scrape_matches_invalid_team passed.")

    def test_scrape_matches_missing_team_name(self):
        """Test match scraping with missing team name"""
        print("Running test_scrape_matches_missing_team_name...")
        token = self.get_auth_token()
        response = self.client.post('/api/v1/matches/scrape',
            json={},
            headers={'Authorization': f'Bearer {token}'})
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        print("test_scrape_matches_missing_team_name passed.")

    def test_matches_ordered_by_date(self):
        """Test that matches are ordered by date"""
        print("Running test_matches_ordered_by_date...")
        token = self.get_auth_token()
        response = self.client.get('/api/v1/matches',
            headers={'Authorization': f'Bearer {token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        matches = data['matches']
        
        # Check that matches are ordered by date (ascending)
        dates = [match['date'] for match in matches]
        self.assertEqual(dates, sorted(dates))
        print("test_matches_ordered_by_date passed.")

    def test_matches_with_results(self):
        """Test matches with and without results"""
        print("Running test_matches_with_results...")
        token = self.get_auth_token()
        response = self.client.get('/api/v1/matches',
            headers={'Authorization': f'Bearer {token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        matches = data['matches']
        
        # Should have some matches with results and some without
        matches_with_results = [m for m in matches if m['result'] is not None]
        matches_without_results = [m for m in matches if m['result'] is None]
        
        self.assertGreater(len(matches_with_results), 0)
        self.assertGreater(len(matches_without_results), 0)
        print("test_matches_with_results passed.")

if __name__ == '__main__':
    unittest.main()