import pytest
from unittest.mock import MagicMock
from Model.PantryModel import PantryModel

@pytest.fixture
def mock_db():
    """Fixture to create a mock database connection."""
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    return mock_connection

def test_get_user_id_by_firebase_uid(mock_db):
    """Test retrieving a user ID by Firebase UID."""
    firebase_uid = "test_uid"
    expected_user = {"id": 1}

    # Mock database query result
    mock_db.cursor.return_value.__enter__.return_value.fetchone.return_value = expected_user

    pantry_model = PantryModel(mock_db)
    result = pantry_model.get_user_id_by_firebase_uid(firebase_uid)

    assert result == expected_user
    mock_db.cursor.return_value.__enter__.return_value.execute.assert_called_once_with(
        "SELECT id FROM Users WHERE firebase_uid = %s", (firebase_uid,)
    )

def test_get_pantry_items_by_user_id(mock_db):
    """Test retrieving pantry items by user ID."""
    user_id = 1
    expected_items = [
        {"id": 1, "ingredient_id": 2, "quantity": 5.0, "added_at": "2024-11-28T12:00:00", "ingredient_name": "Sugar"},
        {"id": 2, "ingredient_id": 3, "quantity": 2.5, "added_at": "2024-11-28T12:30:00", "ingredient_name": "Salt"}
    ]

    # Mock database query result
    mock_db.cursor.return_value.__enter__.return_value.fetchall.return_value = expected_items

    pantry_model = PantryModel(mock_db)
    result = pantry_model.get_pantry_items_by_user_id(user_id)

    assert result == expected_items
    mock_db.cursor.return_value.__enter__.return_value.execute.assert_called_once_with(
        """
        SELECT Pantry.id, Pantry.ingredient_id, Pantry.quantity, Pantry.added_at, Ingredients.name AS ingredient_name
        FROM Pantry
        JOIN Ingredients ON Pantry.ingredient_id = Ingredients.id
        WHERE Pantry.user_id = %s
        """,
        (user_id,)
    )
