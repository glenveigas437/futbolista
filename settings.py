import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ.get("SECRET_KEY")
SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
FOOTBALL_DATA_API_KEY = os.environ.get("FOOTBALL_DATA_API_KEY")
