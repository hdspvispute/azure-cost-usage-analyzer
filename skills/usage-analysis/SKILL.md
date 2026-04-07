# Usage Analysis Skill — ACUA

Guidance for implementing resource listing and usage analysis in Azure Cost & Usage Analyzer using `azure-mgmt-resource` SDK.

## When to Use This Skill

Reference this skill when:
- Implementing the resource listing module (`app/azure/resource_client.py`)
- Writing business logic to group and count resources by type (`app/services/usage_service.py`)
- Building the usage tab UI in Streamlit (`app/ui/usage_page.py` or similar)
- Adding resource listing error handling and fallback behavior
- Writing tests for resource enumeration functions
- Troubleshooting resource API calls or grouping logic

## Tech Context

- **Azure SDK**: `azure-mgmt-resource` (ResourceManagementClient)
- **Scope**: Resource group level — list all resources in a single resource group
- **Required data**:
  - Resource name, type, location, provisioning state
  - Grouped counts by resource type
  - Total resource count
- **Data scope**: All Azure resource types (VMs, storage, networking, compute, etc.)

## Rules

1. **All Azure Resource Management API calls must be in `app/azure/resource_client.py` only** — never call the Azure SDK from service or UI layers.

2. **Business logic (counting by type, grouping, sorting) must be in `app/services/usage_service.py`** — resource_client.py is a thin wrapper around the SDK; all transformations happen in services.

3. **UI must only call `app/services/usage_service.py` — never call Azure SDK or resource_client directly from Streamlit pages** — Streamlit pages should not import anything from `app/azure`.

4. **Always handle empty resource groups without crashing** — if a resource group contains zero resources, return an empty/zero summary instead of failing; show a friendly "no resources found" message in the UI.

5. **If API call fails for any reason (network timeout, permission denied, service error), fall back to mock data** — import from `app/azure/mock_data.py` and log a warning indicating the fallback reason.

6. **Log all API calls and their response status using Python logging** — use `logger.info()` for successful calls and `logger.warning()` or `logger.error()` for failures; omit sensitive identifiers from logs.

7. **Sort resource type counts in descending order before returning to UI** — highest-count resource types appear first; enables users to focus on dominant resource patterns immediately.

## Implementation Pattern

