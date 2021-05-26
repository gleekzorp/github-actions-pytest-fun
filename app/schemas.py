from typing import List
from pydantic import BaseModel


class TodoBase(BaseModel):
    title: str
    complete: bool


class TodoCreate(TodoBase):
    pass

    class Config:
        schema_extra = {
            "example": {
                "title": "Buy Milk",
                "complete": False
            }
        }


class Todo(TodoBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class Todos(BaseModel):
    todos: List[Todo] = []


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    todos: List[Todo] = []

    class Config:
        orm_mode = True


class UserDelete(BaseModel):
    message: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str
    id: int
