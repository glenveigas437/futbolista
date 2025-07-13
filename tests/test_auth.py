import unittest
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

class AuthTestCase(unittest.TestCase):
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

    def test_register_success(self):
        """Test successful user registration"""
        print("Running test_register_success...")
        response = self.client.post('/api/v1/register',
            json={'username': 'newuser', 'password': 'password123'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('success', data)
        self.assertIn('user_id', data)
        self.assertTrue(data['success'])
        print("test_register_success passed.")

    def test_register_duplicate_username(self):
        """Test registration with duplicate username"""
        print("Running test_register_duplicate_username...")
        # First registration
        self.client.post('/api/v1/register',
            json={'username': 'testuser_dup', 'password': 'password123'})
        
        # Second registration with same username
        response = self.client.post('/api/v1/register',
            json={'username': 'testuser_dup', 'password': 'password456'})
        
        self.assertEqual(response.status_code, 409)
        data = json.loads(response.data)
        self.assertIn('error', data)
        print("test_register_duplicate_username passed.")

    def test_register_missing_fields(self):
        """Test registration with missing fields"""
        print("Running test_register_missing_fields...")
        response = self.client.post('/api/v1/register',
            json={'username': 'testuser'})  # Missing password
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        print("test_register_missing_fields passed.")

    def test_login_success(self):
        """Test successful login"""
        print("Running test_login_success...")
        # Register a user first
        self.client.post('/api/v1/register',
            json={'username': 'testuser_login', 'password': 'password123'})
        
        # Login
        response = self.client.post('/api/v1/login',
            json={'username': 'testuser_login', 'password': 'password123'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('token', data)
        self.assertIn('user_id', data)
        print("test_login_success passed.")

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        print("Running test_login_invalid_credentials...")
        # Register a user first
        self.client.post('/api/v1/register',
            json={'username': 'testuser', 'password': 'password123'})
        
        # Login with wrong password
        response = self.client.post('/api/v1/login',
            json={'username': 'testuser', 'password': 'wrongpassword'})
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn('error', data)
        print("test_login_invalid_credentials passed.")

    def test_login_nonexistent_user(self):
        """Test login with non-existent user"""
        print("Running test_login_nonexistent_user...")
        response = self.client.post('/api/v1/login',
            json={'username': 'nonexistent', 'password': 'password123'})
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn('error', data)
        print("test_login_nonexistent_user passed.")

    def test_protected_endpoint_without_token(self):
        """Test accessing protected endpoint without token"""
        print("Running test_protected_endpoint_without_token...")
        response = self.client.get('/api/v1/teams')
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn('error', data)
        print("test_protected_endpoint_without_token passed.")

    def test_protected_endpoint_with_valid_token(self):
        """Test accessing protected endpoint with valid token"""
        print("Running test_protected_endpoint_with_valid_token...")
        # Register and login to get token
        self.client.post('/api/v1/register',
            json={'username': 'testuser', 'password': 'password123'})
        
        login_response = self.client.post('/api/v1/login',
            json={'username': 'testuser', 'password': 'password123'})
        token = json.loads(login_response.data)['token']
        
        # Access protected endpoint with token
        response = self.client.get('/api/v1/teams',
            headers={'Authorization': f'Bearer {token}'})
        
        self.assertEqual(response.status_code, 200)
        print("test_protected_endpoint_with_valid_token passed.")

    def test_protected_endpoint_with_invalid_token(self):
        """Test accessing protected endpoint with invalid token"""
        print("Running test_protected_endpoint_with_invalid_token...")
        response = self.client.get('/api/v1/teams',
            headers={'Authorization': 'Bearer invalid_token'})
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn('error', data)
        print("test_protected_endpoint_with_invalid_token passed.")

    def test_protected_endpoint_with_malformed_header(self):
        """Test accessing protected endpoint with malformed Authorization header"""
        print("Running test_protected_endpoint_with_malformed_header...")
        response = self.client.get('/api/v1/teams',
            headers={'Authorization': 'InvalidFormat token'})
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn('error', data)
        print("test_protected_endpoint_with_malformed_header passed.")

if __name__ == '__main__':
    unittest.main() 