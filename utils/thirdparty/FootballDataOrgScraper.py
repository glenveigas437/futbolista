import os
import requests
from settings import FOOTBALL_DATA_API_KEY
from app.models import Team, League  # Add this import
from app import db  # Add this import

class FootballDataOrgScraper:
    API_BASE_URL = "https://api.football-data.org/v4"

    def __init__(self):
        self.headers = {"X-Auth-Token": FOOTBALL_DATA_API_KEY}

    def fetch_matches_for_team(self, team_name):
        # 1. Get team from DB
        team = Team.query.filter(Team.name.ilike(team_name)).first()
        if not team:
            return []
        team_id = team.fd_team_id
        if not team_id:
            return []
        # 2. Get league and fd_competition
        league = League.query.get(team.league_id) if team.league_id else None
        fd_competition = league.fd_competition if league and league.fd_competition else None
        # 3. Build matches URL with competition filter if available
        matches_url = f"{self.API_BASE_URL}/teams/{team_id}/matches"
        if fd_competition:
            matches_url += f"?competitions={fd_competition}"
        resp = requests.get(matches_url, headers=self.headers)
        if resp.status_code != 200:
            return []
        matches_data = resp.json().get("matches", [])
        matches = []
        for m in matches_data:
            home_team = m["homeTeam"]["name"]
            away_team = m["awayTeam"]["name"]
            date = m["utcDate"][:10]  # YYYY-MM-DD
            result = None
            if m.get("score") and m["score"].get("fullTime"):
                ft = m["score"]["fullTime"]
                if ft["home"] is not None and ft["away"] is not None:
                    result = f"{ft['home']}-{ft['away']}"
            matches.append({
                "home_team": home_team,
                "away_team": away_team,
                "date": date,
                "result": result
            })
        return matches 