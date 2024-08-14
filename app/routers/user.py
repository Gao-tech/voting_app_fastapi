from typing import Annotated
from fastapi import FastAPI, HTTPException, Path, Response, APIRouter, Depends, status
from app.models import User, UserCreate, UserShow
from app.db import Session, get_session

router = APIRouter(tags=["Users"])

@router.post("/users")
async def post_user(user_data: UserCreate, session: Session=Depends(get_session))-> UserShow:
    user = User.model_validate(user_data)
 
    session.commit()  
    session.refresh(user)
    return user
    

@router.get("/users/{user_id}", status_code=status.HTTP_201_CREATED, response_model=UserShow)
async def get_users(
    user_id: Annotated[int, Path(title="The user id")],
    session: Session=Depends(get_session)) -> UserShow:

    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The applicant with id {user_id} is not found")
    return user



