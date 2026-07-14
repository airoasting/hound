# 채널: 샤오위저우 팟캐스트 (小宇宙) · 오디오 전사

팟캐스트·오디오 안에 든 정보를 **텍스트로 전사해** 읽는 채널. 인터뷰·대담·업계 이야기가 산다.
에피소드 페이지가 서버에서 그려져(SSR) **로그인 없이 제목·쇼노트·지표·오디오 직링크가 다 나온다.**
([access-tiers.md](access-tiers.md) 참조)

## URL 구조

- 에피소드: `xiaoyuzhoufm.com/episode/<24자리 hex ID>`
- 팟캐스트: `xiaoyuzhoufm.com/podcast/<24자리 hex ID>`

ID는 24자리 16진수다. **임의로 만들어 넣지 않는다.** 없는 ID는 404다. ID는 검색으로 얻는다.

## 긁는 순서

1. **에피소드 찾기.** `WebSearch`로 `site:xiaoyuzhoufm.com [키워드]`. 팟캐스트 이름을 알면 iTunes
   검색 API로 URL을 정확히 잡을 수 있다: `WebFetch`로
   `https://itunes.apple.com/search?term=[이름]&media=podcast&country=CN`.
2. **에피소드 페이지 열기.** `WebFetch`로 `xiaoyuzhoufm.com/episode/<ID>`를 연다. 로그인·JS 실행 없이
   제목, 쇼노트(shownotes) 전문, 설명, 발행일, 재생시간, 지표가 그대로 나온다. **쇼노트를 먼저 읽어**
   에피소드가 무엇을 다루는지, 어느 구간에 답이 있는지 좁힌다.
3. **오디오 직링크 확보.** 페이지 HTML에 mp3 주소가 두 곳에 박혀 있다.
   - `og:audio` 메타태그: `<meta property="og:audio" content="https://media.xyzcdn.net/....mp3">`
   - 백업: `<script id="__NEXT_DATA__">` JSON 안 `props.pageProps.episode.media.source.url`
   둘 중 하나를 파싱해 `media.xyzcdn.net/....mp3` 직링크를 얻는다.
4. **전사.** 직링크를 `curl -L`로 받아(무로그인, range 지원) Whisper 계열로 전사한다. Groq Whisper
   (무료 키) 같은 전사 API가 있으면 그걸, 없으면 로컬 `whisper`. 긴 에피소드는 3번에서 읽은 쇼노트로
   관련 구간을 특정한 뒤 그 부분만 전사하면 빠르다.

## 도구 선택 (아프게 배운 것)

- **Jina Reader는 쓰지 않는다.** 2025년부터 API 키를 요구해 무키 상태에서 `r.jina.ai`가 401을 낸다.
  어차피 페이지가 SSR이라 그냥 `WebFetch`면 본문이 다 나온다.
- **`yt-dlp`에 의존하지 않는다.** 샤오위저우 전용 extractor가 없어 generic이 og:audio를 잡을 때도,
  못 잡을 때도 있다. HTML에서 og:audio를 직접 파싱하는 편이 확실하다.

## 챙길 숫자 (공개 노출 확인됨)

| 지표 | 필드 | 어디에 |
|---|---|---|
| 재생 수 (播放) | `playCount` | 에피소드 |
| 댓글 수 (评论) | `commentCount` | 에피소드 |
| 좋아요 (拍手) | `clapCount` | 에피소드 |
| 재생시간·발행일 | `duration`(초), `pubDate` | 에피소드 |
| 에피소드 수 | `episodeCount` | 팟캐스트 |

- **구독자 수는 공개되지 않는다.** `subscriberCount`는 null로 나오니 "비공개"로 표시하고 지어내지 않는다.

## 요령

- 유튜브 영상도 자막이 없으면 같은 방식(오디오 전사)으로 처리한다. [youtube.md](youtube.md)와 연계.
- 댓글 본문 전체는 SSR에 일부만 담긴다. 숫자(commentCount)는 공개지만, 전체 댓글은 로그인 벽 뒤일 수
  있으니 그렇게 표시한다.
