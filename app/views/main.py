from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..models import Team, Match, Prediction
import requests
from sqlalchemy import desc
# from ..api.v1 import jwt_required  # No longer needed for page routes
from flask import jsonify

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('base.html')

@main.route('/teams', methods=['GET', 'POST'])
def teams():
    if request.method == 'POST':
        team_name = request.form.get('team_name')
        if team_name:
            # Call the API endpoint to search and add the team
            api_url = url_for('api_v1.api_search_and_add_team', _external=True)
            resp = requests.post(api_url, json={'team_name': team_name})
            if resp.status_code == 200:
                flash(f"Team '{team_name}' added or already exists.", 'success')
            else:
                flash(f"Could not add team: {resp.json().get('error', 'Unknown error')}", 'danger')
        return redirect(url_for('main.teams'))

    # Classic pagination and search
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 5))
    search = request.args.get('search', '').strip()
    query = Team.query
    if search:
        query = query.filter(Team.name.ilike(f'%{search}%'))
    # Order by favourite first, then name ascending
    pagination = query.order_by(desc(Team.favourite), Team.name).paginate(page=page, per_page=per_page, error_out=False)
    teams = pagination.items
    return render_template('teams.html', teams=teams, pagination=pagination, search=search)

@main.route('/matches')
def matches():
    teams = Team.query.order_by(desc(Team.favourite), Team.name).all()
    favourite_teams = [t for t in teams if t.favourite]
    return render_template('matches.html', teams=teams, favourite_teams=favourite_teams)

@main.route('/leaderboard')
def leaderboard():
    predictions = Prediction.query.all()
    # Leaderboard logic placeholder
    return render_template('leaderboard.html', predictions=predictions)

@main.route('/your-predictions')
def your_predictions():
    return render_template('your_predictions.html')

@main.route('/stats')
def stats():
    return render_template('stats.html') 