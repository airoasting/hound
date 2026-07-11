#!/usr/bin/env python3
"""
robot-radar 수집 엔진.

한 주제(기본: robot)에 대해 최근 N일(기본 7일) 유튜브 영상을 모아
조회수 기준 top K(기본 10)를 뽑는다. 결과를 candidates.json / top.json 으로 저장.

두 엔진:
  1) YouTube Data API v3  — 환경변수 YOUTUBE_API_KEY 가 있으면 자동 사용 (정밀·빠름)
  2) yt-dlp               — 키가 없으면 사용 (설정 불필요, 항상 동작)

핵심 원칙: 어떤 엔진이든 '정확한 게시 시각(timestamp)'으로 N일 창을 재확인해
          기간을 벗어난 영상은 버린다. 검색 필터의 느슨함을 코드가 보정한다.

사용 예:
  python3 collect.py --pack robot --days 7 --top 10 --out ./run
  python3 collect.py --pack robot --days 7 --top 10 --region KR --lang ko --out ./run
  python3 collect.py --pack robot --rank velocity --no-shorts --out ./run
"""
import argparse, json, os, re, sys, subprocess, time, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_PACKS = os.path.join(HERE, "..", "assets", "topic-packs.json")

# 업로드 기간 sp 필터 (coarse). 정확한 컷은 timestamp 로 다시 한다.
SP_TODAY      = "EgIIAg%3D%3D"   # 24시간
SP_THIS_WEEK  = "EgIIAw%3D%3D"   # 이번 주
SP_THIS_MONTH = "EgIIBA%3D%3D"   # 이번 달
SP_THIS_YEAR  = "EgIIBQ%3D%3D"   # 올해


def log(*a):
    print(*a, file=sys.stderr, flush=True)


def sp_for_days(days):
    if days <= 1:
        return SP_TODAY
    if days <= 7:
        return SP_THIS_WEEK
    if days <= 31:
        return SP_THIS_MONTH
    return SP_THIS_YEAR


def ytdlp_cmd():
    """yt-dlp 실행 경로 결정. 바이너리 우선, 없으면 python 모듈."""
    from shutil import which
    if which("yt-dlp"):
        return ["yt-dlp"]
    return [sys.executable, "-m", "yt_dlp"]


# ----------------------------- yt-dlp 엔진 -----------------------------

def yt_flat_search(query, days, per_query, ytcmd):
    """검색 결과를 flat 으로 받아 후보(view_count 포함)를 리턴."""
    q = urllib.parse.quote_plus(query)
    url = f"https://www.youtube.com/results?search_query={q}&sp={sp_for_days(days)}"
    cmd = ytcmd + ["--flat-playlist", "--dump-json", "--no-warnings",
                   "--playlist-end", str(per_query), url]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=90).stdout
    except subprocess.TimeoutExpired:
        log(f"  [flat timeout] {query}")
        return []
    rows = []
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        vid = d.get("id")
        if not vid:
            continue
        rows.append({
            "id": vid,
            "title": d.get("title") or "",
            "channel": d.get("channel") or d.get("uploader") or "",
            "flat_views": d.get("view_count") or 0,
            "duration": d.get("duration") or 0,
            "query": query,
        })
    return rows


def yt_full_meta(vid, ytcmd):
    """단일 영상 full 메타데이터. android 클라이언트가 쓰로틀링에 강함."""
    url = f"https://www.youtube.com/watch?v={vid}"
    for client in ("android", "web_safari", "tv"):
        cmd = ytcmd + ["--dump-json", "--no-warnings",
                       "--extractor-args", f"youtube:player_client={client}", url]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
        except subprocess.TimeoutExpired:
            continue
        out = r.stdout.strip()
        if not out:
            continue
        try:
            d = json.loads(out)
        except json.JSONDecodeError:
            continue
        return normalize(d, vid)
    return None


def normalize(d, vid):
    """엔진별 메타를 공통 레코드로."""
    ts = d.get("timestamp")
    upload = d.get("upload_date")  # YYYYMMDD
    if ts is None and upload:
        try:
            ts = int(datetime.strptime(upload, "%Y%m%d").replace(tzinfo=timezone.utc).timestamp())
        except ValueError:
            ts = None
    return {
        "id": vid,
        "title": d.get("title") or "",
        "channel": d.get("channel") or d.get("uploader") or "",
        "channel_id": d.get("channel_id") or d.get("uploader_id") or "",
        "views": int(d.get("view_count") or 0),
        "likes": int(d.get("like_count") or 0) if d.get("like_count") is not None else None,
        "comments": int(d.get("comment_count") or 0) if d.get("comment_count") is not None else None,
        "duration": int(d.get("duration") or 0),
        "timestamp": ts,
        "description": (d.get("description") or "")[:500],
        "url": f"https://www.youtube.com/watch?v={vid}",
        "thumbnail": f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg",
    }


