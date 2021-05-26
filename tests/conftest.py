import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy_utils import database_exists, create_database, drop_database
from app.database import Base, get_db
from app.main import app
from app.schemas import TodoCreate, UserCreate
from app.crud import create_user, create_todo

SQLALCHEMY_DATABASE_URL = os.environ.get(
    "POSTGRES_URL_TEST", "sqlite:///./test_db.db")

engine = create_engine(SQLALCHEMY_DATABASE_URL)


def get_test_db():
    SessionLocal = sessionmaker(bind=engine)
    test_db = SessionLocal()

    try:
        yield test_db
    finally:
        test_db.close()


@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    """
    Create a clean database on every test case.
    We use the `sqlalchemy_utils` package here for a few helpers in consistently
    creating and dropping the database.
    """
    if database_exists(SQLALCHEMY_DATABASE_URL):
        drop_database(SQLALCHEMY_DATABASE_URL)
    create_database(SQLALCHEMY_DATABASE_URL)  # Create the test database.
    Base.metadata.create_all(engine)  # Create the tables.
    # Mock the Database Dependency
    app.dependency_overrides[get_db] = get_test_db
    yield  # Run the tests.
    drop_database(SQLALCHEMY_DATABASE_URL)  # Drop the test database.


@pytest.fixture
def test_db_session():
    """Returns an sqlalchemy session, and after the test tears down everything properly."""

    SessionLocal = sessionmaker(bind=engine)

    session: Session = SessionLocal()
    yield session
    # Drop all data after each test
    for tbl in reversed(Base.metadata.sorted_tables):
        engine.execute(tbl.delete())
    # put back the connection to the connection pool
    session.close()


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def credentials():
    return {'username': "test1", 'password': "test1"}


@pytest.fixture
def create_single_user(test_db_session, credentials):
    new_user = UserCreate(**credentials)
    return create_user(test_db_session, new_user)


@pytest.fixture
def create_single_todo(test_db_session, create_single_user):
    new_todo = TodoCreate(title="Buy Milk", complete=False)
    return create_todo(db=test_db_session, todo=new_todo, user_id=create_single_user.id)


@pytest.fixture
def login(create_single_user, client, credentials):
    url = '/login'
    payload = {
        "username": credentials.get('username'),
        "password": credentials.get('password')
    }

    response = client.post(url, data=payload)
    return response.json()
