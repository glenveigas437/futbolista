import unittest
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, Team, Match, Prediction, League
from werkzeug.security import generate_password_hash

class PredictionsAPITestCase(unittest.TestCase):
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
        
        # Create test league with unique ID
        league = League(id=2001, name='Test Premier League')
        db.session.add(league)
        db.session.commit()
        
        # Create test teams with unique IDs
        teams = [
            Team(id=2001, name='Test Chelsea', league_id=2001),
            Team(id=2002, name='Test Arsenal', league_id=2001),
            Team(id=2003, name='Test Manchester United', league_id=2001),
            Team(id=2004, name='Test Liverpool', league_id=2001)
        ]
        db.session.add_all(teams)
        db.session.commit()
        
        # Create test matches with unique IDs
        matches = [
            Match(id=2001, home_team_id=2001, away_team_id=2002, date='2025-01-01', result='2-1'),
            Match(id=2002, home_team_id=2003, away_team_id=2004, date='2025-01-02', result='1-1'),
            Match(id=2003, home_team_id=2001, away_team_id=2003, date='2025-01-03', result=None),
            Match(id=2004, home_team_id=2002, away_team_id=2004, date='2025-01-04', result=None)
        ]
        db.session.add_all(matches)
        db.session.commit()

    def get_auth_token(self):
        """Helper method to get authentication token"""
        # Always register a user before login to ensure a valid token
        username = 'testuser_api_predictions'
        password = 'password123'
        self.client.post('/api/v1/register',
            json={'username': username, 'password': password})
        response = self.client.post('/api/v1/login',
            json={'username': username, 'password': password})
        if response.status_code == 200:
            return json.loads(response.data)['token']
        return None

    def test_add_prediction_success(self):
        """Test successful prediction addition"""
        print("Running test_add_prediction_success...")
        token = self.get_auth_token()
        response = self.client.post('/api/v1/predictions',
            json={'match_id': 2003, 'home_score': 2, 'away_score': 1},
            headers={'Authorization': f'Bearer {token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('success', data)
        self.assertTrue(data['success'])
        print("test_add_prediction_success passed.")

    def test_add_prediction_invalid_match(self):
        """Test prediction addition with invalid match ID"""
        print("Running test_add_prediction_invalid_match...")
        token = self.get_auth_token()
        response = self.client.post('/api/v1/predictions',
            json={'match_id': 999, 'home_score': 2, 'away_score': 1},
            headers={'Authorization': f'Bearer {token}'})
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        print("test_add_prediction_invalid_match passed.")

    def test_add_prediction_missing_fields(self):
        """Test prediction addition with missing fields"""
        print("Running test_add_prediction_missing_fields...")
        token = self.get_auth_token()
        response = self.client.post('/api/v1/predictions',
            json={'match_id': 2003, 'home_score': 2},  # Missing away_score
            headers={'Authorization': f'Bearer {token}'})
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        print("test_add_prediction_missing_fields passed.")

    def test_add_duplicate_prediction(self):
        """Test adding duplicate prediction for same match"""
        print("Running test_add_duplicate_prediction...")
        token = self.get_auth_token()
        
        # Add first prediction
        self.client.post('/api/v1/predictions',
            json={'match_id': 2003, 'home_score': 2, 'away_score': 1},
            headers={'Authorization': f'Bearer {token}'})
        
        # Try to add second prediction for same match
        response = self.client.post('/api/v1/predictions',
            json={'match_id': 2003, 'home_score': 1, 'away_score': 1},
            headers={'Authorization': f'Bearer {token}'})
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        print("test_add_duplicate_prediction passed.")

    def test_get_predictions_success(self):
        """Test successful predictions retrieval"""
        print("Running test_get_predictions_success...")
        token = self.get_auth_token()
        
        # Add a prediction first
        self.client.post('/api/v1/predictions',
            json={'match_id': 2003, 'home_score': 2, 'away_score': 1},
            headers={'Authorization': f'Bearer {token}'})
        
        response = self.client.get('/api/v1/predictions',
            headers={'Authorization': f'Bearer {token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        print("test_get_predictions_success passed.")

    def test_get_predictions_data_structure(self):
        """Test that predictions have correct data structure"""
        print("Running test_get_predictions_data_structure...")
        token = self.get_auth_token()
        
        # Add a prediction first
        self.client.post('/api/v1/predictions',
            json={'match_id': 2003, 'home_score': 2, 'away_score': 1},
            headers={'Authorization': f'Bearer {token}'})
        
        response = self.client.get('/api/v1/predictions',
            headers={'Authorization': f'Bearer {token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        prediction = data[0]
        
        self.assertIn('id', prediction)
        self.assertIn('match_id', prediction)
        self.assertIn('home_team', prediction)
        self.assertIn('away_team', prediction)
        self.assertIn('date', prediction)
        self.assertIn('predicted_result', prediction)
        self.assertIn('actual_result', prediction)
        self.assertIn('correct', prediction)
        print("test_get_predictions_data_structure passed.")

    def test_get_predictions_empty(self):
        """Test predictions retrieval when user has no predictions"""
        print("Running test_get_predictions_empty...")
        token = self.get_auth_token()
        response = self.client.get('/api/v1/predictions',
            headers={'Authorization': f'Bearer {token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 0)
        print("test_get_predictions_empty passed.")

    def test_prediction_correct_calculation(self):
        """Test that correct predictions are marked as correct"""
        print("Running test_prediction_correct_calculation...")
        token = self.get_auth_token()
        
        # Add prediction for match with known result (2-1)
        self.client.post('/api/v1/predictions',
            json={'match_id': 2001, 'home_score': 2, 'away_score': 1},
            headers={'Authorization': f'Bearer {token}'})
        
        response = self.client.get('/api/v1/predictions',
            headers={'Authorization': f'Bearer {token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertGreater(len(data), 0, "No predictions found - check if prediction was created")
        prediction = data[0]
        
        self.assertEqual(prediction['predicted_result'], '2-1')
        self.assertEqual(prediction['actual_result'], '2-1')
        self.assertTrue(prediction['correct'])
        print("test_prediction_correct_calculation passed.")

    def test_prediction_incorrect_calculation(self):
        """Test that incorrect predictions are marked as incorrect"""
        print("Running test_prediction_incorrect_calculation...")
        token = self.get_auth_token()
        
        # Add prediction for match with known result (2-1) but predict different (1-1)
        self.client.post('/api/v1/predictions',
            json={'match_id': 2001, 'home_score': 1, 'away_score': 1},
            headers={'Authorization': f'Bearer {token}'})
        
        response = self.client.get('/api/v1/predictions',
            headers={'Authorization': f'Bearer {token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertGreater(len(data), 0, "No predictions found - check if prediction was created")
        prediction = data[0]
        
        self.assertEqual(prediction['predicted_result'], '1-1')
        self.assertEqual(prediction['actual_result'], '2-1')
        self.assertFalse(prediction['correct'])
        print("test_prediction_incorrect_calculation passed.")

    def test_prediction_pending_calculation(self):
        """Test that predictions for matches without results are marked as pending"""
        print("Running test_prediction_pending_calculation...")
        token = self.get_auth_token()
        
        # Add prediction for match without result
        self.client.post('/api/v1/predictions',
            json={'match_id': 2003, 'home_score': 2, 'away_score': 1},
            headers={'Authorization': f'Bearer {token}'})
        
        response = self.client.get('/api/v1/predictions',
            headers={'Authorization': f'Bearer {token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        prediction = data[0]
        
        self.assertEqual(prediction['predicted_result'], '2-1')
        self.assertIsNone(prediction['actual_result'])
        self.assertFalse(prediction['correct'])
        print("test_prediction_pending_calculation passed.")

    def test_prediction_team_names(self):
        """Test that team names are correctly included in predictions"""
        print("Running test_prediction_team_names...")
        token = self.get_auth_token()
        
        # Add prediction
        self.client.post('/api/v1/predictions',
            json={'match_id': 2003, 'home_score': 2, 'away_score': 1},
            headers={'Authorization': f'Bearer {token}'})
        
        response = self.client.get('/api/v1/predictions',
            headers={'Authorization': f'Bearer {token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        prediction = data[0]
        
        self.assertEqual(prediction['home_team'], 'Test Chelsea')
        self.assertEqual(prediction['away_team'], 'Test Manchester United')
        print("test_prediction_team_names passed.")

    def test_prediction_date_format(self):
        """Test that prediction date is correctly formatted"""
        print("Running test_prediction_date_format...")
        token = self.get_auth_token()
        
        # Add prediction
        self.client.post('/api/v1/predictions',
            json={'match_id': 2003, 'home_score': 2, 'away_score': 1},
            headers={'Authorization': f'Bearer {token}'})
        
        response = self.client.get('/api/v1/predictions',
            headers={'Authorization': f'Bearer {token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        prediction = data[0]
        
        self.assertEqual(prediction['date'], '2025-01-03')
        print("test_prediction_date_format passed.")

    def test_multiple_predictions_same_user(self):
        """Test that a user can have multiple predictions"""
        print("Running test_multiple_predictions_same_user...")
        token = self.get_auth_token()
        
        # Add first prediction
        self.client.post('/api/v1/predictions',
            json={'match_id': 2001, 'home_score': 2, 'away_score': 1},
            headers={'Authorization': f'Bearer {token}'})
        
        # Add second prediction for different match
        self.client.post('/api/v1/predictions',
            json={'match_id': 2002, 'home_score': 1, 'away_score': 1},
            headers={'Authorization': f'Bearer {token}'})
        
        response = self.client.get('/api/v1/predictions',
            headers={'Authorization': f'Bearer {token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2, f"Expected 2 predictions, got {len(data)}")
        print("test_multiple_predictions_same_user passed.")

if __name__ == '__main__':
    unittest.main()