"""Tests for app/services/cost_service.py."""
import pytest
from unittest.mock import MagicMock, patch
from app.services.cost_service import CostService


def _make_service(mock_rows=None, api_raises=False):
    """Helper: build CostService with a mocked CostClient."""
    credential = MagicMock()
    with patch("app.services.cost_service.CostClient") as MockClient:
        instance = MockClient.return_value
        if api_raises:
            instance.get_resource_group_cost.side_effect = Exception("API error")
        else:
            mock_result = MagicMock()
            mock_result.rows = mock_rows
            instance.get_resource_group_cost.return_value = mock_result if mock_rows is not None else None
        service = CostService(credential, "sub-123")
        service.cost_client = instance  # inject mock
    return service


# ── Happy path ──────────────────────────────────────────────────────────────

def test_get_cost_summary_happy_path():
    """Live data returns aggregated summary with is_mock=False."""
    rows = [
        ["Compute", "microsoft.compute/virtualmachines", 100.0],
        ["Storage", "microsoft.storage/storageaccounts", 50.0],
        ["Compute", "microsoft.compute/virtualmachines", 25.0],
    ]
    service = _make_service(mock_rows=rows)
    result = service.get_cost_summary("rg-test")

    assert result["is_mock"] is False
    assert result["total_cost"] == 175.0
    assert "Compute" in result["by_service"]
    assert "Storage" in result["by_service"]
    assert result["by_service"]["Compute"] == 125.0
    assert result["by_service"]["Storage"] == 50.0


def test_get_cost_summary_schema_keys():
    """Result always contains required schema keys."""
    rows = [["Compute", "microsoft.compute/virtualmachines", 10.0]]
    service = _make_service(mock_rows=rows)
    result = service.get_cost_summary("rg-test")

    for key in ("total_cost", "by_service", "by_resource_type", "top_drivers", "is_mock"):
        assert key in result, f"Missing key: {key}"


def test_get_cost_summary_sorted_descending():
    """by_service is sorted descending by cost."""
    rows = [
        ["Storage", "microsoft.storage/storageaccounts", 10.0],
        ["Compute", "microsoft.compute/virtualmachines", 90.0],
        ["Networking", "microsoft.network/loadbalancers", 30.0],
    ]
    service = _make_service(mock_rows=rows)
    result = service.get_cost_summary("rg-test")

    costs = list(result["by_service"].values())
    assert costs == sorted(costs, reverse=True)


def test_top_drivers_max_5():
    """top_drivers never exceeds 5 entries."""
    rows = [[f"Svc{i}", f"type{i}", float(i * 10)] for i in range(1, 10)]
    service = _make_service(mock_rows=rows)
    result = service.get_cost_summary("rg-test")

    assert len(result["top_drivers"]) <= 5


def test_top_drivers_sorted_descending():
    """top_drivers is ordered highest cost first."""
    rows = [
        ["Compute", "microsoft.compute/virtualmachines", 200.0],
        ["Storage", "microsoft.storage/storageaccounts", 50.0],
        ["Networking", "microsoft.network/loadbalancers", 150.0],
    ]
    service = _make_service(mock_rows=rows)
    result = service.get_cost_summary("rg-test")

    driver_costs = [d["cost"] for d in result["top_drivers"]]
    assert driver_costs == sorted(driver_costs, reverse=True)


# ── Empty / no data ──────────────────────────────────────────────────────────

def test_get_cost_summary_none_result_returns_mock():
    """API returns None → fallback mock with is_mock=True."""
    service = _make_service(mock_rows=None)
    result = service.get_cost_summary("rg-empty")

    assert result["is_mock"] is True
    assert "total_cost" in result


def test_get_cost_summary_empty_rows_returns_mock():
    """API returns result with empty rows → fallback mock."""
    service = _make_service(mock_rows=[])
    result = service.get_cost_summary("rg-empty")

    assert result["is_mock"] is True


# ── Error / fallback ─────────────────────────────────────────────────────────

def test_get_cost_summary_api_exception_returns_mock(caplog):
    """API raises exception → fallback mock with warning logged."""
    import logging
    credential = MagicMock()
    with patch("app.services.cost_service.CostClient") as MockClient:
        MockClient.return_value.get_resource_group_cost.side_effect = Exception("timeout")
        service = CostService(credential, "sub-123")
        with caplog.at_level(logging.WARNING, logger="app.services.cost_service"):
            result = service.get_cost_summary("rg-fail")

    assert result["is_mock"] is True


def test_get_cost_summary_logs_fallback_warning(caplog):
    """Fallback activation is logged at WARNING level."""
    import logging
    service = _make_service(mock_rows=None)
    with caplog.at_level(logging.WARNING, logger="app.services.cost_service"):
        service.get_cost_summary("rg-empty")

    assert any("mock fallback" in r.message.lower() for r in caplog.records)
