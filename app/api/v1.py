from flask import Blueprint, jsonify, request
from ..models import Team, Match, Prediction, League, FavouriteTeam, User
from utils.thirdparty.FootballDataOrgScraper import FootballDataOrgScraper
from sqlalchemy.exc import IntegrityError
from app import db
import jwt
import datetime
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from sqlalchemy import func
import random

api_v1 = Blueprint('api_v1', __name__)

def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        if not token:
            print('JWT DEBUG: No token found in headers')
            return jsonify({'error': 'Token is missing!'}), 401
        try:
            print('JWT DEBUG: Decoding token:', token)
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = data['user_id']
        except Exception as e:
            print('JWT DEBUG: Decode error:', e)
            return jsonify({'error': 'Token is invalid!'}), 401
        return f(user_id, *args, **kwargs)
    return decorated

@api_v1.route('/teams', methods=['GET'])
@jwt_required
def api_teams(user_id):
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    league_id = request.args.get('league_id')
    query = Team.query
    if league_id:
        query = query.filter_by(league_id=league_id)
    search = request.args.get('search', '').strip()
    if search:
        query = query.filter(Team.name.ilike(f'%{search}%'))
    pagination = query.order_by(Team.name).paginate(page=page, per_page=per_page, error_out=False)
    teams = pagination.items
    # Get all favourited team ids for this user
    fav_team_ids = set(ft.team_id for ft in FavouriteTeam.query.filter_by(user_id=user_id).all())
    return jsonify({
        'teams': [
            {'id': t.id, 'name': t.name, 'logo_url': t.logo_url, 'stadium': t.stadium, 'favourite': t.id in fav_team_ids, 'league_id': t.league_id}
            for t in teams
        ],
        'total': pagination.total,
        'page': pagination.page,
        'per_page': pagination.per_page,
        'pages': pagination.pages
    })

@api_v1.route('/matches', methods=['GET'])
@jwt_required
def api_matches(user_id):
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    league_id = request.args.get('league_id')
    team_id = request.args.get('team_id')
    query = Match.query
    if league_id:
        query = query.join(Team, Match.home_team_id == Team.id).filter(Team.league_id == league_id)
    if team_id:
        query = query.filter((Match.home_team_id == team_id) | (Match.away_team_id == team_id))
    pagination = query.order_by(Match.date.asc()).paginate(page=page, per_page=per_page, error_out=False)
    matches = pagination.items
    return jsonify({
        'matches': [
            {
                'id': m.id,
                'home_team': m.home_team.name if m.home_team else None,
                'away_team': m.away_team.name if m.away_team else None,
                'date': m.date,
                'result': m.result
            } for m in matches
        ],
        'total': pagination.total,
        'page': pagination.page,
        'per_page': pagination.per_page,
        'pages': pagination.pages
    })

# New endpoint: fetch matches for a given team
@api_v1.route('/teams/<int:team_id>/matches', methods=['GET'])
@jwt_required
def api_team_matches(user_id, team_id):
    matches = Match.query.filter(
        (Match.home_team_id == team_id) | (Match.away_team_id == team_id)
    ).all()
    return jsonify([
        {
            'id': m.id,
            'home_team': m.home_team.name if m.home_team else None,
            'away_team': m.away_team.name if m.away_team else None,
            'date': m.date,
            'result': m.result
        } for m in matches
    ])

@api_v1.route('/teams/search', methods=['POST'])
@jwt_required
def api_search_and_add_team(user_id):
    data = request.get_json()
    team_name = data.get('team_name')
    if not team_name:
        return jsonify({'error': 'team_name is required'}), 400

    existing = Team.query.filter_by(name=team_name).first()
    if existing:
        # Check if favourited by this user
        fav = FavouriteTeam.query.filter_by(user_id=user_id, team_id=existing.id).first()
        return jsonify({'team': {'id': existing.id, 'name': existing.name, 'logo_url': existing.logo_url, 'stadium': existing.stadium, 'favourite': bool(fav)}, 'added': False})

    # For user-added teams, generate a unique ID (negative to avoid conflicts with Football-Data.org IDs)
    while True:
        new_id = -random.randint(1000, 9999)
        if not Team.query.get(new_id):
            break
    
    new_team = Team(id=new_id, name=team_name, logo_url=None, stadium=None, favourite=False)
    try:
        db.session.add(new_team)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Team already exists'}), 409

    return jsonify({'team': {'id': new_team.id, 'name': new_team.name, 'logo_url': new_team.logo_url, 'stadium': new_team.stadium, 'favourite': False}, 'added': True})

