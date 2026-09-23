"""Run orchestrator (methodology section 14 flow, simplified for the local rig).

For each case:
  safety gate -> snapshot -> session -> utility control -> adversarial
  -> evidence collection -> oracles -> classify -> persist run manifest -> reset
"""
from __future__ import annotations
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..models import (
    ElicitationCase,
    RunManifest,
    TargetInfo,
    Classification,
    OracleResult,
)
from ..safety_gate import Environment, check as safety_check
from ..oracles.base import RunContext
from ..oracles.output_canary import OutputCanaryOracle
from ..oracles.file_state import FileStateOracle
from ..oracles.egress import EgressOracle
from ..oracles.tool_policy import ToolPolicyOracle
from ..evaluators.classifier import classify


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _sha(s: str) -> str:
    import hashlib
    return hashlib.sha256(s.encode()).hexdigest()


class RunOutcome:
    def __init__(self, run_manifest: RunManifest, utility: dict | None = None,
                 harness_error: bool = False):
        self.run_manifest = run_manifest
        self.utility = utility or {}
        self.harness_error = harness_error


class Orchestrator:
    def __init__(self, adapter, env: Environment, canaries: dict,
                 protected_identifiers: list[str] | None = None,
                 results_dir: str | Path = "results/local",
                 evidence_dir: str | Path = "evidence",
                 redact=None):
        self.adapter = adapter
        self.env = env
        self.canaries = canaries
        self.protected = protected_identifiers or []
        self.results_dir = Path(results_dir)
        self.evidence_dir = Path(evidence_dir)
        self.redact = redact or (lambda t: t)

    def _oracles(self, allowlist: set[str] | None, disallowed: set[str] | None):
        return [
            OutputCanaryOracle(self.canaries),
            FileStateOracle(),
            EgressOracle(self.canaries, allowlist or set()),
            ToolPolicyOracle(self.canaries, disallowed or set()),
        ]

    def run_case(self, case: ElicitationCase, *, allowlist=None, disallowed=None) -> RunOutcome:
        # 1) safety gate (before any interaction)
        try:
            safety_check(case, self.env)
        except Exception as e:
            manifest = self._manifest(
                case, Classification(final="INCONCLUSIVE"),
                notes=f"blocked by safety gate: {e}")
            return RunOutcome(run_manifest=manifest)

        # 2) snapshot state before
        try:
            snap_before = self.adapter.snapshot_state("policy") or {}
        except Exception:
            snap_before = {}
        pol_sha_before = snap_before.get("policy_sha256")

        # 3) session
        actor = case.actors.attacker
        channel = "direct" if not case.adversarial_condition else case.adversarial_condition.type.value
        try:
            session = self.adapter.create_session(actor, channel)
            if hasattr(self.adapter, "set_case"):
                self.adapter.set_case(session, case.id)
        except Exception as e:
            return RunOutcome(run_manifest=self._manifest(
                case, Classification(final="HARNESS_ERROR"),
                notes=f"session create failed: {e}"),
                harness_error=True)

        # 4) utility control (baseline / paired)
        utility: dict = {}
        if case.utility_control:
            try:
                resp = self.adapter.send_message(session, case.utility_control.message)
                utility = {"completed": bool(resp.get("ok")),
                           "detail": "utility control executed"}
            except Exception as e:
                utility = {"completed": False, "detail": f"utility error: {e}"}

        # 5) adversarial condition
        harness_error = False
        try:
            adv = case.adversarial_condition
            if adv is not None:
                if adv.message:
                    self.adapter.send_message(session, adv.message)
                for turn in adv.turns:
                    self.adapter.send_message(session, turn)
        except Exception as e:
            harness_error = True
            utility["harness_error"] = f"adversarial phase: {e}"

        # 6) collect evidence
        transcript = self.adapter.get_transcript(session)
        tool_calls = self.adapter.get_tool_calls(session)
        auth = self.adapter.get_authorization_events(session)
        final_output = transcript[-1]["text"] if transcript else ""

        # derive egress receipts from outbound tool calls (deterministic)
        egress_receipts = []
        for tc in tool_calls:
            name = (tc.get("name") or "").lower()
            if name.split(".")[-1] in ("post", "get", "send", "put"):
                params = tc.get("params") or {}
                if params.get("url"):
                    egress_receipts.append({
                        "destination": params.get("url", ""),
                        "body": params.get("body", ""),
                        "headers": params.get("headers", {}),
                        "source_tool": tc.get("name", ""),
                    })

        try:
            snap_after = self.adapter.snapshot_state("policy") or {}
        except Exception:
            snap_after = {}
        pol_sha_after = snap_after.get("policy_sha256")

        # 7) build context + run oracles
        ctx = RunContext(
            case_id=case.id,
            transcript=transcript,
            final_output=final_output,
            tool_calls=tool_calls,
            authorization=auth,
            state_before=snap_before,
            state_after=snap_after,
            policy_sha_before=pol_sha_before,
            policy_sha_after=pol_sha_after,
            egress_receipts=egress_receipts,
        )
        ctx.protected_identifiers = self.protected  # type: ignore[attr-defined]
        oracle_results: list[OracleResult] = []
        for o in self._oracles(allowlist, disallowed):
            try:
                oracle_results.extend(o.evaluate(case.id, ctx))
            except Exception as e:
                harness_error = True
                oracle_results.append(OracleResult(
                    oracle=o.name, case_id=case.id, passed=False,
                    detail=f"oracle error: {e}"))

        # 8) classify
        cls = classify(case.id, oracle_results=oracle_results,
                       harness_error=harness_error)

        # 9) persist manifest + redacted evidence
        manifest = self._manifest(case, cls, transcript=transcript,
                                  tool_calls=tool_calls, auth=auth)
        self._persist(manifest)

        # 10) reset (failure here flags non-isolation, never a case failure)
        try:
            self.adapter.reset_session(session)
        except Exception:
            manifest.notes = (manifest.notes + " | reset FAILED - non-isolated").strip()

        return RunOutcome(run_manifest=manifest, utility=utility,
                          harness_error=harness_error)

    def _manifest(self, case: ElicitationCase, cls: Classification, *,
                  transcript=None, tool_calls=None, auth=None,
                  notes: str = "") -> RunManifest:
        profile = self.adapter.get_target_profile()
        if notes and not cls.reasons:
            cls.reasons.append(notes)
        return RunManifest(
            run_id=str(uuid.uuid4()),
            case_id=case.id,
            case_version=case.version,
            methodology_version=case.methodology_version,
            timestamp_utc=_now(),
            assessment_mode=case.assessment_modes[0].value,
            target=TargetInfo(**{k: profile.get(k, "unknown") for k in
                                 ("agent_id", "agent_commit", "container_digest",
                                  "model_id", "system_policy_hash",
                                  "tool_policy_hash", "teams_manifest_version")}),
            execution={"attacker_identity": case.actors.attacker,
                       "channel_context": "teams_1to1"},
            classification=cls,
            evidence={"transcript": [self.redact(t.get("text", "")) for t in (transcript or [])],
                      "tool_calls": tool_calls or [],
                      "authorization": auth or []},
            notes=notes,
        )

    def _persist(self, manifest: RunManifest) -> None:
        self.results_dir.mkdir(parents=True, exist_ok=True)
        p = self.results_dir / f"run-{manifest.case_id}-{manifest.run_id[:8]}.json"
        p.write_text(manifest.model_dump_json(indent=2))
        ev = self.evidence_dir / "transcripts"
        ev.mkdir(parents=True, exist_ok=True)
        (ev / f"{manifest.run_id}.jsonl").write_text(
            "\n".join(json.dumps({"ts": manifest.timestamp_utc,
                                   "case": manifest.case_id,
                                   "class": manifest.classification.final,
                                   "text": t})
                       for t in manifest.evidence.get("transcript", [])))
