import logging
from app.azure.resource_client import ResourceClient
from app.azure.mock_data import get_mock_usage_data

logger = logging.getLogger(__name__)


class UsageService:
    """Business logic for resource usage analysis."""

    def __init__(self, credential, subscription_id):
        self.resource_client = ResourceClient(credential, subscription_id)

    def get_resource_group_usage(self, resource_group_name):
        """
        Get processed resource usage summary for UI.

        Args:
            resource_group_name: Name of the resource group.

        Returns:
            dict with keys: total_count, by_type, resources, is_mock
        """
        resources = self.resource_client.list_resources_in_group(resource_group_name)

        if resources is None:
            logger.warning("Resource list unavailable; using mock fallback.")
            return get_mock_usage_data(is_fallback=True)

        if not resources:
            logger.info(f"Resource group '{resource_group_name}' contains no resources.")
            return {"total_count": 0, "by_type": {}, "resources": [], "is_mock": False}

        try:
            summary = self._process_resources(resources)
            summary["is_mock"] = False
            return summary
        except Exception as e:
            logger.error(f"Error processing resource list: {str(e)}", exc_info=True)
            logger.warning("Processing failed; falling back to mock data.")
            return get_mock_usage_data(is_fallback=True)

    def _process_resources(self, resources):
        """Aggregate resources by type (sorted descending) and build resource list."""
        type_counts = {}
        resource_list = []

        for resource in resources:
            resource_type = getattr(resource, "type", "Unknown") or "Unknown"
            type_counts[resource_type] = type_counts.get(resource_type, 0) + 1
            resource_list.append(
                {
                    "name": getattr(resource, "name", "Unknown"),
                    "type": resource_type,
                    "location": getattr(resource, "location", "Unknown"),
                }
            )

        sorted_types = dict(
            sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
        )

        return {
            "total_count": len(resources),
            "by_type": sorted_types,
            "resources": resource_list,
            "is_mock": False,
        }
