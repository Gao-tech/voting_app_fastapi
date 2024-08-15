from fastapi import FastAPI, Response, APIRouter
from app.models import Vote

router = APIRouter(tags=["Votes"])

@router.post("/votes/")
async def get_vote(vote: Vote):
    pass

