# -*- coding: utf-8 -*-
"""2026-11-26 02:59 巡检：定稿本轮新增的 1 条 NLLB 机翻。

Every 为媒体科技公司名称，NLLB 误译为「每个团队」；$17.5M / $110M
被误放大为「17.5 亿 / 110 亿美元」。以人工定稿回填数据文件与三层覆盖表。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

FIXES = [
    {
        "title": "Every Raises $17.5M Series A at $110M Valuation to Help Teams Adopt AI",
        "title_zh": "媒体科技公司 Every 完成 1750 万美元 A 轮融资，估值 1.1 亿美元，助力团队应用 AI",
        "summary_zh": (
            "媒体与科技公司 Every 于 2026 年 11 月 25 日宣布完成 1750 万美元 A 轮融资，"
            "投后估值 1.1 亿美元，资金将用于打造面向个人和团队的一体化订阅服务，帮助人们把 AI 真正用起来。"
            "本轮由 IA Ventures 的 Jesse Beyroutey 领投，Atlantic 首席执行官 Nicholas Thompson、"
            "Stainless 首席执行官 Alex Rattray 以及 Betaworks 参投。"
        ),
    },
]


def main():
    db = json.load(open(DATA, encoding="utf-8"))
    items = db["items"] if isinstance(db, dict) else db
    titles = json.load(open(T_JSON, encoding="utf-8"))
    summaries = json.load(open(S_JSON, encoding="utf-8"))

    by_title = {fx["title"].strip(): fx for fx in FIXES}
    changed = 0
    for it in items:
        fx = by_title.get((it.get("title") or "").strip())
        if fx:
            it["title_zh"] = fx["title_zh"]
            it["summary_zh"] = fx["summary_zh"]
            it["translated"] = True
            it["method"] = "nllb+manual"
            changed += 1
            print("fixed:", it.get("date"), it.get("time"), it.get("title", "")[:60])

    for fx in FIXES:
        titles[fx["title"]] = fx["title_zh"]
        summaries[fx["title"]] = fx["summary_zh"]

    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    with open(T_JSON, "w", encoding="utf-8") as f:
        json.dump(titles, f, ensure_ascii=False, indent=2)
    with open(S_JSON, "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)

    print("回填条目:", changed)
    assert changed == len(FIXES), "定稿条目数不符：%d != %d" % (changed, len(FIXES))


if __name__ == "__main__":
    main()
