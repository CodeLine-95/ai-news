"""用修复后的抓取逻辑回填存量条目的半句摘要。

背景（2026-11-01 巡检发现）：
    旧版 `_entry_summary` 采取「取第一个长度 >= 20 的候选」策略，
    对 The Verge / MIT Tech Review / NVIDIA Blog 这类同时提供
    <summary> 与 <content> 的源，会选中被源站截断在半句的 <summary>，
    把完整的 <content> 丢掉。库内因此残留 44 条半句英文摘要，
    对应译文同样半句，且句中关键事实丢失。

本脚本：
    1) 重新抓取各源 RSS，用修复后的 `_entry_summary` 得到完整摘要；
    2) 若新摘要比库内更完整（以完整句收尾且更长的部分更多），
       则更新库内英文摘要并标记为待重译；
    3) 用 NLLB 重译这些条目的标题与摘要；
    4) 重生成报告。

注意：运行期间请勿同时运行 server.py（两者会争写 data/news.json）。

用法：
    python3 backfill_complete.py            # 全量回填
    python3 backfill_complete.py --dry-run  # 只报告将要做的改动
"""
import argparse
import json
import os
import re
import sys
import time

import feedparser
import requests

import fetcher
import translate
import report

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "news.json")


def _collect_source_summaries():
    """重新抓取各源，返回 {link: 完整摘要}。"""
    out = {}
    for name, url in fetcher.FEEDS:
        if name in ("VentureBeat", "Unite.AI", "Google DeepMind", "Google Blog"):
            continue
        try:
            r = requests.get(
                url,
                timeout=25,
                headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                                      "Chrome/131.0.0.0 Safari/537.36"},
            )
            if r.status_code >= 400:
                print(f"[backfill] {name} HTTP {r.status_code}，跳过", flush=True)
                continue
            items = fetcher._parse_entries(r.content, name, 12)
        except Exception as e:
            print(f"[backfill] {name} 抓取失败 {type(e).__name__}，跳过", flush=True)
            continue
        got = 0
        for it in items:
            s = it.get("summary") or ""
            if s and fetcher._is_complete(s):
                out[it["link"]] = s
                got += 1
        print(f"[backfill] {name} 取到 {got} 条完整摘要", flush=True)
    return out


def _sentence_count(text):
    """统计句子数，用于判断新摘要的信息量是否更足。"""
    return max(1, len([s for s in re.split(r"[.!?]\s+", text or "") if s.strip()]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="只报告不写文件")
    args = ap.parse_args()

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    items = data.get("items", [])

    print("[backfill] 重新抓取各源摘要 ...", flush=True)
    fresh = _collect_source_summaries()
    print(f"[backfill] 共取到 {len(fresh)} 条完整摘要", flush=True)

    # 找出需要回填的条目：库内摘要半句结尾，且新摘要是完整句
    targets = []
    for it in items:
        link = it.get("link") or ""
        old = it.get("summary") or ""
        new = fresh.get(link)
        if not new or not old:
            continue
        old_ok = fetcher._is_complete(old)
        new_ok = fetcher._is_complete(new)
        if old_ok and not new_ok:
            continue
        # 新摘要必须更完整：句数更多，或结尾由半句变完整句
        better = (not old_ok and new_ok) or (
            _sentence_count(new) > _sentence_count(old) and len(new) > len(old) * 0.8
        )
        if better:
            targets.append((it, old, new))

    print(f"[backfill] 待回填 {len(targets)} 条", flush=True)
    for it, old, new in targets[:10]:
        print(f"  - {it['source']:16} {it['title'][:38]}")
        print(f"      旧({len(old)}) ...{old[-55:]!r}")
        print(f"      新({len(new)}) ...{new[-55:]!r}")
    if len(targets) > 10:
        print(f"  ... 另有 {len(targets) - 10} 条", flush=True)

    if not targets:
        print("[backfill] 无需回填", flush=True)
        return 0
    if args.dry_run:
        print("[backfill] dry-run，未写文件", flush=True)
        return 0

    # 更新英文摘要
    for it, old, new in targets:
        it["summary"] = new

    # 重译这些条目的标题与摘要
    print("[backfill] 翻译引擎加载中 ...", flush=True)
    t0 = time.time()
    translate.translate_list(["warmup"])
    print(f"[backfill] 模型就绪，用时 {time.time() - t0:.1f}s", flush=True)

    titles = [it["title"] for it, _, _ in targets]
    summaries = [it["summary"] for it, _, _ in targets]
    zh_titles, m1 = translate.translate_list(titles, beams=2)
    zh_summaries, m2 = translate.translate_list_chunked(summaries, beams=3)

    ok = 0
    for k, (it, _, _) in enumerate(targets):
        t, s = zh_titles[k], zh_summaries[k]
        if t and t != it["title"]:
            it["title_zh"] = t
            it["translated"] = True
        if s:
            it["summary_zh"] = s
            ok += 1
        it["method"] = m1 if m1 != "none" else m2

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[backfill] 回填 {ok} 条译文，已写回 {DATA_FILE}", flush=True)

    report.main()
    print("[backfill] 报告已重新生成", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
