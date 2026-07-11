# 채널: 샤오홍슈 (小红书, RED / XiaoHongShu)

중국 MZ의 라이프스타일·뷰티·소비·여행 후기 본진. 실사용 리뷰와 트렌드가 산다. 로그인 벽이 강해
**공개 범위만** 쫓는다. ([access-tiers.md](access-tiers.md) 참조)

## 긁는 순서

1. **웹 검색.** `WebSearch`로 `site:xiaohongshu.com [키워드]`(중국어). 공개 노트가 잡힌다.
2. **공개 노트 열기.** URL을 `WebFetch`/Jina Reader로 연다. 공개 게시물 본문·태그가 보인다.
3. **실제 크롬 세션(정공법).** 검색·댓글·피드는 대부분 로그인을 요구한다. 사용자 허락 하에 실제 로그인된
   크롬(claude-in-chrome)으로 **읽기만**. Agent-Reach의 OpenCLI/xiaohongshu-mcp 역할.

## 요령 · 가드레일

- 중국 소비 트렌드·제품 실사용 반응 조사에 강하다. 중국어 키워드 필수.
- 로그인·비공개는 우회하지 않고 "샤오홍슈 로그인 필요"로 보고한다.
