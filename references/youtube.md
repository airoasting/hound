# 채널: 유튜브 (영상 속 정보 + 기간·순위 집계)

영상 안에 답이 있을 때가 많다. 세 가지 쓰임이 있고, 쓰임마다 방법이 다르다.
([access-tiers.md](access-tiers.md) 참조)

## 쓰임 1. 영상 찾기 (특정 주제의 영상 목록)

- `WebSearch`로 `site:youtube.com [키워드]` 검색이 가장 빠르다. 제목·링크를 얻는다.
- 네이버 `search_blog`/`search_webkr`에도 "유튜브 정리" 글이 많으니 교차로 훑는다.

## 쓰임 2. 영상 내용 읽기 (자막·설명·댓글)

`yt-dlp`로 영상을 **본문처럼** 읽는다. (없으면 `pip install yt-dlp` 또는 `brew install yt-dlp`)

- **자막 추출:** `yt-dlp --skip-download --write-auto-sub --sub-lang ko,en --sub-format vtt <URL>`
- **메타·설명·조회수:** `yt-dlp --skip-download --print "%(title)s|%(view_count)s|%(upload_date)s|%(channel)s" <URL>`
- **스로틀링 회피(중요):** 여러 영상을 연타하면 YouTube가 봇으로 차단한다("The page needs to be
  reloaded" 에러). 반드시 **`--extractor-args "youtube:player_client=android,ios,tv"`**를 붙이고
  `--sleep-requests 1`로 간격을 둔다. `web_safari` 단독 클라이언트는 잘 막힌다.
- 자막이 없으면 브라우저로 영상 페이지를 열어 설명란과 transcript 패널을 읽는다([web.md](web.md) 4칸).

## 쓰임 3. 기간·순위 영상 집계 (예: "최근 한 달 로봇 영상 top 10")

이건 개별 검색으로는 못 푼다. **`scripts/yt_collect.py`가 정공법이다.** (robot-radar에서 흡수한
검증된 엔진. 조회수·게시일을 실측해 기간 창으로 거르고 채널 중복까지 제거한다.)

```bash
# 최근 한 달(30일) 로봇 영상 조회수 top 10
python3 scripts/yt_collect.py --pack robot --days 30 --top 10 --out ./run
# (리포트 생성 전) 각 영상 요약을 top.json 의 note 에 채운다 (아래 참고)
python3 scripts/yt_render.py --top ./run/top.json --out ./run
```

**리포트를 만들기 전에 영상마다 2~3문장 요약을 채운다.** `top.json`의 각 항목에는 `note` 필드가 있다.
영상 제목과 설명(`description`)을 근거로, 그 영상이 무엇을 다루는지 2~3문장으로 요약해 `note`에 넣는다.
입니다체로, 자연스러운 한국어로, 주술 구조를 맞춰 쓴다. 원문에 없는 내용은 지어내지 않는다. 그런 다음
`yt_render.py`를 돌리면 요약이 리포트의 각 영상 카드 아래(MD·HTML)에 그대로 들어간다. 요약이 비어 있으면
리포트도 비어 보이니, 항상 채운 뒤 렌더링한다.

**왜 이게 되고 수동 검색은 안 되나 (아프게 배운 교훈):**

- 유튜브 조회수 상위는 몇 년 된 초대박 영상(1억+ 뷰)이 독식한다. 그냥 "조회수순"으로 뽑으면 최근
  영상이 영원히 밀려난다. `yt_collect.py`는 **검색 URL에 업로드 기간 필터(`sp` 파라미터)를 박아**
  flat 검색 단계부터 기간 내 영상만 모은다. `EgIIBA%3D%3D`=이번 달, `EgIIAw%3D%3D`=이번 주.
- 그다음 각 영상의 **정확한 timestamp로 `지금 - N일` 창을 다시** 걸어, 느슨한 검색 필터를 코드가 보정한다.
- android 클라이언트 + 병렬(ThreadPoolExecutor)로 스로틀링을 피하며 메타를 취득한다.

주요 옵션(자세한 근거는 [youtube-ranking-notes.md](youtube-ranking-notes.md)):

| 원하는 것 | 옵션 |
|---|---|
| 지금 뜨는(신선도) 우선 | `--rank velocity` |
| 한국 영상 위주 | `--region KR --lang ko` |
| 롱폼만 | `--no-shorts` |
| 후보를 더 넓게 | `--per-query 30 --max-candidates 50` |
| 정밀·고속(키 있으면) | `export YOUTUBE_API_KEY=...` 후 그대로 실행 |

**다른 주제로 확장:** 주제는 `assets/topic-packs.json`에 `queries`/`include`/`exclude`로 정의한다.
로봇 말고 다른 주제의 기간 top N이 필요하면 팩을 하나 추가하고 `--pack <이름>`으로 부른다.
