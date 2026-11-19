# -*- coding: utf-8 -*-
"""11:00 巡检修复：11 点调度新增条目中发现 1 条 NLLB 机翻硬伤，人工定稿。

硬伤：
- "midtier model"（中端/中档模型）被误译为「中产车型」
- "Carbon"（竞品模型代号）被误译为「碳」，"three-times faster than Carbon"
  被译成「是碳速度的三倍」语义崩坏

覆盖三层（与历史巡检一致）：
1) data/news.json 内条目直接回填（立即生效）
2) data/titles_override.json / data/summaries_override.json（持久卷 JSON 层）
3) 运行 scripts/regen_overrides.py 同步到 manual_overrides.py（代码层）
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

FIXES = {
    "Google’s latest midtier model Gemini 4 Neon is three-times faster than Carbon and wins on some metrics": {
        "title_zh": "Google 最新中端模型 Gemini 4 Neon 比 Carbon 快三倍，并在部分指标上胜出",
        "summary_zh": "在夏季低调蛰伏、竞争对手如 Anthropic PBC 与 OpenAI Group PBC 相继推出强大的新前沿模型之后，Google LLC 正发起反击。",
    },
}


def main():
    with open(os.path.join(DATA, "news.json"), encoding="utf-8") as f:
        db = json.load(f)
    items = db["items"] if isinstance(db, dict) else db
    changed = 0
    for it in items:
        en = (it.get("title") or "").strip()
        if en in FIXES:
            fx = FIXES[en]
            it["title_zh"] = fx["title_zh"]
            it["summary_zh"] = fx["summary_zh"]
            it["translated"] = True
            it["method"] = "nllb+manual"
            changed += 1
            print("fixed:", it.get("date"), it.get("time"), en[:60])

    tpath = os.path.join(DATA, "titles_override.json")
    spath = os.path.join(DATA, "summaries_override.json")
    tov = json.load(open(tpath, encoding="utf-8")) if os.path.exists(tpath) else {}
    sov = json.load(open(spath, encoding="utf-8")) if os.path.exists(spath) else {}
    for en, fx in FIXES.items():
        tov[en] = fx["title_zh"]
        sov[en] = fx["summary_zh"]
    with open(tpath, "w", encoding="utf-8") as f:
        json.dump(tov, f, ensure_ascii=False, indent=2)
    with open(spath, "w", encoding="utf-8") as f:
        json.dump(sov, f, ensure_ascii=False, indent=2)
    with open(os.path.join(DATA, "news.json"), "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    print("changed:", changed, "/", len(FIXES))
    print("title overrides:", len(tov), "summary overrides:", len(sov))


if __name__ == "__main__":
    main()
