from fastapi import FastAPI, APIRouter, Path, Query, Response, status, HTTPException, Depends
from sqlalchemy import delete, func
from ..models import Applicant, ApplicantCreate, ApplicantUpdate, ApplicantWithPositions, Experience, Position, PositionWithVotes, StatusURLChoice, User, Vote
from sqlmodel import Session, select
from typing import Annotated
from ..db import get_session
from .. oauth2 import get_current_user
from sqlalchemy.orm import selectinload


router = APIRouter(tags=['Applicants']) #prefix="/posts"


@router.get("/applicants", response_model=list[ApplicantWithPositions])
async def get_applicants(status: StatusURLChoice | None =  None,
                         q: Annotated[str| None, Query(max_length = 20)] = None,
                         session: Session=Depends(get_session)) -> list[ApplicantWithPositions]:

    # Fetch all applicants with their positions pre-loaded
    applicants = session.exec(select(Applicant).options(selectinload(Applicant.position))).all()

    #Query votes for each position
    vote_counts_query=(
        select(Position.id, func.count(Vote.app_pos_id).label("vote_counts"))
        .join(Vote, Vote.app_pos_id == Position.id, isouter=True)
        .group_by(Position.id)
    )
    vote_counts = session.exec(vote_counts_query).all()

    # create a dictionary to map position IDs to their vote counts
    vote_counts_dict = {position_id: vote_count for position_id, vote_count in vote_counts}

    # Initialize the list of applicants to return
    applicant_list = []

    #Filter by status, admin change from pending to approved or rejected
    if status:
        applicants = [app for app in applicants if app.status.value.lower() == status.value]  #In enum status.value to get value

    #iterates over each applicant in the list of applicants retrieved from the database
    for applicant in applicants:
        #query parameter q will search the fullname and positions
        # if q:
        #     applicants= [app for app in applicants if q.lower() in (app.fname +" "+ app.lname).lower() or PositionURLChoice]
        if q and not (q.lower() in (applicant.fname + " " + applicant.lname).lower()):
            continue

         # Assemble positions with vote counts for each applicant
        positions_with_votes =[
            PositionWithVotes(
                id=position.id,
                position=position.position,
                priority=position.priority,
                vote_count=vote_counts_dict.get(position.id, 0)
            ) #The vote_count is retrieved from the vote_counts dictionary

            #For each applicant, iterates through their associated positions.Part of list comprehension
            for position in applicant.position
        ]

        """
    applicant.positions = [
    Position(id=1, name="Position A", priority=1),
    Position(id=2, name="Position B", priority=2)]

    vote_counts = {1: 5, 2: 3}

    positions_with_votes = [
    PositionWithVotes(id=1, name="Position A", priority=1, vote_count=5),
    PositionWithVotes(id=2, name="Position B", priority=2, vote_count=3)
]
"""
    # Create the ApplicantWithPositions object
        applicant_with_positions = ApplicantWithPositions(
            id=applicant.id,
            fname=applicant.fname,
            lname=applicant.lname,
            status=applicant.status.value,
            department=applicant.department,
            email=applicant.email,
            position=positions_with_votes # Include positions with vote counts
        ) 

        applicant_list.append(applicant_with_positions)

    return applicant_list


@router.get("/applicants/{applicant_id}", response_model=ApplicantWithPositions)
def get_applicant(applicant_id: Annotated[int, Path(title="The Applicant ID")],
                  session: Session=Depends(get_session),
                  current_user: User=Depends(get_current_user)) -> ApplicantWithPositions:

    # applicant = session.get(Applicant, applicant_id)
    applicant = session.exec(select(Applicant).where(Applicant.id==applicant_id).options(selectinload(Applicant.position))).first()
    if applicant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The applicant with id {applicant_id} is not found")

    vote_counts_query=(
        select(Position.id, func.count(Vote.app_pos_id).label("vote_counts"))
        .join(Vote, Vote.app_pos_id==Position.id, isouter=True)
        .group_by(Position.id)
    )
    vote_counts = session.exec(vote_counts_query).all()
    # create a dictionary to map position IDs to their vote counts
    vote_counts_dict = {position_id: vote_count for position_id, vote_count in vote_counts}

    positions_with_votes =[
        PositionWithVotes(
            id=position.id,
            position=position.position,
            priority=position.priority,
            vote_count=vote_counts_dict.get(position.id, 0)
        )
        for position in applicant.position
    ]
    applicant_with_positions = ApplicantWithPositions(
        id=applicant.id,
        fname=applicant.fname,
        lname=applicant.lname,
        status=applicant.status.value,
        department=applicant.department,
        email=applicant.email,
        position=positions_with_votes
    )

    return applicant_with_positions


