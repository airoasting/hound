# 채널: 빌리빌리 (Bilibili, 哔哩哔哩)

중국 최대 영상 커뮤니티. 기술 리뷰·튜토리얼·서브컬처. 중국 제품·기술 정보는 유튜브보다 여기가 두껍다.
**핵심: 영상 페이지는 JS 셸이라 스크랩이 안 된다. 메타·통계·자막·탄막은 무로그인 공개 JSON API로
가져온다.** ([access-tiers.md](access-tiers.md) 참조)

## 접근 현실 (직접 확인)

- **`WebSearch`가 bilibili.com에 닿는다**(레딧과 달리 차단 아님). 검색 스니펫에 조회수·좋아요까지 실려
  나올 때가 많아 디스커버리가 강하다.
- **영상 페이지 `WebFetch`는 JS 셸이다.** 제목·설명·통계가 HTML에 없고 추천 사이드바만 그려진다. 그러니
  메타데이터는 페이지 스크랩이 아니라 **JSON API**로 가져온다.
- **공개 API(`view`·`player`·탄막)는 무로그인 `code:0`이다.** 내부 검색 API만 -412 리스크컨트롤 대상이다.

## 긁는 순서

1. **디스커버리.** `WebSearch`로 `site:bilibili.com [중국어 키워드]`. 영상 URL(`/video/BV...`)에서 **BVID**와
   스니펫 지표를 얻는다. 빌리빌리 내부 검색 API(`x/web-interface/search/type`)는 412(HTML 안티크롤
   페이지)가 확률적으로 떠 불안정하고 `buvid3` 쿠키만으로는 안 풀리니, WebSearch가 더 안정적인 발견 경로다.
2. **영상 정보·통계·cid 확보(앵커).** `WebFetch`로 `https://api.bilibili.com/x/web-interface/view?bvid=<BVID>`.
   `code:0`이면 제목·설명·업로더와 **전체 통계(조회·탄막·좋아요·코인·즐겨찾기·댓글·공유)**, 그리고 자막·
   탄막에 필요한 **`cid`**까지 온다. 무로그인이고 412와 무관하다. **이 엔드포인트가 접근의 중심축이다.**
3. **자막(있으면).** `WebFetch`로 `https://api.bilibili.com/x/player/v2?bvid=<BVID>&cid=<cid>`를 열어
   `data.subtitle.subtitles[]`의 `.json` 자막 URL을 fetch한다. 배열이 비면 그 영상은 무로그인 자막이
   없는 것이다. 사람이 단 CC는 무로그인으로 보이지만 **AI 생성 자막은 로그인(SESSDATA)이 필요**하니,
   비어 있으면 지어내지 말고 4번(탄막)으로 대체한다.
4. **탄막(자막 대체 텍스트원).** 시청자 반응이 탄막에 텍스트로 쌓인다. `curl`로
   `https://comment.bilibili.com/<cid>.xml`을 받는데, 응답이 raw deflate 압축이라 풀어야 한다.
   ```bash
   curl -s "https://comment.bilibili.com/<cid>.xml" \
     | python3 -c "import sys,zlib; print(zlib.decompress(sys.stdin.buffer.read(), -15).decode('utf-8'))"
   ```
   `<d p="...">텍스트</d>` 요소가 각 탄막이다. cid는 2번에서 얻는다. 무로그인으로 견고하다.
5. **오디오(최후).** 자막도 탄막도 부족하면 `yt-dlp`로 오디오를 받아 전사한다([xiaoyuzhou.md](xiaoyuzhou.md)
   연계). 단 빌리빌리는 yt-dlp에 412를 자주 걸어 불안정하다. 쿠키·재시도·간격을 전제로 한 최후 수단으로 둔다.

## 챙길 숫자

`view` 응답에서 조회수·탄막 수·좋아요·코인·즐겨찾기·댓글·공유를 함께 회수한다. 화제성은 조회수와
탄막 수를 겹쳐 가늠한다.

## 요령 · 가드레일

- 중국 제품·부품·로봇 정보는 **중국어 키워드**로 판다. 한국어·영어로 안 나오던 게 나온다.
- 테스트가 필요하면 `aid=2`(`BV1xx411c7mD`, 빌리빌리 최고(最古) 영상)를 쓴다. `aid=1`은 숨김 처리돼
  `code:62002`를 낸다.
- 로그인이 필요한 AI 자막·비공개 콘텐츠는 우회하지 않고 "빌리빌리 로그인 필요"로 표시한다.
