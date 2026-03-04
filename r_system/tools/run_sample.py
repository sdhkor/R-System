import json
from pathlib import Path

from r_system.policy_engine import evaluate_policy


ROOT = Path(__file__).resolve().parents[2]
SAMPLE = ROOT / "r_system" / "examples" / "risk_state.sample.json"


def main():
    risk_state = json.loads(SAMPLE.read_text(encoding="utf-8"))
    decision = evaluate_policy(risk_state)
    print(json.dumps(decision, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()