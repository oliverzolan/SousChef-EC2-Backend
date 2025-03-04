import pytest
from unittest.mock import patch, MagicMock
from Config.Fb import initialize_firebase, verify_firebase_token

@patch("Config.FB.Fb.firebase_admin")
@patch("Config.FB.Fb.get_secret")
def test_initialize_firebase(mock_get_secret, mock_firebase_admin):
    """
    Test Firebase initialization with mocked dependencies.
    """
    # Mock the secret returned by get_secret
    mock_get_secret.return_value = {
        "Private-Key": "mock_private_key",
        "Project-Id": "mock_project_id",
        "Project-Key-Id": "mock_key_id",
        "Client-Email": "mock_client_email",
        "Client-Id": "mock_client_id",
        "Auth-URL": "mock_auth_url",
        "Token-Uri": "mock_token_uri",
        "Auth-Provider": "mock_auth_provider",
        "Client-Cert": "mock_client_cert",
    }

    # Mock Firebase admin SDK
    mock_firebase_admin._apps = []

    # Call initialize_firebase
    initialize_firebase()

    # Verify that firebase_admin.initialize_app was called
    mock_firebase_admin.initialize_app.assert_called_once()

    # Verify that get_secret was called with the correct arguments
    mock_get_secret.assert_called_once()


@patch("Config.FB.Fb.auth.verify_id_token")
def test_verify_firebase_token(mock_verify_id_token):
    """
    Test Firebase token verification with mocked Firebase admin auth.
    """
    # Mock the token verification process
    mock_verify_id_token.return_value = {"uid": "mock_firebase_uid"}

    # Call verify_firebase_token with a test token
    id_token = "test_token"
    result = verify_firebase_token(id_token)

    # Verify that the mocked method was called
    mock_verify_id_token.assert_called_once_with(id_token)

    # Assert that the result matches the mocked UID
    assert result == "mock_firebase_uid"


if __name__ == "__main__":
    pytest.main()