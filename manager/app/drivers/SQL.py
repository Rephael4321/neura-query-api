from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import ResourceClosedError, ProgrammingError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.schema import Table
from sqlalchemy import MetaData
from sqlalchemy import text
import decimal
import re

class SQLDriver():
    def __init__(self, uri):
        self.engine = create_async_engine(uri)
    
    def _convert_row(self, row):
        return {
            key: float(value) if isinstance(value, decimal.Decimal) else value
            for key, value in row.items()
        }

    async def getProvider(self):
        return self.engine.dialect.name

    async def execute(self, query: str) -> dict:
        async_session = sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession)

        async with async_session() as session:
            try:
                result = await session.execute(text(query))
                rows = [self._convert_row(row) for row in result.mappings().all()]
                result = {
                    "result": "success",
                    "type": "list",
                    "message": rows
                    }
            except ResourceClosedError:
                await session.commit()
                result = {
                    "result": "success",
                    "type": "str",
                    "message": "Query executed successfully"
                    }
            except ProgrammingError:
                result = {
                    "result": "failed",
                    "type": "str",
                    "message": "Command execution failed"
                    }
            return result

    async def fetchMetadata(self) -> list[Table]:
        try:
            metadata_tables = []
            async with self.engine.begin() as connection:
                metadata = MetaData()
                await connection.run_sync(metadata.reflect)

                for item in metadata.tables.items():
                    metadata_tables.append(item[1])

                return metadata_tables
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
