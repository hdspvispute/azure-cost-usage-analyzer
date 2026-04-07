# Cost Analysis Skill — ACUA

Guidance for implementing cost data retrieval and analysis in Azure Cost & Usage Analyzer using `azure-mgmt-costmanagement` SDK.

## When to Use This Skill

Reference this skill when:
- Implementing the cost data retrieval module (`app/azure_api/cost_client.py`)
- Writing business logic to process and aggregate cost data (`app/services/cost_service.py`)
- Building the cost tab UI in Streamlit (`app/ui/cost_tab.py` or similar)
- Adding cost-related error handling and fallback behavior
- Writing tests for cost data functions
- Troubleshooting cost API calls or data transformations

## Tech Context

- **Azure SDK**: `azure-mgmt-costmanagement` (CostManagementClient)
- **Scope**: Resource group level queries only
- **Time range**: Last 30 days (fixed in v1, no date range selection)
- **Required data**: 
  - Total cost for the resource group
  - Breakdown by service (e.g., Compute, Storage, Networking)
  - Breakdown by resource type (e.g., Virtual Machines, App Service Plans)
  - Top 5 cost drivers by resource
- **Data characteristics**: Cost data from Azure may be delayed 24–48 hours; not real-time

## Rules

1. **All Azure Cost Management API calls must be in `app/azure_api/cost_client.py` only** — never call the Azure SDK from service or UI layers.

2. **Business logic (aggregation, sorting, filtering) must be in `app/services/cost_service.py`** — cost_client.py is a thin wrapper around the SDK; all transformations happen in services.

3. **UI must only call `app/services/cost_service.py` — never call Azure SDK or cost_client directly from Streamlit pages** — Streamlit pages should not import anything from `app/azure`.

4. **Always handle the case where cost data is empty** — new resource groups may have no spend history; show a friendly message like "No cost data available for this resource group yet."

5. **If any API call fails for any reason (network timeout, permission denied, rate limit, service unavailable), fall back to mock data** — import from `app/azure_api/mock_data.py` and log a warning indicating the fallback reason.

6. **Log all API calls and their response status using Python logging** — use `logger.info()` for successful calls and `logger.warning()` or `logger.error()` for failures; omit sensitive data from logs.

7. **Use cache-first reads with explicit refresh** — default to SQLite snapshot reads and fetch fresh Azure data only when user requests refresh.

8. **Document in code and UI that cost data may be delayed up to 48 hours** — do not assume the returned data represents real-time spend; include a timestamp label if possible.

## Implementation Pattern

