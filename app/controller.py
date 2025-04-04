from fastapi import APIRouter, Depends, HTTPException
from ServerManager import ServerManager
from models.PydanticModels import SignupUser, SigninUser, URI, DBQuery, AIQuery
from auth import get_current_user
from engine import engine
from dbKit import DBKitManager

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
            400: {"description": "username or password are incorrect!"}
            }
        )
async def signIn(
    user: SigninUser,
    manager: ServerManager = Depends()
    ) -> dict:
    """Sign in existing user"""

    try:
        access_token = await manager.signIn(engine, user.username, user.password)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    
    db_kit_manager.setKit(user.username)

    return access_token

@router.post(
    path="/fetch_metadata",
        responses={
            400: {"description": "password authentication failed for user *db_owner*"},
            400: {"description": "database *db_name* does not exist"},
            400: {"description": "database *database* does not exist!"},
            400: {"description": "unknown host!"},
            400: {"description": "username or password are incorrect!"},
            400: {"description": "connection failed, no respond for too long! check your connection details (port, host, etc.)"},
            }
)
async def fetchMetadata(
    uri: URI,
    user: dict = Depends(get_current_user),
    manager: ServerManager = Depends()
    ) -> dict:
    """Fetch metadata of your database"""

    db_kit = db_kit_manager.getKit(user["sub"])
    db_kit.setProvider(manager.getProvider(uri.uri))
    provider = db_kit.getProvider()

    try:
        response = await manager.fetchMetadata(provider, uri.uri)
    # Non existing provider
    except UnboundLocalError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    # Invalid username or password
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    # May happen after trying to use supabase with wrong credentials
    except TimeoutError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
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

    db_kit = db_kit_manager.getKit(user["sub"])
    provider = db_kit.getProvider()

    try:
        response = await manager.queryDB(provider, db_query.uri, db_query.query)
        if response["result"].get("metadata"):
            db_kit.setMetadata(response.pop("metadata"))
    except Exception as e:
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

    db_kit = db_kit_manager.getKit(user["sub"])
    provider = db_kit.getProvider()
    metadata = db_kit.getMetadata()

    try:
        response = await manager.queryAI(metadata, provider, ai_query.query, ai_query.uri)
        if response["result"].get("metadata"):
            db_kit.setMetadata(response.pop("metadata"))
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    return response
