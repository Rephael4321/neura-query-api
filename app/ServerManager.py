from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from models.ORM import User, Login
from drivers.AlternatingMetadataKeywords import AlternatingMetadataKeywords
from drivers.SQL import SQLDriver
from datetime import timedelta
from auth import hash_password, create_access_token, verify_password
from ai.AI import AI
from config import ACCESS_TOKEN_EXPIRE_MINUTES
from config_log import logger

class ServerManager():
    def __init__(self):
        self.username = ""
    
    def setUsername(self, username: str) -> None:
        self.username = username

    async def _queryDB(self, db_provider: str, db_uri: str, db_query: str) -> dict:
        sql_driver = SQLDriver(db_uri)

        db_queries_list = db_query.split(";")
        if db_queries_list[-1].strip() == "":
            db_queries_list.pop()
        db_queries_list = list(map(lambda command: command.strip() + ";", db_queries_list))

        success_rate = 0
        for db_query in db_queries_list:
            result = await sql_driver.execute(db_query)
            if result["result"] == "success":
                success_rate += 1
        logger.info(f"Execution success rate: {success_rate} out of {len(db_queries_list)} executed successfully. USERNAME: {self.username}")

        db_query = db_query.upper()
        for keyword in AlternatingMetadataKeywords:
            if db_query.find(keyword.name) != -1:
                metadata = await self.fetchMetadata(db_uri)
                result["metadata"] = metadata
                break

        return result

    async def signUp(self, engine: AsyncEngine, name: str, email: str, username: str, password: str) -> dict:
        async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

        async with async_session() as session:
            async with session.begin():
                existing_email = await session.execute(select(User).where(User.email == email))
                if existing_email.scalar_one_or_none():
                    raise ValueError(f"email {email} already registered!")
                user = User(name=name, email=email)
                session.add(user)
                await session.flush()

                existing_user = await session.execute(select(Login).where(Login.username == username))
                if existing_user.scalar_one_or_none():
                    raise ValueError(f"username {username} already registered!")
                login = Login(username=username, password=hash_password(password), user=user)
                session.add(login)
                await session.commit()

        access_token = create_access_token(data={"sub": username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        return {"access_token": access_token, "token_type": "bearer"}

    async def signIn(self, engine: AsyncEngine, username: str, password: str) -> dict:
        async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

        async with async_session() as session:
            result = await session.execute(select(Login).where(Login.username == username))
            login = result.scalar_one_or_none()
            if login is None:
                raise ValueError(f"username or password are incorrect!")
            else:
                hashed_password = login.password
            verified_password = verify_password(password, hashed_password)
            if (not verified_password):
                raise ValueError(f"username or password are incorrect!")

        access_token = create_access_token(data={"sub": login.username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        return {"access_token": access_token, "token_type": "bearer"}

    async def getProvider(self, db_uri: str) -> str:
        sql_driver = SQLDriver(db_uri)
        return await sql_driver.getProvider()

    async def fetchMetadata(self, db_uri: str) -> list[str]:
        sql_driver = SQLDriver(db_uri)

        metadata = await sql_driver.fetchMetadata()
        metadata = [repr(table) for table in metadata]
        return metadata

    async def queryDB(self, db_provider: str, db_uri: str, db_query: str) -> dict:
        logger.info(f"DB query: {db_query}. USERNAME: {self.username}")
        result = await self._queryDB(db_provider, db_uri, db_query)
        return {"result": result, "command": db_query}

    async def queryAI(self, metadata: list[str], db_provider: str, query: str, db_uri: str) -> dict:
        logger.info(f"User AI query: {query}. USERNAME: {self.username}")
        ai = AI()
        response = await ai.route_prompt(metadata, db_provider, query)
        logger.info(f"AI response: {response}. USERNAME: {self.username}")
        if response["responder"] == "DB":
            result = await self._queryDB(db_provider, db_uri, response["content"])
            return {"result": result, "command": response["content"]}
        return {"result": {"result": "success", "type": "str", "message": response["content"]}, "command": ""}
