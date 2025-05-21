from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from engines import requests_engine
from models.ORM import JWT, DBConnection, DBResponse, AIResponse
from Status import Status
from config_log import logger


class RequestsManager():
    async def _commitNewRequest(self, new_request: JWT | DBConnection | DBResponse | AIResponse):
        async_session = sessionmaker(requests_engine, expire_on_commit=False, class_=AsyncSession)

        async with async_session() as session:
            async with session.begin():
                session.add(new_request)
                await session.flush()
                await session.refresh(new_request)

        return new_request.id

    async def _getRecordData(self, record_id: int, record_model: JWT | DBConnection | DBResponse | AIResponse, username: str, success_fields: list[str]):
        async_session = sessionmaker(requests_engine, expire_on_commit=False, class_=AsyncSession)

        async with async_session() as session:
            result = await session.get(record_model, record_id)
            if result is None or result.username != username:
                response = {"error": "record ID does not exist!"}
            else:
                if result.status == Status.SUCCESS.value:
                    success_properties_dict = {field: getattr(result, field) for field in success_fields}
                    response = {"status": result.status, **success_properties_dict}
                elif result.status == Status.PENDING.value:
                    response = {"status": result.status}
                else:
                    response = {"status": result.status, "failure_reason": result.failure_reason}

        return response

    async def createSignUpJWTRequest(self, name: str, email: str, username: str):
        new_jwt_request = JWT(
            name=name,
            email=email,
            username=username,
            status=Status.PENDING.value
        )

        record_id = await self._commitNewRequest(new_jwt_request)

        return record_id

    async def createSignInJWTRequest(self, username: str):
        new_jwt_request = JWT(
            username=username,
            status=Status.PENDING.value
        )

        record_id = await self._commitNewRequest(new_jwt_request)

        return record_id

    async def createDBConnectionRequest(self, username: str, uri:str = ""):
        new_db_connection_request = DBConnection(
            username=username,
            uri=uri,
            status=Status.PENDING.value
        )

        record_id = await self._commitNewRequest(new_db_connection_request)

        return record_id

    async def createDBResponseRequest(self, username: str, db_query: str):
        new_db_response_request = DBResponse(
            username=username,
            db_query=db_query,
            status=Status.PENDING.value
        )

        record_id = await self._commitNewRequest(new_db_response_request)

        return record_id

    async def createAIResponseRequest(self, username: str, ai_query: str):
        new_ai_response_request = AIResponse(
            username=username,
            ai_query=ai_query,
            status=Status.PENDING.value
        )

        record_id = await self._commitNewRequest(new_ai_response_request)

        return record_id

    async def getJWTResponse(self, record_id: int):
        async_session = sessionmaker(requests_engine, expire_on_commit=False, class_=AsyncSession)

        async with async_session() as session:
            result = await session.get(JWT, record_id)
        
        jwt_response = {"status": result.status, "failure_reason": result.failure_reason, "jwt": result.jwt, "has_uri": result.has_uri}
        return jwt_response

    async def getRequestStatus(self, record_id: int, topic: str, username: str):
        if topic == "connect_db":
            response = await self._getRecordData(record_id, DBConnection, username, [])
        elif topic == "query_db":
            response = await self._getRecordData(record_id, DBResponse, username, ["result", "result_type"])
        elif topic == "query_ai":
            response = await self._getRecordData(record_id, AIResponse, username, ["responder", "response", "db_response_id"])
            if response.get("responder") == "DB":
                response = await self._getRecordData(response["db_response_id"], DBResponse, username, ["result", "result_type", "db_query"])
                response = {**response, "responder": "DB"}
            elif response.get("responder") == "AI":
                response = {"status": response["status"], "response": response["response"], "responder": "AI"}
        else:
            response = {"error": "topic name does not exist!"}

        return response
