#!/usr/bin/env python3
"""
Hound 검색 결과 저장기.

찾은 결과(또는 못 찾은 증거 보고)를 JSON으로 받아 output/{오늘날짜}_{순번}/ 폴더에
result.md 와 result.html 두 파일로 저장한다. HTML은 assets/result-template.html 을 채운다.
매번 손으로 마크다운·HTML을 조립하지 않게 하려고 이 작업만 코드로 고정했다.

1.3.0부터 결과의 품질 관리를 함께 한다.
  - 경로 표시: 항목마다 어느 채널·경로(MCP, API, 브라우저, 간접, 대체 등)로 얻었는지, 언제 확인했는지 적는다.
    대체·간접 경로가 섞이면 결과 머리에 "네이버 원본 아님" 같은 배지를 단다.
  - 근거 최저선: status가 found인데 서로 다른 채널이 2곳 미만이면 partial로 낮춘다
    (single_source_ok: true면 유지).
  - 중복 제거: 추적 파라미터·www·m·끝 슬래시·#조각을 지운 URL이 같으면 한 항목으로 합친다.
  - 링크 안전: http(s) 주소만 링크로 만든다.

입력 JSON 스키마 (stdin 또는 --in 파일):
{
  "title":   "결과 제목(한 줄)",
  "request": "사용자 요청 원문",
  "channels":["네이버","유튜브"],           # 훑은 채널
  "status":  "found",                       # found | partial | notfound (없으면 found 값으로 정함)
  "found":   true,                          # 1.2.0까지의 형식. status가 없을 때만 쓴다
  "single_source_ok": false,                # 지표가 강한 1차 출처 하나로 충분할 때만 true
  "answer":  "핵심 답 한두 문장",
  "items": [
    {"name":"자료 제목", "url":"https://...",
     "channel":"유튜브",                     # 이 자료를 얻은 채널
     "route":"yt-dlp",                       # MCP / API / WebFetch / 브라우저 / 로그인 세션 / 간접 / 대체(구글 뉴스) 등
     "as_of":"2026-11-22",                   # 지표를 확인한 날짜(시각)
     "metric":"조회수 1,145,653", "summary":"2~3문장 요약(입니다체)"}
  ],
  "channel_status": [                       # 채널마다 어떻게 됐는지 (선택)
    {"channel":"네이버", "status":"blocked", "route":"MCP 없음", "note":"구글 뉴스로 대체"}
  ],                                         # status: hit | empty | blocked | skipped
  "notice":    "결과 머리에 따로 적을 말(선택)",
  "crosscheck": "교차 검증 한 줄",
  "trace":      "추적 메모 한 줄",
  "blocked":    "막힌 지점(로그인 벽 등)",
  "notfound": {                             # status가 notfound일 때
     "target":"쫓은 대상", "queries":["검색어"], "channels":["갈아탄 채널"],
     "blocked":"막힌 지점", "next":"다음 수"
  }
}

사용:
  python3 scripts/save_result.py --in data.json
  echo '{...}' | python3 scripts/save_result.py
  # 순번을 직접 지정하려면 --seq 02, 뿌리 폴더를 바꾸려면 --out-root output
결과: 저장한 폴더 경로를 마지막 줄에 출력한다. 최저선·중복 처리 내용은 stderr로 알린다.
"""
import argparse, html, json, os, re, sys
from datetime import datetime
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TEMPLATE = os.path.join(ROOT, "assets", "result-template.html")

STATUS_LABEL = {"found": "찾음", "partial": "부분 발견", "notfound": "못 찾음"}
CH_STATUS_LABEL = {"hit": "결과 있음", "empty": "0건", "blocked": "막힘", "skipped": "건너뜀"}
SUBSTITUTE_PREFIXES = ("대체", "간접")
TRACKING_KEYS = {"fbclid", "gclid", "igshid", "igsh", "mc_cid", "mc_eid", "ref", "ref_src",
                 "spm", "si", "feature", "share_source", "from_spmid", "vd_source"}


