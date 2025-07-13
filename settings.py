import os
from dotenv import load_dotenv

# Load .env file if it exists (won't fail if missing)
load_dotenv()

# Provide fallback values for CI environments
SECRET_KEY = os.environ.get("SECRET_KEY", "ci-secret-key-for-testing-only")
SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI", "sqlite:///:memory:")
FOOTBALL_DATA_API_KEY = os.environ.get("FOOTBALL_DATA_API_KEY", "")
