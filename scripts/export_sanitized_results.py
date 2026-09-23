"""Export sanitized aggregate metrics for publication (no raw evidence).

Usage: python scripts/export_sanitized_results.py --from results/local --out results/sanitized-public
"""
import argparse
import json
from collections import Counter
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="src", default="results/local")
    ap.add_argument("--out", default="results/sanitized-public")
    a = ap.parse_args()

    src, out = Path(a.src), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    runs = [json.loads(p.read_text()) for p in src.glob("run-*.json")]
    counts = Counter(r.get("classification", {}).get("final") for r in runs)
    by_case = {}
    for r in runs:
        by_case.setdefault(r["case_id"], []).append(
            r.get("classification", {}).get("final"))
    # SANITIZED: aggregate counts only. No transcripts, no identifiers, no refs.
    payload = {
        "total_runs": len(runs),
        "classification_counts": dict(counts),
        "per_case": {k: dict(Counter(v)) for k, v in sorted(by_case.items())},
        "note": "Aggregated results only. Raw evidence never leaves the local rig.",
    }
    (out / "sanitized-metrics.json").write_text(json.dumps(payload, indent=2))
    print(f"wrote {out / 'sanitized-metrics.json'}")


if __name__ == "__main__":
    main()
