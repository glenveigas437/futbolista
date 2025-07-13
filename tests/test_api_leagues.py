import unittest
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, Team, Match, Prediction, League
from werkzeug.security import generate_password_hash

class LeaguesAPITestCase(unittest.TestCase):
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
        # Create test users
        users = [
            User(username='user1', password_hash='hash', score=10),
            User(username='user2', password_hash='hash', score=15),
            User(username='user3', password_hash='hash', score=5)
        ]
        db.session.add_all(users)
        db.session.commit()
        self.user_ids = [user.id for user in users]
        
        # Create test leagues
        leagues = [
            League(id=1, name='Premier League', country='England', fd_competition='PL'),
            League(id=2, name='La Liga', country='Spain', fd_competition='PD'),
            League(id=3, name='Bundesliga', country='Germany', fd_competition='BL1')
        ]
        db.session.add_all(leagues)
        db.session.commit()
        
        # Create test teams
        teams = [
            Team(id=1, name='Chelsea', league_id=1),
            Team(id=2, name='Arsenal', league_id=1),
            Team(id=3, name='Barcelona', league_id=2),
            Team(id=4, name='Bayern Munich', league_id=3)
        ]
        db.session.add_all(teams)
        db.session.commit()
        
        # Create test matches
        matches = [
            Match(id=1, home_team_id=1, away_team_id=2, date='2025-01-01', result='2-1'),
            Match(id=2, home_team_id=3, away_team_id=4, date='2025-01-02', result='1-1')
        ]
        db.session.add_all(matches)
        db.session.commit()
        
        # Create test predictions
        predictions = [
            Prediction(user_id=self.user_ids[0], match_id=1, predicted_result='2-1', points_awarded=3),
            Prediction(user_id=self.user_ids[1], match_id=1, predicted_result='1-1', points_awarded=0),
            Prediction(user_id=self.user_ids[2], match_id=2, predicted_result='1-1', points_awarded=3)
        ]
        db.session.add_all(predictions)
        db.session.commit()

    def get_auth_token(self):
        """Helper method to get authentication token"""
        # Always register a user before login to ensure a valid token
        username = 'testuser_api_leagues'
        password = 'password123'
        self.client.post('/api/v1/register',
            json={'username': username, 'password': password})
        response = self.client.post('/api/v1/login',
            json={'username': username, 'password': password})
        if response.status_code == 200:
            return json.loads(response.data)['token']
        return None

    def test_get_leagues_success(self):
        print("Running test_get_leagues_success...")

        print("test_get_leagues_success passed.")