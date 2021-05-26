from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app import schemas, crud, authentication
from app.database import get_db

router = APIRouter(tags=["Users"])


@router.post("/create-user", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db, user=user)


@router.get('/get-user/{user_id}', response_model=schemas.User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    return crud.get_user(db, user_id=user_id)


@router.delete('/delete-user', response_model=schemas.UserDelete)
def delete_user(db: Session = Depends(get_db), current_user: schemas.User = Depends(authentication.get_current_user)):
    return crud.delete_user(db, user_id=current_user.id)
