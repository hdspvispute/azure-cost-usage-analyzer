"""Tests for app/azure/auth.py — credential initialization."""
import os
import pytest
from unittest.mock import patch, MagicMock
from azure.core.exceptions import ClientAuthenticationError
from app.azure_api.auth import (
    initialize_credentials,
    validate_credentials,
    get_auth_source_label,
    _ensure_azure_cli_on_path,
)


def test_initialize_credentials_success():
    """Happy path: DefaultAzureCredential returns a credential object."""
    mock_cred = MagicMock()
    with patch("app.azure_api.auth.DefaultAzureCredential", return_value=mock_cred) as mock_ctor:
        result = initialize_credentials()
    assert result is mock_cred
    mock_ctor.assert_called_once_with(exclude_interactive_browser_credential=True)


def test_initialize_credentials_raises_on_auth_failure():
    """Auth failure: ClientAuthenticationError is propagated to caller."""
    with patch(
        "app.azure_api.auth.DefaultAzureCredential",
        side_effect=ClientAuthenticationError(message="no credential"),
    ):
        with pytest.raises(ClientAuthenticationError):
            initialize_credentials()


def test_initialize_credentials_logs_success(caplog):
    """Auth success is logged at INFO level."""
    import logging
    mock_cred = MagicMock()
    with patch("app.azure_api.auth.DefaultAzureCredential", return_value=mock_cred):
        with caplog.at_level(logging.INFO, logger="app.azure_api.auth"):
            initialize_credentials()
    assert any("initialized successfully" in r.message for r in caplog.records)


def test_initialize_credentials_logs_error_on_failure(caplog):
    """Auth failure is logged at ERROR level."""
    import logging
    with patch(
        "app.azure_api.auth.DefaultAzureCredential",
        side_effect=ClientAuthenticationError(message="fail"),
    ):
        with caplog.at_level(logging.ERROR, logger="app.azure_api.auth"):
            with pytest.raises(ClientAuthenticationError):
                initialize_credentials()
    assert any("Failed to initialize" in r.message for r in caplog.records)


def test_validate_credentials_requests_management_token():
    """Credential validation should request ARM scope token."""
    mock_cred = MagicMock()
    validate_credentials(mock_cred)
    mock_cred.get_token.assert_called_once_with("https://management.azure.com/.default")


def test_get_auth_source_label_for_default_credential():
    """DefaultAzureCredential gets a friendly source label."""
    class DefaultAzureCredential:
        pass

    label = get_auth_source_label(DefaultAzureCredential())
    assert "DefaultAzureCredential" in label


def test_ensure_azure_cli_on_path_adds_existing_dir(monkeypatch):
    """Helper should prepend discovered Azure CLI directory to PATH."""
    cli_dir = r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin"
    monkeypatch.setenv("PATH", r"C:\Windows\System32")
    monkeypatch.setattr("app.azure_api.auth.os.path.isdir", lambda p: p == cli_dir)
    monkeypatch.delenv("AZURE_CLI_PATH", raising=False)

    _ensure_azure_cli_on_path()

    updated = os.environ["PATH"].split(os.pathsep)
    assert updated[0] == cli_dir
