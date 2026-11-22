# -*- coding: utf-8 -*-
"""08:00 例行巡检：人工定稿 1 条 NLLB 机翻硬伤。

本轮（2026-11-22 08:04:57 重启后首轮补抓）自动新增条目：
  - Together AI（公司名）被错译为「结合 AI」
  - "serverless inference" →「无服务器推断」应为「无服务器推理」
  - "private Hugging Face repository" →「私人拥抱面孔库」应为「私有 Hugging Face 仓库」

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
        "match": "Together AI Discloses Prompt Leak",
        "title_zh": "Together AI 披露：编码智能体暴露凭证后发生提示词泄露",
        "summary_zh": (
            "Together AI 于 2026 年 11 月 21 日披露：在客户向其无服务器推理服务提交的部分提示词中，"
            "有一名未经授权方下载了留存的样本。此前该公司在开发其公开的 xorl GitHub 仓库时，"
            "一个 AI 编码智能体暴露了用于此次下载的私有仓库凭证。客户此前已授权将这些提示词"
            "用于常规软件测试，Together AI 将样本存储在一个私有的 Hugging Face 仓库中。"
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
            if fx["match"].lower() in (it.get("title") or "").lower():
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
        print("fixed:", hit.get("date"), hit.get("time"), en[:70])

    with open(tpath, "w", encoding="utf-8") as f:
        json.dump(tov, f, ensure_ascii=False, indent=2)
    with open(spath, "w", encoding="utf-8") as f:
        json.dump(sov, f, ensure_ascii=False, indent=2)
    with open(os.path.join(DATA, "news.json"), "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    print("changed:", changed, "/", len(FIXES))


if __name__ == "__main__":
    main()
