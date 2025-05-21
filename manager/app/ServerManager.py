from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker, selectinload
from sqlalchemy.future import select
from engines import users_engine
from models.ORM import User, Login, Uri, JWT, DBConnection, DBResponse, AIResponse
from drivers.AlternatingMetadataKeywords import AlternatingMetadataKeywords
from drivers.SQL import SQLDriver
from datetime import timedelta
from auth import hash_password, create_access_token, verify_password
from ai.AI import AI, Responders
from config import ACCESS_TOKEN_EXPIRE_MINUTES
from config_log import logger
from RequestsManager import RequestsManager
from dbKit import DBKitManager
import orjson

class ServerManager():
    def __init__(self):
        self.requestsManager = RequestsManager()
        self.db_kit_manager = DBKitManager()
        self.ai_manager = AI()

    async def _queryDB(self, uri: str, db_query: str, username: str) -> dict:
        sql_driver = SQLDriver(uri)

        db_queries_list = db_query.split(";")
        if db_queries_list[-1].strip() == "":
            db_queries_list.pop()
        db_queries_list = list(map(lambda command: command.strip() + ";", db_queries_list))

        for db_query in db_queries_list:
            result = await sql_driver.execute(db_query)

        db_query = db_query.upper()
        for keyword in AlternatingMetadataKeywords:
            if db_query.find(keyword.name) != -1:
                metadata = await self._fetchMetadata(uri)
                db_kit = self.db_kit_manager.getKit(username)
                if db_kit is None:
                    logger.warning("DB kit for user can't be found. Probably after service manager restart. Please sign in again!")
                    return
                db_kit.setMetadata(metadata)
                break

        return result

    async def _getUserData(self, username: str) -> Login:
        async_session = sessionmaker(users_engine, expire_on_commit=False, class_=AsyncSession)

        async with async_session() as session:
            result = await session.execute(
                    select(Login).where(Login.username == username).options(
                        selectinload(Login.user).selectinload(User.uris)
                    )
                )
            user_data = result.scalar_one_or_none()

        return user_data

    async def _getUri(self, username: str) -> str | None:
        user_data = await self._getUserData(username)
        login_obj = user_data
        user_obj = login_obj.user
        uris = user_obj.uris

        if len(uris) > 0:
            uri = user_data.user.uris[0].uri
            return uri

    async def _getProvider(self, uri: str) -> str:
        sql_driver = SQLDriver(uri)
        return await sql_driver.getProvider()

    async def _addUri(self, username: str, new_uri: str) -> None:
        user_data = await self._getUserData(username)
        user = user_data.user

        async_session = sessionmaker(users_engine, expire_on_commit=False, class_=AsyncSession)

        async with async_session() as session:
            user = await session.merge(user)

            # TODO: Implement multiple db uri per user
            for uri in user.uris:
                await session.delete(uri)

            new_uri = Uri(uri=new_uri, user_id=user.id)
            session.add(new_uri)
            await session.commit()

    async def _fetchMetadata(self, uri: str) -> list[str]:
        sql_driver = SQLDriver(uri)

        metadata = await sql_driver.fetchMetadata()
        metadata = [repr(table) for table in metadata]
        return metadata

    async def signUp(self, record_id: int, password: str) -> dict:
        jwt_data = await self.requestsManager.retrieveJWTData(record_id)
        name = jwt_data.name
        email = jwt_data.email
        username = jwt_data.username

        async_session = sessionmaker(users_engine, expire_on_commit=False, class_=AsyncSession)

        async with async_session() as session:
            async with session.begin():
                existing_email = await session.execute(select(User).where(User.email == email))
                if existing_email.scalar_one_or_none():
                    await self.requestsManager.markFailedRecord(record_id, JWT, f"email {email} already registered!")
                    return
                existing_user = await session.execute(select(Login).where(Login.username == username))
                if existing_user.scalar_one_or_none():
                    await self.requestsManager.markFailedRecord(record_id, JWT, f"username {username} already registered!")
                    return

                user = User(name=name, email=email)
                session.add(user)
                await session.flush()
                login = Login(username=username, password=hash_password(password), user=user)
                session.add(login)
                await session.commit()

        access_token = create_access_token(data={"sub": username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        await self.requestsManager.insertJWT(record_id, access_token, False)
        self.db_kit_manager.setKit(username)

    async def signIn(self, record_id: int, password: str) -> dict:
        jwt_data = await self.requestsManager.retrieveJWTData(record_id)
        username = jwt_data.username
        user_data = await self._getUserData(username)

        if user_data is None:
            await self.requestsManager.markFailedRecord(record_id,  JWT, f"username or password are incorrect!")
            return

        hashed_password = user_data.password
        verified_password = verify_password(password, hashed_password)
        if not verified_password:
            await self.requestsManager.markFailedRecord(record_id, JWT, f"username or password are incorrect!")
            return

        access_token = create_access_token(data={"sub": user_data.username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        db_kit = self.db_kit_manager.setKit(username)
        uri = await self._getUri(username)
        if uri:
            await self.requestsManager.insertJWT(record_id, access_token, True)
            db_kit.setProvider(await self._getProvider(uri))
            db_kit.setMetadata(await self._fetchMetadata(uri))
        else:
            await self.requestsManager.insertJWT(record_id, access_token, False)

    async def connectDB(self, record_id: int):
        db_connection_data = await self.requestsManager.retrieveDBConnectionData(record_id)
        username = db_connection_data.username
        uri = db_connection_data.uri if db_connection_data.uri else self._getUri(username)

        if not uri:
            await self.requestsManager.markFailedRecord(record_id, DBConnection, f"no db uri for user {username}!")
            return

        try:
            db_kit = self.db_kit_manager.getKit(username)
            if db_kit is None:
                await self.requestsManager.markFailedRecord(record_id, DBConnection, "jwt is valid, but user is not singed in. Please sign in again!")
                logger.warning("DB kit for user can't be found. Probably after service manager restart. Please sign in again!")
                return
            db_kit.setProvider(await self._getProvider(uri))
            db_kit.setMetadata(await self._fetchMetadata(uri))
            await self._addUri(username, uri)
            await self.requestsManager.markSuccessDBConnectionRecord(record_id)
        except UnboundLocalError as e:
            await self.requestsManager.markFailedRecord(record_id, DBConnection, f"UnboundLocalError, can't fetch metadata. {e}.")
        except ValueError as e:
            await self.requestsManager.markFailedRecord(record_id, DBConnection, f"ValueError, can't fetch metadata. {e}.")
        except TimeoutError as e:
            await self.requestsManager.markFailedRecord(record_id, DBConnection, f"TimeoutError, can't fetch metadata. {e}.")
        except Exception as e:
            await self.requestsManager.markFailedRecord(record_id, DBConnection, f"Exception, can't fetch metadata. {e}.")

    async def queryDB(self, record_id: int) -> dict:
        db_response_data = await self.requestsManager.retrieveDBResponseData(record_id)
        username = db_response_data.username
        db_query = db_response_data.db_query
        uri = await self._getUri(username)

        if not uri:
            await self.requestsManager.markFailedRecord(record_id, DBResponse, f"Uri not found for user '{username}'")
            logger.error("Error from ServerManager module, queryDB method:")
            logger.error(f"Uri not found for user '{username}'")
            return

        result = await self._queryDB(uri, db_query, username)
        response_type = result["type"]
        if response_type == "list":
            result["message"] = "\x1f".join(orjson.dumps(item).decode("utf-8") for item in result["message"])
        if result["result"] == "success":
            await self.requestsManager.markSuccessDBResponseRecord(record_id, result["message"], response_type)
        else:
            await self.requestsManager.markFailedRecord(record_id, DBResponse, "Command execution failed")

    async def queryAI(self, record_id: int) -> dict:
        ai_response_data = await self.requestsManager.retrieveAIResponseData(record_id)
        username = ai_response_data.username
        ai_query = ai_response_data.ai_query
        db_kit = self.db_kit_manager.getKit(username)
        if db_kit is None:
            await self.requestsManager.markFailedRecord(record_id, AIResponse, "jwt is valid, but user is not singed in. Please sign in again!")
            logger.warning("DB kit for user can't be found. Probably after service manager restart. Please sign in again!")
            return
        provider = db_kit.getProvider()
        metadata = db_kit.getMetadata()

        response = await self.ai_manager.route_prompt(metadata, provider, ai_query)
        responder = response["responder"].upper()
        if responder == Responders.AI.name:
            await self.requestsManager.markSuccessAIResponseRecord(record_id, responder, response=response["content"])
        elif responder == Responders.DB.name:
            db_record_id = await self.requestsManager.createDBResponseRequest(username, response["content"])
            await self.requestsManager.markSuccessAIResponseRecord(record_id, responder, db_response_id=db_record_id)
            await self.queryDB(db_record_id)
        elif responder == Responders.NONE.name:
            await self.requestsManager.markFailedRecord(record_id, AIResponse, response["content"])
