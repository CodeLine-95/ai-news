# -*- coding: utf-8 -*-
"""04:00 巡检补轮：定稿启动轮新抓到的 2 条 NLLB 机翻条目。

- 04:03 TechCrunch “Nvidia hits pause on chip shipments to Southeast Asia”
  被译成「Nvidia 在东南亚的芯片运输中暂停」，语义倒置；按原文重述。
- 03:56 Unite.AI “Canada Invests $700 Million More to Expand AI Compute Access Fund”
  被译成「加拿大投资了 7 亿美元更多」「打开了特定部门的呼叫」，机翻腔明显。

回填 news.json + JSON 覆盖表，再由 scripts/regen_overrides.py 固化到代码层。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

FIX = {
    "Nvidia hits pause on chip shipments to Southeast Asia": (
        "英伟达暂停向东南亚发运芯片",
        "随着美国加紧阻止 AI 芯片流入中国，英伟达已通知制造合作伙伴暂停向马来西亚、"
        "新加坡、泰国和印度尼西亚发运服务器。",
    ),
    "Canada Invests $700 Million More to Expand AI Compute Access Fund": (
        "加拿大再投 7 亿美元扩大 AI 算力获取基金",
        "加拿大政府于 2026 年 11 月 26 日追加 7 亿美元，将 AI 算力获取基金规模扩大至 "
        "10 亿美元，并面向医疗与生命科学项目启动专项征集。人工智能与数字创新部长 "
        "Evan Solomon 在多伦多宣布了下一阶段计划。",
    ),
}


def main():
    db = json.load(open(os.path.join(DATA, "news.json"), encoding="utf-8"))
    items = db["items"] if isinstance(db, dict) else db

    tpath = os.path.join(DATA, "titles_override.json")
    spath = os.path.join(DATA, "summaries_override.json")
    tov = json.load(open(tpath, encoding="utf-8")) if os.path.exists(tpath) else {}
    sov = json.load(open(spath, encoding="utf-8")) if os.path.exists(spath) else {}

    changed = 0
    matched = set()
    for it in items:
        en = it.get("title") or ""
        if en in FIX:
            matched.add(en)
            title_zh, summary_zh = FIX[en]
            for key, value in (("title_zh", title_zh), ("summary_zh", summary_zh)):
                if it.get(key) != value:
                    it[key] = value
                    it["translated"] = True
                    it["method"] = "nllb+manual"
                    changed += 1
                    print("[fix] %s: %s" % (key, en[:58]))
            tov[en] = title_zh
            sov[en] = summary_zh

    missing = set(FIX) - matched
    if missing:
        print("[warn] 未匹配到条目:", missing)

    json.dump(tov, open(tpath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(sov, open(spath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(db, open(os.path.join(DATA, "news.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("[fix] 变更 %d 处 | 覆盖表 标题 %d 条 / 摘要 %d 条"
          % (changed, len(tov), len(sov)))


if __name__ == "__main__":
    main()
