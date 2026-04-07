"""Optional live Azure integration tests for cost and usage data.

These tests are skipped by default and run only when all of the following are set:
- RUN_LIVE_AZURE_TESTS=1
- AZURE_SUBSCRIPTION_ID=<subscription>
- AZURE_RESOURCE_GROUP=<resource-group>
"""
import os
import pytest
from app.azure_api.auth import initialize_credentials
from app.services.cost_service import CostService
from app.services.usage_service import UsageService


RUN_LIVE = os.getenv("RUN_LIVE_AZURE_TESTS") == "1"
SUBSCRIPTION_ID = os.getenv("AZURE_SUBSCRIPTION_ID")
RESOURCE_GROUP = os.getenv("AZURE_RESOURCE_GROUP")


pytestmark = pytest.mark.skipif(
    not (RUN_LIVE and SUBSCRIPTION_ID and RESOURCE_GROUP),
    reason=(
        "Live Azure tests disabled. Set RUN_LIVE_AZURE_TESTS=1, "
        "AZURE_SUBSCRIPTION_ID, and AZURE_RESOURCE_GROUP."
    ),
)


def test_live_cost_data_contract():
    """Validates that live/mock cost payload has expected shape and numeric fields."""
    credential = initialize_credentials()
    service = CostService(credential, SUBSCRIPTION_ID)

    result = service.get_cost_summary(RESOURCE_GROUP)

    assert "is_mock" in result
    assert isinstance(result.get("total_cost"), (int, float))
    assert isinstance(result.get("by_service"), dict)
    assert isinstance(result.get("by_resource_type"), dict)
    assert isinstance(result.get("top_drivers"), list)


def test_live_usage_data_contract():
    """Validates that live/mock usage payload has expected shape and list entries."""
    credential = initialize_credentials()
    service = UsageService(credential, SUBSCRIPTION_ID)

    result = service.get_resource_group_usage(RESOURCE_GROUP)

    assert "is_mock" in result
    assert isinstance(result.get("total_count"), int)
    assert isinstance(result.get("by_type"), dict)
    assert isinstance(result.get("resources"), list)

    if result["resources"]:
        first = result["resources"][0]
        assert "name" in first
        assert "type" in first
        assert "location" in first
