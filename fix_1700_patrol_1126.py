# -*- coding: utf-8 -*-
"""17:00 例行巡检：定稿 12:32 Unite.AI 的 RoboSense 条目机翻腔。

原文：RoboSense LiDAR Sales Surge as Robotics and AI Sensing Expand
问题：
- 标题「销售升」为 NLLB 截断，完整语义应为「销量激增」；
  "AI Sensing" 宜译「AI 感知」，而非「人工智能传感的扩大」。
- 摘要 "a separate sensing development" 被误译为「一个独立的感觉发展」，
  "reported" 宜译「披露/报告称」，数字与单位需补空格。

按项目既有模式回填 news.json + JSON 覆盖表，再由
scripts/regen_overrides.py 同步到代码层 manual_overrides.py。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

FIX = {
    "RoboSense LiDAR Sales Surge as Robotics and AI Sensing Expand": (
        "机器人与 AI 感知需求扩大，RoboSense 激光雷达销量激增",
        "RoboSense 于 2026 年 11 月 25 日披露：2026 年第三季度未经审计营收同比增长 65.2%，达 6.727 亿元人民币；激光雷达销量同比增长 210.1%，约 57.55 万台。其 Space Camera 产品也进入多家全球 AI 公司的供应链，成为激光雷达出货增长之外的另一项感知业务进展。",
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
    for it in items:
        en = it.get("title") or ""
        if en not in FIX:
            continue
        title_zh, summary_zh = FIX[en]
        if it.get("title_zh") != title_zh:
            it["title_zh"] = title_zh
            it["translated"] = True
            it["method"] = "nllb+manual"
            changed += 1
            print("[fix] title:", en[:60], "->", title_zh)
        if it.get("summary_zh") != summary_zh:
            it["summary_zh"] = summary_zh
            it["translated"] = True
            it["method"] = "nllb+manual"
            changed += 1
            print("[fix] summary:", en[:60])
        tov[en] = title_zh
        sov[en] = summary_zh

    json.dump(tov, open(tpath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(sov, open(spath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(db, open(os.path.join(DATA, "news.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("[fix] 变更 %d 处 | 覆盖表 标题 %d 条 / 摘要 %d 条"
          % (changed, len(tov), len(sov)))


if __name__ == "__main__":
    main()
