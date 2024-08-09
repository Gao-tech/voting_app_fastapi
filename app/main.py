import datetime
from fastapi import FastAPI, HTTPException, Path, Query, Response, status
from typing import Annotated
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, time
from app.schemas import StatusURLChoice, ApplicantBase, ApplicantCreate, ApplicantWithID, Experience


app = FastAPI()
    

while True:
    try:
        conn = psycopg2.connect(host='localhost', database='voting_fastapi',user='postgres',
                                password='root',cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print('Database connection was successful')
        break
    except Exception as error:
        print("Connecting to database failed")
        print("Error:", error)
        time.sleep(2)


post_applicants = [{
   "applicant_id": 1,
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
   "applicant_id": 2,
   "fname": "Lucy",
   "lname": "Chen",
   "email": "lucy@gmail.com",
   "position": "Vice_President",
   "status": "approved",
   "department":"Technology",
   "published": False,
   
}]    


@app.get("/")
async def root():
    return {"message": "welcome to my api"}


@app.get("/applicants")
async def get_applicants(status: StatusURLChoice | None =  None,
                        #  q: Annotated[str| None, Query(max_length = 20)] = None 
                         ) -> list[ApplicantWithID]:
    # cursor.execute("""SELECT * FROM applicants""")
    # applicants = cursor.fetchall()
    # return {"message": applicants}
    applicant_list = [ApplicantWithID(**app) for app in post_applicants] # here convert dict into an instance of 'Applicant' Class
    if status:
        applicant_list = [app for app in applicant_list if app.status.value.lower() == status.value]  #In enum status.value to get value
    
    if q:
        # app.fullname = app.fname + app.lname
        # print(app.fullname)
        applicant_list = [app for app in applicant_list if q.lower() in app.fname.lower()]

    return applicant_list


@app.get("/applicants/{applicant_id}")
def get_applicant(applicant_id: Annotated[int, Path(title="The Applicant ID")]) -> ApplicantWithID:
    # cursor.execute("""SELECT * FROM applicants WHERE id = %s""", str(applicant_id))
    # applicant = cursor.fetchone()
    # if applicant is None:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The applicant with id {applicant_id} is not found")
    # return {"applicant_detail": applicant}
    try:
        applicant = next(app for app in post_applicants if app["applicant_id"] == applicant_id)
        return ApplicantWithID(**applicant)

    except StopIteration:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The applicant with id {applicant_id} is not found")


@app.post("/applicants", status_code=status.HTTP_201_CREATED)
async def create_applicant(applicant_data: ApplicantCreate) -> ApplicantWithID:
    # cursor.execute("""INSERT INTO applicants(fname, lname, email, position, status, published) VALUES(%s,%s,%s,%s,%s,%s) RETURNING *""",(applicant_data.fname, applicant_data.lname, applicant_data.email, applicant_data.position, applicant_data.status, applicant_data.published))
    # new_applicant = cursor.fetchone()
    # conn.commit()
    # return {"data": new_applicant}

    id = post_applicants[-1]["applicant_id"] + 1
    applicant = ApplicantWithID(applicant_id=id, **applicant_data.model_dump()).model_dump()
    post_applicants.append(applicant)
    return applicant

    
    # applicant = ApplicantWithID(fname = applicant_data.fname, lname =applicant_data.lname, 
    #                             email=applicant_data.email, position=applicant_data.position, 
    #                             status=applicant_data.status, published=applicant_data.published,
    #                             department=applicant_data.department)
    # post_applicants.append(applicant)
    # if applicant_data.experience:
    #     for experience in applicant_data:
    #         experience_obj = Experience(title=applicant_data.title, description=applicant_data.description)


@app.delete("/applicants/{applicant_id}")
async def delete_applicant(applicant_id: Annotated[int, Path(title="The Applicant ID")]):
    # cursor.execute("""DELETE FROM applicants WHERE id = %s returning *""", (applicant_id,))
    # deleted_applicant = cursor.fetchone()
    # conn.commit()
    # if deleted_applicant is None:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The applicant with id {applicant_id} is not found")
    # return Response(status_code=status.HTTP_204_NO_CONTENT)
    pass

@app.put("/applicants/{applicant_id}")
async def update_applicant(applicant_id: Annotated[int, Path(title="The Applicant ID")],
                           applicant:ApplicantWithID):
    # cursor.execute("""UPDATE applicants SET status = %s, published = %s WHERE id = %s RETURNING*""",
    #                 (applicant.status, applicant.published, str(applicant_id)))
    # updated_applicant = cursor.fetchone()
    # conn.commit()
    # if updated_applicant is None:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The applican with id {applicant_id} is not found")
    # return {"data": updated_applicant}
    pass