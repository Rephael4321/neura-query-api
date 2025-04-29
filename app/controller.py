from fastapi import APIRouter, Depends, HTTPException
from ServerManager import ServerManager
from models.PydanticModels import SignupUser, SigninUser, URI, DBQuery, AIQuery
from auth import get_current_user
from engine import engine
from dbKit import DBKitManager
from config_log import logger

db_kit_manager = DBKitManager()
router = APIRouter()

@router.get("/ping")
async def ping() -> dict:
    return {"message": "pong from neura query fastapi sever"}

@router.post(
        path="/sign_up",
        responses={
            400: {"description": "email *email* already registered!"},
            400: {"description": "username *username* already registered!"}
            }
        )
async def signUp(
    user: SignupUser,
    manager: ServerManager = Depends()
    ) -> dict:
    """Sign up new user"""

    try:
        access_token = await manager.signUp(engine, user.name, user.email, user.username, user.password)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    db_kit_manager.setKit(user.username)

    return access_token

@router.post(
        path="/sign_in",
        responses={
            400: {"description": "Exception, can't fetch metadata. *e*. USERNAME: *username*"},
            400: {"description": "username or password are incorrect!"},
            }
        )
async def signIn(
    user: SigninUser,
    manager: ServerManager = Depends()
    ) -> dict:
    """Sign in existing user"""

    username = user.username
    
    try:
        response = await manager.signIn(engine, user.username, user.password)
        db_kit_manager.setKit(username)
        if response["has_db_uri"]:
            manager.setUsername(username)
            db_uri = await manager.getDbUri(engine, username)
            db_kit = db_kit_manager.getKit(username)
            db_kit.setProvider(await manager.getProvider(db_uri))
            try:
                metadata = await manager.fetchMetadata(db_uri)
                db_kit.setMetadata(metadata)
            except Exception as e:
                logger.error(f"Exception, can't fetch metadata. {e}. USERNAME: {username}")
                raise HTTPException(
                    status_code=400,
                    detail=str(e)
                )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    return response

@router.post(
    path="/connect_db",
        responses={
            400: {"description": "password authentication failed for user *db_owner*"},
            400: {"description": "database *db_name* does not exist"},
            400: {"description": "database *database* does not exist!"},
            400: {"description": "unknown host!"},
            400: {"description": "username or password are incorrect!"},
            400: {"description": "connection failed, no respond for too long! check your connection details (port, host, etc.)"},
            }
)
async def connectDB(
    uri: URI,
    user: dict = Depends(get_current_user),
    manager: ServerManager = Depends()
    ) -> dict:
    """Connect your DB with NeuraQuery"""

    username = user["sub"]
    db_uri = uri.uri
    manager.setUsername(username)
    db_kit = db_kit_manager.getKit(username)

    try:
        db_kit.setProvider(await manager.getProvider(uri.uri))
        await manager.addDbUri(engine, username, db_uri)
        response = await manager.fetchMetadata(db_uri)
    # Non existing provider
    except UnboundLocalError as e:
        logger.error(f"UnboundLocalError, can't fetch metadata. {e}. USERNAME: {username}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    # Invalid username or password
    except ValueError as e:
        logger.error(f"ValueError, can't fetch metadata. {e}. USERNAME: {username}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    # May happen after trying to use supabase with wrong credentials
    except TimeoutError as e:
        logger.error(f"TimeoutError, can't fetch metadata. {e}. USERNAME: {username}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Exception, can't fetch metadata. {e}. USERNAME: {username}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    db_kit.setMetadata(response)

    return {"message": "metadata fetched successfully"}

@router.post(
    path="/query_db",
)
async def queryDB(
    db_query: DBQuery,
    user: dict = Depends(get_current_user),
    manager: ServerManager = Depends()
    ) -> dict:
    """Query your database with db query"""

    username = user["sub"]
    manager.setUsername(username)
    db_kit = db_kit_manager.getKit(username)
    db_uri = await manager.getDbUri(engine, username)
    provider = db_kit.getProvider()

    try:
        response = await manager.queryDB(provider, db_uri, db_query.query)
        if response["result"].get("metadata"):
            db_kit.setMetadata(response.pop("metadata"))
    except Exception as e:
        logger.error(f"Exception, query DB failed. {e}. USERNAME: {username}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    return response

@router.post(
    path="/query_ai",
)
async def queryAI(
    ai_query: AIQuery,
    user: dict = Depends(get_current_user),
    manager: ServerManager = Depends()
    ) -> dict:
    """Query AI for db query"""

    username = user["sub"]
    manager.setUsername(username)
    db_kit = db_kit_manager.getKit(username)
    db_uri = await manager.getDbUri(engine, username)
    provider = db_kit.getProvider()
    metadata = db_kit.getMetadata()

    try:
        response = await manager.queryAI(metadata, provider, ai_query.query, db_uri)
        if response["result"].get("metadata"):
            db_kit.setMetadata(response.pop("metadata"))
    except Exception as e:
        logger.error(f"Exception, query AI failed. {e}. USERNAME: {username}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    return response