```python
# app/azure_api/cost_client.py
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
        logger.info("CostClient initialized")
    
    def get_resource_group_cost(self, subscription_id, resource_group_name, days_back=30):
        """
        Retrieve cost data for a resource group for the last N days.
        
        Args:
            subscription_id: Azure subscription ID
            resource_group_name: Name of the resource group
            days_back: Number of days to look back (default 30)
        
        Returns:
            dict: Raw cost query result or None if empty/failed
        
        Raises:
            Exception: Logs exceptions internally; does not raise (caller handles fallback)
        """
        try:
            scope = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}"
            end_date = datetime.utcnow().date()
            start_date = end_date - timedelta(days=days_back)
            
            query = QueryDefinition(
                type="Usage",
                timeframe="Custom",
                time_period=QueryTimePeriod(
                    from_property=f"{start_date}T00:00:00Z",
                    to=f"{end_date}T23:59:59Z"
                ),
                dataset=QueryDataset(
                    granularity="Daily",
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
            logger.info(f"Cost query succeeded for {resource_group_name}, rows: {len(result.rows) if result.rows else 0}")
            return result
        except Exception as e:
            logger.error(f"Cost query failed for {resource_group_name}: {str(e)}", exc_info=True)
            return None


# app/services/cost_service.py
import logging
from app.azure_api.cost_client import CostClient
from app.azure_api.mock_data import get_mock_cost_data

logger = logging.getLogger(__name__)

class CostService:
    """Business logic for cost data processing."""
    
    def __init__(self, credential):
        self.cost_client = CostClient(credential)
    
    def get_cost_summary(self, subscription_id, resource_group_name):
        """
        Get processed cost summary for UI: total cost, top drivers, breakdown.
        
        Args:
            subscription_id: Azure subscription ID
            resource_group_name: Name of the resource group
        
        Returns:
            dict with keys: total_cost, by_service, by_resource_type, top_drivers, is_mock
        """
        # Attempt to fetch live data
        result = self.cost_client.get_resource_group_cost(subscription_id, resource_group_name)
        
        # If API returned None or no rows, use mock fallback
        if result is None or not result.rows:
            logger.warning("Cost data unavailable, using mock fallback data")
            return get_mock_cost_data(is_fallback=True)
        
        # Process and aggregate the result
        try:
            cost_summary = self._process_cost_rows(result.rows)
            cost_summary["is_mock"] = False
            return cost_summary
        except Exception as e:
            logger.error(f"Error processing cost data: {str(e)}", exc_info=True)
            logger.warning("Processing failed, falling back to mock data")
            return get_mock_cost_data(is_fallback=True)
    
    def _process_cost_rows(self, rows):
        """Aggregate and sort cost rows into summary structure."""
        total = 0.0
        by_service = {}
        by_resource = {}
        by_resource_detail = {}
        
        for row in rows:
            cost = float(row[-1]) if row[-1] else 0.0
            total += cost
            service = row[-2] or "Unknown"
            resource = row[-3] or "Unknown"
            
            by_service[service] = by_service.get(service, 0.0) + cost
            by_resource[resource] = by_resource.get(resource, 0.0) + cost
            by_resource_detail[f"{resource}"] = by_resource_detail.get(resource, 0.0) + cost
        
        # Sort and get top 5
        top_drivers = sorted(by_resource_detail.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_cost": round(total, 2),
            "by_service": {k: round(v, 2) for k, v in sorted(by_service.items(), key=lambda x: x[1], reverse=True)},
            "by_resource_type": {k: round(v, 2) for k, v in sorted(by_resource.items(), key=lambda x: x[1], reverse=True)},
            "top_drivers": [{"name": k, "cost": round(v, 2)} for k, v in top_drivers],
            "is_mock": False,
        }


# app/ui/cost_tab.py (Streamlit example)
import streamlit as st
from app.services.cost_service import CostService

if subscription_id and resource_group_name:
    cost_service = CostService(credential)
    summary = cost_service.get_cost_summary(subscription_id, resource_group_name)
    
    st.metric("Total Cost (Last 30 Days)", f"${summary['total_cost']}")
    
    if summary.get("is_mock"):
        st.warning("⚠️ Displaying mock data (live data unavailable)")
    
    if not summary["by_service"]:
        st.info("No cost data available for this resource group yet.")
    else:
        st.subheader("Breakdown by Service")
        st.bar_chart(summary["by_service"])
```

## Expected Output

The `get_cost_summary()` function returns a dictionary with this structure:

```python
{
    "total_cost": 123.45,  # Total spend in USD
    "by_service": {
        "Compute": 87.50,
        "Storage": 25.00,
        "Networking": 10.95,
    },
    "by_resource_type": {
        "Virtual Machines": 80.00,
        "Storage Accounts": 25.00,
        "Load Balancer": 18.45,
    },
    "top_drivers": [
        {"name": "vm-prod-01", "cost": 45.00},
        {"name": "storage-account-1", "cost": 25.00},
        {"name": "app-service-plan", "cost": 20.00},
        {"name": "vm-dev-01", "cost": 18.00},
        {"name": "sql-database", "cost": 15.45},
    ],
    "is_mock": False,  # True if fallback data was used
}
```

When mock fallback is triggered, `is_mock` is set to `True` and the UI displays a visual warning (`st.warning()`).

## Limitations

- **v1 only supports fixed 30-day window** — no date range selection, date range picker will be a future feature
- **No forecasting or cost trend analysis** — only snapshots of spend data
- **No budget alerts or anomaly detection** — the app displays data only, does not warn about overspend
- **No cost breakdown by cost allocation tags** — only service and resource type breakdowns in v1
- **Cost data latency: up to 48 hours** — users must understand that yesterday's costs may not yet be visible

## Common Mistakes

| Mistake | Fix |
|---|---|
| Calling `CostManagementClient` directly from Streamlit pages | Create a thin wrapper in `app/azure_api/cost_client.py` and call service layer (`app/services/cost_service.py`) from UI only. |
| Caching cost data across user sessions | Do not use `@st.cache_data` for cost queries; fetch fresh data every time resource group changes. |
| Not handling empty cost datasets | Check if `result.rows` is empty or None; show a friendly "No cost data available" message instead of crashing. |
| Forgetting to log API calls and failures | Log start/end of API calls with `logger.info()`; log failures with full exception context using `logger.error(exc_info=True)`. |
| Mixing business logic in the Azure client | Keep `cost_client.py` focused on API interaction only; put all aggregation, sorting, and calculations in `cost_service.py`. |
