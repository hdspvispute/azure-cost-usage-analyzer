import logging
from azure.mgmt.subscription import SubscriptionClient
from azure.core.exceptions import AzureError

logger = logging.getLogger(__name__)


class AzureSubscriptionClient:
    """Thin wrapper around Azure Subscription Management API."""

    def __init__(self, credential):
        self.client = SubscriptionClient(credential)
        logger.info("AzureSubscriptionClient initialized.")

    def list_subscriptions(self):
        """
        List all subscriptions accessible to the authenticated user.

        Returns:
            list: List of subscription objects, or None if failed.
        """
        try:
            subscriptions = list(self.client.subscriptions.list())
            logger.info(f"Retrieved {len(subscriptions)} subscriptions.")
            return subscriptions
        except AzureError as e:
            logger.error(f"Failed to list subscriptions: {str(e)}", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"Unexpected error listing subscriptions: {str(e)}", exc_info=True)
            return None
