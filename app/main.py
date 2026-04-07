import logging
import streamlit as st
from azure.core.exceptions import ClientAuthenticationError
from app.azure.auth import initialize_credentials
from app.ui.sidebar import render_sidebar
from app.ui.cost_tab import render_cost_tab
from app.ui.usage_tab import render_usage_tab

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

    subscription_id, resource_group_name = render_sidebar(credential)

    st.title("☁️ Azure Cost & Usage Analyzer")

    cost_tab, usage_tab = st.tabs(["💰 Cost Analysis", "📦 Resource Usage"])

    with cost_tab:
        render_cost_tab(credential, subscription_id, resource_group_name)

    with usage_tab:
        render_usage_tab(credential, subscription_id, resource_group_name)


def _get_credential():
    """Initialize Azure credentials; return None and show friendly error on failure."""
    try:
        return initialize_credentials()
    except ClientAuthenticationError:
        st.error(
            "🔐 Azure authentication failed. "
            "Please run `az login` in your terminal and restart the app."
        )
        logger.error("Azure authentication failed; running without live credential.")
        return None
    except Exception as e:
        st.error(f"⚠️ Unexpected authentication error: {str(e)}")
        logger.error(f"Unexpected auth error: {str(e)}", exc_info=True)
        return None


if __name__ == "__main__":
    main()
