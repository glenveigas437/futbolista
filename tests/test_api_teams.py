import unittest
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, Team, League, FavouriteTeam
from werkzeug.security import generate_password_hash

class TeamsAPITestCase(unittest.TestCase):
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
        # Create test league with unique ID
        league = League(id=1001, name='Test Premier League')
        db.session.add(league)
        db.session.commit()
        
        # Create test teams with unique IDs
        teams = [
            Team(id=1001, name='Test Chelsea', logo_url='chelsea.png', stadium='Stamford Bridge', league_id=1001),
            Team(id=1002, name='Test Arsenal', logo_url='arsenal.png', stadium='Emirates Stadium', league_id=1001),
            Team(id=1003, name='Test Manchester United', logo_url='manutd.png', stadium='Old Trafford', league_id=1001),
            Team(id=1004, name='Test Liverpool', logo_url='liverpool.png', stadium='Anfield', league_id=1001),
            Team(id=1005, name='Test Manchester City', logo_url='mancity.png', stadium='Etihad Stadium', league_id=1001)
        ]
        db.session.add_all(teams)
        db.session.commit()

    def get_auth_token(self):
        """Helper method to get authentication token"""
        # Always register a user before login to ensure a valid token
        username = 'testuser_api_teams'
        password = 'password123'
        self.client.post('/api/v1/register',
            json={'username': username, 'password': password})
        response = self.client.post('/api/v1/login',
            json={'username': username, 'password': password})
        if response.status_code == 200:
            token_data = json.loads(response.data)
            # Create favourite relationship for this user
            user_id = token_data['user_id']
            fav = FavouriteTeam(user_id=user_id, team_id=1001)
            with self.app.app_context():
                db.session.add(fav)
                db.session.commit()
            return token_data['token']
        return None

    def test_get_teams_success(self):
        """Test successful teams retrieval"""
        print("Running test_get_teams_success...")
        token = self.get_auth_token()
        response = self.client.get('/api/v1/teams',
            headers={'Authorization': f'Bearer {token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('teams', data)
        self.assertIn('total', data)
        self.assertIn('page', data)
        self.assertIn('per_page', data)
        self.assertIn('pages', data)
        self.assertEqual(len(data['teams']), 5)
        print("test_get_teams_success passed.")

    def test_get_teams_with_search(self):
        """Test teams retrieval with search parameter"""
        print("Running test_get_teams_with_search...")
        token = self.get_auth_token()
        response = self.client.get('/api/v1/teams?search=chelsea',
            headers={'Authorization': f'Bearer {token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['teams']), 1)
        self.assertEqual(data['teams'][0]['name'], 'Test Chelsea')
        print("test_get_teams_with_search passed.")

    def test_get_teams_with_league_filter(self):
        """Test teams retrieval with league filter"""
        print("Running test_get_teams_with_league_filter...")
        token = self.get_auth_token()
        response = self.client.get('/api/v1/teams?league_id=1001',
            headers={'Authorization': f'Bearer {token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['teams']), 5)
        print("test_get_teams_with_league_filter passed.")

    def test_get_teams_pagination(self):
        """Test teams pagination"""
        print("Running test_get_teams_pagination...")
        token = self.get_auth_token()
        response = self.client.get('/api/v1/teams?page=1&per_page=2',
            headers={'Authorization': f'Bearer {token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['teams']), 2)
        self.assertEqual(data['page'], 1)
        self.assertEqual(data['per_page'], 2)
        print("test_get_teams_pagination passed.")

    def test_get_teams_favourite_status(self):
        """Test that favourite status is correctly returned"""
        print("Running test_get_teams_favourite_status...")
        token = self.get_auth_token()
        response = self.client.get('/api/v1/teams',
            headers={'Authorization': f'Bearer {token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Find Test Chelsea (should be favourited)
        chelsea = next((team for team in data['teams'] if team['name'] == 'Test Chelsea'), None)
        self.assertIsNotNone(chelsea)
        self.assertTrue(chelsea['favourite'])
        
        # Find Test Arsenal (should not be favourited)
        arsenal = next((team for team in data['teams'] if team['name'] == 'Test Arsenal'), None)
        self.assertIsNotNone(arsenal)
        self.assertFalse(arsenal['favourite'])
        print("test_get_teams_favourite_status passed.")

    def test_search_and_add_team_success(self):
        """Test successful team search and add"""
        print("Running test_search_and_add_team_success...")
        token = self.get_auth_token()
        response = self.client.post('/api/v1/teams/search',
            json={'team_name': 'Tottenham Hotspur'},
            headers={'Authorization': f'Bearer {token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('team', data)
        self.assertTrue(data['added'])
        self.assertEqual(data['team']['name'], 'Tottenham Hotspur')
        print("test_search_and_add_team_success passed.")

    def test_search_and_add_existing_team(self):
        """Test search and add for existing team"""
        print("Running test_search_and_add_existing_team...")
        token = self.get_auth_token()
        response = self.client.post('/api/v1/teams/search',
            json={'team_name': 'Test Chelsea'},
            headers={'Authorization': f'Bearer {token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('team', data)
        self.assertFalse(data['added'])
        self.assertEqual(data['team']['name'], 'Test Chelsea')
        print("test_search_and_add_existing_team passed.")

    def test_search_and_add_team_missing_name(self):
        """Test search and add with missing team name"""
        print("Running test_search_and_add_team_missing_name...")
        token = self.get_auth_token()
        response = self.client.post('/api/v1/teams/search',
            json={},
            headers={'Authorization': f'Bearer {token}'})
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        print("test_search_and_add_team_missing_name passed.")

    def test_favourite_team_success(self):
        """Test successful team favouriting"""
        print("Running test_favourite_team_success...")
        token = self.get_auth_token()
        response = self.client.post('/api/v1/teams/1002/favourite',
            headers={'Authorization': f'Bearer {token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['id'], 1002)
        self.assertTrue(data['favourite'])
        print("test_favourite_team_success passed.")

    def test_unfavourite_team_success(self):
        """Test successful team unfavouriting"""
        print("Running test_unfavourite_team_success...")
        token = self.get_auth_token()
        # First favourite the team
        self.client.post('/api/v1/teams/1002/favourite',
            headers={'Authorization': f'Bearer {token}'})
        
        # Then unfavourite it
        response = self.client.delete('/api/v1/teams/1002/favourite',
            headers={'Authorization': f'Bearer {token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['id'], 1002)
        self.assertFalse(data['favourite'])
        print("test_unfavourite_team_success passed.")

    def test_favourite_nonexistent_team(self):
        """Test favouriting non-existent team"""
        print("Running test_favourite_nonexistent_team...")
        token = self.get_auth_token()
        response = self.client.post('/api/v1/teams/999/favourite',
            headers={'Authorization': f'Bearer {token}'})
        
        # Should still return 200 but with favourite=False
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['id'], 999)
        self.assertTrue(data['favourite'])
        print("test_favourite_nonexistent_team passed.")

    def test_team_matches_endpoint(self):
        """Test getting matches for a specific team"""
        print("Running test_team_matches_endpoint...")
        token = self.get_auth_token()
        response = self.client.get('/api/v1/teams/1001/matches',
            headers={'Authorization': f'Bearer {token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        print("test_team_matches_endpoint passed.")

if __name__ == '__main__':
    unittest.main()