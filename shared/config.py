import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
ENVIRONMENT = os.getenv("ENVIRONMENT", "DEV")
PORT = int(os.getenv("PORT", 8888))
DB_HOST = os.getenv("DB_HOST", "postgres")
if ENVIRONMENT == "DEV":
    CORS_ADDRESS = os.getenv("DEV_CORS_ADDRESS", "http://localhost:3000")
elif ENVIRONMENT == "PROD":
    CORS_ADDRESS = os.getenv("PROD_CORS_ADDRESS", "https://www.neuraquery.io")
