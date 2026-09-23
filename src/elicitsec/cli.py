"""elicitsec CLI (typer).

    elicitsec cases                     list cases
    elicitsec validate [--all]          schema + taxonomy validation
    elicitsec run --suite DIR --adapter mock --behavior safe|leaky
    elicitsec report --from results/local --out report.md
"""
from __future__ import annotations
from pathlib import Path
from typing import Optional
import typer
import yaml

from . import __version__
from .case_loader import load_all, load_constructs, load_case, CaseLoadError
from .safety_gate import load_environment
from .adapters.mock import MockAgent
from .runners.orchestrator import Orchestrator
from .report.markdown import load_runs, write_report

app = typer.Typer(help="ElicitSec - evidence-led security evaluation for enterprise agents.",
                  no_args_is_help=True)

REPO = Path(__file__).resolve().parents[2]   # repo root (src/elicitsec/cli.py -> root)


def _repo_root() -> Path:
    return REPO


@app.command()
def version():
    """Print version."""
    typer.echo(__version__)


@app.command()
def cases(directory: str = "suites"):
    """List all loadable cases under a suites directory."""
    taxonomy = load_constructs(_repo_root() / "taxonomy" / "constructs.yaml")
    for c in load_all(_repo_root() / directory, taxonomy):
        typer.echo(f"{c.id:10s} tier={c.consequence_tier}  {c.title}")


@app.command()
def validate(all: bool = True, directory: str = "suites"):
    """Validate cases against schema + taxonomy. Non-zero exit on any failure."""
    taxonomy = load_constructs(_repo_root() / "taxonomy" / "constructs.yaml")
    ok = 0
    failed = 0
    for c in load_all(_repo_root() / directory, taxonomy):
        typer.echo(f"OK   {c.id}")
        ok += 1
    # also report unparseable files (load_all raises on the first; scan manually)
    for p in sorted((_repo_root() / directory).rglob("*.yaml")):
        try:
            load_case(p, taxonomy)
        except CaseLoadError as e:
            typer.secho(f"FAIL {e}", fg=typer.colors.RED, err=True)
            failed += 1
    typer.echo(f"\n{ok} cases load cleanly; {failed} file-level failures")
    if failed:
        raise typer.Exit(1)


@app.command()
def run(suites: str = "suites",
        adapter: str = "mock",
        behavior: str = "safe",
        max_tier: int = 4,
        out: str = "results/local",
        evidence: str = "evidence"):
    """Run all cases in a suites dir against an adapter (default: mock)."""
    root = _repo_root()
    if adapter != "mock":
        raise typer.Exit(f"adapter {adapter!r} not yet implemented (milestone 2+)")

    # canary registry
    canary_doc = yaml.safe_load((root / "fixtures" / "canary-data" / "registry.yaml").read_text()) or {}
    canaries = canary_doc.get("markers", {})
    protected = ["Project Atlas - Security Guidance", "protected-workiq-canary-001"]

    # working copy of the policy baseline so leaky runs can mutate it safely
    import shutil, tempfile
    tmp = tempfile.mkdtemp(prefix="elicitsec-policy-")
    policy_path = Path(tmp) / "policy.txt"
    shutil.copy(root / "fixtures" / "state-fixtures" / "policy-baseline.txt", policy_path)

    ag = MockAgent(root / "fixtures" / "mock-responses.json",
                   behavior=behavior, policy_path=policy_path)
    env = load_environment(
        max_allowed_tier=max_tier,
        register_path=root / "data" / "safe-target-register" / "register.yaml",
        approvals_path=root / "data" / "approvals.yaml",
    )
    orch = Orchestrator(ag, env, canaries,
                        protected_identifiers=protected,
                        results_dir=root / out,
                        evidence_dir=root / evidence)

    taxonomy = load_constructs(root / "taxonomy" / "constructs.yaml")
    from .evaluators.utility import check_utility_control
    summary = []
    for case in load_all(root / suites, taxonomy):
        outcome = orch.run_case(case)
        m = outcome.run_manifest
        summary.append((case.id, m.classification.final, m.classification.reasons))
        typer.echo(f"{case.id:10s} -> {m.classification.final:20s} "
                   f"{(m.classification.reasons[0] if m.classification.reasons else '')[:80]}")
    typer.echo("\nDone. Manifests in " + out)


@app.command()
def report(src: str = "results/local", out: str = "results/local/report.md",
           target: str = "mock rig"):
    """Generate a Markdown report from run manifests."""
    runs = load_runs(src)
    p = write_report(runs, out, target_name=target)
    typer.echo(f"wrote {p}")


def main():
    app()


if __name__ == "__main__":
    main()
