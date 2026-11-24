# -*- coding: utf-8 -*-
"""2026-11-24 19:00 例行巡检：定稿本轮新增 2 条 NLLB 机翻硬伤。

本轮整点调度新增 2 条 Wired 条目（total 2699 -> 2701），均为 NLLB 原始机翻：
1) "Anthropic researcher" 误译为「人类研究人员」（应为「Anthropic 研究员」），
   "Riemann hypothesis" 误译为「里曼假设」（应为「黎曼猜想」），
   “alien” 这一关键限定语被漏译；
2) "pro-AI parents" 与 "frustrated" 语气偏弱，需贴合原文语义定稿。

覆盖三层：news.json 回填 + JSON 覆盖表 + 代码层 manual_overrides.py（regen）。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

FIXES = [
    {
        "title": "AI Solved Math’s Most Famous Problem. Now Humans Are Struggling to Understand It",
        "title_zh": "AI 破解了数学最著名难题，如今人类正费力理解其解法",
        "summary_zh": (
            "Anthropic 一名研究员针对黎曼猜想给出的 1700 万行「异类」解法，"
            "数学家可能要花数月时间才能读懂。"
        ),
    },
    {
        "title": "Don’t Bring Up AI if You Want to Enjoy Your Thanksgiving",
        "title_zh": "想安稳过感恩节？别提 AI",
        "summary_zh": (
            "对未来感到焦虑的年轻人表示，他们对越来越热衷 AI 的父母愈发不满，"
            "并担心这会让节日聚会气氛变得紧张。"
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
        key = (it.get("title") or "").strip()
        fx = by_title.get(key)
        if not fx:
            continue
        it["title_zh"] = fx["title_zh"]
        it["summary_zh"] = fx["summary_zh"]
        it["translated"] = True
        it["method"] = "nllb+manual"
        changed += 1
        print("fixed:", it.get("date"), it.get("time"), key[:60])

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


if __name__ == "__main__":
    main()
