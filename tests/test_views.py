import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, Team, Match, League

class ViewsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['TESTING'] = True
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
        league = League(id=999, name='Test Premier League')
        db.session.add(league)
        db.session.commit()
        
        # Create test teams with unique IDs
        teams = [
            Team(id=9991, name='Test Chelsea', logo_url='chelsea.png', stadium='Stamford Bridge', league_id=999, favourite=True),
            Team(id=9992, name='Test Arsenal', logo_url='arsenal.png', stadium='Emirates Stadium', league_id=999, favourite=False),
            Team(id=9993, name='Test Manchester United', logo_url='manutd.png', stadium='Old Trafford', league_id=999, favourite=True)
        ]
        db.session.add_all(teams)
        db.session.commit()

    def test_home_page(self):
        print("Running test_home_page...")

        print("test_home_page passed.")