from fastapi import FastAPI, Response, APIRouter, HTTPException, status, Depends
from sqlalchemy import select
from sqlmodel import Session
from ..models import User, Vote, VoteUpdate
from ..db import get_session
from ..oauth2 import get_current_user


router = APIRouter(tags=["Votes"])

# @router.post("/votes/", status_code=status.HTTP_201_CREATED)
# async def get_vote(vote: VoteCreate, session: Session=Depends(get_session), current_user: User=Depends(get_current_user))->Vote:

#     # check_vote = session.exec(select(Vote).where(Vote.app_pos_id==vote.app_pos_id, Vote.user_id==current_user.id)).first()
#     # applicant = session.get(Applicant, applicant_id)

#     check_vote = session.get(Vote, app_pos_id)
#     #Check if the user wants to vote
#     if vote.dir==1:
#         #check if the user has already voted for this specific applicant_position
#         if check_vote:
#             raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
#                                 detail=f"User with ID {current_user.id} has already voted for {vote.app_pos_id} applicant with the position")
#         #check if the user has already voted 5 times
#         total_vote = session.exec(select(Vote).where(Vote.user_id==current_user.id)).all()
#         if len(total_vote) >= 5:
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
#                 detail="User can only vote a maximum of five times, you can remove one previous vote and continue")
        
#         new_vote = Vote(app_pos_id=vote.app_pos_id, user_id=current_user.id, dir=vote.dir)
#         session.add(new_vote)
#         session.commit()
#         session.refresh(new_vote)
#         return {"message":"Vote added successfully"}
    
#     #check if the user wants to remove the vote
#     elif vote.dir==0:
#         #check if the vote exists in the Vote table
#         if check_vote is None:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
#                                 detail=f"Vote for applicant position {vote.app_pos_id} does not exist.")
#         session.delete(check_vote)
#         session.commit()
#         return {"message": "Vote removed successfully"}
    
#     else:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
#                             detail="Invalid direction. Use 1 for upvote and 0 for removing vote.")



@router.post("/votes/", status_code=status.HTTP_201_CREATED)
async def upvote(vote: VoteUpdate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
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
            detail="You can only vote a maximum of five times. Remove a previous vote to continue."
        )
    
    # Create a new vote
    new_vote = Vote(app_pos_id=vote.app_pos_id, user_id=current_user.id, dir=1)
    session.add(new_vote)
    session.commit()
    session.refresh(new_vote)
    
    return {"message": "Vote added successfully"}


@router.delete("/votes/", status_code=status.HTTP_200_OK)
async def remove_vote(vote: VoteUpdate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    # Check if the vote exists and ensure we retrieve a mapped instance
    existing_vote = session.exec(
        select(Vote).where(Vote.app_pos_id == vote.app_pos_id, Vote.user_id == current_user.id)
    ).scalar_one_or_none()  # This ensures the result is either None or a Vote instance
    
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
