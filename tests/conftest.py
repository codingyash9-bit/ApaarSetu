"""
Pytest configuration and test fixtures for APAAR Nexus.
"""
import pytest
from app import create_app
from extensions import db


@pytest.fixture
def app():
    """Create and configure a testing app instance."""
    application = create_app("testing")

    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Test client fixture."""
    return app.test_client()
