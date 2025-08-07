"""
Pytest configuration and fixtures
"""

import asyncio
from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings
from app.database import Base, get_db
from app.main import app

# Test database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Create test engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create test session
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    # Create tables
    Base.metadata.create_all(bind=engine)

    # Create session
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        # Drop tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session) -> Generator[TestClient, None, None]:
    """Create a test client with dependency overrides."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def test_settings():
    """Get test settings."""
    return get_settings()


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "phone_number": "+1234567890",
        "password": "TestPassword123!",
        "first_name": "Test",
        "last_name": "User",
    }


@pytest.fixture
def sample_message_data():
    """Sample message data for testing."""
    return {"content": "Test message content", "template_name": "test_template"}


@pytest.fixture
def sample_group_data():
    """Sample group data for testing."""
    return {"group_id": -1001234567890, "title": "Test Group", "username": "test_group"}


@pytest.fixture
def sample_schedule_data():
    """Sample schedule data for testing."""
    return {
        "name": "Test Schedule",
        "message_template": "Test message",
        "target_groups": [-1001234567890],
        "schedule_type": "once",
        "scheduled_time": "2024-12-31T23:59:59",
    }


@pytest.fixture
def auth_headers(client, sample_user_data):
    """Get authentication headers for testing."""
    # Register user
    response = client.post("/api/v1/auth/register", json=sample_user_data)
    assert response.status_code == 200

    # Login
    login_data = {
        "phone_number": sample_user_data["phone_number"],
        "password": sample_user_data["password"],
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200

    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def mock_telegram_client():
    """Mock Telegram client for testing."""
    from unittest.mock import Mock

    mock_client = Mock()
    mock_client.is_connected.return_value = True
    mock_client.get_me.return_value = Mock(
        id=123456789, first_name="Test", last_name="Bot", username="test_bot"
    )

    return mock_client


# Async fixtures
@pytest.fixture
async def async_client() -> AsyncGenerator[TestClient, None]:
    """Create an async test client."""
    async with TestClient(app) as test_client:
        yield test_client


# Markers
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.slow = pytest.mark.slow
