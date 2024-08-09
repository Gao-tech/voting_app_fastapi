from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


class StatusURLChoice(str, Enum): # for query parameters
    PENDING = "pending"
    APPROVED = "approved"
    REJECT = "reject"

class StatusChoice(str, Enum): # for database and POST when sending and getting data
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECT = "Reject"

class PositionChoice(str, Enum):  # for database and POST when sending and getting data
    PRESIDENT = "President"
    VICE_PRESIDENT = "Vice_President"
    OMBUDMAN = "Ombudman"
    COMMUNICATOR = "Communicator"
    TECH_SUPPORT= "Tech_Support"
    FINANCE_OFFICER = "Finance_Officer"

class DepartmentChoice(str, Enum):
    CULTURE = "Culture"
    HEALTH = "Health"
    TEACHING = "Teaching"
    TECHNOLOGY = "Technology"


class Experience(BaseModel):
    title: str
    description: str = Field(None, max_length=100)

class ApplicantBase(BaseModel):
    fname: str
    lname: str
    email: EmailStr

    #using raw SQL to setup created_at in DB or use sqlmodel to set up in class
class Applicant(ApplicantBase):
    # applicant_id: int
    position: PositionChoice 
    status: StatusChoice 
    published: bool = False
    department: DepartmentChoice | None = None
    experience: list[Experience] = []

class ApplicantCreate(Applicant):
    @field_validator("status", mode="before")
    def title_case_status(cls, value):
        return value.title()
    
    @field_validator("position", mode="before")
    def title_case_position(cls, value):
        return value.title()

class ApplicantWithID(Applicant):    
    applicant_id: int

class UserBase(BaseModel):
    fname: str
    lname: str
    email: EmailStr
    password: str

class UserCreate(UserBase):
    pass    

class UserLogin(BaseModel):
    email: EmailStr