def engine_ytdlp(pack, days, per_query, max_candidates):
    ytcmd = ytdlp_cmd()
    log(f"[engine] yt-dlp ({' '.join(ytcmd)})")
    pool = {}
    for query in pack["queries"]:
        rows = yt_flat_search(query, days, per_query, ytcmd)
        log(f"  flat '{query}': {len(rows)}건")
        for r in rows:
            ex = pool.get(r["id"])
            if ex is None or r["flat_views"] > ex["flat_views"]:
                pool[r["id"]] = r
    ranked_flat = sorted(pool.values(), key=lambda r: r["flat_views"], reverse=True)
    pick = ranked_flat[:max_candidates]
    log(f"[pool] 고유 {len(pool)}건 → full 메타 취득 상위 {len(pick)}건")

    records = []
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(yt_full_meta, r["id"], ytcmd): r for r in pick}
        for fut in as_completed(futs):
            base = futs[fut]
            m = fut.result()
            if m is None:
                log(f"  [meta fail] {base['id']}")
                continue
            m["query"] = base["query"]
            records.append(m)
    log(f"[meta] {len(records)}건 취득 완료")
    return records


# ----------------------------- API 엔진 -----------------------------

def api_get(path, params):
    params = dict(params)
    params["key"] = os.environ["YOUTUBE_API_KEY"]
    url = "https://www.googleapis.com/youtube/v3/" + path + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=30) as resp:
        return json.loads(resp.read().decode())


def iso8601_dur_to_sec(s):
    if not s:
        return 0
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", s)
    if not m:
        return 0
    h, mi, se = (int(x) if x else 0 for x in m.groups())
    return h * 3600 + mi * 60 + se


