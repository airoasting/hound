#!/usr/bin/env python3
"""
verify_access.py — 채널 참조 문서(references/*.md)의 접근 주장이 아직 유효한지 실측한다.

각 채널 문서는 "이 엔드포인트를 이렇게 열면 이런 결과가 온다"는 검증된 주장 위에 서 있다.
플랫폼의 차단 정책·API 스펙은 수시로 바뀌므로, 이 스크립트로 주기적으로(예: 분기 1회)
현실이 문서와 아직 맞는지 확인한다. 문서와 같은 방식(브라우저 UA curl)으로 때려 본다.

판정:
  PASS  현실이 문서의 주장과 일치한다.
  FAIL  드리프트. 해당 문서를 다시 검증·수정해야 한다(guards에 문서명 표시).
  ERROR 네트워크·도구 오류로 확인 자체가 안 됐다(차단인지 일시 장애인지 사람이 판단).
  SKIP  curl로 재현 불가한 채널(MCP·브라우저 전용).

종료 코드 = FAIL 개수. 0이면 모든 문서가 현실과 일치.

사용:  python3 scripts/verify_access.py
"""

import json
import subprocess
import sys

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
TIMEOUT = 20


def curl(url, headers=None):
    """(status:int, body:str)를 돌려준다. status 0 = 요청 자체 실패."""
    cmd = ["curl", "-s", "-L", "--max-time", str(TIMEOUT),
           "-A", UA, "-w", "\n__HTTP_STATUS__%{http_code}", url]
    for h in (headers or []):
        cmd[1:1] = ["-H", h]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True,
                             errors="replace", timeout=TIMEOUT + 10).stdout
    except subprocess.TimeoutExpired:
        return 0, ""
    marker = "__HTTP_STATUS__"
    if marker in out:
        body, _, status = out.rpartition(marker)
        try:
            return int(status.strip()), body
        except ValueError:
            return 0, body
    return 0, out


# --- 개별 체크. 각 함수는 (ok: bool|None, detail: str)을 돌려준다. None = ERROR ---

def chk_jina():
    st, _ = curl("https://r.jina.ai/https://example.com")
    if st == 0:
        return None, "요청 실패"
    # 문서 주장(2026-11-21): 키 없이도 200. 401로 돌아가면 문서를 다시 '키 필요'로 고친다.
    return st == 200, f"무키 상태 status={st} (기대 200)"


def chk_reddit():
    st, _ = curl("https://www.reddit.com/r/LocalLLaMA/hot.json?limit=2")
    if st == 0:
        return None, "요청 실패"
    # 문서 주장: 비로그인 .json은 막혔다(403/429). 200이면 오히려 문서가 낡은 것.
    return st in (403, 429), f".json status={st} (기대 403/429=차단)"


def chk_v2ex():
    st, body = curl("https://www.v2ex.com/api/topics/hot.json")
    if st == 0:
        return None, "요청 실패"
    return st == 200 and body.lstrip().startswith("["), f"status={st}, JSON={body.lstrip()[:1]!r}"


def chk_github():
    st, body = curl("https://api.github.com/search/repositories?q=claude-code&sort=stars")
    if st == 0:
        return None, "요청 실패"
    has_items = '"items"' in body
    return st == 200 and has_items, f"status={st}, items={'있음' if has_items else '없음'}"


def chk_xiaoyuzhou():
    st, body = curl("https://www.xiaoyuzhoufm.com/episode/684942fcb23ed76e6080316e")
    if st == 0:
        return None, "요청 실패"
    has_audio = "og:audio" in body and "media.xyzcdn.net" in body
    return st == 200 and has_audio, f"status={st}, og:audio+mp3={'노출' if has_audio else '없음'}"


def chk_xueqiu():
    st, body = curl("https://xueqiu.com/S/SH600519")
    if st == 0:
        return None, "요청 실패"
    waf = "_waf" in body or "aliyun_waf" in body
    # 문서 주장: 무쿠키 plain fetch는 WAF 난독화만 반환(내용 없음).
    return st == 200 and waf, f"status={st}, WAF벽={'있음(문서대로)' if waf else '없음(쿠키벽 완화?)'}"


def chk_xiaohongshu():
    # 문서 주장(2026-11-21): xiaohongshu.com/explore는 rednote.com으로 리다이렉트된다.
    # 비브라우저 요청은 rednote.com/login에 도착한다(피드는 인앱 브라우저로 연다).
    cmd = ["curl", "-s", "-L", "-o", "/dev/null", "--max-time", str(TIMEOUT), "-A", UA,
           "-w", "%{http_code} %{url_effective}", "https://www.xiaohongshu.com/explore"]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT + 10).stdout.split()
    except subprocess.TimeoutExpired:
        return None, "요청 실패"
    if len(out) != 2 or out[0] == "000":
        return None, "요청 실패"
    st, final = int(out[0]), out[1]
    moved = "rednote.com" in final
    return st == 200 and moved, f"/explore status={st}, 최종={final} (기대 200 + rednote.com)"


def chk_fxtwitter():
    st, body = curl("https://api.fxtwitter.com/jack/status/20")
    if st == 0:
        return None, "요청 실패"
    try:
        txt = json.loads(body).get("tweet", {}).get("text")
    except Exception:
        txt = None
    return st == 200 and bool(txt), f"status={st}, 본문={'회수됨' if txt else '없음'}"


