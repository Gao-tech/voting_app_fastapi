from fastapi import FastAPI
from .routers import applicant, user, auth, vote
from app.db import init_db

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
app.include_router(vote.router)

 


