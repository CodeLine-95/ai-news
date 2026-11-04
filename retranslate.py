"""用当前最优引擎（NLLB）重译全部历史英文条目，并重新生成报告。

用于引擎升级后的批量回填：旧译文（opus-mt）质量偏低，
一次性用 NLLB 重译可显著提升可读性。

注意：重译期间请勿同时运行 server.py（两者会争写 data/news.json）。
重译完成后重启服务即可加载新译文。

用法：
    python3 retranslate.py            # 全量重译
    python3 retranslate.py --limit 30 # 仅重译前 30 条（试跑）
"""
import argparse
import json
import os
import sys
import time

import translate
import report
import fetcher

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "news.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="最多重译条数，0=不限")
    ap.add_argument("--batch", type=int, default=8, help="每批条数")
    args = ap.parse_args()

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    items = data.get("items", [])
    targets = [it for it in items if it.get("lang") == "en"]
    if args.limit:
        targets = targets[: args.limit]

    print(f"待重译 {len(targets)} 条，引擎加载中 ...", flush=True)
    t0 = time.time()
    translate.translate_list(["warmup"])  # 触发模型加载
    print(f"模型就绪，用时 {time.time() - t0:.1f}s", flush=True)

    done = 0
    t0 = time.time()
    for i in range(0, len(targets), args.batch):
        batch = targets[i : i + args.batch]
        # 先清洗存量英文摘要的尾部噪声（站点推广语 / 截断标记），再送入翻译
        for it in batch:
            cleaned = fetcher._strip_tail_noise(it.get("summary") or "")
            if cleaned != (it.get("summary") or ""):
                it["summary"] = cleaned
        titles = [it["title"] for it in batch]
        summaries = [it.get("summary") or "" for it in batch]

        # 标题用 beam=2 保质量；摘要更长，用贪心解码显著提速
        zh_titles, m1 = translate.translate_list(titles, beams=2)
        zh_summaries, m2 = translate.translate_list_chunked(summaries, beams=3)

        for k, it in enumerate(batch):
            t = zh_titles[k]
            s = zh_summaries[k]
            if t and t != it["title"]:
                it["title_zh"] = t
                it["translated"] = True
            if s:
                it["summary_zh"] = s
            it["method"] = m1 if m1 != "none" else m2

        done += len(batch)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        elapsed = time.time() - t0
        speed = done / elapsed if elapsed > 0 else 0
        eta = (len(targets) - done) / speed if speed > 0 else 0
        print(
            f"[{done}/{len(targets)}] 引擎={m1} 用时{elapsed:.0f}s "
            f"速度{speed:.2f}条/s 预计剩余{eta:.0f}s",
            flush=True,
        )

    report.main()
    print("重译完成", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
