"""Tests for auth controls in app/ui/sidebar.py."""
from types import SimpleNamespace
from app.ui import sidebar as sidebar_ui


class _FakeSidebar:
    def __init__(self):
        self.success_messages = []
        self.warning_messages = []
        self.captions = []

    def subheader(self, _text):
        return None

    def success(self, text):
        self.success_messages.append(text)

    def warning(self, text):
        self.warning_messages.append(text)

    def caption(self, text):
        self.captions.append(text)

    def markdown(self, _text):
        return None

    def button(self, _label, key=None):
        return False


def _make_fake_st(session_state):
    sidebar = _FakeSidebar()

    fake_st = SimpleNamespace(
        sidebar=sidebar,
        session_state=session_state,
        rerun=lambda: None,
    )
    return fake_st, sidebar


def test_render_auth_controls_shows_authenticated_state(monkeypatch):
    """Sidebar should show authenticated status from session state."""
    fake_st, fake_sidebar = _make_fake_st(
        {
            "azure_auth_ok": True,
            "azure_auth_source": "DefaultAzureCredential (Azure CLI or Managed Identity)",
        }
    )
    monkeypatch.setattr(sidebar_ui, "st", fake_st)

    sidebar_ui._render_auth_controls()

    assert any("Authenticated via:" in msg for msg in fake_sidebar.success_messages)


def test_render_auth_controls_shows_not_authenticated_state(monkeypatch):
    """Sidebar should show warning when auth session state is not set."""
    fake_st, fake_sidebar = _make_fake_st({})
    monkeypatch.setattr(sidebar_ui, "st", fake_st)

    sidebar_ui._render_auth_controls()

    assert any("not currently authenticated" in msg.lower() for msg in fake_sidebar.warning_messages)
