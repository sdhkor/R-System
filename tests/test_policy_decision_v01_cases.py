import json
from pathlib import Path

import pytest

try:
    import jsonschema
except ImportError:  # pragma: no cover
    jsonschema = None


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "r_system" / "schemas" / "policy_decision.v0.1.schema.json"


@pytest.mark.skipif(jsonschema is None, reason="jsonschema not installed")
@pytest.mark.parametrize(
    "obj",
    [
        {
            "schema_version": "policy_decision.v0.1",
            "ts": "2026-03-05T00:00:00",
            "decision": "ALLOW",
            "risk_regime": "NORMAL",
            "controls": {
                "entry_allowed": True,
                "exit_allowed": True,
                "reduce_only": False,
                "max_positions": 20,
                "max_total_exposure_pct": 100,
                "max_symbol_weight_pct": 10,
                "order_throttle": {"max_orders_per_min": 60, "min_seconds_between_orders": 1},
                "cooldown_minutes": 0,
            },
            "reasons": ["BASELINE:ok"],
            "meta": {"policy_set_id": "R.v0.1"},
        },
        {
            "schema_version": "policy_decision.v0.1",
            "ts": "2026-03-05T00:00:00",
            "decision": "BLOCK",
            "risk_regime": "RISK_OFF",
            "controls": {
                "entry_allowed": False,
                "exit_allowed": True,
                "reduce_only": True,
                "max_positions": 5,
                "max_total_exposure_pct": 30,
                "max_symbol_weight_pct": 5,
                "order_throttle": {"max_orders_per_min": 10, "min_seconds_between_orders": 6},
                "cooldown_minutes": 30,
            },
            "reasons": ["LOSS:dd_limit", "MARKET:risk_off"],
            "meta": {"policy_set_id": "R.v0.1"},
        },
        {
            "schema_version": "policy_decision.v0.1",
            "ts": "2026-03-05T00:00:00",
            "decision": "LIQUIDATE_ONLY",
            "risk_regime": "LIQUIDATE_ONLY",
            "controls": {
                "entry_allowed": False,
                "exit_allowed": True,
                "reduce_only": True,
                "max_positions": 0,
                "max_total_exposure_pct": 0,
                "max_symbol_weight_pct": 0,
                "order_throttle": {"max_orders_per_min": 5, "min_seconds_between_orders": 10},
                "cooldown_minutes": 0,
            },
            "reasons": ["DD:hard_stop => liquidate_only"],
            "meta": {"policy_set_id": "R.v0.1"},
        },
        {
            "schema_version": "policy_decision.v0.1",
            "ts": "2026-03-05T00:00:00",
            "decision": "HALT",
            "risk_regime": "HALT",
            "controls": {
                "entry_allowed": False,
                "exit_allowed": False,
                "reduce_only": True,
                "max_positions": 0,
                "max_total_exposure_pct": 0,
                "max_symbol_weight_pct": 0,
                "order_throttle": {"max_orders_per_min": 0, "min_seconds_between_orders": 999},
                "cooldown_minutes": 60,
            },
            "reasons": ["SAFETY:manual_halt"],
            "meta": {"policy_set_id": "R.v0.1"},
        },
    ],
)
def test_policy_decision_v01_schema_accepts_min_cases(obj):
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.validate(instance=obj, schema=schema)