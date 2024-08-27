from fastapi import FastAPI, Response, APIRouter, HTTPException, status, Depends
from sqlalchemy import select
from sqlmodel import Session
from ..models import Applicant, Position, User, Vote, VoteCreate
from ..db import get_session
from ..oauth2 import get_current_user


router = APIRouter(tags=["Votes"])

@router.post("/votes/", status_code=status.HTTP_201_CREATED)
async def get_vote(vote: VoteCreate, session: Session=Depends(get_session), current_user: User=Depends(get_current_user))-> Vote:

    #Check if the applicant_postion exisits in the Postion table
    positin = session.exec(select(Position).where(Position.id==vote.app_pos_id)).first()
    if not positin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Applicant with position of ID{vote.app_pos_id} doesn't exit.")

    #Check if the user wants to vote
    if (vote.dir==1):
        #check if the user has already voted for this specific applicant_position
        found_vote = session.exec(select(Vote).where(Vote.app_pos_id==vote.app_pos_id, Vote.user_id==current_user.id))
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                detail=f"User with ID {current_user.id} has already voted for {vote.app_pos_id} applicant with the position")
        #check if the user has already voted 5 times
        total_vote = session.exec(select(Vote).where(Vote.user_id==current_user.id)).all()
        if len(total_vote) >= 5:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                detail="User can only vote a maximum of five times, you can remove one previous vote and continue")
        
        new_vote = Vote(app_pos_id=vote.app_pos_id, user_id=current_user.id, dir=vote.dir)
        session.add(new_vote)
        session.commit()
        session.refresh(new_vote)
        return {"message":"Vote added successfully"}
    
    #check if the user wants to remove the vote
    elif (vote.dir==0):
        #check if the vote exists in the Vote table
        found_vote = session.exec(select(Vote).where(Vote.app_pos_id==vote.app_pos_id, Vote.user_id==current_user.id))
        if found_vote:
            session.delete(found_vote)
            session.commit()
            return {"message": "Vote removed successfully"}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Vote for applicant position {vote.app_pos_id} by user {current_user.id} does not exist")

