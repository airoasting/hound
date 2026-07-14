# scripts

여기에는 결정적(deterministic) 다단계 작업만 스크립트로 있습니다. 채널을 긁는 일 대부분은 도구 호출
한두 번으로 끝나므로 스크립트가 없습니다. 이는 누락이 아니라 의도된 설계입니다.

- `yt_collect.py`, `yt_render.py`: 유튜브 기간·순위 집계와 리포트(아래 설명).
- `save_result.py`: 찾은 결과(또는 증거 보고)를 JSON으로 받아 `output/{날짜}_{순번}/`에 `result.md`와
  `result.html`로 저장합니다. 매번 손으로 마크다운·HTML을 조립하지 않게 이 작업만 코드로 고정했습니다.
  사용법은 [SKILL.md](../SKILL.md)의 "결과 저장"을 봅니다.
- `verify_access.py`: 채널 문서(`references/*.md`)의 접근 주장이 아직 유효한지 실측합니다(아래 설명).

## 왜 채널을 긁는 스크립트는 없나

Hound는 대부분의 채널을 도구 호출 한두 번으로 처리합니다. 네이버는 검색 MCP, 웹과 레딧과 V2EX와
GitHub은 검색과 페이지 열람, RSS는 피드 열람으로 끝납니다. 이런 작업은 코드로 감쌀 이유가 없습니다.
스크립트를 늘리면 유지보수 부담만 생기고, 설치가 필요 없다는 강점도 사라집니다. 그래서 여기 있는
스크립트는 손으로 하면 자주 틀리는 결정적 다단계 작업(유튜브 순위 집계, 결과 파일 저장)뿐입니다.

## 파일

- `yt_collect.py`: 한 주제의 기간 안 영상을 모아 조회수 순위 top N을 뽑습니다. 검색, 메타데이터 취득,
  정확한 게시일로 기간 재확인, 조회수 정렬, 채널 중복 제거를 정확히 밟습니다. yt-dlp(키 불필요)를 기본으로
  쓰고, `YOUTUBE_API_KEY`가 있으면 더 빠른 API 경로를 씁니다. 손으로 하면 유튜브의 느슨한 기간 필터와
  봇 차단 때문에 자주 어긋나서 코드로 고정했습니다.
- `yt_render.py`: 위 수집 결과를 마크다운과 HTML 리포트로 만듭니다.
- `save_result.py`: 검색 결과 JSON을 받아 `output/{날짜}_{순번}/`에 `result.md`와 `result.html`을 만듭니다.
- `verify_access.py`: 각 채널 문서가 근거로 삼는 엔드포인트를 문서와 같은 방식(브라우저 UA curl)으로 때려
  보고 PASS/FAIL로 보고합니다. 플랫폼의 차단 정책·API 스펙은 수시로 바뀌므로, 분기 1회쯤 돌려 문서가
  현실과 아직 맞는지 확인합니다. FAIL이 뜨면 그 문서를 다시 실측·수정합니다. MCP·브라우저 전용 채널
  (네이버·유튜브·페이스북 등)은 curl로 재현할 수 없어 SKIP으로 표시합니다. 종료 코드는 FAIL 개수입니다.
  실행: `python3 scripts/verify_access.py`

유튜브 사용법은 [references/youtube.md](../references/youtube.md)와
[references/youtube-ranking-notes.md](../references/youtube-ranking-notes.md), 결과 저장은
[SKILL.md](../SKILL.md)의 "결과 저장"에 있습니다.

## 새 스크립트를 언제 추가하나

다음을 모두 만족할 때만 추가합니다. 여러 단계를 정확한 순서로 밟아야 하고, 손으로 하면 자주 틀리며,
여러 요청에서 똑같이 반복됩니다. 한두 번의 도구 호출로 끝나는 작업은 스크립트로 만들지 않습니다.
