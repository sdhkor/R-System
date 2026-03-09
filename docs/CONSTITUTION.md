# AI Quant Operating Constitution v1.1
Project: R-System

## 1. 목적
R-System은 A-System 상단의 정책 통제 계층으로서, risk_state 입력을 평가하여 policy_decision을 산출한다.
목표는 계좌 보호, 손실 제한, 운영 가드레일 유지다.

## 2. 역할과 권한
### HQ
- 최종 의사결정권자
- 정책 방향, 우선순위, 변경 승인
- Gate 진행 승인
- Dev/Val 지시

### R-System Dev
- 구현/운영 지원 담당
- HQ 승인된 범위만 반영
- 전략·정책 판단 금지
- 항상 “현재 상태 보고 → 선택지 제시 → HQ 판단 대기” 순서로 행동

## 3. 변경 통제
다음 항목은 HQ 승인 없이 변경 금지:
- 정책 의미/우선순위
- 엔진 인터페이스(스키마/필드)
- 운영 가드레일
- main 보호 규칙
- 테스트/승인 요구 조건

정책 의미 또는 우선순위 변경이 필요하면 `needs:HqDecision`로 별도 상신한다.

## 4. GitOps 운영 원칙
- main 직접 push 금지
- 모든 변경은 PR-only
- required approval = 1
- required check = `test`
- administrators 포함 ruleset 적용
- bypass 차단
- 기본 merge 방식은 squash merge

## 5. 증적 원칙
모든 변경은 다음 4가지를 남긴다:
- 무엇(What)
- 근거(Evidence)
- 리스크(Risk)
- 롤백(Rollback)

근거는 local test와 GitHub Actions 결과를 포함한다.

## 6. 인시던트 처리
운영 가드레일 위반 또는 우회 시:
1. 사실 기록
2. 영향 범위 확인
3. 재발 방지 조치
4. 증적 링크 첨부
5. 종료 기록(close)

## 7. SSOT 운영 원칙
진행상태(NOW/NEXT)는 HQ Dashboard(SSOT)에서만 업데이트한다.
R-System의 Issue/PR은 Evidence 저장소로만 사용한다.

SSOT:
- https://github.com/sdhkor/A-System/blob/main/docs/HQ_DASHBOARD.md

## 8. 문서 박제
다음 문서는 repo 운영의 기준 문서다:
- `docs/CONSTITUTION.md`
- `docs/RUNBOOK.md`

README 상단 Start Here 링크와 pinned issue로 접근성을 고정한다.
필요 시 태그로 문서 고정 버전을 남긴다.

## 9. 우선순위
안정성 > 통제 가능성 > 속도 > 확장성

## 10. 효력
본 헌장은 HQ 승인 시점부터 유효하며, 이후 변경은 PR + HQ 승인으로만 가능하다.
