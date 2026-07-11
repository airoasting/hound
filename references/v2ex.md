# 채널: V2EX

중화권 개발자·기술 커뮤니티. 프로그래밍, 창업, 원격근무, 기술 제품 토론이 산다. **공개 JSON API가
있어 무설정으로 긁힌다.** ([access-tiers.md](access-tiers.md) 참조)

## 긁는 순서 (무로그인)

1. **공개 API를 `WebFetch`.**
   - 인기 토픽: `https://www.v2ex.com/api/topics/hot.json`
   - 최신 토픽: `https://www.v2ex.com/api/topics/latest.json`
   - 노드별 토픽: `https://www.v2ex.com/api/topics/show.json?node_name=노드`
   - 토픽 상세·댓글: `https://www.v2ex.com/api/replies/show.json?topic_id=ID`
2. **웹 검색.** `WebSearch`로 `site:v2ex.com [키워드]`로 특정 토픽을 찾은 뒤 위 API로 상세를 연다.

## 요령

- 기술 제품·서비스에 대한 개발자들의 솔직한 평가를 얻기 좋다.
- 중국어·영어 키워드 모두 시도한다. 개발 용어는 영어가 많다.
