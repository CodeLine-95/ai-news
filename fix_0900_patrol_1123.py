# -*- coding: utf-8 -*-
"""09:00 例行巡检：人工定稿本轮新增 1 条 NLLB 机翻术语硬伤。

本轮 09:00 整点调度自动新增条目（Unite.AI / 09:14 Jay Clayton）：
  - 摘要把 Jay Clayton 译作「国家情报局长」，与同日 06:48 条目的
    「国家情报总监」不一致；Director of National Intelligence 应为「国家情报总监」。
  - 摘要把 acting national cyber director 译作「国家网络局长代理」，
    与标题「代理国家网络总监」自相矛盾，统一为「代理国家网络总监」。
  - 人名保留英文并补中文译名括注，符合全站术语惯例。

固化覆盖三层：
1) data/news.json 内条目直接回填
2) data/titles_override.json / data/summaries_override.json（JSON 层）
3) 再运行 scripts/regen_overrides.py 同步到 manual_overrides.py（代码层）
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

FIXES = [
    {
        "match": "jay-clayton-to-temporarily-serve-as-acting-national-cyber-director/",
        "title_zh": "杰伊·克莱顿将暂时兼任代理国家网络总监",
        "summary_zh": (
            "Axios 于 2026 年 11 月 23 日报道，国家情报总监杰伊·克莱顿（Jay Clayton）"
            "将在克尔斯滕·A·戴维斯（Kirsten A. Davies）等待参议院确认期间，"
            "暂时兼任代理国家网络总监，把他的情报与 AI 协调职责同政府网络政策办公室的"
            "领导职责合并于一身。在戴维斯获得参议院确认前，她将在国家网络总监办公室"
            "（ONCD）担任高级顾问。"
        ),
    },
]


def main():
    with open(os.path.join(DATA, "news.json"), encoding="utf-8") as f:
        db = json.load(f)
    items = db["items"] if isinstance(db, dict) else db

    tpath = os.path.join(DATA, "titles_override.json")
    spath = os.path.join(DATA, "summaries_override.json")
    tov = json.load(open(tpath, encoding="utf-8")) if os.path.exists(tpath) else {}
    sov = json.load(open(spath, encoding="utf-8")) if os.path.exists(spath) else {}

    changed = 0
    for fx in FIXES:
        hit = None
        for it in items:
            if fx["match"].lower() in (it.get("link") or "").lower():
                hit = it
                break
        if not hit:
            print("MISS:", fx["match"])
            continue
        en = hit["title"]
        hit["title_zh"] = fx["title_zh"]
        hit["summary_zh"] = fx["summary_zh"]
        hit["translated"] = True
        hit["method"] = "nllb+manual"
        tov[en] = fx["title_zh"]
        sov[en] = fx["summary_zh"]
        changed += 1
        print("fixed:", hit.get("date"), hit.get("time"), en, "->", fx["title_zh"])

    with open(tpath, "w", encoding="utf-8") as f:
        json.dump(tov, f, ensure_ascii=False, indent=2)
    with open(spath, "w", encoding="utf-8") as f:
        json.dump(sov, f, ensure_ascii=False, indent=2)
    with open(os.path.join(DATA, "news.json"), "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    print("changed:", changed, "/", len(FIXES))


if __name__ == "__main__":
    main()
