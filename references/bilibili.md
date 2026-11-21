# 채널: 빌리빌리 (Bilibili, 哔哩哔哩)

중국 최대 영상 커뮤니티. 기술 리뷰·튜토리얼·서브컬처. 중국 제품·기술 정보는 유튜브보다 여기가 두껍다.
**핵심: 영상 페이지는 JS 셸이라 `WebFetch` 스크랩이 안 된다. 메타·통계는 `yt-dlp`로, 탄막은 공개 XML로
가져온다.** ([access-tiers.md](access-tiers.md) 참조)

## 접근 현실 (실측 2026-11-21)

| 경로 | 결과 |
|---|---|
| `yt-dlp -J` | 됨. 제목·업로더·게시일·조회·좋아요·댓글 수가 온다. `cid`는 오지 않는다 |
| 탄막 XML (`comment.bilibili.com/<cid>.xml`) | 됨 |
| `view` API (`api.bilibili.com/x/web-interface/view`) | curl에서 **412**. 문서가 예전에 적은 "무로그인 `code:0`"과 다르다. `WebFetch`로는 아직 시험하지 않았다 |
| 인앱 브라우저·Claude in Chrome | 홈이 열린다 |
| `WebSearch` | bilibili.com에 닿는다. 스니펫에 조회수·좋아요가 실릴 때가 많다 |

- **영상 페이지 `WebFetch`는 JS 셸이다.** 제목·설명·통계가 HTML에 없다. 메타데이터는 페이지 스크랩이
  아니라 `yt-dlp`나 API로 가져온다.
- **내부 검색 API(`x/web-interface/search/type`)는 412 리스크컨트롤 대상이다.** 발견은 WebSearch로 한다.

## 긁는 순서 (되는 것부터)

1. **디스커버리.** `WebSearch`로 `site:bilibili.com [중국어 키워드]`. 영상 URL(`/video/BV...`)에서 **BVID**와
   스니펫 지표를 얻는다.
2. **영상 정보·통계: `yt-dlp`.** 
   ```bash
   yt-dlp --ies default,-generic -J --skip-download "https://www.bilibili.com/video/<BVID>"
   ```
   JSON에서 `title`, `uploader`, `upload_date`, `view_count`, `like_count`, `comment_count`를 회수한다.
   코인·즐겨찾기·탄막 수와 `cid`는 여기에 없다.
3. **`cid`와 전체 통계가 필요하면 `view` API.** `WebFetch`로
   `https://api.bilibili.com/x/web-interface/view?bvid=<BVID>`. `code:0`이면 코인·즐겨찾기·탄막·공유 수와
   **`cid`**가 온다. 412가 나면 다시 시도하지 않는다. 그때는 탄막·자막 없이 2번 숫자로 마무리하거나,
   검색 스니펫과 다른 채널로 보강한다.
4. **자막(cid가 있을 때).** `WebFetch`로 `https://api.bilibili.com/x/player/v2?bvid=<BVID>&cid=<cid>`를 열어
   `data.subtitle.subtitles[]`의 `.json` 자막 URL을 fetch한다. 배열이 비면 무로그인 자막이 없는 것이다.
   **AI 생성 자막은 로그인(SESSDATA)이 필요**하니, 비어 있으면 지어내지 말고 5번(탄막)으로 대체한다.
5. **탄막(cid가 있을 때).** 시청자 반응이 탄막에 텍스트로 쌓인다. 응답이 raw deflate 압축이라 풀어야 한다.
   ```bash
   curl -s "https://comment.bilibili.com/<cid>.xml" \
     | python3 -c "import sys,zlib; print(zlib.decompress(sys.stdin.buffer.read(), -15).decode('utf-8'))"
   ```
   `<d p="...">텍스트</d>` 요소가 각 탄막이다. 무로그인으로 견고하다.
6. **오디오(최후).** 자막도 탄막도 부족하면 `yt-dlp`로 오디오를 받아 전사한다([xiaoyuzhou.md](xiaoyuzhou.md)
   연계).

## 챙길 숫자

`yt-dlp`에서 조회수·좋아요·댓글 수를, `view` API가 열리면 탄막 수·코인·즐겨찾기·공유까지 회수한다.
화제성은 조회수와 탄막 수를 겹쳐 가늠한다. 확인하지 못한 숫자는 비워 둔다.

## 요령 · 가드레일

- 중국 제품·부품·로봇 정보는 **중국어 키워드**로 판다. 한국어·영어로 안 나오던 게 나온다.
- 테스트가 필요하면 `aid=2`(`BV1xx411c7mD`, 빌리빌리 최고(最古) 영상)를 쓴다. `aid=1`은 숨김 처리돼
  `code:62002`를 낸다.
- 로그인이 필요한 AI 자막·비공개 콘텐츠는 우회하지 않고 "빌리빌리 로그인 필요"로 표시한다.
