import jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException,status
from datetime import datetime, timedelta, timezone
from sqlmodel import Session, select
from .models import TokenData, User
from .db import get_session
from .config import settings

oauth2_schema = OAuth2PasswordBearer(tokenUrl="login")


# SECRET_KEY
# Algorithm
# Expriation time

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPERIE_MINUTES = settings.access_token_expire_minutes

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc)+timedelta(ACCESS_TOKEN_EXPERIE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)

    return encoded_jwt
    
def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("user_id")
        if id is None:
            raise credentials_exception
        token_data = TokenData(id=id)  # here to extract id only but can do more.
    except jwt.PyJWKError:
        raise credentials_exception
    
    return token_data

#to protect the endpoint. Login to verify if it is a valid user.
def get_current_user(token: str=Depends(oauth2_schema), session: Session=Depends(get_session)):
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                                         detail=f"Could not validate credentials", 
                                         headers={"WWW-Authenticate": "Bearer"})
    
    token = verify_access_token(token, credential_exception)
    user = session.exec(select(User).where(User.id==token.id)).first()

    return user
