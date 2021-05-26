from fastapi import FastAPI
from . import models
from .database import engine
from .routers import todo, user, authentication as auth

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(auth.router)
app.include_router(todo.router)
app.include_router(user.router)
