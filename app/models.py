from . import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(512), nullable=False)
    score = db.Column(db.Integer, default=0)

class League(db.Model):
    __tablename__ = 'leagues'
    id = db.Column(db.Integer, primary_key=True, autoincrement=False)  # Football-Data.org league ID
    name = db.Column(db.String(100), unique=True, nullable=False)
    website = db.Column(db.String(255))
    country = db.Column(db.String(100))
    fd_competition = db.Column(db.String(100))  # Football-Data.org competition code
    teams = db.relationship('Team', backref='league', lazy=True)

class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True, autoincrement=False)  # Football-Data.org team ID
    name = db.Column(db.String(100), unique=True, nullable=False)
    logo_url = db.Column(db.String(255))
    stadium = db.Column(db.String(100))
    favourite = db.Column(db.Boolean, default=False)
    league_id = db.Column(db.Integer, db.ForeignKey('leagues.id'))

class Match(db.Model):
    __tablename__ = 'matches'
    id = db.Column(db.Integer, primary_key=True, autoincrement=False)  # Football-Data.org match ID
    home_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    away_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    date = db.Column(db.String(50))
    result = db.Column(db.String(20))
    home_team = db.relationship('Team', foreign_keys=[home_team_id], backref='home_matches')
    away_team = db.relationship('Team', foreign_keys=[away_team_id], backref='away_matches')

class Prediction(db.Model):
    __tablename__ = 'predictions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'))
    predicted_result = db.Column(db.String(20))
    points_awarded = db.Column(db.Integer, default=0)
    user = db.relationship('User', backref='predictions')
    match = db.relationship('Match', backref='predictions')

class FavouriteTeam(db.Model):
    __tablename__ = 'favourite_teams'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    user = db.relationship('User', backref='favourite_teams')
    team = db.relationship('Team', backref='favourited_by') 