from fastapi import FastAPI, Response, APIRouter, HTTPException, status, Depends
from sqlalchemy import select
from sqlmodel import Session
from ..models import Position, User, Vote, VoteUpdate
from ..db import get_session
from ..oauth2 import get_current_user


router = APIRouter(tags=["Votes"])

@router.post("/votes/", status_code=status.HTTP_201_CREATED)
async def upvote(vote: VoteUpdate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):

 #Check if the applicant_postion exisits in the Postion table
    positin = session.exec(select(Position).where(Position.id==vote.app_pos_id)).first()
    if not positin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The Applicant with position of ID {vote.app_pos_id} doesn't exit.")

    # Check if the vote already exists
    existing_vote = session.exec(
        select(Vote).where(Vote.app_pos_id == vote.app_pos_id, Vote.user_id == current_user.id)
    ).first()
    
    if existing_vote:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User {current_user.id} has already voted for position {vote.app_pos_id}."
        )
    
    # Check if user has reached the vote limit
    total_votes = session.exec(
        select(Vote).where(Vote.user_id == current_user.id)
    ).all()
    
    if len(total_votes) >= 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can only vote a maximum of five times. Remove a previous vote to continue.")
    
    # Create a new vote
    new_vote = Vote(app_pos_id=vote.app_pos_id, user_id=current_user.id)
    session.add(new_vote)
    session.commit()
    session.refresh(new_vote)
    
    return {"message": "Vote added successfully"}


@router.delete("/votes/", status_code=status.HTTP_200_OK)
async def remove_vote(vote: VoteUpdate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    # Check if the vote exists and ensure we retrieve a mapped instance
    existing_vote = session.exec(
        select(Vote).where(Vote.app_pos_id == vote.app_pos_id, Vote.user_id == current_user.id)
    ).scalar_one_or_none()  
    # is designed to return a mapped instance or None, ensuring compatibility with operations like session.delete()
    
    if not existing_vote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vote for position {vote.app_pos_id} by user {current_user.id} does not exist."
        )

    # Delete the existing vote
    try:
        session.delete(existing_vote)
        session.commit()
    except TypeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error. Expected a Vote instance but got something else."
        )
    return {"message": "Vote removed successfully"}