def engine_api(pack, days, per_query, max_candidates, region, lang):
    log("[engine] YouTube Data API v3")
    published_after = datetime.now(timezone.utc).timestamp() - days * 86400
    published_after_iso = datetime.fromtimestamp(published_after, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    ids = {}
    for query in pack["queries"]:
        params = {"part": "snippet", "type": "video", "order": "viewCount",
                  "publishedAfter": published_after_iso, "q": query,
                  "maxResults": min(per_query, 50)}
        if region:
            params["regionCode"] = region
        if lang:
            params["relevanceLanguage"] = lang
        try:
            res = api_get("search", params)
        except Exception as e:
            log(f"  [api search fail] {query}: {e}")
            continue
        for it in res.get("items", []):
            vid = it["id"].get("videoId")
            if vid:
                ids[vid] = query
        log(f"  search '{query}': 누적 {len(ids)}건")
    id_list = list(ids.keys())[:max_candidates * 2]
    records = []
    for i in range(0, len(id_list), 50):
        chunk = id_list[i:i + 50]
        try:
            res = api_get("videos", {"part": "snippet,statistics,contentDetails",
                                     "id": ",".join(chunk)})
        except Exception as e:
            log(f"  [api videos fail] {e}")
            continue
        for it in res.get("items", []):
            sn, st = it.get("snippet", {}), it.get("statistics", {})
            vid = it["id"]
            ts = None
            pub = sn.get("publishedAt")
            if pub:
                try:
                    ts = int(datetime.strptime(pub, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp())
                except ValueError:
                    ts = None
            records.append({
                "id": vid, "title": sn.get("title") or "",
                "channel": sn.get("channelTitle") or "", "channel_id": sn.get("channelId") or "",
                "views": int(st.get("viewCount") or 0),
                "likes": int(st["likeCount"]) if "likeCount" in st else None,
                "comments": int(st["commentCount"]) if "commentCount" in st else None,
                "duration": iso8601_dur_to_sec(it.get("contentDetails", {}).get("duration")),
                "timestamp": ts, "description": (sn.get("description") or "")[:500],
                "url": f"https://www.youtube.com/watch?v={vid}",
                "thumbnail": f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg",
                "query": ids.get(vid, ""),
            })
    log(f"[meta] {len(records)}건 취득 완료")
    return records


# ----------------------------- 필터 · 랭킹 -----------------------------

def is_relevant(rec, pack):
    hay = (rec["title"] + " " + rec["channel"] + " " + rec.get("description", "")).lower()
    inc = pack.get("include") or []
    exc = pack.get("exclude") or []
    if any(x.lower() in hay for x in exc):
        return False
    if inc and not any(x.lower() in hay for x in inc):
        return False
    return True


def enrich(rec, now_ts):
    age_h = max((now_ts - rec["timestamp"]) / 3600.0, 0.5) if rec.get("timestamp") else None
    rec["age_hours"] = round(age_h, 1) if age_h else None
    rec["velocity"] = round(rec["views"] / (age_h / 24.0), 0) if age_h else None  # 하루당 조회수
    v = rec["views"] or 1
    eng = 0
    if rec.get("likes"):
        eng += rec["likes"]
    if rec.get("comments"):
        eng += rec["comments"]
    rec["engagement_rate"] = round(eng / v, 4)
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack", default="robot")
    ap.add_argument("--packs-file", default=DEFAULT_PACKS)
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--per-query", type=int, default=20, help="쿼리당 flat 후보 수")
    ap.add_argument("--max-candidates", type=int, default=30, help="full 메타 취득 상한")
    ap.add_argument("--rank", choices=["views", "velocity"], default="views")
    ap.add_argument("--per-channel", type=int, default=2, help="채널당 최대 게재 수")
    ap.add_argument("--min-views", type=int, default=0)
    ap.add_argument("--no-shorts", action="store_true", help="60초 미만 제외")
    ap.add_argument("--region", default="")
    ap.add_argument("--lang", default="")
    ap.add_argument("--engine", choices=["auto", "ytdlp", "api"], default="auto")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    packs = json.load(open(args.packs_file, encoding="utf-8"))
    if args.pack not in packs:
        log(f"[error] pack '{args.pack}' 없음. 사용 가능: {[k for k in packs if not k.startswith('_')]}")
        sys.exit(2)
    pack = packs[args.pack]

    use_api = args.engine == "api" or (args.engine == "auto" and os.environ.get("YOUTUBE_API_KEY"))
    now_ts = datetime.now(timezone.utc).timestamp()

    if use_api:
        records = engine_api(pack, args.days, args.per_query, args.max_candidates, args.region, args.lang)
        engine_name = "youtube-data-api-v3"
    else:
        records = engine_ytdlp(pack, args.days, args.per_query, args.max_candidates)
        engine_name = "yt-dlp"

    # 중복 id 제거
    seen, uniq = set(), []
    for r in records:
        if r["id"] in seen:
            continue
        seen.add(r["id"])
        uniq.append(r)

    window_start = now_ts - args.days * 86400
    kept, dropped = [], []
    for r in uniq:
        reason = None
        if not r.get("timestamp"):
            reason = "게시일 미상"
        elif r["timestamp"] < window_start:
            reason = "기간 초과"
        elif not is_relevant(r, pack):
            reason = "주제 불일치"
        elif args.no_shorts and r["duration"] and r["duration"] < 60:
            reason = "쇼츠 제외"
        elif r["views"] < args.min_views:
            reason = "최소 조회수 미달"
        if reason:
            r["drop_reason"] = reason
            dropped.append(r)
        else:
            kept.append(enrich(r, now_ts))

    keyfn = (lambda r: (r["views"],)) if args.rank == "views" else (lambda r: (r["velocity"] or 0,))
    kept.sort(key=lambda r: (keyfn(r), r["velocity"] or 0, r["engagement_rate"]), reverse=True)

    # 채널 중복 제거
    top, per_ch = [], {}
    for r in kept:
        ch = r["channel_id"] or r["channel"]
        if per_ch.get(ch, 0) >= args.per_channel:
            continue
        per_ch[ch] = per_ch.get(ch, 0) + 1
        top.append(r)
        if len(top) >= args.top:
            break

    for i, r in enumerate(top, 1):
        r["rank"] = i

    os.makedirs(args.out, exist_ok=True)
    start_d = datetime.fromtimestamp(window_start, timezone.utc).strftime("%Y-%m-%d")
    end_d = datetime.fromtimestamp(now_ts, timezone.utc).strftime("%Y-%m-%d")
    meta = {
        "topic": args.pack, "label": pack.get("label", args.pack),
        "engine": engine_name, "rank_by": args.rank,
        "window_days": args.days, "window_start": start_d, "window_end": end_d,
        "generated_at": datetime.fromtimestamp(now_ts, timezone.utc).strftime("%Y-%m-%d %H:%MZ"),
        "candidates_total": len(uniq), "kept": len(kept), "returned": len(top),
        "region": args.region or "global", "lang": args.lang or "any",
    }
    json.dump({"meta": meta, "top": top}, open(os.path.join(args.out, "top.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    json.dump({"meta": meta, "kept": kept, "dropped": dropped},
              open(os.path.join(args.out, "candidates.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    log("")
    log(f"=== {meta['label']} | {start_d} ~ {end_d} | 엔진 {engine_name} | 조회수기준 {args.rank} ===")
    log(f"후보 {len(uniq)} → 통과 {len(kept)} → 게재 {len(top)}")
    for r in top:
        log(f"  {r['rank']:>2}. {r['views']:>9,}회  {r['channel'][:20]:<20}  {r['title'][:52]}")
    print(os.path.join(args.out, "top.json"))


if __name__ == "__main__":
    main()
