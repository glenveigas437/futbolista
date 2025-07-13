from settings import FOOTBALL_DATA_API_KEY
import requests

class FootballData:
    def __init__(self):
        self.api_base_url = "https://api.football-data.org/v4"
        self.api_key = FOOTBALL_DATA_API_KEY
        self.headers = {"X-Auth-Token": self.api_key}

    def search_team_by_name(self, team_name):
        url = f"{self.api_base_url}/teams?name={team_name}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            data = response.json()
            return data.get("teams", [])
        return []

    def fetch_matches_for_team(self, team_id):
        url = f"{self.api_base_url}/teams/{team_id}/matches"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            data = response.json()
            return data.get("matches", [])
        return [] 