```python
# app/azure/resource_client.py
import logging
from azure.mgmt.resource import ResourceManagementClient
from azure.core.exceptions import AzureError

logger = logging.getLogger(__name__)

class ResourceClient:
    """Thin wrapper around Azure Resource Management API."""
    
    def __init__(self, credential):
        self.client = ResourceManagementClient(credential)
        logger.info("ResourceClient initialized")
    
    def list_resources_in_group(self, subscription_id, resource_group_name):
        """
        List all resources in a resource group.
        
        Args:
            subscription_id: Azure subscription ID
            resource_group_name: Name of the resource group
        
        Returns:
            list: List of resource objects or None if failed
        
        Raises:
            Exception: Logs exceptions internally; does not raise (caller handles fallback)
        """
        try:
            resources = self.client.resources.list_by_resource_group(
                resource_group_name=resource_group_name,
                filter=None  # List all resources, no filtering
            )
            # Convert iterator to list to enable inspection
            resource_list = list(resources)
            logger.info(f"Listed {len(resource_list)} resources in {resource_group_name}")
            return resource_list
        except AzureError as e:
            logger.error(f"Failed to list resources in {resource_group_name}: {str(e)}", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"Unexpected error listing resources: {str(e)}", exc_info=True)
            return None


# app/services/usage_service.py
import logging
from app.azure.resource_client import ResourceClient
from app.azure.mock_data import get_mock_usage_data

logger = logging.getLogger(__name__)

class UsageService:
    """Business logic for resource usage analysis."""
    
    def __init__(self, credential):
        self.resource_client = ResourceClient(credential)
    
    def get_resource_group_usage(self, subscription_id, resource_group_name):
        """
        Get processed resource usage summary for UI: total count, breakdown by type.
        
        Args:
            subscription_id: Azure subscription ID
            resource_group_name: Name of the resource group
        
        Returns:
            dict with keys: total_count, by_type (sorted desc), is_mock
        """
        # Attempt to fetch live resource list
        resources = self.resource_client.list_resources_in_group(
            subscription_id, 
            resource_group_name
        )
        
        # If API returned None (error) or empty list, handle accordingly
        if resources is None:
            logger.warning("Resource list unavailable, using mock fallback data")
            return get_mock_usage_data(is_fallback=True)
        
        if not resources:
            logger.info(f"Resource group {resource_group_name} is empty")
            return {
                "total_count": 0,
                "by_type": {},
                "is_mock": False,
            }
        
        # Process and aggregate the resource list
        try:
            usage_summary = self._process_resources(resources)
            usage_summary["is_mock"] = False
            return usage_summary
        except Exception as e:
            logger.error(f"Error processing resource list: {str(e)}", exc_info=True)
            logger.warning("Processing failed, falling back to mock data")
            return get_mock_usage_data(is_fallback=True)
    
    def _process_resources(self, resources):
        """Aggregate resources by type and sort descending."""
        type_counts = {}
        
        for resource in resources:
            # Extract resource type (e.g., "Microsoft.Compute/virtualMachines")
            resource_type = resource.type if hasattr(resource, 'type') else "Unknown"
            
            # Increment count for this type
            if resource_type not in type_counts:
                type_counts[resource_type] = 0
            type_counts[resource_type] += 1
        
        # Sort by count descending
        sorted_types = sorted(
            type_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        return {
            "total_count": len(resources),
            "by_type": {k: v for k, v in sorted_types},  # Already sorted desc
            "is_mock": False,
        }


# app/ui/usage_page.py (Streamlit example)
import streamlit as st
from app.services.usage_service import UsageService

if subscription_id and resource_group_name:
    usage_service = UsageService(credential)
    summary = usage_service.get_resource_group_usage(subscription_id, resource_group_name)
    
    st.metric("Total Resources", summary['total_count'])
    
    if summary.get("is_mock"):
        st.warning("⚠️ Displaying mock data (live data unavailable)")
    
    if summary['total_count'] == 0:
        st.info("No resources found in this resource group.")
    else:
        st.subheader("Resources by Type")
        # Display as a bar chart
        st.bar_chart(summary['by_type'])
        
        # Optionally, display as a table for detailed view
        st.subheader("Resource Type Counts")
        for resource_type, count in summary['by_type'].items():
            st.write(f"**{resource_type}**: {count}")
```

## Expected Output

The `get_resource_group_usage()` function returns a dictionary with this structure:

```python
{
    "total_count": 12,  # Total number of resources
    "by_type": {
        "Microsoft.Compute/virtualMachines": 3,
        "Microsoft.Storage/storageAccounts": 2,
        "Microsoft.Network/networkInterfaces": 4,
        "Microsoft.Network/virtualNetworks": 1,
        "Microsoft.Compute/availabilitySets": 1,
        "Microsoft.Network/publicIPAddresses": 1,
    },
    "is_mock": False,  # True if fallback data was used
}
```

Note: `by_type` is always sorted in descending order by count. If the resource group is empty:

```python
{
    "total_count": 0,
    "by_type": {},
    "is_mock": False,
}
```

When mock fallback is triggered, `is_mock` is set to `True` and the UI displays a visual warning (`st.warning()`).

## Limitations

- **Lists resources, not metrics** — this skill lists resource names and types only. Azure Monitor data (CPU, memory, disk I/O) requires a different API (`azure-mgmt-monitor`); that is out of scope for v1.

- **No filtering by resource type in v1** — the app lists all resources; filtering or searching by type is a future feature.

- **No resource properties beyond type and name** — provisioning state and location are available but not actively used in v1 display.

## Common Mistakes

| Mistake | Fix |
|---|---|
| Calling `ResourceManagementClient` directly from Streamlit pages | Create a thin wrapper in `app/azure/resource_client.py` and call service layer (`app/services/usage_service.py`) from UI only. |
| Not handling empty resource groups — assuming resources exist and crashing if zero | Check if resource list is empty and return graceful empty summary; show "No resources found" in UI. |
| Forgetting to sort resource type counts before returning to UI | Always return `by_type` sorted descending by count; do this in `_process_resources()` so UI gets pre-sorted data. |
| Storing full resource objects in memory without pagination for large RGs | For resource groups with thousands of resources, convert iterator to list carefully; consider adding pagination/batching if needed later. |
| Not logging API calls or failures | Log all resource list calls with `logger.info()`; log failures with full exception context using `logger.error(exc_info=True)`. |
