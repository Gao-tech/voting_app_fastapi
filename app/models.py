import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator
from sqlmodel import SQLModel, Field, Relationship


class StatusURLChoice(str, Enum): # for query parameters
    PENDING = "pending"
    APPROVED = "approved"
    REJECT = "reject"

class StatusChoice(str, Enum): # for database and POST when sending and getting data
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECT = "Reject"

class PositionURLChoice(str, Enum):  # for query parameters
    PRESIDENT = "president"
    VICE_PRESIDENT = "vice-president"
    OMBUDMAN = "ombudman"
    COMMUNICATOR = "communicator"
    TECH_SUPPORT= "tech_support"
    FINANCE_OFFICER = "finance-officer"

class PositionChoice(str, Enum):  # for database and POST when sending and getting data
    PRESIDENT = "President"
    VICE_PRESIDENT = "Vice-President"
    OMBUDMAN = "Ombudman"
    COMMUNICATOR = "Communicator"
    TECH_SUPPORT= "Tech_Support"
    FINANCE_OFFICER = "Finance-Officer"

class DepartmentChoice(str, Enum):
    CULTURE = "Culture"
    HEALTH = "Health"
    TEACHING = "Teaching"
    TECHNOLOGY = "Technology"


class ExperienceBase(SQLModel):
    title: str
    description: str = Field(None, max_length=100)
    applicant_id: int | None = Field(default=None, foreign_key="applicant.id")  
    #default=None sets the default value of applicant_id to None when creating an instance of the Experience model

class Experience(ExperienceBase, table=True):
    id: int = Field(default=None, primary_key=True)
    applicant: "Applicant" = Relationship(back_populates="experience")

class ApplicantBase(SQLModel):
    fname: str
    lname: str
    email: EmailStr
    position: PositionChoice
    status: StatusChoice 
    published: bool = False
    department: DepartmentChoice | None = None
    # disabled: bool | None = False 

class ApplicantCreate(ApplicantBase):
    experience: list[ExperienceBase] | None = None

    @field_validator("status", mode="before")
    def title_case_status(cls, value):
        return value.title()
    
    @field_validator("position", mode="before")
    def title_case_position(cls, value):
        return value.title()
    
    #using raw SQL to setup created_at in DB or use sqlmodel to set up in class
class Applicant(ApplicantBase, table=True):
    id: int = Field(default=None, primary_key=True) 
    experience: list[Experience] = Relationship(back_populates="applicant")

    created_at: datetime.datetime

    class Config:                # update to the pydantic V2    .
        from_attributes = True
    
# class UserBase(SQLModel):
#     fname: str
#     lname: str
#     email: EmailStr
#     password: str

# class UserCreate(UserBase):
#     pass    

# class UserLogin(BaseModel):
#     email: EmailStr

# class User(UserBase, table=True):
#     id : int = Field(default=None, primary_key=True)
#     created_at: datetime