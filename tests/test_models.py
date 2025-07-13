import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, Team, Match, Prediction, League, FavouriteTeam
from werkzeug.security import generate_password_hash

class ModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(testing=True)
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_user_creation(self):
        """Test user creation and password hashing"""
        print("Running test_user_creation...")
        with self.app.app_context():
            user = User(
                username='testuser',
                password_hash=generate_password_hash('password123'),
                score=0
            )
            db.session.add(user)
            db.session.commit()
            
            self.assertIsNotNone(user.id)
            self.assertEqual(user.username, 'testuser')
            self.assertEqual(user.score, 0)
            print("test_user_creation passed.")

    def test_league_creation(self):
        """Test league creation"""
        print("Running test_league_creation...")
        with self.app.app_context():
            league = League(
                id=1,
                name='Premier League',
                website='https://premierleague.com',
                country='England',
                fd_competition='PL'
            )
            db.session.add(league)
            db.session.commit()
            
            self.assertEqual(league.id, 1)
            self.assertEqual(league.name, 'Premier League')
            print("test_league_creation passed.")

    def test_team_creation(self):
        """Test team creation with league relationship"""
        print("Running test_team_creation...")
        with self.app.app_context():
            league = League(id=1, name='Premier League')
            db.session.add(league)
            db.session.commit()
            
            team = Team(
                id=1,
                name='Chelsea',
                logo_url='chelsea.png',
                stadium='Stamford Bridge',
                league_id=league.id
            )
            db.session.add(team)
            db.session.commit()
            
            self.assertEqual(team.name, 'Chelsea')
            self.assertEqual(team.league.name, 'Premier League')
            print("test_team_creation passed.")

    def test_match_creation(self):
        """Test match creation with team relationships"""
        print("Running test_match_creation...")
        with self.app.app_context():
            # Create teams
            home_team = Team(id=1, name='Chelsea')
            away_team = Team(id=2, name='Arsenal')
            db.session.add_all([home_team, away_team])
            db.session.commit()
            
            match = Match(
                id=1,
                home_team_id=home_team.id,
                away_team_id=away_team.id,
                date='2025-01-01',
                result='2-1'
            )
            db.session.add(match)
            db.session.commit()
            
            self.assertEqual(match.home_team.name, 'Chelsea')
            self.assertEqual(match.away_team.name, 'Arsenal')
            self.assertEqual(match.result, '2-1')
            print("test_match_creation passed.")

    def test_prediction_creation(self):
        """Test prediction creation with user and match relationships"""
        print("Running test_prediction_creation...")
        with self.app.app_context():
            # Create user
            user = User(username='testuser', password_hash='hash')
            db.session.add(user)
            
            # Create teams and match
            home_team = Team(id=1, name='Chelsea')
            away_team = Team(id=2, name='Arsenal')
            match = Match(id=1, home_team_id=home_team.id, away_team_id=away_team.id, date='2025-01-01')
            db.session.add_all([home_team, away_team, match])
            db.session.commit()
            
            prediction = Prediction(
                user_id=user.id,
                match_id=match.id,
                predicted_result='2-1',
                points_awarded=3
            )
            db.session.add(prediction)
            db.session.commit()
            
            self.assertEqual(prediction.user.username, 'testuser')
            self.assertEqual(prediction.match.home_team.name, 'Chelsea')
            self.assertEqual(prediction.points_awarded, 3)
            print("test_prediction_creation passed.")

    def test_favourite_team_creation(self):
        """Test favourite team relationship"""
        print("Running test_favourite_team_creation...")
        with self.app.app_context():
            user = User(username='testuser', password_hash='hash')
            team = Team(id=1, name='Chelsea')
            db.session.add_all([user, team])
            db.session.commit()
            
            fav = FavouriteTeam(user_id=user.id, team_id=team.id)
            db.session.add(fav)
            db.session.commit()
            
            self.assertEqual(fav.user.username, 'testuser')
            self.assertEqual(fav.team.name, 'Chelsea')
            print("test_favourite_team_creation passed.")

    def test_user_predictions_relationship(self):
        """Test user predictions backref"""
        print("Running test_user_predictions_relationship...")
        with self.app.app_context():
            user = User(username='testuser', password_hash='hash')
            db.session.add(user)
            
            home_team = Team(id=1, name='Chelsea')
            away_team = Team(id=2, name='Arsenal')
            match = Match(id=1, home_team_id=home_team.id, away_team_id=away_team.id, date='2025-01-01')
            db.session.add_all([home_team, away_team, match])
            db.session.commit()
            
            prediction = Prediction(
                user_id=user.id,
                match_id=match.id,
                predicted_result='2-1'
            )
            db.session.add(prediction)
            db.session.commit()
            
            self.assertEqual(len(user.predictions), 1)
            self.assertEqual(user.predictions[0].predicted_result, '2-1')
            print("test_user_predictions_relationship passed.")

    def test_team_matches_relationship(self):
        """Test team matches relationships"""
        print("Running test_team_matches_relationship...")
        with self.app.app_context():
            team1 = Team(id=1, name='Chelsea')
            team2 = Team(id=2, name='Arsenal')
            db.session.add_all([team1, team2])
            db.session.commit()
            
            match1 = Match(id=1, home_team_id=team1.id, away_team_id=team2.id, date='2025-01-01')
            match2 = Match(id=2, home_team_id=team2.id, away_team_id=team1.id, date='2025-01-02')
            db.session.add_all([match1, match2])
            db.session.commit()
            
            self.assertEqual(len(team1.home_matches), 1)
            self.assertEqual(len(team1.away_matches), 1)
            self.assertEqual(len(team2.home_matches), 1)
            self.assertEqual(len(team2.away_matches), 1)
            print("test_team_matches_relationship passed.")

if __name__ == '__main__':
    unittest.main() 