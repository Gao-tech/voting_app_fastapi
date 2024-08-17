from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from ..db import get_session
from ..models import User, Token
from ..utils import hash, verify
from ..oauth2 import create_access_token

router = APIRouter(tags=["Authentication"])

# UserLogin -> OAuth2PasswordRequestForm: store into two fields: username, password.-> here username is email
@router.post("/login", response_model=Token)
def login(user_credentials: OAuth2PasswordRequestForm=Depends(), session: Session=Depends(get_session)):
    user = session.exec(select(User).where(User.email==user_credentials.username)).first()

    if not user:    #email doesn't exist
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")
    
    if not verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")
    
    # create a token -> return token
    access_token = create_access_token(data = {"user_id": user.id})   # add user_id as the payload
    
    return {"access_token": access_token,"token_type": "bearer"}
