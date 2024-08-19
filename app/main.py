from fastapi import FastAPI
from app.routers import auth, vote
from .routers import applicant, user
from app.db import init_db
from pydantic import BaseSettings

class Settings(BaseSettings):
    database_password: str = "locolhost"
    database_username: str = "postgress"
    secret_key: str= "fdsfifjdi23r3"

settings = Settings()
print(settings.database_password)

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(applicant.router)
app.include_router(user.router)
app.include_router(vote.router)
app.include_router(auth.router)

 


