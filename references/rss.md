# 채널: RSS / Atom 피드

블로그·뉴스·릴리스·팟캐스트의 원천 피드. 무설정, 무키. 특정 사이트의 새 글을 시간순으로 훑을 때 최고다.
([access-tiers.md](access-tiers.md) 참조)

## 긁는 순서

1. **피드 URL 찾기.** 흔한 경로를 시도한다: `사이트/rss`, `사이트/feed`, `사이트/atom.xml`,
   `사이트/index.xml`, `사이트/rss.xml`. 블로그 플랫폼(티스토리 `/rss`, 워드프레스 `/feed`, 네이버블로그
   `rss.blog.naver.com/아이디.xml`)은 규칙적이다.
2. **피드 파싱.** `WebFetch`로 피드 XML을 열어 항목(제목·링크·날짜·요약)을 읽는다. 대량·정밀 파싱이
   필요하면 `python3 -c "import feedparser; ..."`(`pip install feedparser`).
3. **본문.** 피드 요약이 짧으면 각 항목 링크를 [access-tiers.md](access-tiers.md)의 본문 추출 사다리로 연다.

## 요령

- "이 블로그 최근 글 흐름"을 원하면 검색보다 RSS가 정확하고 시간순이다.
- 여러 피드를 모아 날짜순으로 병합하면 주제별 타임라인이 된다.
