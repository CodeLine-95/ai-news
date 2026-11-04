"""修复存量超长摘要的翻译质量问题。

背景：
    IEEE Spectrum AI 的 RSS 把整篇正文塞进 description（最长 2.4 万字符），
    而离线 NLLB 模型输入上限 384 token，超长输入被静默截断，
    导致中文译文只覆盖原文开头约 5%，并在长生成末尾出现重复退化
    （"美国，美国，美国…" / "请问，请问，请问…"）。

本脚本做三件事：
    1. 用抓取层新增的句边界截断，把超长英文摘要裁到可完整翻译的长度；
    2. 剥离摘要开头的赞助商前缀（"This article is brought to you by X ."）；
    3. 用 NLLB 重译这些条目，并对缺失摘要的条目尝试从文章页补齐。

注意：运行前请先停止 server.py，避免两者争写 data/news.json。

用法：
    python3 backfill_long_summaries.py
"""
import json
import os
import sys
import time

import fetcher
import translate
import enrich_summaries
import report

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "news.json")

LONG_THRESHOLD = 1000


def main():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    items = data.get("items", [])
    log = []

    # --- 1) 找出需要修复的条目 ---
    long_items = [
        it for it in items
        if len((it.get("summary") or "").strip()) > LONG_THRESHOLD
    ]
    missing_items = [
        it for it in items
        if it.get("lang") == "en"
        and not (it.get("summary_zh") or "").strip()
    ]
    log.append("超长摘要条目 = %d" % len(long_items))
    log.append("缺失译文摘要条目 = %d" % len(missing_items))

    if not long_items and not missing_items:
        log.append("无需修复")
        open(os.path.join(BASE, "data", "_backfill_log.txt"), "w", encoding="utf-8").write("\n".join(log))
        report.main()
        return 0

    # --- 2) 截断超长英文摘要 + 剥离赞助商前缀 ---
    for it in long_items:
        en = (it.get("summary") or "").strip()
        before = len(en)
        cleaned = fetcher._strip_head_sponsor(en)
        cleaned = fetcher._truncate_summary(cleaned)
        it["summary"] = cleaned
        it["summary_zh"] = ""   # 标记需重译
        log.append("截断 %s %s | %d -> %d | %s" % (
            it["date"], it["time"], before, len(cleaned), (it.get("title") or "")[:48]
        ))

    # --- 3) 补齐缺失摘要（从文章页 og:description 取） ---
    for it in missing_items:
        if (it.get("summary") or "").strip():
            continue
        desc = enrich_summaries.page_description(it.get("link") or "")
        if desc:
            it["summary"] = fetcher._truncate_summary(desc)
            log.append("补齐摘要 %s %s | %s | %d 字" % (
                it["date"], it["time"], (it.get("title") or "")[:40], len(desc)
            ))
        else:
            log.append("补齐失败（源未提供） %s %s | %s" % (
                it["date"], it["time"], (it.get("title") or "")[:48]
            ))

    # --- 4) 重译所有待修条目 ---
    todo = [it for it in items if not (it.get("summary_zh") or "").strip()]
    log.append("待重译 = %d" % len(todo))

    if todo:
        print("翻译引擎加载中 ...", flush=True)
        t0 = time.time()
        translate.translate_list(["warmup"])
        log.append("模型就绪，用时 %.1fs" % (time.time() - t0))

        for i in range(0, len(todo), 4):
            batch = todo[i: i + 4]
            titles = [it.get("title") or "" for it in batch]
            summaries = [it.get("summary") or "" for it in batch]
            zh_titles, m1 = translate.translate_list(titles, beams=2)
            zh_sums, m2 = translate.translate_list_chunked(summaries, beams=2)
            for k, it in enumerate(batch):
                if zh_titles[k] and zh_titles[k] != it.get("title"):
                    it["title_zh"] = zh_titles[k]
                    it["translated"] = True
                if zh_sums[k]:
                    it["summary_zh"] = zh_sums[k]
                it["method"] = m1 if m1 != "none" else m2
            done = min(i + 4, len(todo))
            log.append("[%d/%d] 重译完成" % (done, len(todo)))
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    log.append("已写回 %s" % DATA_FILE)
    report.main()
    log.append("报告已重新生成")

    with open(os.path.join(BASE, "data", "_backfill_log.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(log))
    print("backfill done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
