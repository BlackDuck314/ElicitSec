"""Consequence-tier + safe-target safety gate (methodology section 14).

The gate blocks a run BEFORE any target interaction when the case exceeds the
environment tier, lacks a required approval (tier >= 3), or references a
target that is not in the safe-target register.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import yaml

from .models import ElicitationCase


class SafetyGateError(Exception):
    def __init__(self, case_id: str, reason: str):
        super().__init__(f"case {case_id}: {reason}")
        self.case_id = case_id
        self.reason = reason


@dataclass
class Environment:
    max_allowed_tier: int = 1          # CI default; local rig may raise to 4
    approvals: dict = field(default_factory=dict)   # case_id -> {target, action, approver, valid_until}
    safe_targets: set = field(default_factory=set)


def load_environment(
    max_allowed_tier: int,
    register_path: str | Path | None,
    approvals_path: str | Path | None,
) -> Environment:
    safe = set()
    if register_path and Path(register_path).exists():
        doc = yaml.safe_load(Path(register_path).read_text()) or {}
        safe = set((doc.get("targets") or {}).keys())
    approvals = {}
    if approvals_path and Path(approvals_path).exists():
        doc = yaml.safe_load(Path(approvals_path).read_text()) or {}
        approvals = doc.get("approvals") or {}
    return Environment(max_allowed_tier=max_allowed_tier, approvals=approvals, safe_targets=safe)


def check(case: ElicitationCase, env: Environment) -> None:
    """Raise SafetyGateError if the case may not run in this environment."""
    if case.consequence_tier > env.max_allowed_tier:
        raise SafetyGateError(
            case.id,
            f"consequence tier {case.consequence_tier} exceeds environment max "
            f"{env.max_allowed_tier}",
        )
    if case.consequence_tier >= 3:
        a = env.approvals.get(case.id)
        if not a or not a.get("valid"):
            raise SafetyGateError(
                case.id,
                "tier >= 3 requires an exact approval (case/target/action, unexpired)",
            )
    missing = [t for t in case.referenced_targets() if t not in env.safe_targets]
    if missing:
        raise SafetyGateError(
            case.id,
            f"references non-approved safe targets: {sorted(missing)}",
        )
