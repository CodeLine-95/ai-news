# -*- coding: utf-8 -*-
"""2026-11-02 23:00 例行巡检第三批修复（23:12 首轮新增 2 条）。

1.「Introducing the Grid Protectors Program」
   → 标题「介绍了电网保护程序」漏掉主语且 Program 译法不准
     （Grid Protectors 是项目专名，应作「电网守护者计划」）；
     摘要「未来的计算机校园」——compute campus 指「算力园区」，
     是 NLLB 对 datacenter/campus 复合词的典型误读；
     「保护消费者电力成本」语序错乱。本条人工定稿。
2.「Omen AI adds liquid know-how in $16 million Aquatic Labs acquisition」
   → 「增加了液体技术」——liquid know-how 在数据中心语境下指
     「水冷/水处理技术专长」，直译成「液体技术」完全无法理解；
     「1600 万美元」应为「1,600 万美元」；摘要过短且信息不全，
     按原文事实人工补全。本条人工定稿。

术语规则同步补进 translate.py 的 TERM_FIXES。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

TITLE_FIX = {
    "Introducing the Grid Protectors Program":
        "OpenAI 推出「电网守护者计划」",
    "Omen AI adds liquid know-how in $16 million Aquatic Labs acquisition":
        "Omen AI 以 1,600 万美元收购 Aquatic Labs，补齐水处理技术能力",
}

SUMMARY_FIX = {
    "Introducing the Grid Protectors Program":
        "OpenAI 的「电网守护者计划」将与公用事业公司合作，"
        "帮助未来的算力园区支撑电网可靠性，并保障消费者的用电成本。",
    "Omen AI adds liquid know-how in $16 million Aquatic Labs acquisition":
        "两家致力于解决数据中心水问题的初创公司在一笔 1,600 万美元的交易中合并。"
        "Omen AI 由此获得 Aquatic Labs 在水处理与液冷方面的技术积累，"
        "补齐自身在数据中心水管理上的能力短板。",
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
