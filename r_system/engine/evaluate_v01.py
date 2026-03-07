# -*- coding: utf-8 -*-
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


def _utc_ts() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def evaluate_v01(risk_state: Dict[str, Any], policy_set_id: str = "R.v0.1") -> Dict[str, Any]:
    """
    R v0.1 core policy engine

    Input : risk_state.v0.1 (dict)
    Output: policy_decision.v0.1 (dict)

    원칙:
    - 정책의 "의미/우선순위" 변경은 HQ 승인 필요(needs:HqDecision).
    - v0.1은 다양한 입력 shape를 허용하되, 최상위(top-level) 값이 있으면 최상위를 우선한다.
    """

    reasons: List[str] = []

    # --- tolerate multiple shapes (v0.1 초기: top-level 우선, 없으면 nested fallback) ---
    market = risk_state.get("market", {}) if isinstance(risk_state.get("market", {}), dict) else {}
    loss = risk_state.get("loss", {}) if isinstance(risk_state.get("loss", {}), dict) else {}
    portfolio = risk_state.get("portfolio", {}) if isinstance(risk_state.get("portfolio", {}), dict) else {}

    # NOTE: top-level 우선 (tests/_set이 top-level을 바꿀 수 있으므로)
    crave_total = risk_state.get("crave_total", market.get("crave_total"))
    day_pnl_pct = risk_state.get("day_pnl_pct", loss.get("day_pnl_pct"))
    portfolio_dd_pct = risk_state.get("portfolio_dd_pct", portfolio.get("dd_pct"))

    regime = risk_state.get("regime")  # 예: "normal" | "risk" | "crisis"
    risk_level = risk_state.get("risk_level")  # 0~100 기대

    if day_pnl_pct is not None:
        reasons.append(f"LOSS:day_pnl_pct={day_pnl_pct}")
    if portfolio_dd_pct is not None:
        reasons.append(f"LOSS:portfolio_dd_pct={portfolio_dd_pct}")
    if crave_total is not None:
        reasons.append(f"MARKET:crave_total={crave_total}")
    if regime is not None:
        reasons.append(f"STATE:regime={regime}")
    if risk_level is not None:
        reasons.append(f"STATE:risk_level={risk_level}")

    # --- default ---
    decision = "ALLOW"
    risk_regime = "NORMAL"

    # --- decision rules (priority: HALT > LIQUIDATE_ONLY > BLOCK > ALLOW) ---
    # HALT: 위기 국면/초고위험
    try:
        if (isinstance(regime, str) and regime.lower() == "crisis") or (
            risk_level is not None and int(risk_level) >= 90
        ):
            decision = "HALT"
            risk_regime = "HALT"
            reasons.append("RULE: crisis or risk_level>=90 => HALT")
    except Exception:
        reasons.append("WARN: regime/risk_level parse failed")

    # LIQUIDATE_ONLY: 일간 손실 한도(예시) 초과 시 신규진입 금지 + 청산만
    if decision == "ALLOW":
        try:
            if day_pnl_pct is not None and float(day_pnl_pct) <= -3.0:
                decision = "LIQUIDATE_ONLY"
                risk_regime = "LIQUIDATE_ONLY"
                reasons.append("RULE: day_pnl_pct<=-3.0 => LIQUIDATE_ONLY")
        except Exception:
            reasons.append("WARN: day_pnl_pct parse failed")

    # BLOCK: 시장 과열(crave_total) 기준 (HQ-fixed 예시)
    if decision == "ALLOW":
        try:
            if crave_total is not None and float(crave_total) >= 9:
                decision = "BLOCK"
                risk_regime = "RISK_OFF"
                reasons.append("RULE: crave_total>=9 => RISK_OFF => BLOCK (HQ fixed)")
        except Exception:
            reasons.append("WARN: crave_total parse failed")

    # --- controls ---
    entry_allowed = decision == "ALLOW"
    reduce_only = decision != "ALLOW"

    if decision == "HALT":
        max_positions = 0
        max_total_exposure_pct = 0
        max_symbol_weight_pct = 0
        throttle = {"max_orders_per_min": 3, "min_seconds_between_orders": 20}
        cooldown_minutes = 60
    elif decision == "LIQUIDATE_ONLY":
        max_positions = 0
        max_total_exposure_pct = 0
        max_symbol_weight_pct = 0
        throttle = {"max_orders_per_min": 10, "min_seconds_between_orders": 6}
        cooldown_minutes = 30
    elif decision == "BLOCK":
        max_positions = 5
        max_total_exposure_pct = 30
        max_symbol_weight_pct = 5
        throttle = {"max_orders_per_min": 10, "min_seconds_between_orders": 6}
        cooldown_minutes = 30
    else:  # ALLOW
        max_positions = 10
        max_total_exposure_pct = 100
        max_symbol_weight_pct = 20
        throttle = {"max_orders_per_min": 60, "min_seconds_between_orders": 1}
        cooldown_minutes = 0

    controls = {
        "entry_allowed": entry_allowed,
        "exit_allowed": True,
        "reduce_only": reduce_only,
        "max_positions": max_positions,
        "max_total_exposure_pct": max_total_exposure_pct,
        "max_symbol_weight_pct": max_symbol_weight_pct,
        "order_throttle": throttle,
        "cooldown_minutes": cooldown_minutes,
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