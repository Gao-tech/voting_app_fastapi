from fastapi import FastAPI, APIRouter, Path, Query, Response, status, HTTPException, Depends
from sqlalchemy import delete, func
from ..models import Applicant, ApplicantCreate, ApplicantUpdate, Experience, PositionURLChoice, StatusURLChoice, Position, User, Vote
from sqlmodel import Session, select
from typing import Annotated
from ..db import get_session
from .. oauth2 import get_current_user


router = APIRouter(tags=['Applicants']) #prefix="/posts"


@router.get("/applicants", response_model=list[Applicant])
async def get_applicants(status: StatusURLChoice | None =  None,
                         q: Annotated[str| None, Query(max_length = 20)] = None,
                         session: Session=Depends(get_session)) -> list[Applicant]:

    applicant_list = session.exec(select(Applicant)).all()

    # #Query to calculate total votes for each applicant, according to applied positions
    # query = (select( Position.id.label("position_id"), func.count(Vote.app_pos_id).label("vote_count"))
    #     .join(Vote, Vote.app_pos_id == Position.id, isouter=True)  # Join Vote with Position on app_pos_id
    #     .group_by(Position.id))  # Group by Position_id

    # # Execute the query and fetch the results
    # applicant_list = session.exec(query).all()

    if status:
        applicant_list = [app for app in applicant_list if app.status.value.lower() == status.value]  #In enum status.value to get value
    #q will search the fullname and positions
    if q:
        applicant_list = [app for app in applicant_list if q.lower() in (app.fname +" "+ app.lname).lower() or PositionURLChoice ]

    return applicant_list


@router.get("/applicants/{applicant_id}",response_model= Applicant)
def get_applicant(applicant_id: Annotated[int, Path(title="The Applicant ID")],
                  session: Session=Depends(get_session),
                  current_user: User=Depends(get_current_user)) -> list[Applicant]:

    applicant = session.get(Applicant, applicant_id)
    
    # query = (select(Position.id.label("position_id"),func.count(Vote.app_pos_id).label("vote_count"))
    #     .join(Vote, Vote.app_pos_id == Position.id, isouter=True)  # Join Vote with Position on app_pos_id
    #     .group_by(Position.id))  # Group by Position_id

    # # Execute the query and fetch the results
    # applicant = session.exec(query).first()

    if applicant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The applicant with id {applicant_id} is not found")

    return applicant


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

    new_applicant = Applicant(user_id=current_user.id, **applicant_data_dict)
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
    if applicant.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this applicant")
    
    # Check if the current user is authorized to delete the applicant
    if applicant.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this applicant")

    # Manually delete related records
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
    
    updated_applicant = updated_applicant.model_dump() # convert to a dictionary
    position_data =  updated_applicant.pop('position', None) #remove position_data
    experience_data = updated_applicant.pop('experience', None) #remove experience_data

    updated_applicant = Applicant(user_id=current_user.id, **updated_applicant)
    session.add(new_applicant)
    session.commit()  # Commit to generate the applicant.id
    session.refresh(new_applicant)  # Refresh to get the id

    # check the amount of postions, no more than 2.
    position_query = session.exec(select(Position).where(Position.applicant_id == applicant_id)).all()
    current_positions_count = len(list(position_query))
    if updated_applicant.position:
        new_positions_count = len(updated_applicant.position)
        if current_positions_count + new_positions_count > 2:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                                detail="An applicant can only apply for a maximum of two positions.")
        
    # Replace the existing `db_applicant` with the fields provided in `updated_applicant`
    updated_data = updated_applicant.model_dump(exclude_unset=True)

    for key, value in updated_data.items():
        setattr(db_applicant, key, value)
    if updated_applicant.position:
        db_applicant.position = [Position(**p.model_dump()) for p in updated_applicant.position]

    session.add(db_applicant)
    session.commit()
    session.refresh(db_applicant)
    
    return db_applicant



