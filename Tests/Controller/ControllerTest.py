import pytest
from unittest.mock import MagicMock, patch
from flask import Flask
from Controller.PantryController import pantry_blueprint

@pytest.fixture
def app():
    """Fixture to create a Flask test app."""
    app = Flask(__name__)
    app.register_blueprint(pantry_blueprint)
    app.testing = True
    return app.test_client()

@patch("Controller.PantryController.get_cached_uid")
@patch("Controller.PantryController.PantryModel")
@patch("Controller.PantryController.db.connect_read")
def test_get_user_pantry_success(mock_connect_read, mock_pantry_model, mock_get_cached_uid, app):
    """Test successful retrieval of pantry items."""
    mock_get_cached_uid.return_value = "test_uid"
    mock_connect_read.return_value = MagicMock()
    mock_pantry_model.return_value.get_user_id_by_firebase_uid.return_value = {"id": 1}
    mock_pantry_model.return_value.get_pantry_items_by_user_id.return_value = [
        {"id": 1, "ingredient_id": 2, "quantity": 5.0, "added_at": "2024-11-28T12:00:00", "ingredient_name": "Sugar"}
    ]

    response = app.get("/user/pantry", headers={"Authorization": "test_token"})

    assert response.status_code == 200
    assert response.json == [
        {"id": 1, "ingredient_id": 2, "quantity": 5.0, "added_at": "2024-11-28T12:00:00", "ingredient_name": "Sugar"}
    ]

def test_get_user_pantry_missing_token(app):
    """Test request with missing Authorization token."""
    response = app.get("/user/pantry")

    assert response.status_code == 401
    assert response.json == {"error": "Authorization token is missing"}

@patch("Controller.PantryController.get_cached_uid")
def test_get_user_pantry_invalid_token(mock_get_cached_uid, app):
    """Test request with an invalid Firebase token."""
    mock_get_cached_uid.return_value = None

    response = app.get("/user/pantry", headers={"Authorization": "invalid_token"})

    assert response.status_code == 401
    assert response.json == {"error": "Invalid or expired Firebase token"}

@patch("Controller.PantryController.get_cached_uid")
@patch("Controller.PantryController.PantryModel")
@patch("Controller.PantryController.db.connect_read")
def test_get_user_pantry_no_items(mock_connect_read, mock_pantry_model, mock_get_cached_uid, app):
    """Test request when no pantry items are found."""
    mock_get_cached_uid.return_value = "test_uid"
    mock_connect_read.return_value = MagicMock()
    mock_pantry_model.return_value.get_user_id_by_firebase_uid.return_value = {"id": 1}
    mock_pantry_model.return_value.get_pantry_items_by_user_id.return_value = []

    response = app.get("/user/pantry", headers={"Authorization": "test_token"})

    assert response.status_code == 404
    assert response.json == {"message": "No pantry items found for this user"}
