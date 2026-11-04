"""离线回填脚本：抓取窗口内漏采的条目并翻译入库。

用于一次性修复「每源只取前 N 条」造成的漏采。
与 server.py 的 update_cycle 共用同一套去重/翻译逻辑，
但独立进程运行，避免长时间翻译占住 Web 服务的事件循环。
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import fetcher  # noqa: E402
import translate  # noqa: E402

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "news.json")
TZ = timezone(timedelta(hours=8))
MAX_AGE_DAYS = 30
TRANSLATE_BATCH = 12
SUMMARY_BEAMS = 3


def load():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    now = datetime.now(TZ)
    cutoff = now - timedelta(days=MAX_AGE_DAYS)
    data = load()
    items = data["items"]
    have = {it["id"] for it in items}

    print(f"[backfill] 已有 {len(items)} 条，开始抓取（时间窗 {cutoff:%Y-%m-%d} 起）", flush=True)
    raw = fetcher.fetch_all(since=cutoff)
    print(f"[backfill] 抓取 {len(raw)} 条原始条目", flush=True)

    before = len(items)
    pending = []
    for r in raw:
        nid = fetcher.make_id(r["link"])
        if nid in have:
            continue
        have.add(nid)
        if r["dt"] < cutoff:
            continue
        lang = translate.detect_lang(r["title"])
        item = {
            "id": nid,
            "source": r["source"],
            "link": r["link"],
            "lang": lang,
            "date": r["dt"].strftime("%Y-%m-%d"),
            "time": r["dt"].strftime("%H:%M"),
            "iso": r["dt"].isoformat(),
            "title": r["title"],
            "summary": r["summary"],
            "title_zh": r["title"] if lang == "zh" else "",
            "summary_zh": r["summary"] if lang == "zh" else "",
            "translated": False,
            "method": "",
        }
        if lang == "zh":
            item["translated"] = True
            item["method"] = "native"
        else:
            pending.append(item)
        items.append(item)

    added = len(items) - before
    print(f"[backfill] 新增 {added} 条，待翻译 {len(pending)} 条", flush=True)
    print(f"[backfill] 库内总数 {len(items)}", flush=True)

    done = 0
    for s in range(0, len(pending), TRANSLATE_BATCH):
        group = pending[s : s + TRANSLATE_BATCH]
        zh_titles, m1 = translate.translate_list([it["title"] for it in group])
        zh_summaries, m2 = translate.translate_list_chunked(
            [it["summary"] for it in group], beams=SUMMARY_BEAMS
        )
        gm = m1 if m1 != "none" else m2
        for i, it in enumerate(group):
            t = zh_titles[i] or ""
            s2 = zh_summaries[i] or ""
            it["title_zh"] = t or it["title"]
            it["summary_zh"] = s2 or it["summary"]
            it["translated"] = bool(t) and t != it["title"]
            it["method"] = gm
        done += len(group)
        items.sort(key=lambda x: x["iso"], reverse=True)
        data["items"] = items
        save(data)
        print(f"[backfill] 翻译进度 {done}/{len(pending)}（{gm}）", flush=True)

    print(f"[backfill] 完成：共 {len(items)} 条", flush=True)


if __name__ == "__main__":
    main()
