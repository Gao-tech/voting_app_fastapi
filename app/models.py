import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator
from pydantic.types import conint
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

class VoteBase(SQLModel):
    applicant_position_id: int | None = Field(default=None, foreign_key="applicant.id", primary_key=True)
    user_id: int | None = Field(default=None, foreign_key="user.id", primary_key=True)
    dir: conint(ge=0, le=1)   # type: ignore
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc)) 

class Vote(VoteBase, table=True):
    applicantpostion: "ApplicantPositionBase" = Relationship(back_populates="votes")
    user: "User" = Relationship(back_populates="votes")

class ApplicantPositionBase(SQLModel):
    applicant_id: int | None = Field(default=None, foreign_key="applicant.id", primary_key=True)
    position_id: int | None = Field(default=None, foreign_key="position.id", primary_key=True)

    # position_1: PositionChoice | None = None
    # position_2: PositionChoice | None = None
    
    # @model_validator(mode="before")
    # def validate_and_normalize_positions(cls, values):
    #     pos1 = values.get("position_1")
    #     pos2 = values.get("position_2")
        
    #     # Title-case the positions
    #     if pos1:
    #         values["position_1"] = pos1.title()
    #     if pos2:
    #         values["position_2"] = pos2.title()
        
    #     # If both positions are the same, set position_2 to None
    #     if pos1 and pos2 and pos1 == pos2:
    #         values["position_2"] = None
        
    #     return values   

class ApplicantPosition(ApplicantPositionBase, table=True):
    priority: int = Field(default=None, index=True)  #1 and 2 and will be limited in the code function

    votes: "Vote" = Relationship(back_populates="ApplicantPositionBase")

class PositionBase(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    name: PositionChoice = Field(index=True)

    @field_validator("name", mode="before")
    def title_case_position(cls, value):
        return value.title()

class Position(PositionBase, table=True):
     applicants: list["Applicant"] = Relationship(back_populates="positions", link_model=ApplicantPosition)

class ExperienceBase(SQLModel):
    title: str
    description: str = Field(None, max_length=100)
    applicant_id: int | None = Field(default=None, foreign_key="applicant.id")  

class Experience(ExperienceBase, table=True):
    id: int = Field(default=None, primary_key=True)
    applicant: "Applicant" = Relationship(back_populates="experience")

class ApplicantBase(SQLModel):
    fname: str = Field(index=True)
    lname: str = Field(index=True)
    email: EmailStr = Field(index=True)
    status: StatusChoice =Field(default="Pending", index=True)  
    department: DepartmentChoice = Field(index=True)
    published: bool = False
    user_id: int = Field(default=None, foreign_key="user.id", unique=True)
    
    @field_validator("status", mode="before")
    def title_case_status(cls, value):
        return value.title()

class ApplicantCreate(ApplicantBase):
    experience: list[Experience] | None = None
    
class Applicant(ApplicantBase, table=True):
    id: int = Field(default=None, primary_key=True) 
    experience: list[Experience] = Relationship(back_populates="applicant")
    positions: list[PositionBase] = Relationship(back_populates="applicants", link_model=ApplicantPosition)
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

class UserShow(UserBase):
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))

class User(UserBase, table=True):
    id: int = Field(default=None, primary_key=True)
    # if_applicant: bool = Field(default= False)
    applicant: Optional["Applicant"] = Relationship(back_populates = "user",sa_relationship_kwargs={"uselist": False})
    votes: list["Vote"] = Relationship(back_populates="user")
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))

    @property
    def is_applicant(self) -> bool:
        return self.if_applicant and self.applicant is not None