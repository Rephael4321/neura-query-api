from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import update
from engines import requests_engine
from models.ORM import JWT, DBConnection, DBResponse, AIResponse
from Status import Status

class RequestsManager():
    async def _commitNewRequest(self, new_request: JWT | DBConnection | DBResponse | AIResponse):
        async_session = sessionmaker(requests_engine, expire_on_commit=False, class_=AsyncSession)

        async with async_session() as session:
            async with session.begin():
                session.add(new_request)
                await session.flush()
                await session.refresh(new_request)

        return new_request.id

    async def _retrieveRequestData(self, record_id: int, request_model: JWT | DBConnection | DBResponse | AIResponse) -> list:
        async_session = sessionmaker(requests_engine, expire_on_commit=False, class_=AsyncSession)

        async with async_session() as session:
            result = await session.get(request_model, record_id)
        
        return result

    async def retrieveJWTData(self, record_id: int) -> list:
        result = await self._retrieveRequestData(record_id, JWT)
        return result

    async def retrieveDBConnectionData(self, record_id: int) -> list:
        result = await self._retrieveRequestData(record_id, DBConnection)
        return result

    async def createDBResponseRequest(self, username: str, db_query: str):
        new_db_response_request = DBResponse(
            username=username,
            db_query=db_query,
            status=Status.PENDING.value
        )

        record_id = await self._commitNewRequest(new_db_response_request)

        return record_id

    async def retrieveDBResponseData(self, record_id: int) -> list:
        result = await self._retrieveRequestData(record_id, DBResponse)
        return result

    async def retrieveAIResponseData(self, record_id: int) -> list:
        result = await self._retrieveRequestData(record_id, AIResponse)
        return result

    async def insertJWT(self, record_id: int, jwt: str, has_uri: str):
        async_session = sessionmaker(requests_engine, expire_on_commit=False, class_=AsyncSession)

        async with async_session() as session:
            async with session.begin():
                await session.execute(
                    update(
                        JWT
                    ).where(
                        JWT.id == record_id
                    ).values(
                        jwt=jwt,
                        has_uri=has_uri,
                        status=Status.SUCCESS.value
                    )
                )

    async def markFailedRecord(self, record_id: int, record_model: JWT | DBConnection | DBResponse | AIResponse, failure_reason: str):
        async_session = sessionmaker(requests_engine, expire_on_commit=False, class_=AsyncSession)

        async with async_session() as session:
            async with session.begin():
                await session.execute(
                    update(
                        record_model
                    ).where(
                        record_model.id == record_id
                    ).values(
                        failure_reason=failure_reason,
                        status=Status.FAILED.value
                    )
                )

    async def markSuccessDBConnectionRecord(self, record_id: int):
        async_session = sessionmaker(requests_engine, expire_on_commit=False, class_=AsyncSession)

        async with async_session() as session:
            async with session.begin():
                await session.execute(
                    update(
                        DBConnection
                    ).where(
                        DBConnection.id == record_id
                    ).values(
                        status=Status.SUCCESS.value
                    )
                )

    async def markSuccessDBResponseRecord(self, record_id: int, result: str, result_type: str):
        async_session = sessionmaker(requests_engine, expire_on_commit=False, class_=AsyncSession)

        async with async_session() as session:
            async with session.begin():
                await session.execute(
                    update(
                        DBResponse
                    ).where(
                        DBResponse.id == record_id
                    ).values(
                        result=result,
                        result_type=result_type,
                        status=Status.SUCCESS.value
                    )
                )

    async def markSuccessAIResponseRecord(self, record_id: int, responder: str, db_response_id: int = None, response: str = None):
        async_session = sessionmaker(requests_engine, expire_on_commit=False, class_=AsyncSession)

        async with async_session() as session:
            async with session.begin():
                await session.execute(
                    update(
                        AIResponse
                    ).where(
                        AIResponse.id == record_id
                    ).values(
                        responder=responder,
                        db_response_id=db_response_id,
                        response=response,
                        status=Status.SUCCESS.value
                    )
                )
