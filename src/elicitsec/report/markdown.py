"""Markdown report generator (docs/reports/report-template.md)."""
from __future__ import annotations
import json
from pathlib import Path
from collections import Counter


def load_runs(results_dir: str | Path) -> list[dict]:
    runs = []
    for p in sorted(Path(results_dir).glob("run-*.json")):
        runs.append(json.loads(p.read_text()))
    return runs


def _metric(runs: list[dict], key: str, cls_value: str) -> float:
    if not runs:
        return 0.0
    n = sum(1 for r in runs if r.get("classification", {}).get(key) == cls_value)
    return round(100.0 * n / len(runs), 1)


def build_report(runs: list[dict], *, target_name: str = "mock rig",
                 mode: str = "black_box", methodology_version: str = "0.1") -> str:
    total = len(runs)
    lines = [
        f"# ElicitSec assessment report - {target_name}",
        "",
        f"- Runs: {total}",
        f"- Methodology version: {methodology_version}",
        f"- Assessment mode: {mode}",
        "",
        "## Summary metrics",
        "",
        "| Metric | Value (%) |",
        "|---|---|",
        f"| PASS | {_metric(runs, 'final', 'PASS')} |",
        f"| SAFE_REFUSAL | {_metric(runs, 'final', 'SAFE_REFUSAL')} |",
        f"| OVERREFUSAL | {_metric(runs, 'final', 'OVERREFUSAL')} |",
        f"| SEMANTIC_FAILURE | {_metric(runs, 'final', 'SEMANTIC_FAILURE')} |",
        f"| UNAUTHORIZED_ATTEMPT | {_metric(runs, 'final', 'UNAUTHORIZED_ATTEMPT')} |",
        f"| BOUNDARY_VIOLATION | {_metric(runs, 'final', 'BOUNDARY_VIOLATION')} |",
        f"| REALIZED_HARM | {_metric(runs, 'final', 'REALIZED_HARM')} |",
        f"| PERSISTENT_COMPROMISE | {_metric(runs, 'final', 'PERSISTENT_COMPROMISE')} |",
        f"| HARNESS_ERROR | {_metric(runs, 'final', 'HARNESS_ERROR')} |",
        f"| INCONCLUSIVE | {_metric(runs, 'final', 'INCONCLUSIVE')} |",
        "",
        "## Per-case detail",
        "",
    ]
    by_case: dict[str, list[dict]] = {}
    for r in runs:
        by_case.setdefault(r["case_id"], []).append(r)
    for case_id in sorted(by_case):
        group = by_case[case_id]
        counts = Counter(r["classification"]["final"] for r in group)
        lines.append(f"### {case_id}")
        lines.append(f"- runs: {len(group)}  |  classification: "
                     + ", ".join(f"{k} x{v}" for k, v in sorted(counts.items())))
        worst = min((r["classification"]["final"] for r in group),
                    key=lambda c: {"REALIZED_HARM":0,"PERSISTENT_COMPROMISE":1,"BOUNDARY_VIOLATION":2,
                                   "UNAUTHORIZED_ATTEMPT":3,"SEMANTIC_FAILURE":4,"OVERREFUSAL":5,
                                   "HARNESS_ERROR":6,"INCONCLUSIVE":7,"SAFE_REFUSAL":8,"PASS":9}.get(c, 9))
        sample = next(r for r in group if r["classification"]["final"] == worst)
        reasons = sample["classification"].get("reasons") or []
        for reason in reasons[:4]:
            lines.append(f"  - {reason}")
        lines.append("")
    lines.append("## Reproduction")
    lines.append("")
    lines.append("```sh")
    lines.append("elicitsec run --suite suites --adapter mock --out results/local")
    lines.append("elicitsec report --from results/local --out results/local/report.md")
    lines.append("```")
    return "\n".join(lines) + "\n"


def write_report(runs: list[dict], out_path: str | Path, **kw) -> Path:
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build_report(runs, **kw))
    return out
