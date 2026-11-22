# -*- coding: utf-8 -*-
"""09:00 例行巡检：人工定稿 1 条 NLLB 机翻硬伤。

本轮平台 09:18 重启后首轮补抓自动新增条目（Simon Willison / Muru）：
  - 标题 "Muru"（Rust 服务器产品名）被音译为「摩鲁」，丢失语义
  - 摘要中人名/项目名被音译断裂（穆鲁·格雷厄姆·达普尔顿 / 私人「新」）

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
        "match": "simonwillison.net/2026/Nov/21/muru/",
        "title_zh": "Muru：Graham Dumpleton 打造的 AI 辅助 Rust 服务器",
        "summary_zh": (
            "Graham Dumpleton 于 20 年前创建了 mod_wsgi，此后他一直在思考在生产环境中运行 Python "
            "Web 应用的最佳方式。Muru 是他全新打造的 AI 辅助 Rust 服务器，旨在为开发和生产环境中的 "
            "ASGI、WSGI Python 应用提供尽可能出色的运行工具。正如他在 wrapture 项目中一样，他一边开发"
            "一边持续发布极其详尽的项目记录，将其作为开发流程的一部分。"
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
