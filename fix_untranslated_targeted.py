"""定向回填：仅翻译真正缺译文（summary_zh 为空且 title_zh 缺失/等于原文）的条目。
排除 Simon Willison 标识符型标题（llm 0.37 等，NLLB 正确保留原文，摘要已译）。
完成后重建 AI资讯摘要.md。
"""
import json
import os
import time

import translate
import report

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "news.json")


def main():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    items = data.get("items", data.get("news", []))

    targets = [
        it for it in items
        if (not (it.get("summary_zh") or "").strip())
        and (not (it.get("title_zh") or "").strip() or it.get("title_zh") == it.get("title"))
    ]
    print(f"待回填 {len(targets)} 条", flush=True)
    if not targets:
        report.main()
        print("无需翻译，报告已重建", flush=True)
        return 0

    translate.translate_list(["warmup"])  # 预热
    titles = [it.get("title") or "" for it in targets]
    summaries = [it.get("summary") or "" for it in targets]
    zh_titles, m1 = translate.translate_list(titles, beams=2)
    zh_summaries, m2 = translate.translate_list_chunked(summaries, beams=3)
    for k, it in enumerate(targets):
        t, s = zh_titles[k], zh_summaries[k]
        if t and t != it.get("title"):
            it["title_zh"] = t
            it["translated"] = True
        if s:
            it["summary_zh"] = s
        it["method"] = m1 if m1 != "none" else m2
        print(f"  + {it.get('source')}: {t[:40]}", flush=True)

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    report.main()
    print("回填完成", flush=True)
    return 0


if __name__ == "__main__":
    main()
