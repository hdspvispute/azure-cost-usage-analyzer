"""Tests for app/services/usage_service.py."""
import pytest
from unittest.mock import MagicMock, patch
from app.services.usage_service import UsageService


def _make_resource(name, resource_type, location="eastus"):
    """Helper: create a mock Azure resource object."""
    r = MagicMock()
    r.name = name
    r.type = resource_type
    r.location = location
    return r


def _make_service(resources=None, api_raises=False):
    """Helper: build UsageService with a mocked ResourceClient."""
    credential = MagicMock()
    with patch("app.services.usage_service.ResourceClient") as MockClient:
        instance = MockClient.return_value
        if api_raises:
            instance.list_resources_in_group.side_effect = Exception("API error")
        else:
            instance.list_resources_in_group.return_value = resources
        service = UsageService(credential, "sub-123")
        service.resource_client = instance
    return service


# ── Happy path ───────────────────────────────────────────────────────────────

def test_get_resource_group_usage_happy_path():
    """Live data returns aggregated summary with is_mock=False."""
    resources = [
        _make_resource("vm-1", "Microsoft.Compute/virtualMachines"),
        _make_resource("vm-2", "Microsoft.Compute/virtualMachines"),
        _make_resource("sa-1", "Microsoft.Storage/storageAccounts"),
    ]
    service = _make_service(resources=resources)
    result = service.get_resource_group_usage("rg-test")

    assert result["is_mock"] is False
    assert result["total_count"] == 3
    assert result["by_type"]["Microsoft.Compute/virtualMachines"] == 2
    assert result["by_type"]["Microsoft.Storage/storageAccounts"] == 1


def test_get_resource_group_usage_schema_keys():
    """Result always contains required schema keys."""
    resources = [_make_resource("vm-1", "Microsoft.Compute/virtualMachines")]
    service = _make_service(resources=resources)
    result = service.get_resource_group_usage("rg-test")

    for key in ("total_count", "by_type", "resources", "is_mock"):
        assert key in result, f"Missing key: {key}"


def test_by_type_sorted_descending():
    """by_type is sorted by count descending."""
    resources = [
        _make_resource("nic-1", "Microsoft.Network/networkInterfaces"),
        _make_resource("nic-2", "Microsoft.Network/networkInterfaces"),
        _make_resource("nic-3", "Microsoft.Network/networkInterfaces"),
        _make_resource("vm-1", "Microsoft.Compute/virtualMachines"),
        _make_resource("vm-2", "Microsoft.Compute/virtualMachines"),
        _make_resource("sa-1", "Microsoft.Storage/storageAccounts"),
    ]
    service = _make_service(resources=resources)
    result = service.get_resource_group_usage("rg-test")

    counts = list(result["by_type"].values())
    assert counts == sorted(counts, reverse=True)


def test_resources_list_contains_name_type_location():
    """Each entry in resources list has name, type, and location keys."""
    resources = [_make_resource("vm-1", "Microsoft.Compute/virtualMachines", "westus")]
    service = _make_service(resources=resources)
    result = service.get_resource_group_usage("rg-test")

    assert len(result["resources"]) == 1
    r = result["resources"][0]
    assert r["name"] == "vm-1"
    assert r["type"] == "Microsoft.Compute/virtualMachines"
    assert r["location"] == "westus"


# ── Empty resource group ─────────────────────────────────────────────────────

def test_empty_resource_group_returns_zero_summary():
    """Empty resource group returns zero-count summary without mock."""
    service = _make_service(resources=[])
    result = service.get_resource_group_usage("rg-empty")

    assert result["is_mock"] is False
    assert result["total_count"] == 0
    assert result["by_type"] == {}
    assert result["resources"] == []


# ── API failure / fallback ───────────────────────────────────────────────────

def test_api_returns_none_triggers_mock_fallback():
    """API returns None → fallback mock with is_mock=True."""
    service = _make_service(resources=None)
    result = service.get_resource_group_usage("rg-fail")

    assert result["is_mock"] is True
    assert "total_count" in result


def test_api_exception_triggers_mock_fallback(caplog):
    """API raises exception → fallback mock returned."""
    import logging
    credential = MagicMock()
    with patch("app.services.usage_service.ResourceClient") as MockClient:
        MockClient.return_value.list_resources_in_group.side_effect = Exception("network error")
        service = UsageService(credential, "sub-123")
        with caplog.at_level(logging.WARNING, logger="app.services.usage_service"):
            result = service.get_resource_group_usage("rg-fail")

    assert result["is_mock"] is True


def test_fallback_warning_is_logged(caplog):
    """Fallback activation is logged at WARNING level."""
    import logging
    service = _make_service(resources=None)
    with caplog.at_level(logging.WARNING, logger="app.services.usage_service"):
        service.get_resource_group_usage("rg-fail")

    assert any("mock fallback" in r.message.lower() for r in caplog.records)


# ── Mock data module sanity ───────────────────────────────────────────────────

def test_mock_usage_data_schema():
    """get_mock_usage_data returns expected schema."""
    from app.azure.mock_data import get_mock_usage_data
    data = get_mock_usage_data(is_fallback=True)

    assert data["is_mock"] is True
    assert data["total_count"] > 0
    assert isinstance(data["by_type"], dict)
    assert isinstance(data["resources"], list)
