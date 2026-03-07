from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


def _utc_ts() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def evaluate_v01(risk_state: Dict[str, Any], policy_set_id: str = "R.v0.1") -> Dict[str, Any]:
    """
    R v0.1 core policy engine (stub)

    Input:  risk_state.v0.1 (dict)
    Output: policy_decision.v0.1 (dict)

    NOTE
    - v0.1 목적: '정책 결정 로직의 형태/인터페이스'를 고정하는 것
    - 정책 '의미/우선순위' 변경은 HQ 승인 필요(needs:HqDecision).
    """

    reasons: List[str] = []

    # --- tolerate multiple shapes (v0.1 초기에는 유연하게) ---
    market = risk_state.get("market", {}) if isinstance(risk_state.get("market", {}), dict) else {}
    loss = risk_state.get("loss", {}) if isinstance(risk_state.get("loss", {}), dict) else {}
    portfolio = risk_state.get("portfolio", {}) if isinstance(risk_state.get("portfolio", {}), dict) else {}

    crave_total = market.get("crave_total", risk_state.get("crave_total"))
    day_pnl_pct = loss.get("day_pnl_pct", risk_state.get("day_pnl_pct"))
    dd_pct = portfolio.get("dd_pct", risk_state.get("dd_pct"))

    if day_pnl_pct is not None:
        reasons.append(f"LOSS:day_pnl_pct={day_pnl_pct}")
    if dd_pct is not None:
        reasons.append(f"LOSS:portfolio_dd_pct={dd_pct}")
    if crave_total is not None:
        reasons.append(f"MARKET:crave_total={crave_total}")

    # --- default: ALLOW ---
    decision = "ALLOW"
    risk_regime = "NORMAL"

    # --- HQ-fixed example rule (sample output 기준) ---
    try:
        if crave_total is not None and float(crave_total) >= 9:
            risk_regime = "RISK_OFF"
            decision = "BLOCK"
            reasons.append("RULE:crave_total>=9 => RISK_OFF => BLOCK(HQ fixed)")
    except Exception:
        reasons.append("WARN:crave_total parse failed")

    # --- minimal safe controls (v0.1 baseline) ---
    # Allow: 진입 허용
    # Block: 진입 차단 + 익절/손절 등 청산은 허용
    # Liquidate/Halt(추후): 진입 차단 + reduce-only(감소/청산만) 방향
    controls = {
        "entry_allowed": decision == "ALLOW",
        "exit_allowed": True,
        "reduce_only": decision != "ALLOW",
        "max_positions": 10 if decision == "ALLOW" else 5,
        "max_total_exposure_pct": 100 if decision == "ALLOW" else 30,
        "max_symbol_weight_pct": 20 if decision == "ALLOW" else 5,
        "order_throttle": {
            "max_orders_per_min": 60 if decision == "ALLOW" else 10,
            "min_seconds_between_orders": 1 if decision == "ALLOW" else 6,
        },
        "cooldown_minutes": 0 if decision == "ALLOW" else 30,
    }

    return {
        "schema_version": "policy_decision.v0.1",
        "ts": _utc_ts(),
        "decision": decision,
        "risk_regime": risk_regime,
        "controls": controls,
        "reasons": reasons,
        "meta": {"policy_set_id": policy_set_id},
    }