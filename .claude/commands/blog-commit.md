---
name: blog-commit
description: 코드 리뷰 → 썸네일/포스팅 검증 → main 동기화 → develop 커밋
allowed-tools: Read, Bash, Glob, Grep, Edit, AskUserQuestion
user-invocable: true
---

# 블로그 커밋 스킬

변경사항을 리뷰하고, 썸네일과 포스팅을 검증한 뒤 develop 브랜치에 커밋한다.

## Phase 1: 변경사항 확인

```bash
cd $REPO_ROOT
git status
git diff --stat
git diff
```

- 변경된 파일 목록과 내용을 확인한다.
- 변경사항이 없으면 "커밋할 변경사항이 없습니다"를 출력하고 종료한다.
- 현재 브랜치가 develop이 아니면 "develop 브랜치에서 실행해주세요"를 출력하고 종료한다.

## Phase 2: 코드 리뷰

변경된 파일을 유형별로 리뷰한다.

### 2-1. Hugo 콘텐츠 (content/)
- frontmatter 필수 필드 확인: title, date, tags, description, author, draft
- cover 필드가 있으면 해당 이미지 파일 존재 여부 확인
- draft: false 인지 확인
- 마크다운 문법 오류 확인

### 2-2. 템플릿/테마 (themes/, layouts/)
- HTML 태그 닫힘 확인
- Hugo 템플릿 문법 오류 확인 ({{ }})
- CSS 문법 확인

### 2-3. 스크립트 (scripts/)
- Python 문법 오류 확인 (python3 -m py_compile)
- import 누락 확인

### 2-4. 설정 (hugo.toml, static/)
- 설정값 유효성 확인
- 경로 참조 유효성 확인

### 2-5. 공통
- 민감 정보 노출 여부 (API 키, 토큰, 비밀번호)
- .gitignore에 포함되어야 할 파일이 커밋되지 않는지 확인

리뷰 결과를 요약하여 출력한다:
```
## 코드 리뷰 결과

변경 파일: N개
- ✅ file1.md — 정상
- ✅ file2.html — 정상
- ⚠️ file3.py — 경고: [내용]

이슈: 없음 / N건
```

**이슈가 있으면 수정 후 다시 리뷰한다. 이슈가 없을 때만 다음 Phase로 진행.**

## Phase 3: 썸네일 이미지 검증

커버 이미지가 포함된 포스트가 변경사항에 있으면, 이미지를 검증한다.

### 검증 항목
- cover 필드에 지정된 이미지 파일이 `static/` 하위에 존재하는지 확인
- 이미지를 Read 도구로 열어 눈으로 확인:
  - 날짜가 포스트 date와 일치하는지
  - 가격이 포스트 본문의 가격과 일치하는지
  - 변동률이 `±N.N%` 형식으로 올바르게 표시되는지 (▲/▼ 방향, 색상)
  - 포지션(LONG/SHORT/NEUTRAL)이 포스트 본문과 일치하는지
  - 공포탐욕지수가 포스트 본문과 일치하는지

### 이미지 재생성이 필요한 경우

```bash
python scripts/generate_dashboard.py \
  --date "2026. 03. 27" \
  --price '$69,000' \
  --change="-2.5%" \
  --position NEUTRAL \
  --fear-greed 10 \
  --output static/images/posts/260327-dashboard.png
```

**--change 형식 규칙:**
- 반드시 `+N.N%` 또는 `-N.N%` 형식을 사용한다
- 하락일 때는 반드시 `-` 부호를 붙인다
- `--change` 옵션에 음수를 전달할 때는 `--change="-2.5%"` 형식(= 사용)으로 전달한다

### 재생성 후
- 생성된 이미지를 Read 도구로 열어 올바르게 렌더링되었는지 반드시 확인한다

## Phase 4: main 브랜치 동기화

develop에 커밋하기 전에 main에 새로운 커밋이 있는지 확인하고 동기화한다.

```bash
git fetch origin main
git log develop..origin/main --oneline
```

### 4-1. main에 새 커밋이 없는 경우
- 동기화 불필요. Phase 5로 진행한다.

### 4-2. main에 새 커밋이 있는 경우

```bash
git rebase origin/main
```

- **충돌이 없으면** 그대로 Phase 5로 진행한다.
- **충돌이 발생하면:**
  1. `git rebase --abort`로 rebase를 중단한다.
  2. 충돌 파일 목록과 내용을 사용자에게 보여준다.
  3. 기본 원칙은 main 우선이지만, main의 버그를 수정한 것일 수 있으므로 **반드시 사용자에게 어떻게 해결할지 물어본다**.
  4. 사용자의 지시에 따라 충돌을 해결한다.

## Phase 5: develop 커밋

```bash
git add -A
git status
```

- 변경사항을 분석하여 커밋 메시지를 자동 생성한다.
- 커밋 메시지 형식:

```
<type>: <한글 요약>
```

- type 규칙:
  - `post` — 새 포스팅 추가
  - `trades` — 실매매내역 업데이트
  - `fix` — 기존 포스트/설정/이미지 수정
  - `style` — 테마/CSS 변경
  - `seo` — SEO 관련 변경
  - `feat` — 새 기능 (스크립트, 템플릿 등)
  - `chore` — 기타 (설정, 의존성 등)

- 여러 유형이 섞여 있으면 가장 중요한 변경 기준으로 type을 결정한다.
- **협업자(Co-Authored-By)를 포함하지 않는다.**

```bash
git commit -m "$(cat <<'EOF'
<type>: <요약>
EOF
)"
```

## Phase 6: 완료 보고

```
## 커밋 완료

- 커밋: <hash> <message>
- 브랜치: develop
- main 동기화: ✅ 완료 / ⏭️ 불필요
```
