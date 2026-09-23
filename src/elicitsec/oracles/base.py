"""Oracle base. Deterministic environmental checks + the semantic-judge rule.

The semantic judge (model-based) may label SEMANTIC_FAILURE but can NEVER set
REALIZED_HARM - that requires a deterministic oracle (methodology 13.3).
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
from ..models import OracleResult


class Oracle(ABC):
    name: str = "base"
    deterministic: bool = True

    def __init__(self, canary_registry: dict | None = None):
        self.canaries = canary_registry or {}

    @abstractmethod
    def evaluate(self, case_id: str, ctx: "RunContext") -> list[OracleResult]:
        """Return one OracleResult per check. ctx carries transcript/tool/auth/state/egress."""


class RunContext:
    """Evidence bundle handed to oracles for one run."""
    def __init__(self, case_id: str, *,
                 transcript: list[dict] | None = None,
                 final_output: str = "",
                 tool_calls: list[dict] | None = None,
                 authorization: list[dict] | None = None,
                 audit_events: list[dict] | None = None,
                 egress_receipts: list[dict] | None = None,
                 state_before: dict | None = None,
                 state_after: dict | None = None,
                 policy_sha_before: str | None = None,
                 policy_sha_after: str | None = None):
        self.case_id = case_id
        self.transcript = transcript or []
        self.final_output = final_output
        self.tool_calls = tool_calls or []
        self.authorization = authorization or []
        self.audit_events = audit_events or []
        self.egress_receipts = egress_receipts or []
        self.state_before = state_before
        self.state_after = state_after
        self.policy_sha_before = policy_sha_before
        self.policy_sha_after = policy_sha_after

    @property
    def all_text(self) -> str:
        parts = [self.final_output]
        parts += [t.get("text", "") for t in self.transcript]
        parts += [tc.get("result", "") for tc in self.tool_calls if isinstance(tc.get("result"), str)]
        return "\n".join(parts)
