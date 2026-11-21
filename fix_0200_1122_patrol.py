# -*- coding: utf-8 -*-
"""2026-11-22 02:00 巡检：人工定稿 2 条 NLLB 机翻硬伤。

1) SiliconANGLE《Sovereign AI: Where control becomes an architectural requirement》(11-22 01:50)
   本轮新增。标题 architectural requirement 被误译为「建筑要求」，
   摘要同词却译为「架构要求」，前后不一致；应为「架构要求」。
2) The Verge《Can Anthropic afford to put safety first?》(11-21 23:00)
   Anthropic 为公司名，被 NLLB 按词根误译为「人类」；应为「Anthropic」。

覆盖三层：news.json 回填 + JSON 覆盖表 + 代码层 manual_overrides.py（regen）。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

TITLE_FIX = {
    "Sovereign AI: Where control becomes an architectural requirement":
        "主权 AI：控制权成为一项架构要求",
    "Can Anthropic afford to put safety first?":
        "Anthropic 负担得起把安全放在第一位吗？",
}


def main():
    db = json.load(open(DATA, encoding="utf-8"))
    items = db["items"] if isinstance(db, dict) else db
    changed = 0
    for it in items:
        en = (it.get("title") or "").strip()
        if en in TITLE_FIX and it.get("title_zh") != TITLE_FIX[en]:
            old = it.get("title_zh", "")
            it["title_zh"] = TITLE_FIX[en]
            it["translated"] = True
            it["method"] = "nllb+manual"
            changed += 1
            print("fixed:", it.get("date"), it.get("time"), "\n  OLD:", old, "\n  NEW:", it["title_zh"])
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    titles = json.load(open(T_JSON, encoding="utf-8"))
    added = 0
    for k, v in TITLE_FIX.items():
        if titles.get(k) != v:
            titles[k] = v
            added += 1
    with open(T_JSON, "w", encoding="utf-8") as f:
        json.dump(titles, f, ensure_ascii=False, indent=2)

    print("[fix_0200_1122] news.json 回填 %d 条；标题覆盖表新增/更新 %d 条；覆盖表共 %d 条" %
          (changed, added, len(titles)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
