import logging
from app.azure.cost_client import CostClient
from app.azure.mock_data import get_mock_cost_data

logger = logging.getLogger(__name__)


class CostService:
    """Business logic for cost data processing."""

    def __init__(self, credential, subscription_id):
        self.cost_client = CostClient(credential)
        self.subscription_id = subscription_id

    def get_cost_summary(self, resource_group_name):
        """
        Get processed cost summary for UI: total cost, by-service breakdown, top drivers.

        Args:
            resource_group_name: Name of the resource group.

        Returns:
            dict with keys: total_cost, by_service, by_resource_type, top_drivers, is_mock
        """
        try:
            result = self.cost_client.get_resource_group_cost(
                self.subscription_id, resource_group_name
            )
        except Exception as e:
            logger.error(f"Cost client raised exception: {str(e)}", exc_info=True)
            logger.warning("Cost client error; using mock fallback.")
            return get_mock_cost_data(is_fallback=True)

        if result is None or not result.rows:
            logger.warning("Cost data unavailable or empty; using mock fallback.")
            return get_mock_cost_data(is_fallback=True)

        try:
            summary = self._process_cost_rows(result.rows)
            summary["is_mock"] = False
            return summary
        except Exception as e:
            logger.error(f"Error processing cost data: {str(e)}", exc_info=True)
            logger.warning("Processing failed; falling back to mock data.")
            return get_mock_cost_data(is_fallback=True)

    def _process_cost_rows(self, rows):
        """Aggregate and sort cost rows into summary structure."""
        total = 0.0
        by_service = {}
        by_resource_type = {}
        by_resource_detail = {}

        for row in rows:
            # Expected column order from query grouping: ServiceName, ResourceType, Cost
            service = str(row[0]) if row[0] else "Unknown"
            resource_type = str(row[1]) if row[1] else "Unknown"
            cost = float(row[2]) if row[2] else 0.0

            total += cost
            by_service[service] = by_service.get(service, 0.0) + cost
            by_resource_type[resource_type] = by_resource_type.get(resource_type, 0.0) + cost
            by_resource_detail[resource_type] = by_resource_detail.get(resource_type, 0.0) + cost

        top_drivers = sorted(by_resource_detail.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "total_cost": round(total, 2),
            "by_service": {
                k: round(v, 2)
                for k, v in sorted(by_service.items(), key=lambda x: x[1], reverse=True)
            },
            "by_resource_type": {
                k: round(v, 2)
                for k, v in sorted(by_resource_type.items(), key=lambda x: x[1], reverse=True)
            },
            "top_drivers": [{"name": k, "cost": round(v, 2)} for k, v in top_drivers],
            "is_mock": False,
        }
