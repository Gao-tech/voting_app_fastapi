import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator, model_validator
from pydantic.types import conint
from sqlalchemy import Column
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

class Priority(int, Enum):
    PRIORITY_1 = 1
    PRIORITY_2 = 2

class ExperienceBase(SQLModel):
    title: str
    description: str = Field(None, max_length=100)
    applicant_id: int | None = Field(default=None, foreign_key="applicant.id")  

class Experience(ExperienceBase, table=True):
    id: int = Field(default=None, primary_key=True)
    applicant: "Applicant" = Relationship(back_populates="experience")

# class PositionBase(SQLModel):
#     position: PositionChoice | None = None
#     priority: Priority | None = None
#     applicant_id: int | None = Field(default=None, foreign_key="applicant.id")
    
class PositionBase(SQLModel):
    position: PositionChoice | None = None
    priority: Priority | None = None
    applicant_id: int | None = Field(default=None, foreign_key="applicant.id")

    @field_validator("position", mode="before")
    def title_case_position(cls, value):
        return value.title()

class Position(PositionBase, table=True):
    id: int = Field(default=None, primary_key=True)
    applicant: "Applicant" = Relationship(back_populates="position")
    votes: list["Vote"] = Relationship(back_populates="position")

# Vote model with a foreign key to Position
class VoteBase(SQLModel):
    app_pos_id: int = Field(foreign_key="position.id", primary_key=True, ondelete="CASCADE")
    user_id: int = Field(foreign_key="user.id",primary_key=True, ondelete="CASCADE")
    dir: conint(le=1)  #type: ignore

class Vote(VoteBase, table=True):
    user: "User" = Relationship(back_populates="votes")
    position: Position = Relationship(back_populates="votes")
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))

class ApplicantBase(SQLModel):
    fname: str = Field(index=True)
    lname: str = Field(index=True)
    email: EmailStr = Field(index=True)
    status: StatusChoice =Field(default="Pending", index=True)  
    department: DepartmentChoice = Field(default=None, index=True)
    published: bool = False
    
    @field_validator("status", mode="before")
    def title_case_status(cls, value):
        return value.title()
    
class ApplicantCreate(SQLModel):
    fname: str
    lname: str
    email: EmailStr
    status: StatusChoice = Field(default="Pending")
    department: DepartmentChoice
    published: bool = False
    experience: list[Experience] | None = None
    position: list[Position] | None =  None

class Applicant(ApplicantBase, table=True):
    id: int | None = Field(default=None, primary_key=True) 
    user_id: int = Field(default=None, foreign_key="user.id", ondelete="CASCADE", nullable=False)
    experience: list[Experience] = Relationship(back_populates="applicant")
    position: list[Position] = Relationship(back_populates="applicant")
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
    position: list[PositionChoice] | None = None
    priority: Priority | None = None
    status: StatusChoice | None = None
    published: bool | None = False
    department: DepartmentChoice | None = None
    exprience: str | None =  None

class UserBase(SQLModel):
    fname: str
    lname: str
    email: EmailStr = Field(unique=True)
    
    @field_validator('fname', 'lname', mode="before")
    def validate_and_normalize_name(cls, value):
        if value:
            return value.title()
        return value
    
class UserCreate(UserBase):
    password: str = Field(nullable=False)

class UserShow(UserBase):
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))

class User(UserBase, table=True): # reserved when querying, use "user"
    id: int = Field(default=None, primary_key=True)
    password: str = Field(nullable=False)

    applicant: Optional["Applicant"] = Relationship(back_populates = "user",sa_relationship_kwargs={"uselist": False}) #enhance the relationship one to one
    votes: list["Vote"] = Relationship(back_populates="user")
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))

    @property
    def is_applicant(self) -> bool:
        return self.applicant is not None
    #a way to define a method that acts like an attribute to check whether a user is an applicant without storing an additional field in the database. 
    # The method is computed on the fly whenever it's accessed.

class UserLogin(SQLModel):
    email: EmailStr
    password: str

class Token(SQLModel):
    access_token : str
    token_type: str

class TokenData(BaseModel):
    id: int | None = None
