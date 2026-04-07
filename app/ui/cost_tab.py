import logging
import streamlit as st
import pandas as pd
import plotly.express as px
from app.services.cost_service import CostService

logger = logging.getLogger(__name__)


def render_cost_tab(credential, subscription_id, resource_group_name):
    """
    Render the Cost tab: total cost, by-service chart, top resources table.

    Args:
        credential: DefaultAzureCredential instance (or None).
        subscription_id: Selected Azure subscription ID.
        resource_group_name: Selected resource group name.
    """
    st.subheader("💰 Cost Analysis — Last 30 Days")
    st.caption("ℹ️ Cost data from Azure may be delayed up to 48 hours.")

    if not subscription_id or not resource_group_name:
        st.info("Select a subscription and resource group from the sidebar to view cost data.")
        return

    with st.spinner("Loading cost data..."):
        summary = _fetch_cost_summary(credential, subscription_id, resource_group_name)

    if summary is None:
        st.error("Unable to load cost data. Please try again.")
        return

    if summary.get("is_mock"):
        st.warning("⚠️ Displaying mock data — live Azure data unavailable.")

    _render_total_cost(summary)
    _render_by_service_chart(summary)
    _render_top_drivers_table(summary)


def _fetch_cost_summary(credential, subscription_id, resource_group_name):
    """Fetch cost summary from service layer, return None on unexpected failure."""
    try:
        service = CostService(credential, subscription_id)
        return service.get_cost_summary(resource_group_name)
    except Exception as e:
        logger.error(f"Unexpected error fetching cost summary: {str(e)}", exc_info=True)
        return None


def _render_total_cost(summary):
    """Display total cost metric."""
    total = summary.get("total_cost", 0.0)
    st.metric("Total Cost (USD)", f"${total:,.2f}")


def _render_by_service_chart(summary):
    """Display cost breakdown by service as a bar chart."""
    by_service = summary.get("by_service", {})
    if not by_service:
        st.info("No cost breakdown by service available for this resource group.")
        return

    st.subheader("Breakdown by Service")
    df = pd.DataFrame(
        list(by_service.items()), columns=["Service", "Cost (USD)"]
    ).sort_values("Cost (USD)", ascending=False)

    fig = px.bar(df, x="Service", y="Cost (USD)", title="Cost by Service")
    st.plotly_chart(fig, use_container_width=True)


def _render_top_drivers_table(summary):
    """Display top cost drivers as a table."""
    top_drivers = summary.get("top_drivers", [])
    if not top_drivers:
        st.info("No top cost drivers available.")
        return

    st.subheader("Top 5 Cost Drivers")
    df = pd.DataFrame(top_drivers)
    df.columns = ["Resource / Type", "Cost (USD)"]
    df["Cost (USD)"] = df["Cost (USD)"].map(lambda x: f"${x:,.2f}")
    st.dataframe(df, use_container_width=True)
