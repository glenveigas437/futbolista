# Football Match Predictor & Stats Web App

A modular Flask web application for football fans to view teams, matches, submit predictions, and see leaderboards. Uses MongoDB, Jinja templates, Docker, AWS-ready, and CI/CD with GitHub Actions.

## Structure

```
app/
  __init__.py         # App factory, MongoDB init
  models.py           # MongoDB models/schemas
  views/              # Jinja (HTML) routes
    __init__.py
    main.py
  api/                # REST API routes (JSON)
    __init__.py
    v1.py
  templates/          # Jinja2 HTML templates
    base.html
    teams.html
    matches.html
    leaderboard.html
  static/             # CSS, images, JS

tests/                # Unit tests
  test_basic.py

app.py                # Entrypoint, runs the app
requirements.txt
Dockerfile
README.md
```

## Features
- User authentication
- Football data (teams, matches, predictions)
- Leaderboard
- REST API and Jinja views
- Dockerized, AWS-ready, CI/CD 

## Getting Started

Follow these steps to set up and run the project after forking from GitHub:

### 1. Clone the Repository
```bash
git clone <your-fork-url>
cd futbolista
```

### 2. Set Up a Python Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up PostgreSQL Database
- Make sure PostgreSQL is installed and running.
- Create a database and user (if not already present):

```bash
psql postgres
# In the psql shell, run:
CREATE DATABASE futbolista;
CREATE USER futbolista_user WITH PASSWORD 'bIsEheInPLFduC0Ibcs6t10wIdLoRDZ7';
GRANT ALL PRIVILEGES ON DATABASE futbolista TO futbolista_user;
\q
```

### 5. Configure Environment Variables
- Copy the example or create a `.env` file in the `futbolista` directory:
```
SECRET_KEY=your-secret-key
SQLALCHEMY_DATABASE_URI=postgresql://futbolista_user:bIsEheInPLFduC0Ibcs6t10wIdLoRDZ7@localhost/futbolista
FOOTBALL_DATA_API_KEY=your-football-data-api-key
```

### 6. Restore the Database (Optional, for sample data)
If you want to restore the database with sample data:
```bash
psql -h localhost -U futbolista_user -d futbolista < futbolista_restore_final.sql
```
Or, to create tables and prepopulate:
```bash
python create_tables.py
python prepopulate_db.py
```

### 7. Run the Application
```bash
python app.py
```
- The app will be available at [http://127.0.0.1:5000](http://127.0.0.1:5000)

### 8. Run Tests (Optional)
```bash
pytest
```

## How to Get a Football Data API Key

To use features that require live football data, you need an API key from [Football-Data.org](https://www.football-data.org/):

1. Go to [https://www.football-data.org/](https://www.football-data.org/)
2. Click on "Get your free API Key" or "Sign Up".
3. Register for a free account and verify your email.
4. After logging in, go to your dashboard to find your API key.
5. Copy the API key and add it to your `.env` file as follows:

```
FOOTBALL_DATA_API_KEY=your-football-data-api-key
```

This key is required for the app to fetch live football data from the Football-Data.org API.

---

If you need a step-by-step for a specific OS or want a ready-to-copy README section, let me know! 