def log(msg):
    print(msg, file=sys.stderr)


# ----------------------------- URL 정리 -----------------------------

def is_web_url(u):
    return isinstance(u, str) and u.lower().startswith(("http://", "https://"))


def url_key(u):
    """중복 판정용 키. 표시용 URL은 바꾸지 않는다."""
    if not is_web_url(u):
        return (u or "").strip()
    p = urlsplit(u.strip())
    host = p.netloc.lower()
    for pre in ("www.", "m."):
        if host.startswith(pre):
            host = host[len(pre):]
    q = [(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True)
         if not k.lower().startswith("utm_") and k.lower() not in TRACKING_KEYS]
    path = p.path.rstrip("/") or "/"
    return urlunsplit(("", host, path, urlencode(sorted(q)), ""))


def dedupe(items):
    seen, out, merged = {}, [], 0
    for it in items:
        key = url_key(it.get("url", "")) or f"__noid_{len(out)}"
        if key in seen:
            base = seen[key]
            ch = it.get("channel")
            if ch and ch not in base["_channels"]:
                base["_channels"].append(ch)
            base["_dup"] = base.get("_dup", 0) + 1
            merged += 1
            continue
        it = dict(it)
        it["_channels"] = [it["channel"]] if it.get("channel") else []
        seen[key] = it
        out.append(it)
    for it in out:
        if it["_channels"]:
            it["channel"] = ", ".join(it["_channels"])
    return out, merged


def is_substitute(it):
    if "substitute" in it:
        return bool(it["substitute"])
    return str(it.get("route", "")).startswith(SUBSTITUTE_PREFIXES)


# ----------------------------- 상태·최저선 -----------------------------

def resolve_status(d, items):
    status = d.get("status")
    if status not in STATUS_LABEL:
        status = "found" if d.get("found", True) else "notfound"
    note = None
    if status == "found" and not d.get("single_source_ok"):
        tagged = [it for it in items if it.get("_channels")]
        if tagged:
            distinct = {c for it in tagged for c in it["_channels"]}
            if len(distinct) < 2:
                status = "partial"
                note = (f"근거 최저선 미달: 서로 다른 채널 {len(distinct)}곳에서만 확인돼 '부분 발견'으로 "
                        "낮췄습니다. 1차 출처 하나로 충분하면 single_source_ok: true를 넘깁니다.")
    return status, note


def badges(d, items, status):
    out = []
    if status == "partial":
        out.append(("warn", "부분 발견"))
    routes = []
    for it in items:
        if is_substitute(it):
            r = str(it.get("route") or "대체 경로")
            if r not in routes:
                routes.append(r)
    for r in routes:
        out.append(("warn", f"원본 아님 · {r}"))
    for cs in d.get("channel_status", []) or []:
        if cs.get("status") == "blocked":
            out.append(("", f"{cs.get('channel', '')} 막힘"))
    if d.get("notice"):
        out.append(("warn", d["notice"]))
    return out


# ----------------------------- 마크다운 -----------------------------

def md_link(name, url):
    return f"[{name}]({url})" if is_web_url(url) else f"{name} ({url})" if url else name


def item_route_line(it):
    parts = []
    if it.get("channel"):
        parts.append(f"채널: {it['channel']}")
    if it.get("route"):
        parts.append(f"경로: {it['route']}")
    if it.get("as_of"):
        parts.append(f"확인: {it['as_of']}")
    if it.get("_dup"):
        parts.append(f"중복 {it['_dup']}건 합침")
    return " · ".join(parts)


def channel_status_md(d):
    rows = d.get("channel_status") or []
    if not rows:
        return []
    L = ["## 채널별 상태", "", "| 채널 | 상태 | 경로 | 메모 |", "|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r.get('channel','')} | {CH_STATUS_LABEL.get(r.get('status'), r.get('status',''))} | "
                 f"{r.get('route','')} | {r.get('note','')} |")
    return L + [""]


