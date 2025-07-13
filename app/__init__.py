from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from settings import SECRET_KEY, SQLALCHEMY_DATABASE_URI


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

from .models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from .views import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .api import api_v1 as api_v1_blueprint
    app.register_blueprint(api_v1_blueprint, url_prefix="/api/v1")

    return app 