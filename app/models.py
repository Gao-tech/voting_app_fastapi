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
    TECH_SUPPORT= "Tech-Support"
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

class Experience(ExperienceBase, table=True):
    id: int = Field(default=None, primary_key=True)
    applicant: "Applicant" = Relationship(back_populates="experience")

class ApplicantPositionBase(SQLModel):
    position_1: PositionChoice | None = None
    position_2: PositionChoice | None = None
    Applicant_id: int | None = Field(default=None, foreign_key="applicant.id")

    @field_validator("position_1", "position_2", mode="before")
    def title_case_position(cls, value, values, field):
        positions = [values.get("posotion_1"), values.get("position_2")]
        posiitons = [pos.title() if pos else None for pos in positions]

        values["position_1"], values["position_2"] = positions

        if positions[1] == posiitons[0]:
            values["posiiton_2"] = None

        return values[field.name]

class ApplicantPosition(ApplicantPositionBase, table=True):
    id: int = Field(default=None, primary_key=True)
    applicant: "Applicant" = Relationship(back_populates="positions")

class ApplicantBase(SQLModel):
    fname: str = Field(index=True)
    lname: str = Field(index=True)
    email: EmailStr = Field(index=True)
    status: StatusChoice =Field(default="Pending", index=True)  
    department: DepartmentChoice = Field(index=True)
    published: bool = False
    user_id: int = Field(default=None, foreign_key="user.id", unique=True)
    # disabled: bool | None = False 
    
    @field_validator("status", mode="before")
    def title_case_status(cls, value):
        return value.title()

class ApplicantCreate(ApplicantBase):
    experience: list[Experience] | None = None
    
    #using raw SQL to setup created_at in DB or use sqlmodel to set up in class
class Applicant(ApplicantBase, table=True):
    id: int = Field(default=None, primary_key=True) 
    experience: list[Experience] = Relationship(back_populates="applicant")
    positions: list[PositionChoice] = Relationship(back_populates="applicant")
    user: "User" = Relationship(back_populates="applicant")
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    #the Field's default_factory argument ensures that every time an Applicant instance is created without 
    # a specified created_at value, the field is automatically populated with the current UTC datetime.

    class Config:                # update to the pydantic V2.
        from_attributes = True

class ApplicantUpdate(SQLModel):
    fname: str | None = None
    lname: str | None = None
    email: EmailStr | None = None
    positions: PositionChoice | None = None
    status: StatusChoice | None = None
    published: bool | None = False
    department: DepartmentChoice | None = None


class UserBase(SQLModel):
    fname: str
    lname: str
    email: EmailStr 
    
class UserCreate(UserBase):
    password: str    

class UserLogin(UserBase):
    pass

class User(UserBase, table=True):
    id: int = Field(default=None, primary_key=True)
    applicant: "Applicant" = Relationship(back_populates = "user")
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))