def build_md(d, meta, items, status, floor_note):
    L = [f"# {d['title']}", "", f"- {meta}", f"- 상태: {STATUS_LABEL[status]}", ""]
    bs = badges(d, items, status)
    if bs:
        L += ["> " + " · ".join(b for _, b in bs), ""]
    if floor_note:
        L += [f"> {floor_note}", ""]
    if status in ("found", "partial"):
        L += ["## 핵심 답", "", d.get("answer", ""), "", "## 근거", ""]
        for it in items:
            L.append(f"### {md_link(it['name'], it.get('url', ''))}")
            rl = item_route_line(it)
            if rl:
                L.append(f"- {rl}")
            if it.get("metric"):
                L.append(f"- 지표: {it['metric']}")
            if it.get("summary"):
                L.append(f"- 요약: {it['summary']}")
            L.append("")
        L += channel_status_md(d)
        if d.get("crosscheck"):
            L += ["## 교차 검증", "", d["crosscheck"], ""]
        if d.get("blocked"):
            L += ["## 막힌 지점", "", d["blocked"], ""]
        if d.get("trace"):
            L += ["## 추적 메모", "", d["trace"], ""]
    else:
        nf = d.get("notfound", {})
        L += ["## 못 찾음. 추적 기록", "",
              f"- 쫓은 대상: {nf.get('target','')}",
              f"- 시도한 검색어: {', '.join(nf.get('queries',[]))}",
              f"- 갈아탄 채널: {', '.join(nf.get('channels',[]))}",
              f"- 막힌 지점: {nf.get('blocked','')}",
              f"- 다음 수: {nf.get('next','')}", ""]
        L += channel_status_md(d)
    return "\n".join(L)


# ----------------------------- HTML -----------------------------

def h(s):
    return html.escape(str(s))


def html_link(name, url):
    if is_web_url(url):
        return f'<a href="{h(url)}"><b>{h(name)}</b></a><span class="src">{h(url)}</span>'
    tail = f'<span class="src">{h(url)}</span>' if url else ""
    return f"<b>{h(name)}</b>{tail}"


def channel_status_html(d):
    rows = d.get("channel_status") or []
    if not rows:
        return []
    C = ["<h2>채널별 상태</h2><table><tr><th>채널</th><th>상태</th><th>경로</th><th>메모</th></tr>"]
    for r in rows:
        C.append(f"<tr><td>{h(r.get('channel',''))}</td>"
                 f"<td>{h(CH_STATUS_LABEL.get(r.get('status'), r.get('status','')))}</td>"
                 f"<td>{h(r.get('route',''))}</td><td>{h(r.get('note',''))}</td></tr>")
    C.append("</table>")
    return C


