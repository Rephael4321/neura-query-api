import set_configs
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from controller import router
from config import PORT, ENVIRONMENT, CORS_ADDRESS
from config_log import logger

app = FastAPI(
    title="Neura Query",
    description="Neura Query served by rephael4321",
    version="1.2.3"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[CORS_ADDRESS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "JWT": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header"
        }
    }

    for route in app.routes:
        if getattr(route, "tags", None) and "public" in route.tags:
            continue
        path = route.path
        method = route.methods.pop().lower()
        if path in openapi_schema["paths"] and method in openapi_schema["paths"][path]:
            openapi_schema["paths"][path][method]["security"] = [{"JWT": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == "__main__":
    logger.info(f"FASTAPI RUNNING ON '{ENVIRONMENT}' ENVIRONMENT.")
    logger.info(f"Swagger available on http://localhost:{PORT}/docs#")
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)
