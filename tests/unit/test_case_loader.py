import sys
from pathlib import Path
import pytest
import yaml

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from elicitsec.case_loader import load_case, load_all, load_constructs, CaseLoadError


def test_load_all_canonical_cases():
    taxonomy = load_constructs(REPO / "taxonomy" / "constructs.yaml")
    cases = load_all(REPO / "suites", taxonomy)
    ids = sorted(c.id for c in cases)
    # 6 original canonical cases + II-001 (indirect-injection suite)
    assert len(cases) >= 7
    for expect in ("AUTH-001","DIR-001","EGR-001","II-001","RAG-001","STATE-001","UTIL-001"):
        assert expect in ids


def test_util_case_has_empty_adversarial_message():
    taxonomy = load_constructs(REPO / "taxonomy" / "constructs.yaml")
    c = load_case(REPO / "suites" / "utility-controls" / "UTIL-001.yaml", taxonomy)
    assert c.adversarial_condition.message in (None, "")


def test_bad_case_id_rejected(tmp_path):
    taxonomy = load_constructs(REPO / "taxonomy" / "constructs.yaml")
    p = tmp_path / "bad.yaml"
    doc = yaml.safe_load((REPO / "suites" / "authorization" / "AUTH-001.yaml").read_text())
    doc["id"] = "lower-001"
    p.write_text(yaml.safe_dump(doc))
    with pytest.raises(CaseLoadError):
        load_case(p, taxonomy)


def test_unknown_construct_rejected(tmp_path):
    taxonomy = load_constructs(REPO / "taxonomy" / "constructs.yaml")
    p = tmp_path / "badconstruct.yaml"
    doc = yaml.safe_load((REPO / "suites" / "authorization" / "AUTH-001.yaml").read_text())
    doc["constructs"] = ["OBJ-99"]
    p.write_text(yaml.safe_dump(doc))
    with pytest.raises(CaseLoadError):
        load_case(p, taxonomy)


def test_missing_required_field_rejected(tmp_path):
    taxonomy = load_constructs(REPO / "taxonomy" / "constructs.yaml")
    p = tmp_path / "missing.yaml"
    doc = yaml.safe_load((REPO / "suites" / "authorization" / "AUTH-001.yaml").read_text())
    del doc["utility_control"]
    p.write_text(yaml.safe_dump(doc))
    with pytest.raises(CaseLoadError):
        load_case(p, taxonomy)
