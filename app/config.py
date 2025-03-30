import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 180))
ENVIRONMENT = os.getenv("ENVIRONMENT", "DEV")
if ENVIRONMENT == "DEV":
    CORS_ADDRESS = os.getenv("DEV_CORS_ADDRESS", "http://localhost:3000")
    DB = os.getenv("DEV_DB", "localhost")
elif ENVIRONMENT == "PROD":
    CORS_ADDRESS = os.getenv("PROD_CORS_ADDRESS", "https://www.neuraquery.io")
    DB = os.getenv("PROD_DB", "postgres_for_neura_query")
