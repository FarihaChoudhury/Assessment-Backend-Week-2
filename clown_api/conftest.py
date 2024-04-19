"""This file contains fixtures for testing the API."""

import pytest

from app import app


@pytest.fixture
def fake_clown():
    """Returns an example clown as a dict."""
    return {"clown_id": 17,
            "clown_name": "Bernice",
            "speciality_id": 3}


@pytest.fixture
def test_app():
    """Returns a test version of the API."""
    return app.test_client()


@pytest.fixture
def fake_data():
    """Returns an example clown as a dict."""
    return {"clown_id": 18,
            "clown_name": "Fariha",
            "speciality_id": 3}


@pytest.fixture
def fake_review():
    """Returns an example review as a dict."""
    return {"score": 4}


@pytest.fixture
def fake_invalid_review():
    """Returns an example review as a dict."""
    return {"score": 6}
