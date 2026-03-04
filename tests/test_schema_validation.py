import json
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "r_system" / "schemas"
EXAMPLES = ROOT / "r_system" / "examples"


def _load(p: Path):
    # Out-File(utf8)이 BOM을 붙일 수 있어서 utf-8-sig로 안전하게 읽음
    return json.loads(p.read_text(encoding="utf-8-sig"))


def test_risk_state_sample_matches_schema():
    schema = _load(SCHEMAS / "risk_state.v0.1.schema.json")
    sample = _load(EXAMPLES / "risk_state.sample.json")
    jsonschema.validate(instance=sample, schema=schema)


def test_policy_decision_sample_matches_schema():
    schema = _load(SCHEMAS / "policy_decision.v0.1.schema.json")
    # policy_decision은 run_sample 출력과 동일 구조여야 함 → 예제 파일이 없으면 run_sample 결과를 저장해도 됨
    # 우선은 run_sample로 만든 출력 JSON을 policy_decision.sample.json으로 저장해두는 방식 추천
    sample_path = EXAMPLES / "policy_decision.sample.json"
    assert sample_path.exists(), "policy_decision.sample.json not found. Save run_sample output into this file."
    sample = _load(sample_path)
    jsonschema.validate(instance=sample, schema=schema)