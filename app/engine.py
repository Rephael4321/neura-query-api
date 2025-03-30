from sqlalchemy.ext.asyncio import create_async_engine

from config import DB

engine = create_async_engine(f"postgresql+asyncpg://myuser:mypassword@{DB}:5432/neura_query")
