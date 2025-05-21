from sqlalchemy.ext.asyncio import create_async_engine

from config import DB_HOST

requests_engine = create_async_engine(f"postgresql+asyncpg://myuser:mypassword@{DB_HOST}:5432/requests")
