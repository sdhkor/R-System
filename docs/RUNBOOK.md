# Runbook v1.0
Project: R-System

## 1. 목적
R-System의 일상 운영, 변경 절차, 테스트, 병합, 인시던트 대응을 표준화한다.

## 2. 기본 운영 원칙
- main 직접 push 금지
- 변경은 PR-only
- local `pytest -q` 선행
- GitHub Actions `test` PASS 확인 후 병합
- required approval = 1 유지
- squash merge 기본

## 3. 표준 작업 절차
1. `git switch main && git pull`
2. `git switch -c <topic-branch>`
3. 수정
4. `pytest -q`
5. `git add -A && git commit -m "<type>: <msg>"`
6. `git push -u origin <topic-branch>`
7. PR 생성
8. Actions PASS 확인
9. 승인 후 squash merge
10. 브랜치 삭제(선택)

## 4. 브랜치 네이밍 예시
- `feat/r-...`
- `fix/r-...`
- `docs/r-...`
- `test/r-...`
- `chore/r-...`

## 5. PR 최소 템플릿
- 무엇(What)
- 근거(Evidence)
- 리스크(Risk)
- 롤백(Rollback)

예시:
- local: `pytest -q` PASS
- Actions: `test` PASS

## 6. 변경 금지 항목
HQ 승인 없이 금지:
- 정책 의미/우선순위 변경
- 인터페이스 스키마/필드 변경
- 운영 가드레일 완화
- 승인/체크 요구치 하향
- main 보호 규칙 변경

## 7. 핫픽스 원칙
- 긴급 상황이어도 PR-only 원칙 유지
- 사후 인시던트 로그 필수
- bypass 사용 금지

## 8. 롤백
문제 발생 시:
- 원칙: PR revert
- 필요 시 이전 안정 커밋/태그 기준 복구
- 정책 의미 변경이 수반되면 HQ 승인 후 진행

## 9. SSOT 운영 원칙
진행상태(NOW/NEXT)는 HQ Dashboard(SSOT)에서만 업데이트한다.
Issue/PR은 Evidence 저장소로만 사용한다.

SSOT:
- https://github.com/sdhkor/A-System/blob/main/docs/HQ_DASHBOARD.md

## JIT Approval Procedure
- required approval에 막히면, 승인 전용 2nd account에 write 권한을 임시 부여한다.
- 2nd account로 Approve 1회를 수행한 뒤, 메인 계정으로 merge를 완료한다.
- merge 완료 직후 2nd account collaborator 권한은 즉시 remove한다.
  
## 10. Start Here 유지
README 상단에 다음 링크를 유지한다:
- HQ Dashboard (SSOT)
- Constitution
- Runbook

Pinned Start Here issue에는 일반 링크와 permalink를 함께 기록한다.

