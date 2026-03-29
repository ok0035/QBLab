---
name: blog-deploy
description: 코드 리뷰 → develop 커밋/푸시 → main 머지/푸시 (블로그 배포)
allowed-tools: Read, Bash, Glob, Grep, Edit
user-invocable: true
---

# 블로그 배포 스킬

변경사항을 리뷰하고, develop에 커밋/푸시한 뒤 main에 머지하여 배포한다.

## Phase 1: 변경사항 확인

```bash
cd $REPO_ROOT
git status
git diff --stat
git diff
```

- 변경된 파일 목록과 내용을 확인한다.
- 변경사항이 없으면 "배포할 변경사항이 없습니다"를 출력하고 종료한다.

## Phase 1.5: 썸네일 이미지 검증

커버 이미지가 포함된 포스트가 있으면, 이미지 내용이 포스트 데이터와 일치하는지 확인한다.

### 검증 항목
- cover 필드에 지정된 이미지 파일이 `static/` 하위에 존재하는지 확인
- 이미지를 Read 도구로 열어 눈으로 확인: 가격, 변동률(±N.N%), 포지션, 공포탐욕지수가 포스트 본문과 일치하는지 대조

### 이미지 재생성이 필요한 경우

```bash
python scripts/generate_dashboard.py \
  --price '$69,000' \
  --change="-2.5%" \
  --position NEUTRAL \
  --fear-greed 10 \
  --output static/images/posts/260327-dashboard.png
```

**파라미터 규칙:**
- `--change`: 반드시 `+N.N%` 또는 `-N.N%` 형식. 음수는 `--change="-2.5%"` 형식(= 사용)
- `--position`: LONG, SHORT, NEUTRAL (한글도 가능: 롱, 숏, 관망)
- 이미지에 날짜/URL은 표시하지 않음 (--date 파라미터 없음)
- 하단 표시: "포지션 — 롱/숏/없음", "공포지수 — N"

### 재생성 후
- 생성된 이미지를 Read 도구로 열어 올바르게 렌더링되었는지 반드시 확인한다

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

**이슈가 있으면 수정 후 다시 리뷰한다. 이슈가 없을 때만 Phase 3으로 진행.**

## Phase 3: Hugo 빌드 검증

```bash
cd $REPO_ROOT
hugo --gc --minify 2>&1
```

- 빌드 에러가 있으면 출력하고 중단한다.
- 빌드 성공 시 public/ 은 커밋하지 않는다 (GitHub Actions가 배포 시 빌드).

## Phase 4: develop 커밋 & 푸시

```bash
git add -A
git status
```

- 변경사항을 분석하여 커밋 메시지를 자동 생성한다.
- 커밋 메시지 형식:

```
<type>: <한글 요약>

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
```

- type 규칙:
  - `post` — 새 포스팅 추가
  - `fix` — 기존 포스트/설정 수정
  - `style` — 테마/CSS 변경
  - `seo` — SEO 관련 변경
  - `feat` — 새 기능 (스크립트, 템플릿 등)
  - `chore` — 기타 (설정, 의존성 등)

- 여러 유형이 섞여 있으면 가장 중요한 변경 기준으로 type을 결정한다.

```bash
git commit -m "$(cat <<'EOF'
<type>: <요약>

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
git push origin develop
```

## Phase 5: main 머지 & 푸시

```bash
git checkout main
git merge develop
git push origin main
git checkout develop
```

- fast-forward 머지를 기본으로 한다.
- 충돌이 발생하면 중단하고 사용자에게 알린다.

## Phase 6: 완료 보고

```
## 배포 완료

- 커밋: <hash> <message>
- develop: ✅ pushed
- main: ✅ merged & pushed
- GitHub Actions 배포 트리거됨
- 사이트: https://qblab.kr
```
