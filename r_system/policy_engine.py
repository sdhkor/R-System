from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Tuple

from .config import PolicyConfigV01

Decision = str  # "ALLOW"|"BLOCK"|"LIQUIDATE_ONLY"|"HALT"


def _now_ts() -> str:
    return datetime.now().isoformat()


# HQ 확정: day_pnl_pct = (equity_now - equity_day_start)/equity_day_start*100
def _compute_day_pnl_pct(equity_now: float, equity_day_start: float) -> float:
    if equity_day_start <= 0:
        return 0.0
    return (equity_now - equity_day_start) / equity_day_start * 100.0


# HQ 확정: portfolio_dd_pct = (equity_now - equity_peak)/equity_peak*100  (음수)
def _compute_intraday_dd_pct(equity_now: float, equity_peak: float) -> float:
    if equity_peak <= 0:
        return 0.0
    return (equity_now - equity_peak) / equity_peak * 100.0


def _make_decision(
    *,
    decision: Decision,
    risk_regime: str,
    controls: Dict[str, Any],
    reasons: List[str],
    cfg: PolicyConfigV01,
) -> Dict[str, Any]:
    return {
        "schema_version": "policy_decision.v0.1",
        "ts": _now_ts(),
        "decision": decision,
        "risk_regime": risk_regime,
        "controls": controls,
        "reasons": reasons,
        "meta": {"policy_set_id": cfg.policy_set_id},
    }


def _validate_required_fields(rs: Dict[str, Any]) -> Tuple[bool, List[str]]:
    reasons: List[str] = []

    required_top = ["schema_version", "ts", "market", "account", "execution"]
    for k in required_top:
        if k not in rs:
            reasons.append(f"INPUT_MISSING:{k}")

    if rs.get("schema_version") != "risk_state.v0.1":
        reasons.append("INPUT_INVALID:schema_version")

    market = rs.get("market", {})
    account = rs.get("account", {})
    execution = rs.get("execution", {})

    req_market = ["risk_level", "regime", "commitment_score", "pressure_score", "amplifier_score", "crave_total"]
    req_account = [
        "equity_krw",
        "cash_krw",
        "equity_day_start",
        "equity_peak",
        "positions_count",
        "gross_exposure_pct",
        "max_symbol_weight_pct",
    ]
    req_exec = ["orders_last_60s", "orders_last_5m", "duplicate_hits_60s", "reject_count_60s", "exec_anomaly"]

    for k in req_market:
        if k not in market:
            reasons.append(f"INPUT_MISSING:market.{k}")
    for k in req_account:
        if k not in account:
            reasons.append(f"INPUT_MISSING:account.{k}")
    for k in req_exec:
        if k not in execution:
            reasons.append(f"INPUT_MISSING:execution.{k}")

    return (len(reasons) == 0), reasons


