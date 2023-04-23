import pytest
from pathlib import Path
from httpx import AsyncClient
from pytest import MonkeyPatch
import pytest_asyncio
from sqlalchemy.orm import Session

from app.config import BASE_DIR
from app.main import app
from app.database import Base, engine

mp = MonkeyPatch()
mp.setenv('TESTING', "True")


TEST_DATA_DIR = Path(BASE_DIR, 'tests', 'test_data')


@pytest_asyncio.fixture
async def async_client() -> AsyncClient:
    """
    Async client fixture for testing FastAPI application.

    Returns:
        AsyncClient: An async HTTP client for testing FastAPI applications.
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="function")
def db() -> Session:
    """
    Database session fixture for testing.

    Returns:
        Session: A SQLAlchemy session object for testing database interactions.
    """
    session = Session(autocommit=False, autoflush=False, bind=engine)
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function", autouse=True)
def stdout_format():
    """
    Fixture to print a linebreak before each test.

    This improves readability of test output by separating the output from each test with a linebreak.
    """
    print("")