@router.post("/applicants", status_code=status.HTTP_201_CREATED, response_model=Applicant)
async def create_applicant(applicant_data: ApplicantCreate,
                           session: Session=Depends(get_session), 
                           current_user: User=Depends(get_current_user)) -> Applicant: #force user to login to apply to applicant

    # check if an applicant already exists for the current user
    existing_applicant = session.exec(select(Applicant).where(Applicant.user_id==current_user.id)).first()
    if existing_applicant:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Applicant has already exists.")
    
    applicant_data_dict = applicant_data.model_dump() # convert to a dictionary
    position_data =  applicant_data_dict.pop('position', None) #remove position_data
    experience_data = applicant_data_dict.pop('experience', None) #remove experience_data

    new_applicant = Applicant(user_id=current_user.id, **applicant_data_dict) # convert to pydantic model with user.id from TWJ token
    session.add(new_applicant)
    session.commit()  # Commit to generate the applicant.id
    session.refresh(new_applicant)  # Refresh to get the id

    if len(position_data) > 2:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="You can only select up to two positions")

    if len(position_data) == 2:
            if position_data[0]["position"] == position_data[1]["position"]:
                raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Positions must be different.")
            if position_data[0]["priority"] == position_data[1]["priority"]:
                raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Priority must be different.") 

    for experience_data in applicant_data.experience:
        experience_obj = Experience(
            title=experience_data.title, 
            description=experience_data.description, 
            applicant_id=new_applicant.id) # Build relationship with applicant
        session.add(experience_obj)

    for position_data in applicant_data.position:
        position_obj = Position(
            position=position_data.position,
            priority=position_data.priority,
            applicant_id=new_applicant.id)   

        session.add(position_obj)
   
    session.commit()  #after commit() will get id, then refresh to get all the data including primary key
    session.refresh(new_applicant)
    return new_applicant


@router.delete("/applicants/{applicant_id}",status_code=status.HTTP_404_NOT_FOUND)
async def delete_applicant(applicant_id: Annotated[int, Path(title="The Applicant ID")],
                           session: Session=Depends(get_session),current_user: User=Depends(get_current_user)):
    
    applicant = session.get(Applicant, applicant_id)
    if applicant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The applicant with id {applicant_id} is not found")
    
    # Check if the current user is authorized to delete the applicant
    if applicant.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this applicant")

    # Manually delete related records of Experience and Position in the nested tables and then delete appliant
    session.exec(delete(Experience).where(Experience.applicant_id == applicant_id))
    session.exec(delete(Position).where(Position.applicant_id == applicant_id))

    # Delete the applicant

    session.delete(applicant)
    session.commit()
    return Response(status_code=status.HTTP_404_NOT_FOUND)
    

#update function by admin.-> After approval, user can't update. Admin needs to disable user.
@router.patch("/applicants/{applicant_id}", response_model= Applicant)
async def update_applicant(applicant_id: Annotated[int, Path(title="The Applicant ID.")],
                           updated_applicant:ApplicantUpdate,
                           session: Session=Depends(get_session),
                           current_user: User=Depends(get_current_user)) -> Applicant:

    db_applicant = session.get(Applicant, applicant_id)
    if db_applicant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The applicant with id {applicant_id} is not found")

    if db_applicant.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this applicant")

    # convert to a dictionary, #remove position and experiences data for the format issue and will add later
    updated_data = updated_applicant.model_dump(exclude_unset=True)

    # print(f"Updated data: {updated_data}") ## test

    updated_positions = updated_data.pop('position', None)
    updated_experiences = updated_data.pop('experience', None)

    # print(f"Updated experiences extracted: {updated_experiences}") ## test

    for key, value in updated_data.items():
        setattr(db_applicant, key, value)

    # The applicant offers all the postions data, then we don't need to compare new and the ones in db
    if updated_positions:
        #remove from database first
        session.exec(delete(Position).where(Position.applicant_id == db_applicant.id)) 
        # Validate and add new positions
        if len(updated_positions) > 2:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="You can only select up to two positions")

        if len(updated_positions) == 2:
            if updated_positions[0]["position"] == updated_positions[1]["position"]:
                raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Positions must be different.")
            if updated_positions[0]["priority"] == updated_positions[1]["priority"]:
                raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Priority must be different.") 

        # add updated positions
        for pos in updated_positions:
            new_position = Position(
                position=pos["position"],
                priority=pos["priority"],
                applicant_id=db_applicant.id
            )
            session.add(new_position)

    # Update the experiences if provided
    if updated_experiences:
        # Clear existing experiences
        session.exec(delete(Experience).where(Experience.applicant_id == db_applicant.id))
        # print(f"Updating experiences:{updated_experiences}") ## test

        # Add new experiences
        for exp in updated_experiences:
            new_experience = Experience(
                title=exp["title"],
                description=exp["description"],
                applicant_id=db_applicant.id
            )
            session.add(new_experience)

    session.add(db_applicant)
    session.commit()
    session.refresh(db_applicant)
    
    return db_applicant



