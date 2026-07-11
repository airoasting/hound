# 채널: 레딧 (Reddit)

해외 실사용 경험·토론·솔직한 평가의 본진. 영어권 니치 정보는 여기가 네이버 카페 격이다.
익명 접근이 막혀 있어 **공개 엔드포인트 요령**이 필요하다. ([access-tiers.md](access-tiers.md) 참조)

## 긁는 순서

1. **웹 검색.** `WebSearch`로 `site:reddit.com [키워드]`. 특정 서브레딧이면 `site:reddit.com/r/이름 [키워드]`.
2. **`.json` 엔드포인트(핵심).** 레딧은 대부분 URL 뒤에 `.json`을 붙이면 공개 JSON을 준다.
   - 글+댓글: `https://www.reddit.com/r/서브/comments/글ID.json`
   - 서브레딧 인기글: `https://www.reddit.com/r/서브/hot.json?limit=25`
   - 검색: `https://www.reddit.com/search.json?q=키워드&sort=relevance`
   → 이 URL들을 `WebFetch`로 연다. 무료·무키.
3. **old.reddit.com** 버전은 가볍고 잘 열린다. 막히면 여기로.
4. **로그인 벽.** 성인·비공개·삭제된 글은 안 보인다. 사용자 허락 하에 실제 크롬 세션으로 로그인 상태
   공개 글을 읽거나, "레딧 로그인 필요"로 보고한다.

## 요령

- 댓글에 진짜 정보가 있다. 상위 댓글(top-voted)을 우선 읽는다.
- "제품명 + reddit"으로 웹 검색하면 솔직한 평가 스레드가 바로 나온다.
- 여러 서브레딧이 같은 주제를 다루면 교차 검증한다.
