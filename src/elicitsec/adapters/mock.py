"""Deterministic mock agent adapter.

Reads scripted responses from fixtures/mock-responses.json. Each case entry has
a "safe" and a "leaky" behavior; the adapter runs whichever behavior is
selected (default: safe). This lets oracles and the runner be tested both ways:
- behavior=safe   -> expect PASS / SAFE_REFUSAL (and utility completion)
- behavior=leaky  -> expect the oracles to fire (REALIZED_HARM / UNAUTHORIZED_ATTEMPT)

The mock never touches the network or real state.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from .base import AgentAdapter, AdapterError

class MockAgent:
    def __init__(self, responses_path: str | Path, behavior: str = "safe",
                 policy_path: str | Path | None = None):
        self._responses_path = Path(responses_path)
        self._responses = json.loads(self._responses_path.read_text())
        self._behavior = behavior
        self._sessions: dict[str, dict] = {}
        self._policy_path = Path(policy_path) if policy_path else None
        self._policy_before: str | None = None
        self._policy_after: str | None = None

    def get_target_profile(self) -> dict[str, Any]:
        return {"agent_id": "mock", "model_id": f"mock/{self._behavior}",
                "agent_commit": "mock-0.1", "container_digest": "n/a",
                "system_policy_hash": "mock-policy", "tool_policy_hash": "mock-tools",
                "teams_manifest_version": "n/a"}

    def health_check(self) -> dict[str, Any]:
        return {"ok": True, "adapter": "mock", "behavior": self._behavior}

    def _scripted(self, case_id: str) -> dict:
        entry = self._responses.get("cases", {}).get(case_id)
        if entry is None:
            raise AdapterError(f"no scripted response for case {case_id}")
        return entry[self._behavior]

    def create_session(self, actor_id: str, channel_context: str) -> str:
        sid = f"mock-{channel_context}-{actor_id}"
        self._sessions[sid] = {"actor": actor_id, "channel": channel_context,
                               "transcript": [], "tool_calls": [], "auth": [],
                               "policy_modified": False}
        if self._policy_path and self._policy_path.exists():
            self._policy_before = self._policy_path.read_text()
        return sid

    def send_message(self, session_id: str, message: str,
                     attachments: list[dict] | None = None) -> dict[str, Any]:
        s = self._sessions[session_id]
        s["transcript"].append({"role": "user", "text": message})
        # determine the case this session is running (set by the orchestrator)
        case_id = s.get("case_id", "default")
        script = self._responses.get("cases", {}).get(case_id, {})
        if not script:
            resp = "I can help with that. Please provide more detail."
            s["transcript"].append({"role": "agent", "text": resp})
            return {"ok": True, "text": resp}
        script = script.get(self._behavior) or script.get("safe")
        resp = script.get("response", "")
        s["transcript"].append({"role": "agent", "text": resp})
        for tc in script.get("tool_calls", []):
            s["tool_calls"].append(tc)
            # leaky policy writes actually mutate the policy file (to prove the oracle)
            if tc.get("name") == "agent.set_policy" and self._policy_path and self._policy_path.exists():
                self._policy_path.write_text(self._policy_path.read_text() + "\n# tampered-by-mock\n")
                s["policy_modified"] = True
        for ae in script.get("authorization", []):
            s["auth"].append(ae)
        return {"ok": True, "text": resp}

    def get_transcript(self, session_id: str) -> list[dict[str, Any]]:
        return self._sessions[session_id]["transcript"]

    def get_trace(self, session_id: str) -> list[dict[str, Any]]:
        return self._sessions[session_id].get("trace", self._sessions[session_id]["transcript"])

    def get_tool_calls(self, session_id: str) -> list[dict[str, Any]]:
        return self._sessions[session_id]["tool_calls"]

    def get_authorization_events(self, session_id: str) -> list[dict[str, Any]]:
        return self._sessions[session_id]["auth"]

    def reset_session(self, session_id: str) -> None:
        s = self._sessions.get(session_id)
        if s:
            s["transcript"], s["tool_calls"], s["auth"] = [], [], []
        if self._policy_path and self._policy_path.exists() and self._policy_before is not None:
            self._policy_path.write_text(self._policy_before)   # restore snapshot
            s and s.update({"policy_modified": False})

    def snapshot_state(self, scope: str) -> dict[str, Any]:
        if self._policy_path and self._policy_path.exists():
            return {"scope": scope, "policy_sha256": _sha(self._policy_path.read_text())}
        return {"scope": scope, "policy_sha256": None}

    def restore_state(self, snapshot: dict[str, Any]) -> None:
        # mock only tracks the policy file hash; real restore is a no-op here
        return None

    def set_case(self, session_id: str, case_id: str) -> None:
        self._sessions[session_id]["case_id"] = case_id

def _sha(b: bytes | str) -> str:
    import hashlib
    if isinstance(b, str): b = b.encode()
    return hashlib.sha256(b).hexdigest()
