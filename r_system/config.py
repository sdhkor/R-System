from dataclasses import dataclass


@dataclass(frozen=True)
class PolicyConfigV01:
    policy_set_id: str = "R.v0.1"

    # Loss containment thresholds (HQ 확정 기반: v0.1 시작값)
    daily_max_loss_pct: float = -2.0       # day_pnl_pct <= triggers HALT (reduce-only)
    intraday_dd_limit_pct: float = -5.0    # portfolio_dd_pct <= triggers LIQUIDATE_ONLY

    # Execution safety thresholds (v0.1 보수값)
    flood_orders_60s: int = 20
    dup_hits_60s: int = 3
    reject_spike_60s: int = 5

    # Market regime mapping (갈애 3센서)
    crave_liquidate_only_min: int = 12
    crave_risk_off_min: int = 9
    crave_caution_min: int = 6