#!/usr/bin/env python3
"""
Hound 검색 결과 저장기.

찾은 결과(또는 못 찾은 증거 보고)를 JSON으로 받아 output/{오늘날짜}_{순번}/ 폴더에
result.md 와 result.html 두 파일로 저장한다. HTML은 assets/result-template.html 을 채운다.
매번 손으로 마크다운·HTML을 조립하지 않게 하려고 이 작업만 코드로 고정했다.

입력 JSON 스키마 (stdin 또는 --in 파일):
{
  "title":   "결과 제목(한 줄)",
  "request": "사용자 요청 원문",
  "channels":["네이버","유튜브"],           # 훑은 채널
  "found":   true,                          # 찾았으면 true, 아니면 false
  "answer":  "핵심 답 한두 문장",            # found=true
  "items": [                                # found=true, 근거 목록
    {"name":"자료 제목", "url":"https://...",
     "metric":"팔로워 5,465명 · 직원 110명", "summary":"2~3문장 요약(입니다체)"}
  ],
  "crosscheck": "교차 검증 한 줄",           # 선택
  "trace":      "추적 메모 한 줄",           # 선택
  "blocked":    "막힌 지점(로그인 벽 등)",   # 선택
  "notfound": {                             # found=false 일 때
     "target":"쫓은 대상", "queries":["검색어"], "channels":["갈아탄 채널"],
     "blocked":"막힌 지점", "next":"다음 수"
  }
}

사용:
  python3 scripts/save_result.py --in data.json
  echo '{...}' | python3 scripts/save_result.py
  # 순번을 직접 지정하려면 --seq 02, 뿌리 폴더를 바꾸려면 --out-root output
결과: 저장한 폴더 경로를 마지막 줄에 출력한다.
"""
import argparse, html, json, os, sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TEMPLATE = os.path.join(ROOT, "assets", "result-template.html")


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


def build_md(d, meta):
    L = [f"# {d['title']}", "", f"- {meta}", ""]
    if d.get("found", True):
        L += ["## 핵심 답", "", d.get("answer", ""), "", "## 근거", ""]
        for it in d.get("items", []):
            L.append(f"### [{it['name']}]({it.get('url','')})")
            if it.get("metric"):
                L.append(f"- 지표: {it['metric']}")
            if it.get("summary"):
                L.append(f"- 요약: {it['summary']}")
            L.append("")
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
    return "\n".join(L)


def build_html(d, meta):
    tpl = open(TEMPLATE, encoding="utf-8").read()
    C = []
    if d.get("found", True):
        C.append(f'<div class="answer">{html.escape(d.get("answer",""))}</div>')
        C.append("<h2>근거</h2><ul>")
        for it in d.get("items", []):
            metric = (f'<div style="margin-top:6px"><b style="color:var(--gold)">지표.</b> '
                      f'{html.escape(it["metric"])}</div>') if it.get("metric") else ""
            summ = (f'<div style="margin-top:4px">{html.escape(it["summary"])}</div>'
                    ) if it.get("summary") else ""
            C.append(f'<li><a href="{html.escape(it.get("url",""))}"><b>{html.escape(it["name"])}</b></a>'
                     f'<span class="src">{html.escape(it.get("url",""))}</span>{metric}{summ}</li>')
        C.append("</ul>")
        if d.get("crosscheck"):
            C.append(f'<h2>교차 검증</h2><p class="note">{html.escape(d["crosscheck"])}</p>')
        if d.get("blocked"):
            C.append(f'<h2>막힌 지점</h2><p class="note">{html.escape(d["blocked"])}</p>')
    else:
        nf = d.get("notfound", {})
        C.append('<div class="answer">요청한 정보를 찾지 못했습니다. 아래는 추적 기록입니다.</div>')
        C.append("<h2>추적 기록</h2><ul>")
        C.append(f'<li><b>쫓은 대상</b><div>{html.escape(nf.get("target",""))}</div></li>')
        C.append(f'<li><b>시도한 검색어</b><div>{html.escape(", ".join(nf.get("queries",[])))}</div></li>')
        C.append(f'<li><b>갈아탄 채널</b><div>{html.escape(", ".join(nf.get("channels",[])))}</div></li>')
        C.append(f'<li><b>막힌 지점</b><div>{html.escape(nf.get("blocked",""))}</div></li>')
        C.append(f'<li><b>다음 수</b><div>{html.escape(nf.get("next",""))}</div></li>')
        C.append("</ul>")
    date = d.get("date") or datetime.now().strftime("%Y-%m-%d")
    return (tpl.replace("{{TITLE}}", html.escape(d["title"]))
               .replace("{{META}}", html.escape(meta))
               .replace("{{CONTENT}}", "\n".join(C))
               .replace("{{DATE}}", date))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="infile", help="입력 JSON 파일(없으면 stdin)")
    ap.add_argument("--out-root", default=os.path.join(ROOT, "output"))
    ap.add_argument("--seq", default=None, help="순번 강제 지정(예: 02)")
    args = ap.parse_args()

    raw = open(args.infile, encoding="utf-8").read() if args.infile else sys.stdin.read()
    d = json.loads(raw)

    ymd = (d.get("date") or datetime.now().strftime("%Y-%m-%d")).replace("-", "")
    meta = d.get("meta") or (
        f"검색일 {d.get('date') or datetime.now().strftime('%Y-%m-%d')} · "
        f"채널: {', '.join(d.get('channels', [])) or '-'} · 요청: {d.get('request','')}")

    outdir = next_dir(args.out_root, ymd, args.seq)
    open(os.path.join(outdir, "result.md"), "w", encoding="utf-8").write(build_md(d, meta))
    open(os.path.join(outdir, "result.html"), "w", encoding="utf-8").write(build_html(d, meta))
    print(outdir)


if __name__ == "__main__":
    main()
