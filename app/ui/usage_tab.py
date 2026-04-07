import logging
import streamlit as st
import pandas as pd
import plotly.express as px
from app.services.usage_service import UsageService

logger = logging.getLogger(__name__)


def render_usage_tab(credential, subscription_id, resource_group_name):
    """
    Render the Usage tab: total resources, by-type chart, resources table.

    Args:
        credential: DefaultAzureCredential instance (or None).
        subscription_id: Selected Azure subscription ID.
        resource_group_name: Selected resource group name.
    """
    st.subheader("📦 Resource Usage Analysis")

    if not subscription_id or not resource_group_name:
        st.info("Select a subscription and resource group from the sidebar to view usage data.")
        return

    with st.spinner("Loading resource usage data..."):
        summary = _fetch_usage_summary(credential, subscription_id, resource_group_name)

    if summary is None:
        st.error("Unable to load usage data. Please try again.")
        return

    if summary.get("is_mock"):
        st.warning("⚠️ Displaying mock data — live Azure data unavailable.")

    _render_total_count(summary)
    _render_by_type_chart(summary)
    _render_resources_table(summary)


def _fetch_usage_summary(credential, subscription_id, resource_group_name):
    """Fetch usage summary from service layer, return None on unexpected failure."""
    try:
        service = UsageService(credential, subscription_id)
        return service.get_resource_group_usage(resource_group_name)
    except Exception as e:
        logger.error(f"Unexpected error fetching usage summary: {str(e)}", exc_info=True)
        return None


def _render_total_count(summary):
    """Display total resource count metric."""
    total = summary.get("total_count", 0)
    st.metric("Total Resources", total)


def _render_by_type_chart(summary):
    """Display resource count by type as a bar chart."""
    by_type = summary.get("by_type", {})
    if not by_type:
        st.info("No resources found in this resource group.")
        return

    st.subheader("Resources by Type")
    df = pd.DataFrame(
        list(by_type.items()), columns=["Resource Type", "Count"]
    ).sort_values("Count", ascending=False)

    fig = px.bar(df, x="Resource Type", y="Count", title="Resource Count by Type")
    st.plotly_chart(fig, use_container_width=True)


def _render_resources_table(summary):
    """Display full resource inventory table."""
    resources = summary.get("resources", [])
    if not resources:
        return

    st.subheader("Resource Inventory")
    df = pd.DataFrame(resources)
    if not df.empty:
        df.columns = [col.capitalize() for col in df.columns]
    st.dataframe(df, use_container_width=True)
