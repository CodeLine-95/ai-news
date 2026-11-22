# -*- coding: utf-8 -*-
"""2026-11-22 16:00 巡检：定稿本轮新增 1 条 Tesla FSD V15 的 NLLB 机翻硬伤。

原文：Tesla Rolls Out FSD V15 with Reality View and Vision Upgrades
机翻缺陷：
  - 标题「带有现实视觉和视觉升级」句式生硬、Reality View 未保留专名；
  - 摘要「现场 Tesla 现实视图可视化」「关键干预率提升了 25 倍」
    「Tesla 的人工智能领袖」等表达不符合中文科技新闻习惯。
按三层覆盖表回填：news.json + JSON 表 + 代码层 manual_overrides.py（regen）。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

TITLE = "Tesla Rolls Out FSD V15 with Reality View and Vision Upgrades"

TITLE_FIX = {
    TITLE: "Tesla 推出 FSD V15，带来 Reality View 实景视图与视觉升级",
}

SUMMARY_FIX = {
    TITLE: (
        "Tesla 于 2026 年 11 月 21 日宣布，全自动驾驶（FSD）v15 开始推送，"
        "带来升级的驾驶网络、实时 Tesla Reality View 实景可视化，"
        "以及据公司称关键干预率提升 25 倍。本版本还调整了导航、泊车、"
        "驾驶员监控与速度处理。Tesla AI 负责人 Ashok Elluswamy 表示，"
        "该版本将首先推送给第一批客户。"
    ),
}


def main():
    # 1) 回填 news.json
    db = json.load(open(DATA, encoding="utf-8"))
    items = db["items"] if isinstance(db, dict) else db
    changed = 0
    for it in items:
        en = (it.get("title") or "").strip()
        if en == TITLE:
            it["title_zh"] = TITLE_FIX[en]
            it["summary_zh"] = SUMMARY_FIX[en]
            it["translated"] = True
            it["method"] = "nllb+manual"
            changed += 1
            print("[fix_1600_1122] 回填:", it.get("date"), it.get("time"), en)
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    # 2) 写入 JSON 覆盖表
    titles = json.load(open(T_JSON, encoding="utf-8"))
    summaries = json.load(open(S_JSON, encoding="utf-8"))
    for k, v in TITLE_FIX.items():
        titles[k] = v
    for k, v in SUMMARY_FIX.items():
        summaries[k] = v
    with open(T_JSON, "w", encoding="utf-8") as f:
        json.dump(titles, f, ensure_ascii=False, indent=2)
    with open(S_JSON, "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)

    print("[fix_1600_1122] news.json 回填 %d 条；覆盖表 %d / %d 条" %
          (changed, len(titles), len(summaries)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
