# 채널: 네이버 (정보의 본진)

한국어 정보가 가장 두껍게 쌓이는 곳. 하나만 쓰지 말고 **성격에 맞는 하위 채널을 갈아탄다.**
모두 네이버 검색 MCP 도구(`NaverSearch-search_*`)로 접근한다. ([access-tiers.md](access-tiers.md) 참조)

**이 채널은 무설정이 아니다.** 네이버 검색 MCP와 API 키가 있어야 열린다. MCP가 없으면 아래
"MCP가 없을 때"로 바로 내려간다.

## 먼저 확인할 것: MCP가 연결돼 있나 (실측 2026-11-21)

세션 도구 목록에 `search_news`·`search_blog` 같은 네이버 검색 도구가 있는지 먼저 본다. 없으면 브라우저나
`WebFetch`로 네이버를 열어 보지 않는다. Claude Code 데스크톱 기준으로 세 경로 모두 네이버 도메인을 막는다.

| 경로 | 결과 |
|---|---|
| 네이버 검색 MCP | 연결돼 있을 때만 쓸 수 있다 |
| Claude in Chrome | `search.naver.com`, `news.naver.com`, `m.search.naver.com` 모두 "safety restrictions"로 차단 |
| 인앱 브라우저 | 같은 이유로 차단 |
| `WebFetch` | "unable to fetch from search.naver.com", `blog.naver.com`도 같다 |
| `WebSearch` | 네이버 페이지를 거의 색인하지 않는다. `site:n.news.naver.com`도 다른 매체만 나온다 |

### MCP 설치 (사용자가 직접)

`@isnow890/naver-search-mcp` 1.1.0 이상을 쓴다. hound가 부르는 도구 이름과 같다.

- **NAVER API HUB 키(권장, 신규 발급).** 네이버 클라우드 콘솔에서 Application Services → NAVER API HUB →
  Application 등록 후 인증 정보를 받는다. 환경변수는 `NCP_APIGW_API_KEY_ID`, `NCP_APIGW_API_KEY`다.
  공식 문서 기준 한시적 무료이고, 검색 API는 월 775,000건, 데이터랩은 API별 월 50,000건까지다.
- **개발자센터 키(기존).** 환경변수는 `NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET`다. 이 MCP의 README에 따르면
  2026-07-31부터 신규 발급이 막혔고, 이미 받은 키는 2027-06-30까지 동작한다.

```bash
claude mcp add NaverSearch -s user -e NCP_APIGW_API_KEY_ID=<ID> -e NCP_APIGW_API_KEY=<KEY> -- npx -y @isnow890/naver-search-mcp
```

키는 사용자가 터미널에서 직접 넣는다. 대화창에 붙여 넣게 하지 않는다. 등록 후 새 세션에서 도구가 보인다.

## 하위 채널 지도

| 쫓는 대상 | 도구 | 무엇이 사는가 |
|---|---|---|
| 실사용 후기·정리·튜토리얼 | `search_blog` | 개인 경험, 상세 후기 |
| 커뮤니티 심층 토론 | `search_cafearticle` | 취미·전문 카페의 니치 정보 |
| 질문과 답변 | `search_kin` | 문제 해결, 실무 팁 |
| 최신 뉴스·사실 | `search_news` | 시사, 속보, 검증된 사실 |
| 정의·개념·배경 | `search_encyc` | 백과사전식 정의 |
| 장소·상호 | `search_local` | 지역 업체, 영업정보 |
| 상품·가격 | `search_shop` | 쇼핑, 시세 |
| 이미지 | `search_image` | 시각 자료 |
| 웹문서 종합 | `search_webkr` | 위에 안 걸리는 한국어 웹 |
| 책·전문서 | `search_book` | 도서 정보 |
| 논문·학술 | `search_academic` | 학위·학술 논문, 연구 자료 |
| 검색 트렌드·수요 | `datalab_search` | 키워드 검색량 추이 |

## 긁는 요령

