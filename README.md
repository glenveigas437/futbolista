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