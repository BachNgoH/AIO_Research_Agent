import sys
from fastapi import FastAPI
from dotenv import load_dotenv
from api.controller import router
from fastapi.middleware.cors import CORSMiddleware

load_dotenv(override=True)
app = FastAPI()

@app.get("/")
async def root():
    return {
        "message": "Hello World!",
    }

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


app.include_router(router, prefix="/v1")