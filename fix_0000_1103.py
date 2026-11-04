# -*- coding: utf-8 -*-
"""2026-11-03 00:00 例行巡检修复（00:00 轮新抓到的 1 条）。

00:00 轮新增 1 条（Unite.AI），NLLB 直译存在多处硬伤：

1. 标题「OpenAI 启动了电脑校园的电网守护者计划」
   - 「电脑校园」应为「算力园区」（compute campus 固定中文写法，
     现有术语表只覆盖了「计算机校园」，漏掉「电脑校园」这一变体）；
   - 「启动了……计划」是逐词硬翻，官方中文名应为「电网守护者计划」。
2. 摘要
   - 「格鲁吉亚」把美国佐治亚州译成了国家名（严重事实错误）；
   - 「埃菲金汉县校园」地名音译错误 + campus 误译为校园；
   - 「这是国家计划」漏译 nationwide 的「全国性」；
   - 「安排电力需求减少电网压力时」语序崩坏；
   - 「公用事业，监管机构」缺「公司」且顿号缺失；
   - 「1000 兆瓦」缺千分位。

同时在 translate.py 补齐 6 条确定性术语规则，防止同类直译缺陷复发；
本条标题与摘要人工定稿。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

TITLE_FIX = {
    "OpenAI Launches Grid Protectors Program for Compute Campuses":
        "OpenAI 推出「电网守护者计划」，面向算力园区",
}

SUMMARY_FIX = {
    "OpenAI Launches Grid Protectors Program for Compute Campuses":
        "2026 年 11 月 2 日，OpenAI 启动了「电网守护者计划」，这是一项全国性行动，"
        "旨在让未来的算力园区在电网吃紧时削减用电需求。"
        "起步点是美国佐治亚州：当地规划中的埃芬汉县园区已达成一项协议，"
        "可提供最高 1,000 兆瓦的灵活需求响应。"
        "该公司将与公用事业公司、监管机构和政策制定者合作制定具体安排，"
        "明确削减多少需求、以多快的速度削减，以及可持续多长时间。",
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
