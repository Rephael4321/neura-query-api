from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import ResourceClosedError, ProgrammingError
from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData
from sqlalchemy import text
import re

class SQLDriver():
    def __init__(self, db_uri):
        self.engine = create_async_engine(db_uri)

    async def execute(self, query: str) -> list[dict]:
        async_session = sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession)

        async with async_session() as session:
            try:
                result = await session.execute(text(query))
                result = [dict(row) for row in result.mappings().all()]
                return result
            except ResourceClosedError:
                await session.commit()
                return [{"message": "Query executed successfully"}]
            except ProgrammingError:
                raise ValueError("Error: Multiple command where given")

    async def fetchMetadata(self) -> list[str]:
        try:
            metadata_tables = []
            async with self.engine.begin() as connection:
                metadata = MetaData()
                await connection.run_sync(metadata.reflect)

                for item in metadata.tables.items():
                    metadata_tables.append(item[1])

                tables = [repr(table) for table in metadata_tables]
                return tables
        except Exception as e:
            # Neon
            if type(e).__name__ == "InternalServerError" and str(e).startswith("password authentication failed"):
                raise ValueError("invalid connection details, check your username, password, or host!")
            elif type(e).__name__ == "InvalidCatalogNameError":
                pattern = r'"(.*?)"'
                match_database = re.search(pattern, str(e))
                database = match_database.group(1)
                raise ValueError(f"database '{database}' does not exist!")
            elif type(e).__name__ == "gaierror":
                raise ValueError("unknown host!")
            elif type(e).__name__ == "InvalidPasswordError":
                raise ValueError("username or password are incorrect!")
            # Supabase
            elif isinstance(e, TimeoutError):
                raise TimeoutError("connection failed, no respond for too long! check your connection details (port, host, etc.)")
            else:
                raise ValueError(e)
