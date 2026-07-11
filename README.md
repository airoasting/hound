# Hound 🐕 (사냥개)

![Version](https://img.shields.io/badge/version-1.0.0-2ea44f)
![License](https://img.shields.io/badge/license-MIT-2f81f7)
![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-8A63FF)
![Channels](https://img.shields.io/badge/channels-16-e8873a)
![Works on ChatGPT](https://img.shields.io/badge/works%20on-ChatGPT-10A37F)

> 물면 안 놓는다.

일반 검색이 "검색 결과가 없습니다"로 포기하는 지점에서, Hound는 냄새를 놓지 않는다. 질의를 다시
짜고 채널을 갈아타며 답이 나올 때까지 끝까지 추격한다. 진짜로 없을 때만 멈추고, 그때조차 어디까지
뒤졌는지를 증거로 물어온다.

## 왜 만들었나

한 번 검색해서 안 나오면 대부분의 도구는 거기서 끝난다. 하지만 정작 답답한 순간은 "한 방에 안
나오는" 정보를 찾을 때다. 묻힌 사실, 오래된 자료, 애매한 키워드, 여러 채널을 교차해야 겨우 나오는
답. Hound는 바로 그 자리를 위해 만들었다. 포기하는 검색이 아니라 추격하는 검색이다.

## 무엇을 하나

- **포기하지 않는다.** 0건은 종료가 아니라 재추격 신호다. 검색어와 채널을 바꿔 다시 문다.
- **한 채널에 갇히지 않는다.** 한국인이 정보를 쌓아두는 곳을 빠짐없이 뒤진다.
- **증거로 물어온다.** 찾은 것은 출처와 함께, 못 찾은 것은 추격 기록과 함께 보고한다.

## 어디를 긁나 (채널)

Hound는 하나의 도구가 아니라 **추격을 지휘하는 라우터**다. 무엇을 쫓을지 판단해 알맞은 채널을 붙이고,
각 채널을 긁는 법은 채널별 참조 문서를 따른다. 이 구조는 [Agent-Reach](https://github.com/Panniantong/Agent-Reach)의
채널 추상화에서 따왔다.

| 채널 | 무엇이 사는가 | 참조 |
|---|---|---|
| **네이버** | 블로그·카페·지식iN·뉴스·백과·지역. 한국어 정보의 본진 | [naver.md](references/naver.md) |
| **유튜브** | 영상 속 정보, 실사용 반응, 기간·순위 영상 집계 | [youtube.md](references/youtube.md) |
| **X (트위터)** | 실시간 여론·속보·당사자 발언 | [x-twitter.md](references/x-twitter.md) |
| **쓰레드** | 일상 후기, 한국 사용자 반응, 밈 | [threads.md](references/threads.md) |
| **인스타그램** | 프로필·최근 게시물·해시태그·비주얼 트렌드 | [instagram.md](references/instagram.md) |
| **페이스북** | 공개 페이지·그룹의 지역·커뮤니티 정보 | [facebook.md](references/facebook.md) |
| **레딧** | 해외 실사용 경험·솔직한 평가·니치 토론 | [reddit.md](references/reddit.md) |
| **링크드인** | 인물 경력·회사·채용·B2B | [linkedin.md](references/linkedin.md) |
| **GitHub** | 코드·오픈소스·이슈·릴리스 | [github.md](references/github.md) |
| **RSS/Atom** | 블로그·뉴스·릴리스 원천 피드 | [rss.md](references/rss.md) |
| **빌리빌리** | 중국 기술 리뷰·튜토리얼·서브컬처 | [bilibili.md](references/bilibili.md) |
| **샤오홍슈** | 중국 라이프·소비·여행 실사용 후기 | [xiaohongshu.md](references/xiaohongshu.md) |
| **슈에추 (雪球)** | 중국 증시·종목 토론·투자자 여론 | [xueqiu.md](references/xueqiu.md) |
| **V2EX** | 중화권 개발자·기술 제품 토론 (공개 API) | [v2ex.md](references/v2ex.md) |
| **샤오위저우** | 팟캐스트·오디오 전사해 읽기 | [xiaoyuzhou.md](references/xiaoyuzhou.md) |
| **웹 일반** | 사실·문서·해외 정보·페이지 본문 | [web.md](references/web.md) |

로그인 벽이 있는 채널(X·인스타·페북·레딧·샤오홍슈 등)은 **사용자 허락 하에 실제 로그인된 크롬
(claude-in-chrome)으로 읽기만** 한다. 공통 접근 정책은 [access-tiers.md](references/access-tiers.md) 참조.

## 어떻게 작동하나 — 사냥개 프로토콜

사냥개가 사냥감을 쫓는 흐름 그대로다.

1. **Scent (냄새 맡기)** — 요청을 핵심 개체와 조건으로 분해하고, 검색어를 한 개가 아니라 여러
   갈래로 만든다. 동의어, 상위어, 한국어와 영어, 표기 변형까지 동시에 잡는다.
2. **Track (추격)** — 채널을 골라 병렬 추적한다. 한 채널이 비면 성격이 다른 채널로 갈아탄다.
3. **Hold the line (놓치지 않기)** — 결과가 없으면 멈추지 않고 사다리를 올라간다. 검색어 교정 →
   질의 재구성 → 언어·채널 전환 → 페이지 직접 진입 → 브라우저 직접 로드. 기본 3~4 라운드.
4. **Retrieve (물어오기)** — 출처와 함께 회수하고, 두 곳 이상에서 교차 검증한 뒤 물어온다.

## 언제 발동하나

"무조건 찾아줘", "끝까지 찾아줘", "샅샅이 찾아줘", "탈탈 털어서 찾아줘", "이거 검색해도 안 나오는데
찾아줘", "유튜브에서 로봇 영상 top 10 찾아줘"(기간·순위 집계), `hound`, `사냥개`, `/hound`.
반대로 한 방에 나오는 단순 사실 확인·계산·번역·요약에는 발동하지 않는다.

## 호환성

Hound는 특정 앱에 묶이지 않은 **이식 가능한 스킬**로 썼다.

- **Claude Code** — 네이티브 스킬로 그대로 작동한다. 네이버 검색 MCP, WebSearch, WebFetch, 브라우저,
  `yt-dlp`를 채널 참조 문서대로 갈아타며 추격한다.
- **ChatGPT** — `SKILL.md`와 채널 참조 문서를 커스텀 GPT의 instructions(또는 시스템 프롬프트)에
  넣으면 ChatGPT의 웹 브라우징 위에서 같은 사냥개 프로토콜로 작동한다. 도구 이름만 그 환경의
  검색·브라우징 도구로 바꿔 읽으면 된다. 추격 방식(분해 → 병렬 → 사다리 → 교차검증)은 그대로다.

## 못 찾으면 어떻게 하나

억지로 지어내지 않는다. 대신 추격 기록을 남긴다. 무엇을 쫓았고, 어떤 검색어를 넣었고, 어느 채널까지
갈아탔고, 어디서 막혔는지를 보고한다. 이 기록 자체가 다음 행동의 단서가 된다. 그게 사냥개의 정직함이다.

## 지키는 선

- 로그인·유료 벽 뒤 콘텐츠는 우회하지 않고 정직하게 보고한다.
- 특정 개인의 사적 정보를 여러 채널에서 짜맞추는 추적은 하지 않는다.
- 출처로 확인 안 된 사실, 없는 URL과 숫자를 만들어 채우지 않는다.
- CAPTCHA와 봇 차단을 우회하지 않는다.

## 계보

Hound는 세 스킬의 핵심을 하나로 합쳤다.

- [insane-search](https://github.com/fivetaku/insane-search) — 막히면 포기하지 않고 단계를 올려
  뚫는 에스컬레이션 사다리. Hound의 "물면 안 놓는" 엔진이다.
- [Agent-Reach](https://github.com/Panniantong/Agent-Reach) — 채널별 참조와 자동 failover.
  한 채널이 죽으면 다음 채널로 갈아타는 라우터 구조다.
- [brave-search-skills](https://github.com/brave/brave-search-skills) — 채널 종류별 모듈 검색을
  출처가 붙은 구조화된 결과로 물어오는 방식이다.

## 파일 구성

```
hound/
├── SKILL.md                 # 스킬 본체 (라우터 + 사냥개 프로토콜)
├── README.md                # 이 문서
├── LICENSE                  # MIT
├── references/              # 채널별 긁는 법 + 공통 정책
│   ├── access-tiers.md      # 접근 등급·도구·가드레일 (공통)
│   ├── naver.md
│   ├── youtube.md · youtube-ranking-notes.md
│   ├── x-twitter.md · threads.md · instagram.md · facebook.md
│   ├── reddit.md · linkedin.md · v2ex.md
│   ├── bilibili.md · xiaoyuzhou.md
│   ├── xiaohongshu.md · xueqiu.md
│   ├── github.md · rss.md
│   └── web.md
├── scripts/
│   ├── yt_collect.py        # 유튜브 기간·순위 집계 엔진
│   └── yt_render.py         # 영상 리포트(MD·HTML) 생성
└── assets/
    ├── topic-packs.json     # 유튜브 집계 주제 팩
    ├── template.html        # 리포트 템플릿
    └── thumbnail.svg        # 스킬 썸네일
```

## 라이선스

[MIT](LICENSE) © 2026 AI ROASTING
