from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from . import models, schemas
from app.authentication import Hash


def create_todo(db: Session, todo: schemas.TodoCreate, user_id: int):
    new_todo = models.Todo(**todo.dict(), owner_id=user_id)
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo


def get_todos(db: Session, user_id: int):
    user_todos = db.query(models.Todo).filter(
        models.Todo.owner_id == user_id).all()
    return {"todos": user_todos}


def toggle_complete(db: Session, todo_id: int, current_user_id):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if current_user_id == todo.owner_id:
        todo.complete = not todo.complete
        db.commit()
        db.refresh(todo)
        return todo
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=f"Not authenticated")


def create_user(db: Session, user: schemas.UserCreate):
    db_user = db_user = db.query(models.User).filter(
        models.User.username == user.username).first()
    if db_user is None:
        new_user = models.User(
            username=user.username, hashed_password=Hash.hash_password(user.password))
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT, detail=f"Username Taken")


def get_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        return db_user
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="User Not Found")


def delete_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return {"message": "User Successfully Deleted"}
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="User Not Found")
