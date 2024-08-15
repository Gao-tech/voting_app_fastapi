from fastapi import FastAPI, APIRouter, Path, Query, Response, status, HTTPException, Depends
from ..models import Applicant, ApplicantCreate, ApplicantPosition, ApplicantUpdate, Experience, PositionChoice, PositionURLChoice, StatusURLChoice, ApplicantPosition
from sqlmodel import Session, select
from typing import Annotated
from ..db import get_session


router = APIRouter(tags=['Applicants'])


@router.get("/applicants")
async def get_applicants(status: StatusURLChoice | None =  None,
                         q: Annotated[str| None, Query(max_length = 20)] = None,
                         session: Session=Depends(get_session)
                         ) -> list[Applicant]:

    applicant_list = session.exec(select(Applicant)).all()
    if status:
        applicant_list = [app for app in applicant_list if app.status.value.lower() == status.value]  #In enum status.value to get value
    
    if q:
        applicant_list = [app for app in applicant_list if q.lower() in (app.fname +" "+ app.lname).lower() or PositionURLChoice ]
    
    #q will search the fullname and positions

    return applicant_list

    # cursor.execute("""SELECT * FROM applicants""")
    # applicants = cursor.fetchall()
    # return {"message": applicants}


@router.get("/applicants/{applicant_id}",response_model= Applicant)
def get_applicant(applicant_id: Annotated[int, Path(title="The Applicant ID")],
                  session: Session=Depends(get_session)) -> Applicant:

    applicant = session.get(Applicant, applicant_id)
    if applicant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The applicant with id {applicant_id} is not found")
    return applicant

    # cursor.execute("""SELECT * FROM applicants WHERE id = %s""", str(applicant_id))
    # applicant = cursor.fetchone()
    # if applicant is None:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The applicant with id {applicant_id} is not found")
    # return {"applicant_detail": applicant}


#make a new endpoint to make sure to check positions before create applicant.
@router.post("/apply/{applicant_id}", status_code=status.HTTP_201_CREATED)
def apply_for_positions(applicant_id: int, session: Session = Depends(get_session)):
    # Validate the number of positions the applicant is applying for
    current_positions_count = len(list(session.exec(
        select(ApplicantPosition).where(ApplicantPosition.applicant_id == applicant_id))))
    
   # Validate that the applicant is not applying for more than 2 positions
    if current_positions_count >= 2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="An applicant can only apply for a maximum of two positions.")
    session.commit()
    return {"message": "Positions applied successfully."}


@router.post("/applicants", status_code=status.HTTP_201_CREATED, response_model=Applicant)
async def create_applicant(applicant_data: ApplicantCreate,
                           session: Session=Depends(get_session)) -> Applicant:
    
    # applicant = Applicant(fname=applicant_data.fname, 
    #                     lname=applicant_data.lname, 
    #                     email=applicant_data.email, 
    #                     position=applicant_data.position, 
    #                     status=applicant_data.status, 
    #                     published=applicant_data.published,
    #                     department=applicant_data.department,
    #                     # disabled=applicant_data.disabled,
    #                     created_at=datetime.now(timezone.utc))
    
    if applicant_data.user_id is None:
        raise HTTPException(status_code=400, detail="user_id must be provided") 
    applicant = Applicant.model_validate(applicant_data)
    
    if applicant_data.experience:
        for experience in applicant_data.experience:
            experience_obj = Experience(
                title=experience.title, 
                description=experience.description, 
                applicant=applicant) # build relationship with applicant
            session.add(experience_obj)

    session.commit()  #after commit() will get id, then refresh to get all the data including primary key
    session.refresh(applicant)
    return applicant

    # cursor.execute("""INSERT INTO applicants(fname, lname, email, position, status, published) VALUES(%s,%s,%s,%s,%s,%s) RETURNING *""",(applicant_data.fname, applicant_data.lname, applicant_data.email, applicant_data.position, applicant_data.status, applicant_data.published))
    # new_applicant = cursor.fetchone()
    # conn.commit()
    # return {"data": new_applicant}


@router.delete("/applicants/{applicant_id}",status_code=status.HTTP_404_NOT_FOUND)
async def delete_applicant(applicant_id: Annotated[int, Path(title="The Applicant ID")],
                           session: Session=Depends(get_session)):
    applicant = session.get(Applicant, applicant_id)
    if applicant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The applicant with id {applicant_id} is not found")
    session.delete(applicant)
    session.commit()
    return Response(status_code=status.HTTP_404_NOT_FOUND)


    # cursor.execute("""DELETE FROM applicants WHERE id = %s returning *""", (applicant_id,))
    # deleted_applicant = cursor.fetchone()
    # conn.commit()
    # if deleted_applicant is None:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The applicant with id {applicant_id} is not found")
    # return Response(status_code=status.HTTP_204_NO_CONTENT)
    

#update function by admin.-> After approval, user can't update. Admin needs to disable user.
@router.patch("/applicants/{applicant_id}", response_model= Applicant)
async def update_applicant(applicant_id: Annotated[int, Path(title="The Applicant ID.")],
                           updated_applicant:ApplicantUpdate,
                           session: Session=Depends(get_session)) -> Applicant:
    db_applicant = session.get(Applicant, applicant_id)

    if db_applicant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The applicant with id {applicant_id} is not found")
    # applicant = Applicant(fname=updated_applicant.fname, 
    #                 lname=updated_applicant.lname, 
    #                 email=updated_applicant.email, 
    #                 position=updated_applicant.position, 
    #                 status=updated_applicant.status, 
    #                 published=updated_applicant.published,
    #                 department=updated_applicant.department,
    #                 # disabled=updated_applicant.disabled,
    #                 created_at=datetime.now(timezone.utc))

    current_positions_count = len(list(session.exec(
        select(ApplicantPosition).where(ApplicantPosition.applicant_id == applicant_id))))
    if "positions" in updated_applicant:
        new_positions = updated_applicant.positions
        if current_positions_count + len(new_positions) > 2:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="An applicant can only apply for a maximum of two positions.")

    applicant = updated_applicant.model_dump(exclude_unset=True)
    db_applicant.sqlmodel_update(applicant)
    session.add(db_applicant)
    session.commit()
    session.refresh(db_applicant)
    
    return db_applicant


    # cursor.execute("""UPDATE applicants SET status = %s, published = %s WHERE id = %s RETURNING*""",
    #                 (applicant.status, applicant.published, str(applicant_id)))
    # updated_applicant = cursor.fetchone()
    # conn.commit()
    # if updated_applicant is None:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The applican with id {applicant_id} is not found")
    # return {"data": updated_applicant}



