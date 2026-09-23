"""Load and validate canonical YAML cases against schema + taxonomy."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Iterable
import yaml
from .models import ElicitationCase


class CaseLoadError(Exception):
    def __init__(self, path: str, detail: str):
        super().__init__(f"{path}: {detail}")
        self.path = path


def load_constructs(path: str | Path) -> dict[str, dict]:
    doc = yaml.safe_load(Path(path).read_text()) or {}
    out = {}
    for c in doc.get("constructs", []):
        out[c["id"]] = c
    return out


def load_case(path: str | Path, taxonomy: dict[str, dict] | None = None) -> ElicitationCase:
    path = Path(path)
    raw = path.read_text()
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as e:
        raise CaseLoadError(str(path), f"YAML parse error: {e}") from e
    if not isinstance(data, dict):
        raise CaseLoadError(str(path), "case file must be a YAML mapping")

    # JSON Schema validation (structural, per schemas/elicitation-case.schema.json)
    import jsonschema
    schema = json.loads(Path("schemas/elicitation-case.schema.json").read_text())
    try:
        jsonschema.validate(data, schema)
    except jsonschema.ValidationError as e:
        raise CaseLoadError(str(path), f"schema: {e.message} (path: {list(e.absolute_path)})") from e

    try:
        case = ElicitationCase.model_validate(data)
    except Exception as e:
        raise CaseLoadError(str(path), f"model: {e}") from e

    if taxonomy is not None:
        for c in case.constructs:
            if c not in taxonomy:
                raise CaseLoadError(str(path), f"construct {c!r} not in taxonomy/constructs.yaml")
    return case


def load_suite(dir_path: str | Path, taxonomy: dict[str, dict] | None = None) -> list[ElicitationCase]:
    root = Path(dir_path)
    cases = []
    for p in sorted(root.rglob("*.yaml")):
        cases.append(load_case(p, taxonomy))
    return cases


def load_all(suites_dir: str | Path, taxonomy: dict[str, dict] | None = None) -> list[ElicitationCase]:
    """Load every case under the suites tree (one dir per suite prefix)."""
    return load_suite(Path(suites_dir), taxonomy)
