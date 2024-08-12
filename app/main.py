import datetime
from fastapi import Depends, FastAPI, HTTPException, Path, Query, Response, status
from typing import Annotated
# import psycopg2
# from psycopg2.extras import RealDictCursor
from datetime import datetime, timezone
from sqlmodel import Session, select
from app.models import PositionURLChoice, StatusURLChoice, Applicant, ApplicantCreate, Experience
from app.db import init_db, get_session

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield
    

app = FastAPI(lifespan=lifespan)

    
# while True:
#     try:
#         conn = psycopg2.connect(host='localhost', database='voting_fastapi',user='postgres',
#                                 password='root',cursor_factory=RealDictCursor)
#         cursor = conn.cursor()
#         print('Database connection was successful')
#         break
#     except Exception as error:
#         print("Connecting to database failed")
#         print("Error:", error)
#         time.sleep(2)


post_applicants = [{
   "id": 1,
   "fname": "Nolan",
   "lname": "John",
   "email": "nolan@gmail.com",
   "position": "President",
   "status": "pending",
   "published": False,
   "department":"Health",
   "experience":[
       {'title': "representative", "description": "two years working at IT"}
       ]}, 
{
   "id": 2,
   "fname": "Lucy",
   "lname": "Chen",
   "email": "lucy@gmail.com",
   "position": "Vice_President",
   "status": "approved",
   "department":"Technology",
   "published": False,
   
}]    



@app.get("/applicants")
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


@app.get("/applicants/{applicant_id}")
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


@app.post("/applicants", status_code=status.HTTP_201_CREATED)
async def create_applicant(applicant_data: ApplicantCreate,
                           session: Session=Depends(get_session)) -> Applicant:
    
    applicant = Applicant(fname=applicant_data.fname, 
                        lname=applicant_data.lname, 
                        email=applicant_data.email, 
                        position=applicant_data.position, 
                        status=applicant_data.status, 
                        published=applicant_data.published,
                        department=applicant_data.department,
                        # disabled=applicant_data.disabled,
                        created_at=datetime.now(timezone.utc))
    session.add(applicant)
    
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


@app.delete("/applicants/{applicant_id}",status_code=status.HTTP_404_NOT_FOUND)
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
@app.put("/applicants/{applicant_id}")
async def update_applicant(applicant_id: Annotated[int, Path(title="The Applicant ID. Updated by Admin")],
                           updated_applicant:Applicant,
                           session: Session=Depends(get_session)) -> Applicant:
    applicant = session.get(Applicant, applicant_id)

    if applicant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The applicant with id {applicant_id} is not found")
    applicant = Applicant(fname=updated_applicant.fname, 
                    lname=updated_applicant.lname, 
                    email=updated_applicant.email, 
                    position=updated_applicant.position, 
                    status=updated_applicant.status, 
                    published=updated_applicant.published,
                    department=updated_applicant.department,
                    # disabled=updated_applicant.disabled,
                    created_at=datetime.now(timezone.utc))
    session.add(applicant)
    session.commit()
    session.refresh(applicant)
    
    return applicant


    # cursor.execute("""UPDATE applicants SET status = %s, published = %s WHERE id = %s RETURNING*""",
    #                 (applicant.status, applicant.published, str(applicant_id)))
    # updated_applicant = cursor.fetchone()
    # conn.commit()
    # if updated_applicant is None:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The applican with id {applicant_id} is not found")
    # return {"data": updated_applicant}



