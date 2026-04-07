"""Tests for app/azure/auth.py — credential initialization."""
import pytest
from unittest.mock import patch, MagicMock
from azure.core.exceptions import ClientAuthenticationError
from app.azure.auth import initialize_credentials


def test_initialize_credentials_success():
    """Happy path: DefaultAzureCredential returns a credential object."""
    mock_cred = MagicMock()
    with patch("app.azure.auth.DefaultAzureCredential", return_value=mock_cred):
        result = initialize_credentials()
    assert result is mock_cred


def test_initialize_credentials_raises_on_auth_failure():
    """Auth failure: ClientAuthenticationError is propagated to caller."""
    with patch(
        "app.azure.auth.DefaultAzureCredential",
        side_effect=ClientAuthenticationError(message="no credential"),
    ):
        with pytest.raises(ClientAuthenticationError):
            initialize_credentials()


def test_initialize_credentials_logs_success(caplog):
    """Auth success is logged at INFO level."""
    import logging
    mock_cred = MagicMock()
    with patch("app.azure.auth.DefaultAzureCredential", return_value=mock_cred):
        with caplog.at_level(logging.INFO, logger="app.azure.auth"):
            initialize_credentials()
    assert any("initialized successfully" in r.message for r in caplog.records)


def test_initialize_credentials_logs_error_on_failure(caplog):
    """Auth failure is logged at ERROR level."""
    import logging
    with patch(
        "app.azure.auth.DefaultAzureCredential",
        side_effect=ClientAuthenticationError(message="fail"),
    ):
        with caplog.at_level(logging.ERROR, logger="app.azure.auth"):
            with pytest.raises(ClientAuthenticationError):
                initialize_credentials()
    assert any("Failed to initialize" in r.message for r in caplog.records)
