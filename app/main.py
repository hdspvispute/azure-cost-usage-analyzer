import os
import sys
import logging
import streamlit as st
from azure.core.exceptions import ClientAuthenticationError

# Ensure project root is importable when running: streamlit run app/main.py
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.azure_api.auth import initialize_credentials, validate_credentials, get_auth_source_label
from app.ui.sidebar import render_sidebar
from app.ui.cost_tab import render_cost_tab
from app.ui.usage_tab import render_usage_tab
from app.services.cost_service import CostService
from app.services.usage_service import UsageService
from app.services.local_db import LocalCacheRepository

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    st.set_page_config(
        page_title="Azure Cost & Usage Analyzer",
        page_icon="☁️",
        layout="wide",
    )

    credential = _get_credential()

    subscription_id, resource_group_names, refresh_requested = render_sidebar(credential)

    st.title("☁️ Azure Cost & Usage Analyzer")
    st.caption("Data source: SQLite cache by default. Use 'Refresh from Azure' to fetch latest data.")

    if not subscription_id or not resource_group_names:
        st.info("Select a subscription and one or more resource groups in the sidebar.")
        return

    cache_repo = LocalCacheRepository()
    data_bundle = _load_or_refresh_data(
        cache_repo=cache_repo,
        credential=credential,
        subscription_id=subscription_id,
        resource_group_names=resource_group_names,
        refresh_requested=refresh_requested,
    )

    if data_bundle is None:
        st.error("Unable to load data from Azure or local cache.")
        return

    data_source = data_bundle["source"]
    refreshed_at = data_bundle["refreshed_at"]

    if refreshed_at:
        st.caption(f"Last refreshed: {refreshed_at} UTC | Source: {data_source}")
    else:
        st.caption(f"Source: {data_source}")

    if "mock fallback" in data_source.lower():
        st.warning(
            "Live Azure data was unavailable for this selection. Verify Reader access, Cost Management permissions, and click 'Refresh from Azure'."
        )

    cost_tab, usage_tab = st.tabs(["💰 Cost Analysis", "📦 Resource Usage"])

    with cost_tab:
        render_cost_tab(data_bundle["cost_summary"], resource_group_names)

    with usage_tab:
        render_usage_tab(data_bundle["usage_summary"], resource_group_names)


def _load_or_refresh_data(
    cache_repo,
    credential,
    subscription_id,
    resource_group_names,
    refresh_requested,
):
    """Load from SQLite cache by default; refresh live Azure data on user demand."""
    if not refresh_requested:
        cached = cache_repo.get_snapshot(subscription_id, resource_group_names)
        if cached:
            cached_source = "SQLite cache"
            if cached.get("is_mock"):
                cached_source = "SQLite cache (mock fallback)"
            return {
                "cost_summary": cached["cost_summary"],
                "usage_summary": cached["usage_summary"],
                "refreshed_at": cached["refreshed_at"],
                "source": cached_source,
            }

    if credential is None:
        logger.warning("No Azure credential available and no cache hit for current selection.")
        return None

    cost_service = CostService(credential, subscription_id)
    usage_service = UsageService(credential, subscription_id)

    cost_summary = cost_service.get_cost_summary_for_groups(resource_group_names)
    usage_summary = usage_service.get_resource_group_usage_for_groups(resource_group_names)
    is_mock = bool(cost_summary.get("is_mock") or usage_summary.get("is_mock"))

    cache_repo.save_snapshot(subscription_id, resource_group_names, cost_summary, usage_summary)
    saved = cache_repo.get_snapshot(subscription_id, resource_group_names)

    return {
        "cost_summary": cost_summary,
        "usage_summary": usage_summary,
        "refreshed_at": saved["refreshed_at"] if saved else None,
        "source": "Azure refresh (mock fallback)" if is_mock else "Azure live",
    }


def _get_credential():
    """Initialize Azure credentials; return None and show friendly error on failure."""
    try:
        credential = initialize_credentials()
        validate_credentials(credential)
        st.session_state["azure_auth_ok"] = True
        st.session_state["azure_auth_source"] = get_auth_source_label(credential)
        return credential
    except ClientAuthenticationError:
        st.session_state["azure_auth_ok"] = False
        st.session_state["azure_auth_source"] = ""
        st.error(
            "🔐 Azure authentication failed. "
            "For local runs, execute 'az login' in terminal. For Azure Container Apps, configure managed identity and Reader role."
        )
        logger.error("Azure authentication failed; running without live credential.")
        return None
    except Exception as e:
        st.session_state["azure_auth_ok"] = False
        st.session_state["azure_auth_source"] = ""
        st.error(f"⚠️ Unexpected authentication error: {str(e)}")
        logger.error(f"Unexpected auth error: {str(e)}", exc_info=True)
        return None


if __name__ == "__main__":
    main()
