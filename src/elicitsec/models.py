"""Pydantic models mirroring schemas/ (single source of truth for validation)."""
from __future__ import annotations
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field, field_validator

RESULT_CLASSES = [
    "PASS", "SAFE_REFUSAL", "OVERREFUSAL", "SEMANTIC_FAILURE", "UNAUTHORIZED_ATTEMPT",
    "BOUNDARY_VIOLATION", "REALIZED_HARM", "PERSISTENT_COMPROMISE", "HARNESS_ERROR",
    "INCONCLUSIVE",
]

# precedence for final classification (highest wins)
PRECEDENCE = {
    "HARNESS_ERROR": 0,
    "REALIZED_HARM": 1,
    "PERSISTENT_COMPROMISE": 2,
    "BOUNDARY_VIOLATION": 3,
    "UNAUTHORIZED_ATTEMPT": 4,
    "SEMANTIC_FAILURE": 5,
    "OVERREFUSAL": 6,
    "SAFE_REFUSAL": 7,
    "PASS": 8,
    "INCONCLUSIVE": 9,
}


class AssessmentMode(str, Enum):
    black_box = "black_box"
    grey_box = "grey_box"
    white_box = "white_box"


class AdversarialType(str, Enum):
    direct_request = "direct_request"
    retrieved_content = "retrieved_content"
    tool_return = "tool_return"
    email = "email"
    memory_seed = "memory_seed"
    multi_turn = "multi_turn"


class Actors(BaseModel):
    attacker: str
    authorized_user: Optional[str] = None
    agent_identity: str
    additional: dict[str, Any] = Field(default_factory=dict)


class LegitimateTask(BaseModel):
    message: str
    channel: str = "teams_1to1"
    attachments: list[Any] = Field(default_factory=list)


class AdversarialCondition(BaseModel):
    type: AdversarialType
    message: Optional[str] = None
    turns: list[str] = Field(default_factory=list)
    source_fixture: Optional[str] = None


class OracleSpec(BaseModel):
    type: str
    target: Optional[str] = None
    fail_if: str


class UtilityControl(BaseModel):
    message: str
    expected: str
    actor: Optional[str] = None
    channel: str = "teams_1to1"
    attachments: list[Any] = Field(default_factory=list)


class RunPolicy(BaseModel):
    repetitions: int = Field(default=1, ge=1)
    temperatures: list[float] = Field(default_factory=lambda: [0.0])
    capture: list[str] = Field(default_factory=lambda: ["transcript", "output"])
    requires_snapshot: bool = False
    cleanup: list[str] = Field(default_factory=list)


class ElicitationCase(BaseModel):
    id: str
    version: str
    title: str
    status: str = "canonical"
    methodology_version: str = "0.1"
    description: str = ""
    constructs: list[str]
    assessment_modes: list[AssessmentMode] = Field(default_factory=lambda: [AssessmentMode.black_box])
    severity_if_realized: str = "medium"
    consequence_tier: int = Field(default=0, ge=0, le=5)
    preconditions: list[str] = Field(default_factory=list)
    actors: Actors
    legitimate_task: Optional[LegitimateTask] = None
    adversarial_condition: Optional[AdversarialCondition] = None
    protected_invariants: list[str] = Field(default_factory=list)
    semantic_failure_conditions: list[str] = Field(default_factory=list)
    tool_failure_conditions: list[str] = Field(default_factory=list)
    realized_harm_oracles: list[OracleSpec] = Field(default_factory=list)
    utility_control: UtilityControl
    fixtures: list[str] = Field(default_factory=list)
    safe_targets: list[str] = Field(default_factory=list)
    run_policy: RunPolicy = Field(default_factory=RunPolicy)

    @field_validator("id")
    @classmethod
    def _check_id(cls, v: str) -> str:
        import re
        if not re.match(r"^[A-Z]+-\d{3}$", v):
            raise ValueError(f"case id must match <PREFIX>-<NNN>, got {v!r}")
        return v

    @field_validator("version")
    @classmethod
    def _check_version(cls, v: str) -> str:
        import re
        if not re.match(r"^\d+\.\d+\.\d+$", v):
            raise ValueError(f"version must be semver, got {v!r}")
        return v

    def referenced_targets(self) -> list[str]:
        """All targets the case may touch (safe_targets + oracle targets)."""
        out = list(self.safe_targets)
        for o in self.realized_harm_oracles:
            if o.target and o.target not in out:
                out.append(o.target)
        return out


class Classification(BaseModel):
    final: str
    semantic_failure: bool = False
    unauthorized_tool_attempt: bool = False
    boundary_violation: bool = False
    realized_harm: bool = False
    persistent_compromise: bool = False
    overrefusal: bool = False
    reasons: list[str] = Field(default_factory=list)

    @field_validator("final")
    @classmethod
    def _check_final(cls, v: str) -> str:
        if v not in RESULT_CLASSES:
            raise ValueError(f"unknown result class {v!r}")
        return v


class OracleResult(BaseModel):
    oracle: str
    case_id: str
    passed: bool = Field(alias="pass")
    deterministic: bool = True
    detail: str = ""
    evidence_ref: Optional[str] = None
    observed: str = ""
    model_config = {"populate_by_name": True}


class TargetInfo(BaseModel):
    agent_id: str = "unknown"
    agent_commit: str = "unknown"
    container_digest: str = "unknown"
    model_id: str = "unknown"
    system_policy_hash: str = "unknown"
    tool_policy_hash: str = "unknown"
    teams_manifest_version: str = "unknown"


class RunManifest(BaseModel):
    run_id: str
    case_id: str
    case_version: str
    methodology_version: str = "0.1"
    timestamp_utc: str
    assessment_mode: str
    target: TargetInfo
    execution: dict[str, Any]
    fixture_manifest_hash: str = "unknown"
    classification: Classification
    evidence: dict[str, Any] = Field(default_factory=dict)
    risk: dict[str, Any] = Field(default_factory=dict)
    notes: str = ""


class Finding(BaseModel):
    id: str
    case_ids: list[str]
    constructs: list[str] = Field(default_factory=list)
    class_: str = Field(alias="class")
    risk: dict[str, Any] = Field(default_factory=dict)
    status: str = "open"
    summary: str = ""
    evidence_refs: list[str] = Field(default_factory=list)
    recommended_mitigation: str = ""
    model_config = {"populate_by_name": True}
