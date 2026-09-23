import sys
import importlib
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))


def test_mock_implements_adapter_protocol():
    from elicitsec.adapters.mock import MockAgent
    required = [
        "get_target_profile", "health_check", "create_session", "send_message",
        "get_transcript", "get_trace", "get_tool_calls",
        "get_authorization_events", "reset_session", "snapshot_state",
        "restore_state",
    ]
    for name in required:
        assert hasattr(MockAgent, name), f"MockAgent missing {name}"