def build_html(d, meta, items, status, floor_note):
    tpl = open(TEMPLATE, encoding="utf-8").read()
    C = []
    bs = badges(d, items, status)
    if bs:
        C.append('<div class="badges">' + "".join(
            f'<span class="badge{(" " + k) if k else ""}">{h(t)}</span>' for k, t in bs) + "</div>")
    if floor_note:
        C.append(f'<p class="note">{h(floor_note)}</p>')
    if status in ("found", "partial"):
        C.append(f'<div class="answer">{h(d.get("answer",""))}</div>')
        C.append("<h2>근거</h2><ul>")
        for it in items:
            route = (f'<span class="route">{h(item_route_line(it))}</span>') if item_route_line(it) else ""
            metric = (f'<div style="margin-top:6px"><b style="color:var(--gold)">지표.</b> '
                      f'{h(it["metric"])}</div>') if it.get("metric") else ""
            summ = (f'<div style="margin-top:4px">{h(it["summary"])}</div>') if it.get("summary") else ""
            C.append(f'<li>{html_link(it["name"], it.get("url",""))}{route}{metric}{summ}</li>')
        C.append("</ul>")
        C += channel_status_html(d)
        if d.get("crosscheck"):
            C.append(f'<h2>교차 검증</h2><p class="note">{h(d["crosscheck"])}</p>')
        if d.get("blocked"):
            C.append(f'<h2>막힌 지점</h2><p class="note">{h(d["blocked"])}</p>')
        if d.get("trace"):
            C.append(f'<h2>추적 메모</h2><p class="note">{h(d["trace"])}</p>')
    else:
        nf = d.get("notfound", {})
        C.append('<div class="answer">요청한 정보를 찾지 못했습니다. 아래는 추적 기록입니다.</div>')
        C.append("<h2>추적 기록</h2><ul>")
        C.append(f'<li><b>쫓은 대상</b><div>{h(nf.get("target",""))}</div></li>')
        C.append(f'<li><b>시도한 검색어</b><div>{h(", ".join(nf.get("queries",[])))}</div></li>')
        C.append(f'<li><b>갈아탄 채널</b><div>{h(", ".join(nf.get("channels",[])))}</div></li>')
        C.append(f'<li><b>막힌 지점</b><div>{h(nf.get("blocked",""))}</div></li>')
        C.append(f'<li><b>다음 수</b><div>{h(nf.get("next",""))}</div></li>')
        C.append("</ul>")
        C += channel_status_html(d)
    date = d.get("date") or datetime.now().strftime("%Y-%m-%d")
    vals = {"TITLE": h(d["title"]), "META": h(f"{meta} · 상태: {STATUS_LABEL[status]}"),
            "CONTENT": "\n".join(C), "DATE": h(date)}
    # 한 번에 치환한다. 넣은 값이 {{CONTENT}} 같은 자리표시자를 품고 있어도 다시 치환되지 않는다.
    return re.sub(r"\{\{(TITLE|META|CONTENT|DATE)\}\}", lambda m: vals[m.group(1)], tpl)


# ----------------------------- 저장 -----------------------------

def next_dir(out_root, date, seq=None):
    os.makedirs(out_root, exist_ok=True)
    if seq:
        name = f"{date}_{seq}"
    else:
        n = 1
        while os.path.isdir(os.path.join(out_root, f"{date}_{n:02d}")):
            n += 1
        name = f"{date}_{n:02d}"
    path = os.path.join(out_root, name)
    os.makedirs(path, exist_ok=True)
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="infile", help="입력 JSON 파일(없으면 stdin)")
    ap.add_argument("--out-root", default=os.path.join(ROOT, "output"))
    ap.add_argument("--seq", default=None, help="순번 강제 지정(예: 02)")
    args = ap.parse_args()

    raw = open(args.infile, encoding="utf-8").read() if args.infile else sys.stdin.read()
    d = json.loads(raw)

    items, merged = dedupe(d.get("items", []))
    if merged:
        log(f"[dedupe] 같은 URL {merged}건을 합쳤습니다.")
    status, floor_note = resolve_status(d, items)
    if floor_note:
        log(f"[floor] {floor_note}")

    ymd = (d.get("date") or datetime.now().strftime("%Y-%m-%d")).replace("-", "")
    meta = d.get("meta") or (
        f"검색일 {d.get('date') or datetime.now().strftime('%Y-%m-%d')} · "
        f"채널: {', '.join(d.get('channels', [])) or '-'} · 요청: {d.get('request','')}")

    outdir = next_dir(args.out_root, ymd, args.seq)
    open(os.path.join(outdir, "result.md"), "w", encoding="utf-8").write(
        build_md(d, meta, items, status, floor_note))
    open(os.path.join(outdir, "result.html"), "w", encoding="utf-8").write(
        build_html(d, meta, items, status, floor_note))
    print(outdir)


if __name__ == "__main__":
    main()
