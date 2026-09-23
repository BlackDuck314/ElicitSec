import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from elicitsec.store import ResultsStore


def _manifest(run_id, case_id, cls):
    return {
        "run_id": run_id,
        "case_id": case_id,
        "case_version": "0.1.0",
        "methodology_version": "0.1",
        "timestamp_utc": "2026-01-01T00:00:00Z",
        "assessment_mode": "black_box",
        "target": {"agent_id": "mock", "model_id": "mock/safe",
                   "system_policy_hash": "h", "tool_policy_hash": "t"},
        "execution": {"attacker_identity": "attacker", "channel_context": "teams_1to1"},
        "classification": {"final": cls,
                           "realized_harm": cls == "REALIZED_HARM",
                           "boundary_violation": cls == "BOUNDARY_VIOLATION",
                           "persistent_compromise": cls == "PERSISTENT_COMPROMISE",
                           "unauthorized_tool_attempt": False,
                           "semantic_failure": False,
                           "overrefusal": False},
        "evidence": {"transcript": ["a", "b"], "tool_calls": [], "authorization": []},
        "notes": "",
    }


def test_store_ingest_and_query(tmp_path):
    s = ResultsStore(tmp_path)
    s.append(_manifest("r1", "AUTH-001", "BOUNDARY_VIOLATION"))
    s.append(_manifest("r2", "EGR-001", "REALIZED_HARM"))
    s.append(_manifest("r3", "UTIL-001", "PASS"))
    s.close()

    # reopen and verify persisted
    s2 = ResultsStore(tmp_path)
    try:
        rows = s2.query_rows("SELECT run_id, classification FROM runs ORDER BY run_id")
        assert [r["classification"] for r in rows] == ["BOUNDARY_VIOLATION", "REALIZED_HARM", "PASS"]
        assert len(s2.runs()) == 3

        metrics = s2.metrics()
        by = {m["classification"]: m["n"] for m in metrics}
        assert by["PASS"] == 1 and by["REALIZED_HARM"] == 1

        per = s2.per_case()
        pc = {r["case_id"]: r for r in per}
        assert pc["EGR-001"]["realized_harm"] == 1
    finally:
        s2.close()


def test_store_is_idempotent_on_run_id(tmp_path):
    s = ResultsStore(tmp_path)
    s.append(_manifest("r1", "AUTH-001", "PASS"))
    s.append(_manifest("r1", "AUTH-001", "REALIZED_HARM"))  # same run id -> replace
    s.close()
    s2 = ResultsStore(tmp_path)
    try:
        assert len(s2.runs()) == 1
        assert s2.runs()[0]["classification"] == "REALIZED_HARM"
        # parquet tables exist
        assert (tmp_path / "parquet" / "runs.parquet").exists()
        assert (tmp_path / "parquet" / "metrics.parquet").exists()
        assert (tmp_path / "parquet" / "per_case.parquet").exists()
    finally:
        s2.close()


def test_store_ingest_from_manifests(tmp_path):
    src_dir = tmp_path / "manifests"
    src_dir.mkdir()
    (src_dir / "run-UTIL-001-aaaa.json").write_text(
        __import__("json").dumps(_manifest("x1", "UTIL-001", "PASS")))
    s = ResultsStore(tmp_path)
    n = s.ingest_from_manifests(src_dir)
    assert n == 1
    assert len(s.runs()) == 1
    s.close()
