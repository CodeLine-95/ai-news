# -*- coding: utf-8 -*-
"""10:00 例行巡检：定稿本轮新增的 SiliconANGLE / SAP 裁员条目。

NLLB 机翻把 “Bloomberg” 截成「博社」，语义残缺；同时把
“over 9% of its workforce” 译成「占其劳动力的 9%」，漏掉「以上」。
按英文原文重述，保留产品名与百分比含义，写入人工覆盖表。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

EN_TITLE = "SAP reportedly plans to lay off 10,000+ employees amid AI push"
ZH_TITLE = "据报道，SAP 在 AI 推进过程中计划裁员逾 1 万人"
ZH_SUMMARY = (
    "据报道，企业软件巨头 SAP SE 计划裁员至少 1 万名员工，占其员工总数的 9% 以上。"
    "彭博社今日援引消息人士称，这项重组计划的范围仍可能调整。"
)


def main():
    db_path = os.path.join(DATA, "news.json")
    db = json.load(open(db_path, encoding="utf-8"))
    items = db["items"] if isinstance(db, dict) else db

    tpath = os.path.join(DATA, "titles_override.json")
    spath = os.path.join(DATA, "summaries_override.json")
    tov = json.load(open(tpath, encoding="utf-8")) if os.path.exists(tpath) else {}
    sov = json.load(open(spath, encoding="utf-8")) if os.path.exists(spath) else {}

    changed = 0
    for it in items:
        if (it.get("title") or "").strip() != EN_TITLE:
            continue
        for key, value in (("title_zh", ZH_TITLE), ("summary_zh", ZH_SUMMARY)):
            if it.get(key) != value:
                it[key] = value
                it["translated"] = True
                it["method"] = "nllb+manual"
                changed += 1
        break

    tov[EN_TITLE] = ZH_TITLE
    sov[EN_TITLE] = ZH_SUMMARY

    json.dump(tov, open(tpath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(sov, open(spath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(db, open(db_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("[fix] 定稿 %d 处 | 标题覆盖 %d 条 / 摘要覆盖 %d 条"
          % (changed, len(tov), len(sov)))


if __name__ == "__main__":
    main()
