# R-System GitHub 운영 지침서 v1.0
(대상: R-System Dev / Val / HQ)  
기준일: 2026-03-04  
목표: “정책 엔진(R-System) v0.1”을 Gate 기반으로 안전하게 개발/검증/승인한다.

---

## 0) 운영 원칙 (고정)
1) **Evidence First**: 모든 변경은 Issue/PR/Report로 증명한다.
2) **Gate 기반**: Gate 통과 후 다음 확장.
3) **Main 보호**: main merge는 **HQ 승인 후**에만.
4) **복붙 최소화**: HQ 공유는 “Issue/PR 링크 1개 + 3줄 요약”이 기본.
5) **정책 vs 구현 분리**: 정책 의미 변경은 HQ 승인 없이는 금지(스키마/코드만 바꾸는 것도 의미가 바뀌면 “정책 변경”).

---

## 1) Repo 기본 구조(권장)
- `r_system/` : 패키지 본체
- `schemas/` : JSON Schema (버전 폴더/파일로 관리)
- `examples/` : 샘플 출력(예: `policy_decision.sample.json`)
- `tests/` : pytest 기반 테스트
- `docs/` : 운영문서(이 가이드 포함)
- `reports/` : **gitignore 대상** (산출물은 보통 커밋하지 않음)
  - 단, 폴더 유지용 `.gitkeep`는 허용(운영 안정 목적)

> 원칙: 재현 가능한 샘플은 `examples/`, 실험 산출물은 `reports/`.

---

## 2) 역할/책임
### HQ
- 승인/보류/조건부 승인 결정
- 정책 의미(규칙, 우선순위, 상태 전이) 최종 확정

### R Dev
- 스키마/인터페이스/코드 구현
- PR 제출, 테스트/샘플/문서 동기화 책임

### Val
- 스키마 적합성/회귀 테스트/동작 검증
- Issue로 증거 제출(로그/샘플/재현 절차)

---

## 3) 브랜치 전략
- `main`: 보호 브랜치(직접 push 금지)
- `dev`: 통합 브랜치(선택) — 팀 규모 작으면 생략 가능
- 작업 브랜치 네이밍:
  - `feat/<topic>`
  - `fix/<bug>`
  - `chore/<maintenance>`
  - `docs/<doc>`
  - `test/<coverage>`

> 원칙: 1 PR = 1 목적(범위 과대 금지)

---

## 4) Issue 운영 규칙
### Issue 타입(권장 라벨)
- `type:feature` / `type:bug` / `type:refactor` / `type:docs` / `type:test`
- `gate:0.1` / `gate:1` / `gate:2` / `gate:3`
- `risk:low` / `risk:med` / `risk:high`
- `needs:HqDecision` (정책 의미가 바뀌는 경우 필수)

### Issue 템플릿(본문 최소 요구)
- 목적(1~3줄)
- 변경 범위(파일/모듈)
- 근거/증거(로그/샘플/테스트 결과)
- Done 정의(어떤 출력/테스트면 완료인지)

---

## 5) PR 운영 규칙 (필수 체크리스트)
### PR 생성 규칙
- **반드시 연관 Issue 링크**
- `Closes #<id>` 또는 `Refs #<id>`
- 변경 이유/리스크/롤백 방법 1~2줄 포함

### PR 체크리스트(필수)
- [ ] `pytest -q` 통과
- [ ] 스키마 변경 시: **샘플(`examples/`) 업데이트 + 테스트 보강**
- [ ] breaking 가능성 있으면 라벨 `risk:high` + `needs:HqDecision`
- [ ] 정책 의미 변경이면 “정책 변경”이라고 명시하고 HQ 승인 대기
- [ ] 문서 필요 시 `docs/` 업데이트

### 병합 규칙
- **HQ 승인 전 main merge 금지**
- baseline/Gate 종료 시점에만 main 정리 merge (원칙)

---

## 6) 커밋 메시지 규칙(권장)
- Conventional Commits 스타일:
  - `feat: ...`
  - `fix: ...`
  - `chore: ...`
  - `docs: ...`
  - `test: ...`
  - `refactor: ...`

> 한글/영문 혼용 가능. 핵심은 “검색 가능성/의미 명확성”.

---

## 7) 스키마/버전 관리 규칙
- 스키마 파일명에 버전 명시(예: `policy_decision.v0.1.schema.json`)
- 스키마 변경 시:
  1) 변경 사유
  2) 하위호환 여부
  3) 샘플 갱신
  4) 테스트 갱신
  를 PR 본문에 기록

> 원칙: “스키마가 곧 인터페이스 계약”이다.

---

## 8) 산출물/아티팩트 관리
- `reports/`는 기본 gitignore (실험 로그/덤프는 저장만)
- 공유해야 할 “대표 샘플”만 `examples/`에 커밋
- 대용량/민감정보 포함 파일 커밋 금지

---

## 9) 보안/비밀정보
- API 키/계정/토큰/로컬 경로(개인정보성) 커밋 금지
- `.env` 사용 시 `.env.example`만 커밋
- 로깅에 계정번호 등 민감값 출력 금지(마스킹)

---

## 10) HQ 보고 규칙(복붙 최소화)
R Dev → HQ 보고는 아래만 지킨다.
- “Issue/PR 링크 1개”
- “3줄 요약(무엇/근거/리스크)”
- “HQ가 결정해야 할 1개 질문(있을 때만)”

예시:
- 무엇: v0.1 policy_decision 스키마 확정 + 샘플/테스트 추가
- 근거: pytest 통과 + 샘플 파일 생성
- 리스크: 없음(하위호환 유지)
- 질문: (필요 시) 이 상태로 main merge 승인?

---

## 11) 보호 설정(Repo 관리자용 권장)
- main branch protection:
  - PR 없이 merge 금지
  - status check(예: pytest) 필수
  - 최소 1 승인(review) 필요(가능하면 HQ 또는 지정자)
- CODEOWNERS(선택):
  - `schemas/` 변경은 HQ review 필수로 설정 가능

---

## 12) “핫픽스” 예외 규정
baseline/Gate 운영 중에는 변경 동결이 원칙.
단, 아래만 예외:
- 데이터 누락/크래시/치명적 오류(재현 증거 포함)
- 최소 수정으로 복구 가능
- PR에 `HOTFIX` 명시 + 영향 범위/롤백 1줄

---

## 13) 초기 세팅 체크리스트(1회)
- [ ] labels 세팅(type/gate/risk/needs)
- [ ] Issue/PR 템플릿 추가
- [ ] `reports/` gitignore + `.gitkeep` 정책 확정
- [ ] CI(선택): GitHub Actions로 `pytest -q` 자동화
- [ ] `docs/`에 운영문서(이 파일) 커밋