def chk_bilibili_view():
    # 문서 주장(2026-11-21): view API는 비브라우저 요청에 412를 낸다(보조 경로).
    # code:0으로 열리면 FAIL. 문서에서 view API를 다시 1순위로 올릴지 검토한다.
    st, body = curl("https://api.bilibili.com/x/web-interface/view?aid=2")
    if st == 0:
        return None, "요청 실패"
    try:
        code = json.loads(body).get("code")
    except Exception:
        code = None
    return st == 412, f"status={st}, api code={code} (기대 412)"


def chk_bilibili_ytdlp():
    # 문서 주장(2026-11-21): 빌리빌리 메타·통계는 yt-dlp로 받는다(1순위).
    from shutil import which
    if not which("yt-dlp"):
        return None, "yt-dlp 없음(설치 후 다시 확인)"
    cmd = ["yt-dlp", "--ies", "default,-generic", "-J", "--skip-download", "--no-warnings",
           "https://www.bilibili.com/video/BV1xx411c7mD"]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=90).stdout
        views = json.loads(out).get("view_count")
    except Exception:
        views = None
    return bool(views), f"view_count={views} (기대 숫자)"


def chk_bilibili_danmaku():
    # aid=2(BV1xx411c7mD)의 cid=62131. deflate 압축이라 status/크기만 본다.
    st, body = curl("https://comment.bilibili.com/62131.xml")
    if st == 0:
        return None, "요청 실패"
    return st == 200 and len(body) > 1000, f"status={st}, 크기={len(body)}B"


CHECKS = [
    ("Jina Reader 무키 200",        "access-tiers, linkedin, instagram", chk_jina),
    ("Reddit .json 차단",           "reddit",                            chk_reddit),
    ("V2EX 공개 API",               "v2ex",                              chk_v2ex),
    ("GitHub REST API",             "github",                            chk_github),
    ("샤오위저우 SSR+og:audio",     "xiaoyuzhou",                        chk_xiaoyuzhou),
    ("슈에추 WAF 벽",               "xueqiu",                            chk_xueqiu),
    ("샤오홍슈 → rednote.com",      "xiaohongshu",                       chk_xiaohongshu),
    ("fxtwitter JSON API",          "x-twitter",                         chk_fxtwitter),
    ("빌리빌리 yt-dlp 메타",        "bilibili",                          chk_bilibili_ytdlp),
    ("빌리빌리 view API 412",       "bilibili",                          chk_bilibili_view),
    ("빌리빌리 탄막 XML",           "bilibili",                          chk_bilibili_danmaku),
]

# curl로 재현 불가한 채널(참고용 표시). 브라우저·MCP 경로는 access-tiers.md의 실측 접근표를 손으로 다시 잰다.
SKIPS = [
    ("네이버",     "naver",     "NaverSearch MCP 전용. 브라우저·WebFetch는 도메인 차단(2026-11-21)."),
    ("유튜브",     "youtube",   "yt-dlp 기반. scripts/yt_collect.py로 확인."),
    ("웹 일반",    "web",       "WebSearch/WebFetch 기반. 범용 채널."),
    ("페이스북",   "facebook",  "WebFetch는 빈 셸. 인앱 브라우저로 수동 확인."),
    ("쓰레드",     "threads",   "WebFetch 차단. 인앱 브라우저(threads.com)로 수동 확인."),
    ("링크드인",   "linkedin",  "WebFetch 403. 인앱 브라우저로 수동 확인."),
    ("인스타그램", "instagram", "WebFetch 공개 프로필. 브라우저로 수동 확인."),
    ("RSS",        "rss",       "대상 피드마다 다름. 개별 확인."),
]


def main():
    print("=" * 68)
    print(" Hound 접근 재검증  (references/*.md의 접근 주장이 아직 유효한가)")
    print("=" * 68)

    fails, errors = 0, 0
    for name, guards, fn in CHECKS:
        try:
            ok, detail = fn()
        except Exception as e:  # noqa: BLE001
            ok, detail = None, f"예외: {e}"
        if ok is True:
            tag = "PASS "
        elif ok is False:
            tag = "FAIL "
            fails += 1
        else:
            tag = "ERROR"
            errors += 1
        print(f"[{tag}] {name:<24} | {detail}")
        if ok is False:
            print(f"         └─ 드리프트: references/{guards}.md 재검증 필요")

    print("-" * 68)
    for name, doc, note in SKIPS:
        print(f"[SKIP ] {name:<24} | {note}  (references/{doc}.md)")

    print("=" * 68)
    total = len(CHECKS)
    print(f" 요약: PASS {total - fails - errors} / FAIL {fails} / ERROR {errors}  (검증 {total}건)")
    if fails:
        print(" → FAIL 항목의 문서를 다시 실측하고 고칠 것.")
    elif errors:
        print(" → 네트워크·차단 여부를 사람이 확인할 것(일시 장애일 수 있음).")
    else:
        print(" → 모든 접근 주장이 현실과 일치.")
    print("=" * 68)
    return fails


if __name__ == "__main__":
    sys.exit(main())
