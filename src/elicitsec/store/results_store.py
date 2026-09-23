"""Queryable results store backed by DuckDB + Parquet.

Run manifests remain the canonical JSON artifact (written by the orchestrator's
``_persist``). This store ingests those manifests into a DuckDB file and
materializes flat, queryable tables plus a Parquet export so results, metrics,
and evidence summaries can be analyzed with SQL/Pandas and regressed over time.

Design notes
------------
- DuckDB file location: ``<results_dir>/elicitsec.duckdb``
- Parquet export location: ``<results_dir>/parquet/*.parquet``
- ``append`` is idempotent per ``run_id`` (upsert on ``run_id``).
- Raw evidence (transcript/authorization) stays in the JSON manifests; the
  store records only evidence *metadata* (counts) to keep the DB lean and safe.
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import duckdb


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


_CREATE_RUNS = """
CREATE TABLE IF NOT EXISTS runs (
    run_id              VARCHAR PRIMARY KEY,
    case_id             VARCHAR NOT NULL,
    case_version        VARCHAR,
    methodology_version VARCHAR,
    timestamp_utc       TIMESTAMP,
    assessment_mode     VARCHAR,
    agent_id            VARCHAR,
    model_id            VARCHAR,
    system_policy_hash  VARCHAR,
    tool_policy_hash    VARCHAR,
    classification      VARCHAR,
    realized_harm       BOOLEAN,
    boundary_violation  BOOLEAN,
    unauthorized_attempt BOOLEAN,
    persistent_compromise BOOLEAN,
    semantic_failure    BOOLEAN,
    overrefusal         BOOLEAN,
    evidence_transcript_count INTEGER,
    evidence_tool_call_count  INTEGER,
    evidence_auth_count       INTEGER,
    attacker_identity   VARCHAR,
    channel_context     VARCHAR,
    notes               VARCHAR
);
"""


def _row_from_manifest(m: dict[str, Any]) -> dict[str, Any]:
    """Flatten a RunManifest dict into a single store row."""
    cls = m.get("classification", {})
    target = m.get("target", {})
    ex = m.get("execution", {}) or {}
    ev = m.get("evidence", {}) or {}
    return {
        "run_id": m.get("run_id", ""),
        "case_id": m.get("case_id", ""),
        "case_version": m.get("case_version", ""),
        "methodology_version": m.get("methodology_version", ""),
        "timestamp_utc": m.get("timestamp_utc", ""),
        "assessment_mode": m.get("assessment_mode", ""),
        "agent_id": target.get("agent_id", ""),
        "model_id": target.get("model_id", ""),
        "system_policy_hash": target.get("system_policy_hash", ""),
        "tool_policy_hash": target.get("tool_policy_hash", ""),
        "classification": cls.get("final", ""),
        "realized_harm": bool(cls.get("realized_harm")),
        "boundary_violation": bool(cls.get("boundary_violation")),
        "unauthorized_attempt": bool(cls.get("unauthorized_tool_attempt")),
        "persistent_compromise": bool(cls.get("persistent_compromise")),
        "semantic_failure": bool(cls.get("semantic_failure")),
        "overrefusal": bool(cls.get("overrefusal")),
        "evidence_transcript_count": len(ev.get("transcript", []) or []),
        "evidence_tool_call_count": len(ev.get("tool_calls", []) or []),
        "evidence_auth_count": len(ev.get("authorization", []) or []),
        "attacker_identity": ex.get("attacker_identity", ""),
        "channel_context": ex.get("channel_context", ""),
        "notes": m.get("notes", "") or "",
    }


class ResultsStore:
    """DuckDB-backed queryable store for ElicitSec run manifests."""

    def __init__(self, results_dir: str | Path, db_name: str = "elicitsec.duckdb"):
        self.results_dir = Path(results_dir)
        self.db_path = self.results_dir / db_name
        self.parquet_dir = self.results_dir / "parquet"
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.parquet_dir.mkdir(parents=True, exist_ok=True)
        self._con = duckdb.connect(str(self.db_path))
        self._con.execute(_CREATE_RUNS)

    # -- lifecycle -----------------------------------------------------------
    def close(self) -> None:
        """Close the DuckDB connection (write any pending data)."""
        self._con.close()

    def __enter__(self) -> "ResultsStore":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    # -- ingestion -----------------------------------------------------------
    def append(self, manifest: dict[str, Any] | Any) -> None:
        """Ingest one run manifest (dict or Pydantic RunManifest)."""
        if not isinstance(manifest, dict):
            manifest = manifest.model_dump(mode="json")
        self.append_many([manifest])

    def append_many(self, manifests: Iterable[dict[str, Any] | Any]) -> int:
        rows = []
        for m in manifests:
            if not isinstance(m, dict):
                m = m.model_dump(mode="json")
            rows.append(_row_from_manifest(m))
        if not rows:
            return 0
        # upsert on run_id (replace existing row for the same run). DuckDB
        # supports INSERT OR REPLACE which upserts on the PRIMARY KEY (run_id).
        cols = [
            "run_id","case_id","case_version","methodology_version",
            "timestamp_utc","assessment_mode","agent_id","model_id",
            "system_policy_hash","tool_policy_hash","classification",
            "realized_harm","boundary_violation","unauthorized_attempt",
            "persistent_compromise","semantic_failure","overrefusal",
            "evidence_transcript_count","evidence_tool_call_count",
            "evidence_auth_count","attacker_identity","channel_context","notes",
        ]
        placeholders = ",".join(["?"] * len(cols))
        colstr = ",".join(cols)
        for r in rows:
            self._con.execute(
                f"INSERT OR REPLACE INTO runs ({colstr}) VALUES ({placeholders})",
                [r.get(c) for c in cols],
            )
        self.export_parquet()
        return len(rows)

    def ingest_from_manifests(self, results_dir: str | Path | None = None) -> int:
        """Bulk-import all run-*.json manifests under a results dir."""
        base = self.results_dir if results_dir is None else Path(results_dir)
        manifests = []
        for p in sorted(base.glob("run-*.json")):
            try:
                manifests.append(json.loads(p.read_text()))
            except Exception:
                continue
        return self.append_many(manifests)

    # -- query ---------------------------------------------------------------
    @property
    def con(self) -> duckdb.DuckDBPyConnection:
        return self._con

    def query_rows(self, sql: str, params: dict | None = None) -> "list[dict[str, Any]]":
        """Run SQL and return rows as list-of-dicts (no pandas dependency)."""
        cur = self._con.execute(sql, params or {})
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]

    def runs(self) -> "list[dict[str, Any]]":
        return self.query_rows("SELECT * FROM runs ORDER BY timestamp_utc")

    def metrics(self) -> "list[dict[str, Any]]":
        """Per-classification aggregated percentage-of-runs table (rows-as-dicts)."""
        return self.query_rows(
            "SELECT classification, COUNT(*) AS n, "
            "ROUND(100.0*COUNT(*)/(SELECT COUNT(*) FROM runs), 1) AS pct "
            "FROM runs GROUP BY classification ORDER BY n DESC")

    def per_case(self) -> "list[dict[str, Any]]":
        """Per-case realized-harm/compromise rollup (rows-as-dicts)."""
        return self.query_rows(
            "SELECT case_id, COUNT(*) AS runs, "
            "   COUNT(*) FILTER (WHERE realized_harm) AS realized_harm, "
            "   COUNT(*) FILTER (WHERE persistent_compromise) AS persistent_compromise, "
            "   COUNT(*) FILTER (WHERE boundary_violation) AS boundary_violation, "
            "   COUNT(*) FILTER (WHERE unauthorized_attempt) AS unauthorized_attempt "
            "FROM runs GROUP BY case_id ORDER BY case_id")

    # -- export --------------------------------------------------------------
    def export_parquet(self) -> None:
        """Materialise runs / metrics / per_case tables to Parquet files."""
        self._con.execute(
            f"COPY (SELECT * FROM runs ORDER BY timestamp_utc) "
            f"TO '{self.parquet_dir / 'runs.parquet'}' (FORMAT PARQUET)"
        )
        self._con.execute(
            f"COPY (SELECT * FROM ({self.metrics_sql()})) "
            f"TO '{self.parquet_dir / 'metrics.parquet'}' (FORMAT PARQUET)"
        )
        self._con.execute(
            f"COPY (SELECT * FROM ({self.per_case_sql()})) "
            f"TO '{self.parquet_dir / 'per_case.parquet'}' (FORMAT PARQUET)"
        )

    def metrics_sql(self) -> str:
        return ("SELECT classification, COUNT(*) AS n, "
                "ROUND(100.0*COUNT(*)/(SELECT COUNT(*) FROM runs),1) AS pct "
                "FROM runs GROUP BY classification ORDER BY n DESC")

    def per_case_sql(self) -> str:
        return ("SELECT case_id, COUNT(*) AS runs, "
                "COUNT(*) FILTER (WHERE realized_harm) AS realized_harm, "
                "COUNT(*) FILTER (WHERE persistent_compromise) AS persistent_compromise, "
                "COUNT(*) FILTER (WHERE boundary_violation) AS boundary_violation, "
                "COUNT(*) FILTER (WHERE unauthorized_attempt) AS unauthorized_attempt "
                "FROM runs GROUP BY case_id ORDER BY case_id")

    # -- convenience ---------------------------------------------------------
    def load_runs_as_dicts(self) -> "list[dict[str, Any]]":
        """Return all rows as list-of-dict for the markdown report builder."""
        rows = self._con.execute("SELECT * FROM runs ORDER BY timestamp_utc").fetchall()
        cols = [c[0] for c in self._con.description]
        return [dict(zip(cols, r)) for r in rows]
