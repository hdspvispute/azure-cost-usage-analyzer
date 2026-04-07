import logging
import streamlit as st
from app.azure.subscription_client import AzureSubscriptionClient
from app.azure.resource_client import ResourceClient
from app.azure.mock_data import get_mock_subscriptions, get_mock_resource_groups

logger = logging.getLogger(__name__)


def render_sidebar(credential):
    """
    Render the sidebar with subscription and resource group selectors.

    Args:
        credential: DefaultAzureCredential instance (or None if auth failed).

    Returns:
        tuple: (subscription_id, resource_group_name) — both may be None if not yet selected.
    """
    st.sidebar.title("🔍 Azure Cost & Usage Analyzer")
    st.sidebar.markdown("---")

    subscription_id, subscription_name = _render_subscription_selector(credential)
    resource_group_name = _render_resource_group_selector(credential, subscription_id)

    return subscription_id, resource_group_name


def _render_subscription_selector(credential):
    """Render subscription dropdown. Returns (subscription_id, display_name) or (None, None)."""
    st.sidebar.subheader("Subscription")

    subscriptions = _load_subscriptions(credential)

    if not subscriptions:
        st.sidebar.warning("No subscriptions found. Ensure you have Reader access.")
        return None, None

    options = {sub["display_name"]: sub["subscription_id"] for sub in subscriptions}
    selected_name = st.sidebar.selectbox(
        "Select subscription", list(options.keys()), key="subscription_selector"
    )
    selected_id = options[selected_name]
    logger.info(f"Subscription selected: {selected_name}")
    return selected_id, selected_name


def _render_resource_group_selector(credential, subscription_id):
    """Render resource group dropdown. Returns resource_group_name or None."""
    st.sidebar.subheader("Resource Group")

    if not subscription_id:
        st.sidebar.info("Select a subscription first.")
        return None

    resource_groups = _load_resource_groups(credential, subscription_id)

    if not resource_groups:
        st.sidebar.info("No resource groups found in this subscription.")
        return None

    selected_rg = st.sidebar.selectbox(
        "Select resource group", resource_groups, key="rg_selector"
    )
    logger.info(f"Resource group selected: {selected_rg}")
    return selected_rg


def _load_subscriptions(credential):
    """Load subscriptions from Azure or fall back to mock data."""
    if credential is None:
        logger.warning("No credential; returning mock subscriptions.")
        return get_mock_subscriptions()

    try:
        client = AzureSubscriptionClient(credential)
        subs = client.list_subscriptions()
        if subs:
            return [
                {
                    "subscription_id": s.subscription_id,
                    "display_name": s.display_name,
                }
                for s in subs
            ]
        logger.warning("No subscriptions returned; using mock fallback.")
        return get_mock_subscriptions()
    except Exception as e:
        logger.error(f"Error loading subscriptions: {str(e)}", exc_info=True)
        return get_mock_subscriptions()


def _load_resource_groups(credential, subscription_id):
    """Load resource groups from Azure or fall back to mock data."""
    if credential is None or subscription_id.startswith("mock-"):
        logger.warning("No live credential or mock subscription; returning mock resource groups.")
        return get_mock_resource_groups()

    try:
        client = ResourceClient(credential, subscription_id)
        rgs = client.list_resource_groups()
        if rgs is not None:
            names = [rg.name for rg in rgs]
            return names if names else get_mock_resource_groups()
        logger.warning("No resource groups returned; using mock fallback.")
        return get_mock_resource_groups()
    except Exception as e:
        logger.error(f"Error loading resource groups: {str(e)}", exc_info=True)
        return get_mock_resource_groups()