@api_v1.route('/teams/<int:team_id>/favourite', methods=['POST'])
@jwt_required
def api_favourite_team(user_id, team_id):
    # Add favourite for this user/team if not already exists
    exists = FavouriteTeam.query.filter_by(user_id=user_id, team_id=team_id).first()
    if exists:
        return jsonify({'id': team_id, 'favourite': True})
    fav = FavouriteTeam(user_id=user_id, team_id=team_id)
    db.session.add(fav)
    db.session.commit()
    return jsonify({'id': team_id, 'favourite': True})

@api_v1.route('/teams/<int:team_id>/favourite', methods=['DELETE'])
@jwt_required
def api_unfavourite_team(user_id, team_id):
    fav = FavouriteTeam.query.filter_by(user_id=user_id, team_id=team_id).first()
    if fav:
        db.session.delete(fav)
        db.session.commit()
    return jsonify({'id': team_id, 'favourite': False})

@api_v1.route('/matches/relevant', methods=['GET'])
@jwt_required
def api_relevant_matches(user_id):
    # Get all team IDs in DB
    team_ids = [t.id for t in Team.query.all()]
    # Get all matches where both teams are in DB and not yet predicted
    predicted_match_ids = [p.match_id for p in Prediction.query.all()]
    matches = Match.query.filter(
        Match.home_team_id.in_(team_ids),
        Match.away_team_id.in_(team_ids),
        ~Match.id.in_(predicted_match_ids)
    ).all()
    return jsonify([
        {
            'id': m.id,
            'home_team': m.home_team.name if m.home_team else None,
            'away_team': m.away_team.name if m.away_team else None,
            'date': m.date,
            'result': m.result
        } for m in matches
    ])

@api_v1.route('/predictions', methods=['POST'])
@jwt_required
def api_add_prediction(user_id):
    data = request.get_json()
    # Validate required fields
    match_id = data.get('match_id')
    home_score = data.get('home_score')
    away_score = data.get('away_score')
    if match_id is None or home_score is None or away_score is None:
        return jsonify({'error': 'match_id, home_score, and away_score are required'}), 400
    # Check if match exists
    match = Match.query.get(match_id)
    if not match:
        return jsonify({'error': 'Invalid match_id'}), 400
    # Check for duplicate prediction
    existing = Prediction.query.filter_by(user_id=user_id, match_id=match_id).first()
    if existing:
        return jsonify({'error': 'Prediction already exists for this match'}), 400
    predicted_result = f"{home_score}-{away_score}"
    prediction = Prediction(user_id=user_id, match_id=match_id, predicted_result=predicted_result)
    db.session.add(prediction)
    db.session.commit()
    return jsonify({'success': True, 'prediction_id': prediction.id})

@api_v1.route('/predictions', methods=['GET'])
@jwt_required
def api_get_predictions(user_id):
    predictions = Prediction.query.filter_by(user_id=user_id).all()
    results = []
    for p in predictions:
        match = Match.query.get(p.match_id)
        print(match.home_team.name)
        results.append({
            'id': p.id,
            'match_id': p.match_id,
            'home_team': match.home_team.name if match and match.home_team else None,
            'away_team': match.away_team.name if match and match.away_team else None,
            'date': match.date if match else None,
            'predicted_result': p.predicted_result,
            'actual_result': match.result if match else None,
            'correct': (match.result is not None and match.result == p.predicted_result) if match else False
        })
    return jsonify(results)

