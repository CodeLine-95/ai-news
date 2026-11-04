# -*- coding: utf-8 -*-
"""2026-11-02 23:00 例行巡检第二批修复（22:59 抓到的 1 条新条目）。

「Protecting Your Brand from AI Distortion Calls for a New Enterprise Discipline」
的 NLLB 直译有多处硬伤：

1. 标题「保护您的品牌免受 AI 扭曲要求建立新的企业纪律」——calls for 被吞成
   「要求」，discipline 译成「纪律」在企业语境下应为「方法论」，整句不成句。
2. 「将其混到另一个公司」——confuse with another company 译法与语序双错。
3. 「做出无证指控」——unsupported claims 应为「无依据的说法」。
4. 「都太重视了量」——emphasis on volume 应为「看重内容数量」。
5. 「出版更多的内容」——publish 在内容语境应为「发布」。
6. 「解释他们的业务的不同」——语序断裂。

本条人工定稿标题与摘要；术语规则已同步补进 translate.py 的 TERM_FIXES。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

TITLE_FIX = {
    "Protecting Your Brand from AI Distortion Calls for a New Enterprise Discipline":
        "保护品牌免受 AI 失真，需要一套全新的企业方法论",
}

SUMMARY_FIX = {
    "Protecting Your Brand from AI Distortion Calls for a New Enterprise Discipline":
        "AI 驱动的虚假信息对企业品牌声誉构成严重威胁，而蓄意攻击只是问题的一部分。"
        "AI 系统同样会失真：它们可能依赖过时信息、把这家企业与另一家公司混为一谈，"
        "或作出缺乏依据的说法。多年来，内容营销行业（包括 Skyword）过于看重内容数量——"
        "我们帮品牌发布了更多内容，但这些内容往往没有说清企业究竟有何不同。",
}


def main():
    with open(os.path.join(DATA, "news.json"), encoding="utf-8") as f:
        db = json.load(f)
    items = db["items"] if isinstance(db, dict) else db

    hit = 0
    for it in items:
        t = it.get("title", "")
        if t in TITLE_FIX:
            it["title_zh"] = TITLE_FIX[t]
            it["translated"] = True
            it["method"] = "nllb+manual"
            hit += 1
            print("title fixed:", it["date"], it["time"], it["source"])
        if t in SUMMARY_FIX:
            it["summary_zh"] = SUMMARY_FIX[t]
            it["translated"] = True
            it["method"] = "nllb+manual"

    with open(os.path.join(DATA, "titles_override.json"), encoding="utf-8") as f:
        tov = json.load(f)
    tov.update(TITLE_FIX)
    with open(os.path.join(DATA, "titles_override.json"), "w", encoding="utf-8") as f:
        json.dump(tov, f, ensure_ascii=False, indent=2)

    with open(os.path.join(DATA, "summaries_override.json"), encoding="utf-8") as f:
        sov = json.load(f)
    sov.update(SUMMARY_FIX)
    with open(os.path.join(DATA, "summaries_override.json"), "w", encoding="utf-8") as f:
        json.dump(sov, f, ensure_ascii=False, indent=2)

    with open(os.path.join(DATA, "news.json"), "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    print("fixed items:", hit, "/ expected", len(TITLE_FIX))


if __name__ == "__main__":
    main()
