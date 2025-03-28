from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine("postgresql+asyncpg://myuser:mypassword@postgres_for_neura_query:5432/neura_query")
