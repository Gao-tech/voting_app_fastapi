from fastapi import FastAPI, APIRouter, Path, Query, Response, status, HTTPException, Depends
from ..models import Applicant, ApplicantCreate, ApplicantUpdate, Experience, PositionURLChoice, StatusURLChoice, Position, User
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
    if status:
        applicant_list = [app for app in applicant_list if app.status.value.lower() == status.value]  #In enum status.value to get value
    if q:
        applicant_list = [app for app in applicant_list if q.lower() in (app.fname +" "+ app.lname).lower() or PositionURLChoice ]
    #q will search the fullname and positions

    return applicant_list


@router.get("/applicants/{applicant_id}",response_model= Applicant)
def get_applicant(applicant_id: Annotated[int, Path(title="The Applicant ID")],
                  session: Session=Depends(get_session),
                  current_user: User=Depends(get_current_user)) -> Applicant:

    applicant = session.get(Applicant, applicant_id)
    if applicant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The applicant with id {applicant_id} is not found")
    return applicant


#make a new endpoint to make sure to check positions before create applicant.
@router.post("/apply/{applicant_id}", status_code=status.HTTP_201_CREATED)
def apply_for_positions(applicant_id: int, session: Session=Depends(get_session)): 
    # Validate the number of positions the applicant is applying for
    current_positions_count = len(list(session.exec(
        select(Position).where(Position.applicant_id == applicant_id))))
    
   # Validate that the applicant is not applying for more than 2 positions
    if current_positions_count >= 2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="An applicant can only apply for a maximum of two positions.")
    session.commit()
    return {"message": "Positions applied successfully."}


@router.post("/applicants", status_code=status.HTTP_201_CREATED, response_model=Applicant)
async def create_applicant(applicant_data: ApplicantCreate,
                           session: Session=Depends(get_session), 
                           current_user: User=Depends(get_current_user)) -> Applicant: #force user to login to apply to applicant
    
    # Convert applicant_data to a dictionary and add the user_id
    applicant_data_dict = applicant_data.model_dump()  # Convert to dictionary
    applicant_data_dict['user_id'] = current_user.id  # Add user_id to the dictionary
    applicant = Applicant.model_validate(applicant_data_dict)

    session.add(applicant)
    session.commit()  # Commit to generate the applicant.id
    session.refresh(applicant)  # Refresh to get the id

    if applicant.experience:
        for experience in applicant_data.experience:
            experience_obj = Experience(
                title=experience.title, 
                description=experience.description, 
                applicant_id=applicant.id) # build relationship with applicant
            session.add(experience_obj)

    if applicant.position:
        for position_data in applicant_data.position:
            position_obj = Position(
                position=position_data.position,
                priority=position_data.priority,
                applicant_id=applicant.id)   
            session.add(position_obj)
   
    session.commit()  #after commit() will get id, then refresh to get all the data including primary key
    session.refresh(applicant)
    return applicant


@router.delete("/applicants/{applicant_id}",status_code=status.HTTP_404_NOT_FOUND)
async def delete_applicant(applicant_id: Annotated[int, Path(title="The Applicant ID")],
                           session: Session=Depends(get_session),current_user: User=Depends(get_current_user)):
    
    
    applicant = session.get(Applicant, applicant_id)
    if applicant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The applicant with id {applicant_id} is not found")
    if applicant.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this applicant")

    session.delete(applicant)
    session.commit()
    return Response(status_code=status.HTTP_404_NOT_FOUND)
    

# #update function by admin.-> After approval, user can't update. Admin needs to disable user.
# @router.patch("/applicants/{applicant_id}", response_model= Applicant)
# async def update_applicant(applicant_id: Annotated[int, Path(title="The Applicant ID.")],
#                            updated_applicant:ApplicantUpdate,
#                            session: Session=Depends(get_session),
#                            current_user: User=Depends(get_current_user)) -> Applicant:


#     db_applicant = session.get(Applicant, applicant_id)
#     if db_applicant is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The applicant with id {applicant_id} is not found")

#     if db_applicant.user_id != current_user.id and not current_user.is_admin:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this applicant")

#     current_positions_count = len(list(session.exec(
#         select(Position).where(Position.applicant_id == applicant_id))))
    
#     if updated_applicant.position:
#         new_positions_count = len(updated_applicant.position)
#         if current_positions_count + new_positions_count > 2:
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
#                                 detail="An applicant can only apply for a maximum of two positions.")

#     applicant_data_dict = updated_applicant.model_dump(exclude_unset=True) #Convert to dictionary(fields that are not provided in the update)
#     # applicant_data_dict['user_id'] = current_user.id  # Add user_id to the dictionary
#     # applicant = Applicant.model_validate(applicant_data_dict)
#     applicant_data_dict.pop('user_id', None)  # avoid removing user_id from dict if it's there

#     for key, value in applicant_data_dict.items():
#         setattr(db_applicant, key, value)

#     db_applicant = applicant_data_dict

#     # db_applicant.sqlmodel_update(applicant)
#     session.add(db_applicant)
#     session.commit()
#     session.refresh(db_applicant)
    
#     return db_applicant



@router.patch("/applicants/{applicant_id}", response_model=Applicant)
async def update_applicant(
    applicant_id: Annotated[int, Path(title="The Applicant ID.")],
    updated_applicant: ApplicantUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> Applicant:

    # Fetch the existing applicant from the database
    db_applicant = session.get(Applicant, applicant_id)
    if db_applicant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The applicant with id {applicant_id} is not found")

    # Authorization check
    if db_applicant.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this applicant")

    # Check current number of positions for the applicant
    current_positions_count = len(list(session.exec(select(Position).where(Position.applicant_id == applicant_id))))
    
    # Handle position updates
    if updated_applicant.position:
        new_positions_count = len(updated_applicant.position)
        if current_positions_count + new_positions_count > 2:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                                detail="An applicant can only apply for a maximum of two positions.")

    # Convert updated applicant data to dictionary
    applicant_data_dict = updated_applicant.model_dump(exclude_unset=True)
    applicant_data_dict.pop('user_id', None)  # Ensure user_id is not overwritten

    # db_applicant = Applicant.model_validate(applicant_data_dict)

    # Update fields in db_applicant
    for key, value in applicant_data_dict.items():
        if hasattr(db_applicant, key):
            setattr(db_applicant, key, value)

    # Commit changes to the database
    session.add(db_applicant)
    session.commit()
    session.refresh(db_applicant)
    
    return db_applicant
