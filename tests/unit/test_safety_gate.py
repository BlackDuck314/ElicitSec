import sys
from pathlib import Path
import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from elicitsec.case_loader import load_case, load_constructs
from elicitsec.safety_gate import Environment, check, SafetyGateError, load_environment

TAX = load_constructs(REPO / "taxonomy" / "constructs.yaml")


def _case(rel):
    return load_case(REPO / "suites" / rel, TAX)


def test_tier0_passes_low_env():
    c = _case("direct-injection/DIR-001.yaml")
    check(c, Environment(max_allowed_tier=0, safe_targets={"agent_policy"}))


def test_tier_above_env_blocked():
    c = _case("state-integrity/STATE-001.yaml")   # tier 4
    with pytest.raises(SafetyGateError):
        check(c, Environment(max_allowed_tier=1, safe_targets={"agent_policy"}))


def test_tier3_requires_approval():
    c = _case("egress/EGR-001.yaml")             # tier 3
    env = Environment(max_allowed_tier=4, safe_targets={"egress-sink-local"})
    with pytest.raises(SafetyGateError):
        check(c, env)
    env.approvals["EGR-001"] = {"valid": True, "target": "egress-sink-local"}
    check(c, env)   # now passes


def test_unregistered_target_blocked():
    c = _case("authorization/AUTH-001.yaml")     # tier 2, no approval needed
    with pytest.raises(SafetyGateError):
        check(c, Environment(max_allowed_tier=4, safe_targets=set()))
    check(c, Environment(max_allowed_tier=4, safe_targets={"protected-workiq-canary-001"}))
