from fastapi import FastAPI, Response, APIRouter
from app.models import Vote

router = APIRouter(tags=["Votes"])

