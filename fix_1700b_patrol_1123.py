# -*- coding: utf-8 -*-
"""2026-11-23 17:00 例行巡检（补充）：定稿刷新轮新增的 1 条 NLLB 硬伤。

SiliconANGLE《Robotics component maker coprod raises $6M to take on robotics
'integration hell'》(17:00)：NLLB 把 "integration hell" 译成「机器人技术的
融入」（应为「集成地狱」）、"bring its first line of components to market"
译成「将其第一个组件线上市场」（应为「把首批组件产品线推向市场」）。

覆盖三层：news.json 回填 + JSON 覆盖表 + manual_overrides.py（regen）。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

TITLE_FIX = {
    "Robotics component maker coprod raises $6M to take on robotics ‘integration hell’":
        "机器人组件制造商 Coprod 融资 600 万美元，应对机器人「集成地狱」",
}

SUMMARY_FIX = {
    "Robotics component maker coprod raises $6M to take on robotics ‘integration hell’": (
        "机器人组件制造商 Coprod Inc. 于 2026 年 11 月 23 日宣布完成 600 万美元新一轮融资，"
        "用于减少构建新机器人平台所需的时间与成本。这笔资金将助力公司把首批组件产品线推向市场。"
    ),
}


def main():
    db = json.load(open(DATA, encoding="utf-8"))
    items = db["items"] if isinstance(db, dict) else db
    changed = 0
    for it in items:
        en = (it.get("title") or "").strip()
        if en not in TITLE_FIX:
            continue
        it["title_zh"] = TITLE_FIX[en]
        it["summary_zh"] = SUMMARY_FIX[en]
        it["translated"] = True
        it["method"] = "nllb+manual"
        changed += 1
        print("fixed:", it.get("date"), it.get("time"), en[:60])
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    titles = json.load(open(T_JSON, encoding="utf-8"))
    summaries = json.load(open(S_JSON, encoding="utf-8"))
    added_t = added_s = 0
    for k, v in TITLE_FIX.items():
        if titles.get(k) != v:
            titles[k] = v
            added_t += 1
    for k, v in SUMMARY_FIX.items():
        if summaries.get(k) != v:
            summaries[k] = v
            added_s += 1
    with open(T_JSON, "w", encoding="utf-8") as f:
        json.dump(titles, f, ensure_ascii=False, indent=2)
    with open(S_JSON, "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)

    print("[fix_1700b_1123] news.json 回填 %d 条；标题定稿 %d / 摘要定稿 %d" %
          (changed, added_t, added_s))
    print("[fix_1700b_1123] 覆盖表 %d / %d 条" % (len(titles), len(summaries)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
