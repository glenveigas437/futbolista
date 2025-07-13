from app import create_app, db
from app.models import League, Team, Match
from utils.thirdparty.FootballData import FootballData

app = create_app()
football_data = FootballData()

# List of competition codes to fetch (can be expanded)
COMPETITIONS = [
    'PL',    # Premier League
    'BL1',   # Bundesliga
    'SA',    # Serie A
    'PD',    # La Liga
    'FL1',   # Ligue 1
    'DED',   # Eredivisie
]

with app.app_context():
    for comp_code in COMPETITIONS:
        # Fetch competition info
        comp_url = f"https://api.football-data.org/v4/competitions/{comp_code}"
        resp = football_data.headers and football_data.api_key and football_data
        import requests
        r = requests.get(comp_url, headers=football_data.headers)
        if r.status_code != 200:
            print(f"Failed to fetch competition {comp_code}")
            continue
        comp = r.json()
        league_id = comp['id']
        league = League.query.get(league_id)
        if not league:
            league = League(
                id=league_id,
                name=comp['name'],
                website=comp.get('emblem'),
                country=comp.get('area', {}).get('name'),
                fd_competition=comp_code
            )
            db.session.add(league)
            db.session.commit()
        # Fetch teams in this competition
        teams_url = f"https://api.football-data.org/v4/competitions/{comp_code}/teams"
        r = requests.get(teams_url, headers=football_data.headers)
        if r.status_code != 200:
            print(f"Failed to fetch teams for {comp_code}")
            continue
        teams = r.json().get('teams', [])
        for t in teams:
            team_id = t['id']
            team = Team.query.get(team_id)
            if not team:
                team = Team(
                    id=team_id,
                    name=t['name'],
                    logo_url=t.get('crest'),
                    stadium=t.get('venue'),
                    league_id=league_id
                )
                db.session.add(team)
        db.session.commit()
        # Fetch matches for each team
        for t in teams:
            team_id = t['id']
            matches = football_data.fetch_matches_for_team(team_id)
            for m in matches:
                match_id = m.get('id')
                if not match_id:
                    continue
                match = Match.query.get(match_id)
                if not match:
                    home_team_id = m['homeTeam']['id']
                    away_team_id = m['awayTeam']['id']
                    date = m['utcDate'][:10]
                    result = None
                    score = m.get('score', {}).get('fullTime', {})
                    if score.get('home') is not None and score.get('away') is not None:
                        result = f"{score['home']}-{score['away']}"
                    match = Match(
                        id=match_id,
                        home_team_id=home_team_id,
                        away_team_id=away_team_id,
                        date=date,
                        result=result
                    )
                    db.session.add(match)
            db.session.commit()
    print("Database prepopulated with leagues, teams, and matches!") 