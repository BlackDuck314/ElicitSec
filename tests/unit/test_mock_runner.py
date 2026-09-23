import sys
import json
import shutil
import tempfile
from pathlib import Path
import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

import yaml
from elicitsec.case_loader import load_case, load_constructs
from elicitsec.safety_gate import load_environment
from elicitsec.adapters.mock import MockAgent
from elicitsec.runners.orchestrator import Orchestrator

TAX = load_constructs(REPO / "taxonomy" / "constructs.yaml")
CANARIES = (yaml.safe_load((REPO / "fixtures" / "canary-data" / "registry.yaml").read_text())
            or {}).get("markers", {})


def _make(behavior, max_tier=4):
    tmp = tempfile.mkdtemp(prefix="elicitsec-test-")
    policy = Path(tmp) / "policy.txt"
    shutil.copy(REPO / "fixtures" / "state-fixtures" / "policy-baseline.txt", policy)
    ag = MockAgent(REPO / "fixtures" / "mock-responses.json",
                   behavior=behavior, policy_path=policy)
    env = load_environment(max_allowed_tier=max_tier,
                           register_path=REPO / "data" / "safe-target-register" / "register.yaml",
                           approvals_path=REPO / "data" / "approvals.yaml")
    out = tempfile.mkdtemp(prefix="elicitsec-results-")
    ev = tempfile.mkdtemp(prefix="elicitsec-evidence-")
    orch = Orchestrator(ag, env, CANARIES,
                        protected_identifiers=["protected-workiq-canary-001"],
                        results_dir=out, evidence_dir=ev)
    return orch


def test_safe_behaviors_pass():
    orch = _make("safe")
    for rel, expected in [
        ("authorization/AUTH-001.yaml", "PASS"),
        ("utility-controls/UTIL-001.yaml", "PASS"),
        ("direct-injection/DIR-001.yaml", "PASS"),
    ]:
        case = load_case(REPO / "suites" / rel, TAX)
        outcome = orch.run_case(case)
        assert outcome.run_manifest.classification.final == expected, (rel, outcome)


def test_leaky_auth_is_boundary_violation():
    orch = _make("leaky")
    case = load_case(REPO / "suites" / "authorization" / "AUTH-001.yaml", TAX)
    outcome = orch.run_case(case)
    assert outcome.run_manifest.classification.final == "BOUNDARY_VIOLATION"


def test_leaky_egress_is_realized_harm():
    orch = _make("leaky")
    case = load_case(REPO / "suites" / "egress" / "EGR-001.yaml", TAX)
    outcome = orch.run_case(case)
    assert outcome.run_manifest.classification.final == "REALIZED_HARM"


def test_leaky_rag_is_realized_harm():
    orch = _make("leaky")
    case = load_case(REPO / "suites" / "workiq-rag" / "RAG-001.yaml", TAX)
    outcome = orch.run_case(case)
    assert outcome.run_manifest.classification.final == "REALIZED_HARM"


def test_leaky_state_is_persistent_compromise():
    orch = _make("leaky")
    case = load_case(REPO / "suites" / "state-integrity" / "STATE-001.yaml", TAX)
    outcome = orch.run_case(case)
    assert outcome.run_manifest.classification.final == "PERSISTENT_COMPROMISE"


def test_tier_gate_blocks_high_tier_in_ci_env():
    orch = _make("safe", max_tier=1)
    case = load_case(REPO / "suites" / "state-integrity" / "STATE-001.yaml", TAX)  # tier 4
    outcome = orch.run_case(case)
    assert outcome.run_manifest.classification.final == "INCONCLUSIVE"
    assert "safety gate" in outcome.run_manifest.notes
