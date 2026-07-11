#!/usr/bin/env python3
"""
robot-radar 렌더러.

collect.py 가 만든 top.json 을 읽어 사람이 읽는 리포트(MD + HTML)로 만든다.
각 top 항목에 "note"(한국어 한 줄, 왜 볼 만한가)가 있으면 반영한다.
note 는 SKILL.md 절차대로 모델이 큐레이션해 채운다. 없으면 빈 칸으로 둔다.

사용:
  python3 render.py --top /path/top.json --out /path/outdir
결과: outdir/robot-top10-<start>_to_<end>.md, .html
"""
import argparse, html, json, os
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "..", "assets", "template.html")


def fmt_views(n):
    return f"{n:,}"


def fmt_dur(sec):
    if not sec:
        return "-"
    m, s = divmod(int(sec), 60)
    h, m = divmod(m, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def fmt_date(ts):
    if not ts:
        return "게시일 미상"
    return datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%d")


def kfmt(n):
    if n is None:
        return "-"
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.0f}K"
    return str(int(n))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    data = json.load(open(args.top, encoding="utf-8"))
    meta, top = data["meta"], data["top"]
    os.makedirs(args.out, exist_ok=True)
    stem = f"{meta['topic']}-top{meta['returned']}-{meta['window_start']}_to_{meta['window_end']}"

    title = f"{meta['label']} 유튜브 TOP {meta['returned']} · {meta['window_start']} ~ {meta['window_end']}"
    rank_word = "총 조회수" if meta["rank_by"] == "views" else "조회 속도(하루당)"
    method_line = (f"수집 엔진 {meta['engine']} · 지역 {meta['region']} · 언어 {meta['lang']} · "
                   f"최근 {meta['window_days']}일 · 후보 {meta['candidates_total']}건에서 "
                   f"{rank_word} 기준 정렬, 채널 중복 제거 후 상위 {meta['returned']}건. "
                   f"생성 {meta['generated_at']}.")

    # ---------- MD ----------
    md = [f"# {title}", "", method_line, "",
          "| # | 영상 | 채널 | 조회수 | 게시일 | 길이 | 좋아요 | 왜 볼만한가 |",
          "|---|------|------|-------:|--------|------|-------:|-------------|"]
    for r in top:
        note = (r.get("note") or "").replace("|", "／")
        md.append(f"| {r['rank']} | [{r['title'].replace('|','／')}]({r['url']}) | "
                  f"{r['channel'].replace('|','／')} | {fmt_views(r['views'])} | {fmt_date(r.get('timestamp'))} | "
                  f"{fmt_dur(r['duration'])} | {kfmt(r.get('likes'))} | {note} |")
    md += ["", "## 상세", ""]
    for r in top:
        md.append(f"### {r['rank']}. {r['title']}")
        md.append(f"- 채널: {r['channel']}  ·  조회수 {fmt_views(r['views'])}  ·  "
                  f"게시 {fmt_date(r.get('timestamp'))}  ·  길이 {fmt_dur(r['duration'])}")
        eng = f"{r.get('engagement_rate',0)*100:.2f}%"
        vel = f"{int(r['velocity']):,}/일" if r.get("velocity") else "-"
        md.append(f"- 좋아요 {kfmt(r.get('likes'))}  ·  댓글 {kfmt(r.get('comments'))}  ·  "
                  f"참여율 {eng}  ·  조회 속도 {vel}")
        md.append(f"- 링크: {r['url']}")
        if r.get("note"):
            md.append(f"- 메모: {r['note']}")
        md.append("")
    md_path = os.path.join(args.out, stem + ".md")
    open(md_path, "w", encoding="utf-8").write("\n".join(md))

    # ---------- HTML ----------
    tpl = open(TEMPLATE, encoding="utf-8").read()
    cards = []
    for r in top:
        pills = [f'<span class="pill v">▶ {fmt_views(r["views"])}회</span>',
                 f'<span class="pill">{fmt_date(r.get("timestamp"))}</span>',
                 f'<span class="pill">{fmt_dur(r["duration"])}</span>']
        if r.get("likes") is not None:
            pills.append(f'<span class="pill">♥ {kfmt(r["likes"])}</span>')
        if r.get("velocity"):
            pills.append(f'<span class="pill">{int(r["velocity"]):,}/일</span>')
        note = html.escape(r.get("note") or "")
        cards.append(f"""<div class="card">
  <div class="rank">{r['rank']}</div>
  <a class="thumb" href="{r['url']}"><img src="{r['thumbnail']}" alt="" loading="lazy"></a>
  <div class="body">
    <h3><a href="{r['url']}">{html.escape(r['title'])}</a></h3>
    <div class="chan">{html.escape(r['channel'])}</div>
    <div class="stats">{''.join(pills)}</div>
    <div class="note">{note}</div>
  </div>
</div>""")
    footer = "robot-radar · 데이터 출처 YouTube · 조회수·게시일은 생성 시점 기준"
    out_html = (tpl.replace("{{TITLE}}", html.escape(title))
                   .replace("{{META}}", html.escape(method_line))
                   .replace("{{METHOD}}", "랭킹 기준: " + rank_word +
                            ". 채널당 최대 게재 수를 제한해 한 채널 독점을 막았고, "
                            "주제 관련성·기간·(옵션)쇼츠 필터를 통과한 영상만 실었다.")
                   .replace("{{ITEMS}}", "\n".join(cards))
                   .replace("{{FOOTER}}", footer))
    html_path = os.path.join(args.out, stem + ".html")
    open(html_path, "w", encoding="utf-8").write(out_html)

    print(md_path)
    print(html_path)


if __name__ == "__main__":
    main()
