import copy
import sys
from pathlib import Path

# (혹시라도 ModuleNotFoundError 방지용)
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from r_system.policy_engine import evaluate_policy


BASE_RS = {
    "schema_version": "risk_state.v0.1",
    "ts": "2026-03-04T09:05:00+09:00",
    "market": {
        "risk_level": 10,
        "regime": "normal",
        "commitment_score": 1,
        "pressure_score": 1,
        "amplifier_score": 1,
        "crave_total": 3,
        "evidence": [],
    },
    "account": {
        "equity_krw": 10000000,
        "cash_krw": 5000000,
        "equity_day_start": 10000000,
        "equity_peak": 10000000,
        "day_pnl_pct": 0.0,
        "portfolio_dd_pct": 0.0,
        "positions_count": 0,
        "gross_exposure_pct": 0.0,
        "max_symbol_weight_pct": 0.0,
    },
    "execution": {
        "orders_last_60s": 0,
        "orders_last_5m": 0,
        "duplicate_hits_60s": 0,
        "reject_count_60s": 0,
        "exec_anomaly": False,
        "anomaly_flags": [],
    },
}


def test_input_missing_block():
    rs = copy.deepcopy(BASE_RS)
    del rs["market"]["crave_total"]  # required
    out = evaluate_policy(rs)
    assert out["decision"] == "BLOCK"
    assert out["controls"]["entry_allowed"] is False
    assert out["controls"]["exit_allowed"] is True


def test_exec_anomaly_halt_reduce_only():
    rs = copy.deepcopy(BASE_RS)
    rs["execution"]["exec_anomaly"] = True
    out = evaluate_policy(rs)
    assert out["decision"] == "HALT"
    assert out["controls"]["entry_allowed"] is False
    assert out["controls"]["exit_allowed"] is True   # HQ 확정
    assert out["controls"]["reduce_only"] is True    # HQ 확정


def test_day_pnl_pct_threshold_halt():
    rs = copy.deepcopy(BASE_RS)
    rs["account"]["day_pnl_pct"] = -2.1
    out = evaluate_policy(rs)
    assert out["decision"] == "HALT"
    assert out["controls"]["reduce_only"] is True
    assert out["controls"]["exit_allowed"] is True


def test_crave_total_9_11_block_risk_off():
    rs = copy.deepcopy(BASE_RS)
    rs["market"]["crave_total"] = 9
    out = evaluate_policy(rs)
    assert out["decision"] == "BLOCK"
    assert out["risk_regime"] == "RISK_OFF"
    assert out["controls"]["entry_allowed"] is False
    assert out["controls"]["exit_allowed"] is True


def test_halt_exit_allowed_true_reduce_only_true():
    rs = copy.deepcopy(BASE_RS)
    rs["account"]["day_pnl_pct"] = -2.5
    out = evaluate_policy(rs)
    assert out["decision"] == "HALT"
    assert out["controls"]["exit_allowed"] is True
    assert out["controls"]["reduce_only"] is True