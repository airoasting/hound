# Hound 🐕

![Version](https://img.shields.io/badge/version-1.0.0-2ea44f)
![License](https://img.shields.io/badge/license-MIT-2f81f7)
![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-8A63FF)
![Channels](https://img.shields.io/badge/channels-16-e8873a)
![Zero setup](https://img.shields.io/badge/setup-none-10A37F)

![Hound](assets/thumbnail.png)

> 흔적을 놓치지 않습니다.

Hound는 한 번 검색해서 나오지 않는 정보를 끝까지 추적하는 검색 스킬입니다. 보통의 검색은 결과가
없으면 거기서 멈춥니다. Hound는 질의를 다시 짜고 채널을 바꿔 가며 답이 나올 때까지 추적합니다.
정말로 없을 때만 멈추고, 그때조차 어디까지 찾았는지를 근거와 함께 보고합니다.

## 왜 필요한가

우리가 검색에서 답답함을 느끼는 순간은 대개 한 번에 나오지 않는 정보를 찾을 때입니다. 오래된 자료,
묻힌 사실, 표현이 애매한 키워드, 여러 곳을 겹쳐 봐야 겨우 드러나는 답이 그렇습니다. 기존 도구는
이런 지점에서 결과가 없다고 답하고 손을 뗍니다. Hound는 바로 그 자리를 위해 만들었습니다. 포기하는
검색이 아니라 추적하는 검색입니다.

## 설치가 필요 없습니다

기본 검색은 별도 설치나 API 키가 필요 없습니다. 네이버 검색, 웹 검색, 페이지 열람, 브라우저는 이미
환경에 준비된 도구를 그대로 씁니다. 무설정이라는 점 자체가 Hound의 강점입니다.

선택 설치는 두 가지뿐입니다. 유튜브 자막과 기간별 조회수 순위 집계에는 `yt-dlp`(키 불필요)를 씁니다.
팟캐스트 전사가 필요할 때는 Whisper 계열 도구를 씁니다. 이 두 가지를 쓰지 않는 검색은 아무것도 깔지
않고 바로 동작합니다.

## 무엇을 하나

세 가지 원칙으로 움직입니다.

- **포기하지 않습니다.** 결과 0건은 종료가 아니라 다시 추적하라는 신호입니다. 검색어와 채널을 바꿔
  다시 파고듭니다.
- **한 채널에 머무르지 않습니다.** 한국인이 정보를 쌓아 두는 곳을 빠짐없이 훑습니다.
- **근거와 함께 답합니다.** 찾은 것은 출처와 함께 전하고, 못 찾은 것은 추적 기록과 함께 보고합니다.

## 어디를 찾나 (16개 채널)

Hound는 하나의 거대한 도구가 아니라 추적을 지휘하는 라우터입니다. 무엇을 쫓을지 판단해 알맞은 채널을
붙이고, 각 채널을 다루는 방법은 채널별 참조 문서를 따릅니다. 이 라우터 구조와 채널 구성은
[Agent-Reach](https://github.com/Panniantong/Agent-Reach)의 채널 추상화를 참고했습니다.

| 채널 | 무엇이 있나 | 참조 |
|---|---|---|
| **네이버** | 블로그, 카페, 지식iN, 뉴스, 백과, 지역. 한국어 정보의 본진입니다 | [naver.md](references/naver.md) |
| **유튜브** | 영상 속 정보, 실사용 반응, 기간별 순위 집계 | [youtube.md](references/youtube.md) |
| **X (트위터)** | 실시간 여론, 속보, 당사자 발언 | [x-twitter.md](references/x-twitter.md) |
| **쓰레드** | 일상 후기, 한국 사용자 반응, 밈 | [threads.md](references/threads.md) |
| **인스타그램** | 프로필, 최근 게시물, 해시태그, 비주얼 트렌드 | [instagram.md](references/instagram.md) |
| **페이스북** | 공개 페이지와 그룹의 지역, 커뮤니티 정보 | [facebook.md](references/facebook.md) |
| **레딧** | 해외 실사용 경험, 솔직한 평가, 니치 토론 | [reddit.md](references/reddit.md) |
| **링크드인** | 인물 경력, 회사, 채용, B2B 정보 | [linkedin.md](references/linkedin.md) |
| **GitHub** | 코드, 오픈소스, 이슈, 릴리스 (무설정) | [github.md](references/github.md) |
| **RSS/Atom** | 블로그, 뉴스, 릴리스의 원천 피드 (시간순) | [rss.md](references/rss.md) |
| **빌리빌리** | 중국 기술 리뷰, 튜토리얼, 서브컬처 | [bilibili.md](references/bilibili.md) |
| **샤오홍슈** | 중국 라이프, 소비, 여행 실사용 후기 | [xiaohongshu.md](references/xiaohongshu.md) |
| **슈에추 (雪球)** | 중국 증시, 종목 토론, 투자자 여론 | [xueqiu.md](references/xueqiu.md) |
| **V2EX** | 중화권 개발자와 기술 제품 토론 (공개 API) | [v2ex.md](references/v2ex.md) |
| **샤오위저우** | 팟캐스트와 오디오를 전사해 읽기 | [xiaoyuzhou.md](references/xiaoyuzhou.md) |
| **웹 일반** | 사실, 문서, 해외 정보, 페이지 본문 | [web.md](references/web.md) |

로그인 벽이 있는 채널(X, 인스타그램, 페이스북, 레딧, 샤오홍슈 등)은 사용자 허락 아래 이미 로그인된
크롬(claude-in-chrome)으로 읽기만 합니다. 공통 접근 정책은 [access-tiers.md](references/access-tiers.md)에
정리했습니다.

## 어떻게 작동하나

사냥개가 사냥감을 쫓는 흐름을 그대로 따릅니다.

1. **냄새 맡기 (Scent).** 요청을 핵심 대상과 조건으로 나누고, 검색어를 한 개가 아니라 여러 갈래로
   만듭니다. 동의어, 상위어, 한국어와 영어, 표기 변형을 함께 잡습니다.
2. **추적 (Track).** 성격이 다른 채널을 골라 동시에 추적합니다. 한 채널이 비면 다른 채널로 옮겨 갑니다.
3. **놓치지 않기 (Hold the line).** 결과가 없어도 멈추지 않고 강도를 한 단계씩 올립니다. 검색어 교정,
   질의 재구성, 언어와 채널 전환, 페이지 직접 열람, 브라우저 직접 로드 순으로 올라갑니다. 기본 3~4회를
   돕니다.
4. **회수 (Retrieve).** 찾은 것을 출처와 함께 회수하고, 두 곳 이상에서 교차 검증한 뒤 전달합니다.

## 언제 작동하나

"무조건 찾아줘", "끝까지 찾아줘", "샅샅이 찾아줘", "이거 검색해도 안 나오는데 찾아줘", "유튜브에서 로봇
영상 top 10 찾아줘"처럼 기간이나 순위를 집계해야 하는 요청, 그리고 `hound`, `/hound`라고 부를 때
작동합니다. 반대로 한 번에 나오는 단순 사실 확인, 계산, 번역, 이미 가진 자료의 요약에는 작동하지
않습니다. Hound는 까다로운 추적을 위한 도구입니다.

## 어디서 작동하나

Hound는 특정 앱에 묶이지 않은 이식 가능한 스킬입니다.

- **Claude Code.** 네이티브 스킬로 그대로 작동합니다. 네이버 검색, 웹 검색, 페이지 열람, 브라우저,
  `yt-dlp`를 채널별 참조 문서대로 바꿔 가며 추적합니다.
- **ChatGPT.** SKILL.md와 채널 참조 문서를 커스텀 GPT의 지침에 넣으면, ChatGPT의 웹 브라우징 위에서
  같은 방식으로 작동합니다. 도구 이름만 그 환경의 검색과 브라우징 도구로 바꿔 읽으면 됩니다.

## 찾지 못하면

억지로 지어내지 않습니다. 대신 추적 기록을 남깁니다. 무엇을 쫓았고, 어떤 검색어를 넣었고, 어느
채널까지 옮겨 갔고, 어디서 막혔는지를 보고합니다. 이 기록이 다음 행동의 단서가 됩니다.

## 지키는 원칙

- 로그인이나 결제가 필요한 콘텐츠는 우회하지 않고 정직하게 보고합니다.
- 특정 개인의 사적 정보를 여러 채널에서 짜맞추는 추적은 하지 않습니다.
- 출처로 확인되지 않은 사실이나 없는 URL, 없는 숫자를 지어내지 않습니다.
- CAPTCHA와 봇 차단을 우회하지 않습니다.

## 참고한 프로젝트

Hound는 세 프로젝트의 핵심을 하나로 모았습니다.

- [insane-search](https://github.com/fivetaku/insane-search). 막히면 포기하지 않고 단계를 올려
  뚫는 방식입니다. Hound가 끝까지 추적하는 힘의 바탕입니다.
- [Agent-Reach](https://github.com/Panniantong/Agent-Reach). 채널별 참조와 자동 전환입니다. 한
  채널이 막히면 다음 채널로 옮겨 가는 라우터 구조입니다.
- [brave-search-skills](https://github.com/brave/brave-search-skills). 채널 종류별 검색을
  출처가 붙은 구조화된 결과로 회수하는 방식입니다.

## 파일 구성

```
.                              # 레포 루트
├── SKILL.md                   # 스킬 본체 (라우터와 추적 프로토콜)
├── README.md                  # 이 문서
├── LICENSE                    # MIT
├── references/                # 채널별 방법과 공통 정책
│   ├── access-tiers.md
│   ├── naver.md
│   ├── youtube.md
│   ├── youtube-ranking-notes.md
│   ├── x-twitter.md
│   ├── threads.md
│   ├── instagram.md
│   ├── facebook.md
│   ├── reddit.md
│   ├── linkedin.md
│   ├── v2ex.md
│   ├── bilibili.md
│   ├── xiaoyuzhou.md
│   ├── xiaohongshu.md
│   ├── xueqiu.md
│   ├── github.md
│   ├── rss.md
│   └── web.md
├── scripts/                   # 유튜브 집계 전용 (그 외 채널은 스크립트 불필요)
│   ├── yt_collect.py
│   └── yt_render.py
└── assets/
    ├── topic-packs.json
    ├── template.html
    ├── hound-black.png
    ├── hound_white.png
    ├── thumbnail.svg
    └── thumbnail.png
```

## 라이선스

[MIT](LICENSE) © 2026 AI ROASTING
