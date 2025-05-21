from fastapi import APIRouter, Depends, HTTPException
from models.PydanticModels import SignupUser, SigninUser, URI, DBQuery, AIQuery, RequestStatus
from auth import get_current_user
from dependencies.kafka_producer import getKafkaProducer
from dependencies.requests_manager import getRequestManager
from kafka import KafkaProducer
from RequestsManager import RequestsManager
from Status import Status
import asyncio
from config_log import logger

router = APIRouter()

@router.post(
        path="/sign_up",
        tags=["public"],
        responses={
            400: {"description": "email *email* already registered!"},
            400: {"description": "username *username* already registered!"}
            }
        )
async def sign_up(
    user: SignupUser,
    requestsManager: RequestsManager = Depends(getRequestManager),
    kafkaProducer: KafkaProducer = Depends(getKafkaProducer)
    ) -> dict:
    """Sign up new user"""

    try:
        record_id = await requestsManager.createSignUpJWTRequest(user.name, user.email, user.username)
        data = {"record_id": record_id, "password": user.password}
        kafkaProducer.send("sign_up", value=data)
        kafkaProducer.flush()
        for i in range(10):
            jwt_status = await requestsManager.getJWTResponse(record_id)
            if jwt_status["status"] == Status.SUCCESS.value:
                jwt_token = jwt_status["jwt"]
                break
            elif jwt_status["status"] == Status.FAILED.value:
                raise HTTPException(
                    status_code=400,
                    detail=jwt_status["failure_reason"]
                )
            await asyncio.sleep(1)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    return {"jwt_token": jwt_token}

@router.post(
        path="/sign_in",
        tags=["public"],
        responses={
            400: {"description": "Exception, can't fetch metadata. *e*. USERNAME: *username*"},
            400: {"description": "username or password are incorrect!"},
            }
        )
async def sign_in(
    user: SigninUser,
    requestsManager: RequestsManager = Depends(getRequestManager),
    kafkaProducer: KafkaProducer = Depends(getKafkaProducer)
    ) -> dict:
    """Sign in existing user"""

    try:
        record_id = await requestsManager.createSignInJWTRequest(user.username)
        data = {"record_id": record_id, "password": user.password}
        kafkaProducer.send("sign_in", value=data)
        kafkaProducer.flush()
        for i in range(10):
            jwt_status = await requestsManager.getJWTResponse(record_id)
            if jwt_status["status"] == Status.SUCCESS.value:
                jwt_token = jwt_status["jwt"]
                has_uri = jwt_status["has_uri"]
                break
            elif jwt_status["status"] == Status.FAILED.value:
                raise HTTPException(
                    status_code=400,
                    detail=jwt_status["failure_reason"]
                )
            await asyncio.sleep(1)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    return {"jwt_token": jwt_token, "has_uri": has_uri}

@router.post(
        path="/connect_db",
        tags=["protected"],
        responses={
            400: {"description": "password authentication failed for user *db_owner*"},
            400: {"description": "general exception"},
            }
        )
async def connect_db(
    uri: URI,
    user: dict = Depends(get_current_user),
    requestsManager: RequestsManager = Depends(getRequestManager),
    kafkaProducer: KafkaProducer = Depends(getKafkaProducer)
    ) -> dict:
    """Connect your DB with NeuraQuery"""

    try:
        username = user["sub"]
        uri = uri.uri
        record_id = await requestsManager.createDBConnectionRequest(username, uri)
        data = {"record_id": record_id}
        kafkaProducer.send("connect_db", value=data)
        kafkaProducer.flush()
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    return {"record_id": record_id, "topic_name": "connect_db"}

@router.post(
        path="/query_db",
        tags=["protected"],
        responses={
            400: {"description": "password authentication failed for user *db_owner*"},
            400: {"description": "general exception"},
            }
        )
async def query_db(
    db_query: DBQuery,
    user: dict = Depends(get_current_user),
    requestsManager: RequestsManager = Depends(getRequestManager),
    kafkaProducer: KafkaProducer = Depends(getKafkaProducer)
    ) -> dict:
    """Query your database with db query"""

    username = user["sub"]
    db_query = db_query.query

    try:
        record_id = await requestsManager.createDBResponseRequest(username, db_query)
        data = {"record_id": record_id}
        kafkaProducer.send("query_db", value=data)
        kafkaProducer.flush()
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    return {"record_id": record_id, "topic_name": "query_db"}

@router.post(
        path="/query_ai",
        tags=["protected"],
        responses={
            400: {"description": "query AI failed"}
            }
        )
async def query_ai(
    ai_query: AIQuery,
    user: dict = Depends(get_current_user),
    requestsManager: RequestsManager = Depends(getRequestManager),
    kafkaProducer: KafkaProducer = Depends(getKafkaProducer)
    ) -> dict:
    """Query AI for db query"""

    try:
        username = user["sub"]
        ai_query = ai_query.query
        record_id = await requestsManager.createAIResponseRequest(username, ai_query)
        data = {"record_id": record_id}
        kafkaProducer.send("query_ai", value=data)
        kafkaProducer.flush()
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    return {"record_id": record_id, "topic_name": "query_ai"}

@router.post(
        path="/get_request_status",
        tags=["protected"],
        responses={
            400: {"description": "Exception, can't fetch metadata. *e*. USERNAME: *username*"},
            400: {"description": "username or password are incorrect!"},
            }
        )
async def get_request_status(
    data: RequestStatus,
    user: dict = Depends(get_current_user),
    requestsManager: RequestsManager = Depends(getRequestManager)
    ) -> dict:
    """Get request status"""

    username = user["sub"]
    record_id = data.record_id
    topic_name = data.topic_name
    try:
        request_status = await requestsManager.getRequestStatus(record_id, topic_name, username)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    return request_status