- **정렬.** `sort: "sim"`(유사도, 기본)과 `sort: "date"`(최신순)를 목적에 맞게 쓴다.
  "요즘/최근"이 붙으면 `date`, 정확도가 중요하면 `sim`.
- **오늘·최근 기준이 필요하면** 날짜를 먼저 확정한다. MCP 1.1.0은 날짜 파라미터에 `"today"` 키워드를
  받는다. 예전 버전에 있던 `get_current_korean_time` 도구가 목록에 없으면 Bash로 `TZ=Asia/Seoul date`를
  실행해 오늘 날짜를 얻는다.
- **display**를 7~10으로 넉넉히 잡아 한 번에 넓게 훑는다.
- **검색어는 여러 갈래.** "클로드코드 후기"가 안 나오면 "Claude Code 실사용", "클로드 코드 자동화"처럼
  표기(띄어쓰기·한영)와 동의어를 바꿔 재시도한다.

## 갈아타기 규칙

- 블로그가 광고성 글만 물어오면 → 카페(진짜 토론)나 지식iN(솔직한 질답)으로.
- 뉴스가 안 나오면 → 웹문서(`search_webkr`)로 넓힌다.
- 네이버 전체가 얇으면 → [web.md](web.md)의 WebSearch 영문 검색으로 채널을 바꾼다.

## MCP가 없을 때 (실측 2026-11-21~22)

네이버 원본에는 닿을 수 없다. 같은 정보가 사는 다른 곳으로 옮겨 간다. **검색을 시작하기 전에 사용자에게
한 문장으로 먼저 알린다.** 예: "네이버 검색 MCP가 연결돼 있지 않아 구글 뉴스와 웹 검색으로 찾습니다.
네이버 원본 목록은 아닙니다."

1. **국내 뉴스는 구글 뉴스.** 인앱 브라우저나 Claude in Chrome으로
   `https://www.google.com/search?q=<검색어>&tbm=nws&hl=ko&gl=kr`를 연다. 최근 24시간은 `&tbs=qdr:d`,
   1주일은 `&tbs=qdr:w`를 붙인다. `get_page_text`로 제목·매체·시각을 읽고, 기사 URL이 필요하면 결과
   링크의 `href`를 읽는다. 2026-11-21 크롬 실측에서 10건이 매체·시각과 함께 나왔고(output/20261121_01),
   2026-11-22 인앱 브라우저에서도 결과 본문이 보였다.
   - 같은 사건을 여러 매체가 다룬 기사는 한 묶음으로 합치고, 대표 기사 하나와 "외 N개 매체"로 적는다.
2. **브라우저가 둘 다 없으면 WebSearch 한국어 검색.** 연·월을 넣어 최근 기사를 좁힌다. 날짜가 없는 결과는
   "날짜 미상"으로 표시한다.
3. **블로그·후기도 WebSearch 한국어 검색.** 티스토리, 브런치, velog, 커뮤니티 정리 글이 잡힌다.
4. **결과에 경로를 정직하게 적는다.** 항목마다 `route`를 "대체(구글 뉴스)"나 "대체(웹 검색)"로 저장하고,
   결과 머리에 "네이버 원본 아님"을 표시한다([SKILL.md](../SKILL.md)의 "결과 저장"). 네이버 순위·댓글·공감
   수는 이 경로로 얻을 수 없으니 지어내지 않는다.
5. **사용자에게 MCP 설치를 안내한다.** 위 "MCP 설치"를 보여 준다.

**하지 않는 것.** 도구가 막은 네이버 도메인을 Bash `curl`이나 다른 도구로 다시 열지 않는다. 차단은
도구 정책이고, 다른 도구로 돌아가는 것은 우회다. 채널을 바꾼다.

## 로그인 벽

네이버 검색 결과는 대부분 공개다. 다만 일부 카페 글은 가입·등급이 필요하다. 그런 링크는 본문을
못 여니, 검색 스니펫까지만 근거로 쓰고 "카페 가입 필요"라고 표시한다. 우회하지 않는다.
