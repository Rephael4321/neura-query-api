import set_configs
import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from controller import router
from ServerManager import ServerManager
from config import ENVIRONMENT, CORS_ADDRESS

PORT = 8888

def getManager():
    return ServerManager()

app = FastAPI(
    title="Neura Query",
    description="Neura Query served by rephael4321",
    version="1.2.1"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[CORS_ADDRESS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, dependencies=[Depends(getManager)])

if __name__ == "__main__":
    print(f"RUNNING ON '{ENVIRONMENT}' ENVIRONMENT.")
    print(f"Swagger available on http://localhost:{PORT}/docs#")
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)
