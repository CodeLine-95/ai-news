# -*- coding: utf-8 -*-
"""2026-11-25 00:00 巡检第二轮：定稿 00:00 时段新增的 3 条机翻硬伤。

后台在首轮定稿后又抓到 3 条（total 2746 -> 2749），均为 NLLB 原始机翻：
1) Pinterest：语序错乱，feeds 误作「料」；
2) Wired：honeypot 误作「蜜蜂」（应为「蜜罐」），go rogue 误作「变为徒」；
3) Google Blog：Gemini 误作「双胞胎」，Golden State 指金州勇士，
   Warriors/Valkyries/Chase Center 为专有名词，需准确保留。

同时把首轮 5 条被抓取流程重置的 method 字段修正回 nllb+manual。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

FIXES = [
    {
        "title": "Pinterest will now let parents limit the AI-generated content their teens see",
        "title_zh": "Pinterest 现允许家长限制青少年看到的 AI 生成内容",
        "summary_zh": (
            "在其他社交平台专注于限制青少年使用 AI 聊天机器人之际，Pinterest 选择应对充斥在"
            "青少年信息流中的 AI 生成内容。"
        ),
    },
    {
        "title": "Anthropic Created a Honeypot to Lure AI Agents Into Misbehaving",
        "title_zh": "Anthropic 搭建「蜜罐」，诱使 AI 智能体违规行为",
        "summary_zh": (
            "一项新测试假设 AI 智能体可能失控，并探究它们能否抵御诱惑。"
        ),
    },
    {
        "title": "How Gemini is changing the game for Golden State's organization and fans.",
        "title_zh": "Gemini 如何改变金州球队组织与球迷的体验",
        "summary_zh": (
            "Google Gemini 与金州勇士（Golden State）合作，为勇士队、瓦尔基里女篮（Valkyries）"
            "与大通中心（Chase Center）提供球迷体验与业务运营支持。查看相关新闻。"
        ),
    },
]

# 首轮 5 条被抓取流程重置 method 的标题
FIRST_ROUND = [
    "Amazon’s Decart acquisition is a bet on using software to narrow the gap with Nvidia in the AI chip race",
    "Applied Systems Acquires Tailwind for AI Insurance Document Automation",
    "Three insights you may have missed from theCUBE’s coverage of NetApp INSIGHT",
    "Raising the stakes for enterprise networks with AI modernization",
    "How Trump and Silicon Valley forced Nvidia to take Jensen Huang back",
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
        if fx:
            it["title_zh"] = fx["title_zh"]
            it["summary_zh"] = fx["summary_zh"]
            it["translated"] = True
            it["method"] = "nllb+manual"
            changed += 1
            print("fixed:", it.get("date"), it.get("time"), key[:60])
        elif key in FIRST_ROUND and it.get("method") != "nllb+manual":
            it["method"] = "nllb+manual"
            print("method restored:", it.get("date"), it.get("time"), key[:60])

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
