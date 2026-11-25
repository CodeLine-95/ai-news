# -*- coding: utf-8 -*-
"""17:00 巡检质量修复：修正 Trump/NVIDIA 条目 NLLB 译文语义偏差。

原文：Trump Says He Considered U.S. Government Stake in NVIDIA
NLLB 直译把 considered 误译为「认为」，语义偏离（应为「考虑过」）。
按人工定稿机制写入 titles_override.json / summaries_override.json 并回填 news.json。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")
NEWS = os.path.join(BASE, "data", "news.json")

KEY = "Trump Says He Considered U.S. Government Stake in NVIDIA"
TITLE_ZH = "特朗普表示曾考虑让美国政府持有 NVIDIA 股份"
SUMMARY_ZH = (
    "美国总统唐纳德·特朗普表示，他考虑过让美国政府持有 NVIDIA 的股份，"
    "并将该公司的成功与美国在人工智能领域的领先地位联系起来。"
    "据《纽约邮报》2026 年 11 月 24 日援引 CNBC 的报道，"
    "特朗普将这种可能性与美国政府 2025 年入股 Intel 的做法作了比较。"
)


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    titles = load(T_JSON)
    summaries = load(S_JSON)
    titles[KEY] = TITLE_ZH
    summaries[KEY] = SUMMARY_ZH
    save(T_JSON, titles)
    save(S_JSON, summaries)

    news = load(NEWS)
    fixed = 0
    for it in news["items"]:
        if it.get("title") == KEY:
            it["title_zh"] = TITLE_ZH
            it["summary_zh"] = SUMMARY_ZH
            it["translated"] = True
            it["method"] = "manual"
            fixed += 1
    save(NEWS, news)
    print("标题/摘要覆盖表已更新；回填条目数:", fixed)


if __name__ == "__main__":
    main()
