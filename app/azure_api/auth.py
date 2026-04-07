import logging
import os
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import ClientAuthenticationError

logger = logging.getLogger(__name__)


MANAGEMENT_SCOPE = "https://management.azure.com/.default"


def _ensure_azure_cli_on_path():
    """Add common Azure CLI install locations to PATH for local runs."""
    candidates = [
        r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin",
        r"C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin",
        r"C:\azcli\azure-cli-2.77.0-x64\bin",
    ]

    override = os.getenv("AZURE_CLI_PATH")
    if override:
        candidates.append(os.path.dirname(override))

    existing = [p for p in candidates if p and os.path.isdir(p)]
    if not existing:
        return

    current_path = os.environ.get("PATH", "")
    entries = current_path.split(os.pathsep) if current_path else []
    updated = False
    for folder in existing:
        if folder not in entries:
            entries.insert(0, folder)
            updated = True

    if updated:
        os.environ["PATH"] = os.pathsep.join(entries)


def initialize_credentials():
    """
    Initialize Azure credentials using DefaultAzureCredential.
    Attempts multiple auth methods in order: managed identity, Azure CLI, environment.

    Returns:
        DefaultAzureCredential: Authenticated credential object.

    Raises:
        ClientAuthenticationError: If no valid credential source is found.
    """
    try:
        _ensure_azure_cli_on_path()
        credential = DefaultAzureCredential(exclude_interactive_browser_credential=True)
        logger.info("Azure credentials initialized successfully.")
        return credential
    except ClientAuthenticationError:
        logger.error(
            "Failed to initialize Azure credentials. "
            "Ensure Azure CLI is installed and 'az login' has been run."
        )
        raise


def validate_credentials(credential):
    """Validate that a credential can acquire ARM token for live Azure calls."""
    credential.get_token(MANAGEMENT_SCOPE)
    logger.info("Azure credential token acquisition succeeded.")


def get_auth_source_label(credential):
    """Best-effort auth source label for UI messaging."""
    name = credential.__class__.__name__
    if name == "DefaultAzureCredential":
        return "DefaultAzureCredential (Azure CLI or Managed Identity)"
    return name