def evaluate_policy(risk_state: Dict[str, Any], cfg: PolicyConfigV01 | None = None) -> Dict[str, Any]:
    """
    R-System v0.1 policy evaluation (HQ 고정 순서):
      1) Input validation  -> default BLOCK
      2) Execution Safety
      3) Loss Containment
      4) Market Regime (Crave 3-sensors)
      5) Emit policy_decision
    """
    cfg = cfg or PolicyConfigV01()
    reasons: List[str] = []

    # 1) Input validation
    ok, v_reasons = _validate_required_fields(risk_state)
    if not ok:
        reasons.extend(v_reasons)
        reasons.append("RULE:INPUT_VALIDATION => BLOCK")
        controls = {
            "entry_allowed": False,
            "exit_allowed": True,
            "reduce_only": True,
            "max_positions": 5,
            "max_total_exposure_pct": 30,
            "max_symbol_weight_pct": 5,
            "order_throttle": {"max_orders_per_min": 10, "min_seconds_between_orders": 6},
            "cooldown_minutes": 10,
        }
        return _make_decision(decision="BLOCK", risk_regime="RISK_OFF", controls=controls, reasons=reasons, cfg=cfg)

    market = risk_state["market"]
    account = risk_state["account"]
    execution = risk_state["execution"]

    equity_now = float(account["equity_krw"])
    equity_day_start = float(account["equity_day_start"])
    equity_peak = float(account["equity_peak"])

    computed_day_pnl_pct = _compute_day_pnl_pct(equity_now, equity_day_start)
    computed_dd_pct = _compute_intraday_dd_pct(equity_now, equity_peak)

    day_pnl_pct = float(account.get("day_pnl_pct", computed_day_pnl_pct))
    dd_pct = float(account.get("portfolio_dd_pct", computed_dd_pct))

    # 2) Execution Safety
    if bool(execution["exec_anomaly"]) is True:
        reasons.append("EXEC:exec_anomaly=true => HALT(reduce-only)")
        controls = {
            "entry_allowed": False,
            "exit_allowed": True,   # HQ 확정
            "reduce_only": True,    # HQ 확정
            "max_positions": 0,
            "max_total_exposure_pct": 0,
            "max_symbol_weight_pct": 0,
            "order_throttle": {"max_orders_per_min": 2, "min_seconds_between_orders": 30},
            "cooldown_minutes": 60,
        }
        return _make_decision(decision="HALT", risk_regime="HALT", controls=controls, reasons=reasons, cfg=cfg)

    orders_60s = int(execution["orders_last_60s"])
    dup_60s = int(execution["duplicate_hits_60s"])
    rej_60s = int(execution["reject_count_60s"])

    if orders_60s >= cfg.flood_orders_60s or dup_60s >= cfg.dup_hits_60s or rej_60s >= cfg.reject_spike_60s:
        reasons.append(f"EXEC:spike orders_60s={orders_60s}, dup_60s={dup_60s}, rej_60s={rej_60s} => BLOCK")
        controls = {
            "entry_allowed": False,
            "exit_allowed": True,
            "reduce_only": True,
            "max_positions": 5,
            "max_total_exposure_pct": 30,
            "max_symbol_weight_pct": 5,
            "order_throttle": {"max_orders_per_min": 10, "min_seconds_between_orders": 6},
            "cooldown_minutes": 30,
        }
        return _make_decision(decision="BLOCK", risk_regime="RISK_OFF", controls=controls, reasons=reasons, cfg=cfg)

    # 3) Loss Containment (HQ 기준식 반영)
    reasons.append(f"LOSS:computed_day_pnl_pct={computed_day_pnl_pct:.4f}")
    reasons.append(f"LOSS:computed_dd_pct={computed_dd_pct:.4f}")
    reasons.append(f"LOSS:day_pnl_pct={day_pnl_pct:.4f}")
    reasons.append(f"LOSS:portfolio_dd_pct={dd_pct:.4f}")

    if day_pnl_pct <= cfg.daily_max_loss_pct:
        reasons.append(f"LOSS:day_pnl_pct<={cfg.daily_max_loss_pct} => HALT(reduce-only)")
        controls = {
            "entry_allowed": False,
            "exit_allowed": True,  # HQ 확정
            "reduce_only": True,   # HQ 확정
            "max_positions": 0,
            "max_total_exposure_pct": 0,
            "max_symbol_weight_pct": 0,
            "order_throttle": {"max_orders_per_min": 5, "min_seconds_between_orders": 10},
            "cooldown_minutes": 60,
        }
        return _make_decision(decision="HALT", risk_regime="HALT", controls=controls, reasons=reasons, cfg=cfg)

    if dd_pct <= cfg.intraday_dd_limit_pct:
        reasons.append(f"LOSS:dd_pct<={cfg.intraday_dd_limit_pct} => LIQUIDATE_ONLY(reduce-only)")
        controls = {
            "entry_allowed": False,
            "exit_allowed": True,
            "reduce_only": True,
            "max_positions": 0,
            "max_total_exposure_pct": 10,
            "max_symbol_weight_pct": 0,
            "order_throttle": {"max_orders_per_min": 10, "min_seconds_between_orders": 6},
            "cooldown_minutes": 60,
        }
        return _make_decision(
            decision="LIQUIDATE_ONLY",
            risk_regime="LIQUIDATE_ONLY",
            controls=controls,
            reasons=reasons,
            cfg=cfg,
        )

    # 4) Market Regime (Crave 3-sensors)
    crave_total = int(market["crave_total"])
    amplifier = int(market["amplifier_score"])

    if crave_total >= cfg.crave_liquidate_only_min or amplifier == 5:
        reasons.append(f"MARKET:crave_total={crave_total} or amplifier={amplifier} => LIQUIDATE_ONLY")
        controls = {
            "entry_allowed": False,
            "exit_allowed": True,
            "reduce_only": True,
            "max_positions": 0,
            "max_total_exposure_pct": 10,
            "max_symbol_weight_pct": 0,
            "order_throttle": {"max_orders_per_min": 10, "min_seconds_between_orders": 6},
            "cooldown_minutes": 60,
        }
        return _make_decision(
            decision="LIQUIDATE_ONLY",
            risk_regime="LIQUIDATE_ONLY",
            controls=controls,
            reasons=reasons,
            cfg=cfg,
        )

    # HQ 확정: RISK_OFF = BLOCK(신규진입 완전 차단) + exit_allowed=true
    if cfg.crave_risk_off_min <= crave_total <= 11:
        reasons.append(f"MARKET:crave_total={crave_total} => RISK_OFF => BLOCK(HQ fixed)")
        controls = {
            "entry_allowed": False,
            "exit_allowed": True,
            "reduce_only": True,
            "max_positions": 5,
            "max_total_exposure_pct": 30,
            "max_symbol_weight_pct": 5,
            "order_throttle": {"max_orders_per_min": 10, "min_seconds_between_orders": 6},
            "cooldown_minutes": 30,
        }
        return _make_decision(decision="BLOCK", risk_regime="RISK_OFF", controls=controls, reasons=reasons, cfg=cfg)

    if cfg.crave_caution_min <= crave_total <= 8:
        reasons.append(f"MARKET:crave_total={crave_total} => CAUTION")
        controls = {
            "entry_allowed": True,
            "exit_allowed": True,
            "reduce_only": False,
            "max_positions": 10,
            "max_total_exposure_pct": 60,
            "max_symbol_weight_pct": 7,
            "order_throttle": {"max_orders_per_min": 20, "min_seconds_between_orders": 3},
            "cooldown_minutes": 10,
        }
        return _make_decision(decision="ALLOW", risk_regime="CAUTION", controls=controls, reasons=reasons, cfg=cfg)

    # NORMAL
    reasons.append(f"MARKET:crave_total={crave_total} => NORMAL")
    controls = {
        "entry_allowed": True,
        "exit_allowed": True,
        "reduce_only": False,
        "max_positions": 20,
        "max_total_exposure_pct": 100,
        "max_symbol_weight_pct": 10,
        "order_throttle": {"max_orders_per_min": 30, "min_seconds_between_orders": 2},
        "cooldown_minutes": 0,
    }
    return _make_decision(decision="ALLOW", risk_regime="NORMAL", controls=controls, reasons=reasons, cfg=cfg)