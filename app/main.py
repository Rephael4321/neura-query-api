import set_configs
import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from controller import router
from ServerManager import ServerManager

def getManager():
    return ServerManager()

app = FastAPI(
    title="College Project",
    description="College Project served by rephael4321",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://www.neuraquery.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, dependencies=[Depends(getManager)])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8888, reload=True)