@api_v1.route('/matches/scrape', methods=['POST'])
@jwt_required
def api_scrape_matches(user_id):
    data = request.get_json()
    team_name = data.get('team_name')
    if not team_name:
        return jsonify({'error': 'team_name is required'}), 400
    db_teams = Team.query.all()
    db_team_names = [t.name for t in db_teams]
    scraper = FootballDataOrgScraper()
    matches = scraper.fetch_matches_for_team(team_name)
    print(f"Scraping for: {team_name}")
    print(f"Scraped matches: {matches}")
    inserted = 0
    from sqlalchemy import or_
    for m in matches:
        print(f"Trying to match: {m['home_team']} vs {m['away_team']} on {m['date']}")
        home_team = Team.query.filter(Team.name.ilike(f"%{m['home_team']}%") | Team.name.ilike(f"%{m['home_team'].replace(' ', '')}%")).first()
        away_team = Team.query.filter(Team.name.ilike(f"%{m['away_team']}%") | Team.name.ilike(f"%{m['away_team'].replace(' ', '')}%")).first()
        print(f"Matched home_team: {home_team}")
        print(f"Matched away_team: {away_team}")
        if not home_team or not away_team:
            continue
        exists = Match.query.filter_by(home_team_id=home_team.id, away_team_id=away_team.id, date=m['date']).first()
        if exists:
            continue
        match = Match(home_team_id=home_team.id, away_team_id=away_team.id, date=m['date'], result=m['result'])
        db.session.add(match)
        inserted += 1
    db.session.commit()
    msg = f"Inserted {inserted} new matches for {team_name}. Scraped {len(matches)} matches."
    print(msg)
    return jsonify({'inserted': inserted, 'total_found': len(matches), 'message': msg})

@api_v1.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 409
    user = User(username=username, password_hash=generate_password_hash(password), score=0)
    db.session.add(user)
    db.session.commit()
    return jsonify({'success': True, 'user_id': user.id})

@api_v1.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'error': 'Invalid credentials'}), 401
    token = jwt.encode({'user_id': user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)}, current_app.config['SECRET_KEY'], algorithm='HS256')
    return jsonify({'token': token, 'user_id': user.id})

@api_v1.route('/leagues', methods=['GET'])
@jwt_required
def api_leagues(user_id):
    try:
        leagues = League.query.all()
        return jsonify([
            {'id': l.id, 'name': l.name, 'country': l.country, 'fd_competition': l.fd_competition}
            for l in leagues
        ])
    except Exception as e:
        import traceback
        print('Error in /api/v1/leagues:', traceback.format_exc())
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@api_v1.route('/leaderboard', methods=['GET'])
@jwt_required
def api_leaderboard(user_id):
    users = db.session.query(
        User.id, User.username, func.sum(Prediction.points_awarded).label('score')
    ).outerjoin(Prediction).group_by(User.id).order_by(func.sum(Prediction.points_awarded).desc().nullslast()).all()
    return jsonify([
        {'id': u.id, 'username': u.username, 'score': u.score or 0}
        for u in users
    ])

@api_v1.route('/user/<int:uid>/stats', methods=['GET'])
@jwt_required
def api_user_stats(user_id, uid):
    preds = Prediction.query.filter_by(user_id=uid).all()
    total = len(preds)
    correct = sum(1 for p in preds if p.match and p.match.result == p.predicted_result)
    return jsonify({'user_id': uid, 'total_predictions': total, 'correct_predictions': correct})

@api_v1.route('/team/<int:tid>/stats', methods=['GET'])
@jwt_required
def api_team_stats(user_id, tid):
    matches = Match.query.filter((Match.home_team_id == tid) | (Match.away_team_id == tid)).all()
    played = len(matches)
    wins = 0
    losses = 0
    draws = 0
    for m in matches:
        if not m.result:
            continue
        home_score, away_score = map(int, m.result.split('-'))
        if m.home_team_id == tid:
            if home_score > away_score:
                wins += 1
            elif home_score < away_score:
                losses += 1
            else:
                draws += 1
        elif m.away_team_id == tid:
            if away_score > home_score:
                wins += 1
            elif away_score < home_score:
                losses += 1
            else:
                draws += 1
    return jsonify({'team_id': tid, 'played': played, 'wins': wins, 'losses': losses, 'draws': draws}) 