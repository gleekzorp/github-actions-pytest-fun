from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm.session import Session
from app.database import get_db
from app import crud, schemas

pwd_cxt = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = "8e068befd1448a750ee319fc6508b11c06a3e16cd79b0cef17929eaa9a2a4722"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class Hash():
    def hash_password(password: str):
        return pwd_cxt.hash(password)

    def verify_password(plain_password, hashed_password) -> bool:
        return pwd_cxt.verify(plain_password, hashed_password)


def get_current_user(data: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    token_data = verify_token(data, credentials_exception)
    db_user = crud.get_user(db, user_id=token_data.id)
    return db_user



def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('username')
        id: int = payload.get('id')
        if username is None:
            raise credentials_exception
        if id is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username, id=id)
        return token_data
    except JWTError:
        raise credentials_exception