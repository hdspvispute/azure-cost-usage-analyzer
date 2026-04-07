import logging
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import ClientAuthenticationError

logger = logging.getLogger(__name__)


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
        credential = DefaultAzureCredential()
        logger.info("Azure credentials initialized successfully.")
        return credential
    except ClientAuthenticationError:
        logger.error(
            "Failed to initialize Azure credentials. "
            "Ensure Azure CLI is installed and 'az login' has been run."
        )
        raise
