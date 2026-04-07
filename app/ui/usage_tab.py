import logging
import streamlit as st
import pandas as pd
import plotly.express as px

logger = logging.getLogger(__name__)


def render_usage_tab(summary, resource_group_names):
    """
    Render the Usage tab: total resources, by-type chart, resources table.

    Args:
        summary: Preloaded usage summary dict.
        resource_group_names: Selected resource group names.
    """
    st.subheader("📦 Resource Usage Analysis")
    st.caption(f"Selected resource groups: {', '.join(resource_group_names)}")

    if not resource_group_names:
        st.info("Select at least one resource group from the sidebar to view usage data.")
        return

    if summary is None:
        st.error("Unable to load usage data. Please try again.")
        return

    if summary.get("is_mock"):
        st.warning("⚠️ Displaying mock data — live Azure data unavailable.")

    _render_total_count(summary)
    _render_by_type_chart(summary)
    _render_resources_table(summary)


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
