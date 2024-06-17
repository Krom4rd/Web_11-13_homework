import pytest
from fastapi.testclient import TestClient
from fastapi_limiter.depends import RateLimiter
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models.models import Base
from app.database.database import get_db


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


@pytest.fixture(scope="module")
def session():
    """
    Creates an SQLite database session for the duration of the test module.

    This fixture sets up the database, creates all tables, and yields a session
    object for database interaction. The database is dropped after the tests
    are completed.

    Yields:
        Session: A SQLAlchemy session object for database operations.
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module")
def client(session):
    """
    Provides a TestClient instance with an overridden database dependency.

    This fixture overrides the `get_db` dependency in the FastAPI app to use
    the test database session. It yields a TestClient instance for making API
    requests during tests.

    :yields: A TestClient instance for making API requests.
    """
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)


@pytest.fixture(scope="module")
def user():
    """
    Provides a dictionary with sample user data.

    This fixture returns a dictionary containing sample user details such as
    username, email, and password.

    :return: A dictionary with sample user data.
    :rtype: dict
    """
    return {
        "username": "admin",
        "email": "admin@admin.com",
        "password": "newpassword"
    }


@pytest.fixture(scope="function")
def mock_rate_limit(mocker):
    """
    Mocks the RateLimiter dependency to disable rate limiting during tests.

    This fixture uses `mocker` to patch the `RateLimiter` dependency, setting
    its return value to False to effectively disable rate limiting.

    :param mocker: The mocker fixture provided by pytest-mock.
    :type mocker: MockerFixture

    :return: The mock object for the RateLimiter dependency.
    :rtype: Mock
    """
    mock_rate_limit = mocker.patch.object(
        RateLimiter, '__call__', autospec=True
    )
    mock_rate_limit.return_value = False