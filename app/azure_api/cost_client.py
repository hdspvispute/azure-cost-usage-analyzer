import logging
from datetime import datetime, timedelta
from azure.mgmt.costmanagement import CostManagementClient
from azure.mgmt.costmanagement.models import (
    QueryDefinition,
    QueryTimePeriod,
    QueryDataset,
    QueryAggregation,
    QueryGrouping,
)

logger = logging.getLogger(__name__)


class CostClient:
    """Thin wrapper around Azure Cost Management API."""

    def __init__(self, credential):
        self.client = CostManagementClient(credential)
        logger.info("CostClient initialized.")

    def get_resource_group_cost(self, subscription_id, resource_group_name, days_back=30):
        """
        Retrieve cost data for a resource group for the last N days.

        Args:
            subscription_id: Azure subscription ID.
            resource_group_name: Name of the resource group.
            days_back: Number of days to look back (default 30).

        Returns:
            Query result object, or None if failed/empty.
        """
        try:
            scope = (
                f"/subscriptions/{subscription_id}"
                f"/resourceGroups/{resource_group_name}"
            )
            end_date = datetime.utcnow().date()
            start_date = end_date - timedelta(days=days_back)

            query = QueryDefinition(
                type="Usage",
                timeframe="Custom",
                time_period=QueryTimePeriod(
                    from_property=f"{start_date}T00:00:00Z",
                    to=f"{end_date}T23:59:59Z",
                ),
                dataset=QueryDataset(
                    granularity="None",
                    aggregation={
                        "totalCost": QueryAggregation(name="PreTaxCost", function="Sum")
                    },
                    grouping=[
                        QueryGrouping(type="Dimension", name="ServiceName"),
                        QueryGrouping(type="Dimension", name="ResourceType"),
                    ],
                ),
            )

            result = self.client.query.usage(scope, query)
            row_count = len(result.rows) if result.rows else 0
            logger.info(
                f"Cost query succeeded for '{resource_group_name}', rows: {row_count}."
            )
            return result
        except Exception as e:
            logger.error(
                f"Cost query failed for '{resource_group_name}': {str(e)}",
                exc_info=True,
            )
            return None
