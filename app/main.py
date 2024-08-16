# import psycopg2
# from psycopg2.extras import RealDictCursor
from fastapi import FastAPI
from .routers import applicant, user
from app.db import init_db

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield
    

app = FastAPI(lifespan=lifespan)

app.include_router(applicant.router)
app.include_router(user.router)

    
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
]    


