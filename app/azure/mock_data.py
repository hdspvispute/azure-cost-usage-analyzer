"""
Mock data for local development, demos, and fallback scenarios.
Used when Azure APIs are unavailable or return empty responses.
"""


def get_mock_subscriptions():
    """Return mock subscription list."""
    return [
        {"subscription_id": "mock-sub-001", "display_name": "Mock Subscription A"},
        {"subscription_id": "mock-sub-002", "display_name": "Mock Subscription B"},
    ]


def get_mock_resource_groups():
    """Return mock resource group list."""
    return ["mock-rg-web", "mock-rg-data", "mock-rg-dev"]


def get_mock_cost_data(is_fallback=True):
    """
    Return mock cost summary data.

    Args:
        is_fallback: Whether this was triggered as a fallback (default True).

    Returns:
        dict: Mock cost summary matching CostService output structure.
    """
    return {
        "total_cost": 342.75,
        "by_service": {
            "Compute": 210.00,
            "Storage": 85.50,
            "Networking": 47.25,
        },
        "by_resource_type": {
            "microsoft.compute/virtualmachines": 210.00,
            "microsoft.storage/storageaccounts": 85.50,
            "microsoft.network/loadbalancers": 47.25,
        },
        "top_drivers": [
            {"name": "vm-prod-01", "cost": 120.00},
            {"name": "vm-prod-02", "cost": 90.00},
            {"name": "storage-prod", "cost": 85.50},
            {"name": "lb-frontend", "cost": 30.00},
            {"name": "vm-dev-01", "cost": 17.25},
        ],
        "is_mock": is_fallback,
    }


def get_mock_usage_data(is_fallback=True):
    """
    Return mock usage summary data.

    Args:
        is_fallback: Whether this was triggered as a fallback (default True).

    Returns:
        dict: Mock usage summary matching UsageService output structure.
    """
    return {
        "total_count": 11,
        "by_type": {
            "Microsoft.Network/networkInterfaces": 4,
            "Microsoft.Compute/virtualMachines": 3,
            "Microsoft.Storage/storageAccounts": 2,
            "Microsoft.Network/virtualNetworks": 1,
            "Microsoft.Network/publicIPAddresses": 1,
        },
        "resources": [
            {"name": "vm-prod-01", "type": "Microsoft.Compute/virtualMachines", "location": "eastus"},
            {"name": "vm-prod-02", "type": "Microsoft.Compute/virtualMachines", "location": "eastus"},
            {"name": "vm-dev-01", "type": "Microsoft.Compute/virtualMachines", "location": "eastus"},
            {"name": "nic-vm-prod-01", "type": "Microsoft.Network/networkInterfaces", "location": "eastus"},
            {"name": "nic-vm-prod-02", "type": "Microsoft.Network/networkInterfaces", "location": "eastus"},
            {"name": "nic-vm-dev-01", "type": "Microsoft.Network/networkInterfaces", "location": "eastus"},
            {"name": "nic-extra", "type": "Microsoft.Network/networkInterfaces", "location": "eastus"},
            {"name": "storage-prod", "type": "Microsoft.Storage/storageAccounts", "location": "eastus"},
            {"name": "storage-backup", "type": "Microsoft.Storage/storageAccounts", "location": "eastus"},
            {"name": "vnet-main", "type": "Microsoft.Network/virtualNetworks", "location": "eastus"},
            {"name": "pip-frontend", "type": "Microsoft.Network/publicIPAddresses", "location": "eastus"},
        ],
        "is_mock": is_fallback,
    }
