import logging
from azure.mgmt.resource import ResourceManagementClient
from azure.core.exceptions import AzureError

logger = logging.getLogger(__name__)


class ResourceClient:
    """Thin wrapper around Azure Resource Management API."""

    def __init__(self, credential, subscription_id):
        self.client = ResourceManagementClient(credential, subscription_id)
        logger.info("ResourceClient initialized.")

    def list_resource_groups(self):
        """
        List all resource groups in the subscription.

        Returns:
            list: List of resource group objects, or None if failed.
        """
        try:
            rgs = list(self.client.resource_groups.list())
            logger.info(f"Retrieved {len(rgs)} resource groups.")
            return rgs
        except AzureError as e:
            logger.error(f"Failed to list resource groups: {str(e)}", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"Unexpected error listing resource groups: {str(e)}", exc_info=True)
            return None

    def list_resources_in_group(self, resource_group_name):
        """
        List all resources in a resource group.

        Args:
            resource_group_name: Name of the resource group.

        Returns:
            list: List of resource objects, or None if failed.
        """
        try:
            resources = list(
                self.client.resources.list_by_resource_group(
                    resource_group_name=resource_group_name,
                    filter=None,
                )
            )
            logger.info(f"Listed {len(resources)} resources in '{resource_group_name}'.")
            return resources
        except AzureError as e:
            logger.error(
                f"Failed to list resources in '{resource_group_name}': {str(e)}",
                exc_info=True,
            )
            return None
        except Exception as e:
            logger.error(f"Unexpected error listing resources: {str(e)}", exc_info=True)
            return None
