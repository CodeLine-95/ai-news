# -*- coding: utf-8 -*-
"""16:00 例行巡检：定稿 16:00 轮次新增 2 条的 NLLB 机翻腔。

- 15:14 Unite.AI《Skanska Wins Additional Award for New Georgia Data Center》：
  "award" 在建筑工程语境指「合同/订单」，被误译为「奖项」；
  "Georgia" 是美国佐治亚州，被误译为「格鲁吉亚」。
- 15:19 Unite.AI《GeoIntelX to Apply AI to Angola’s National Geological Archives》：
  品牌名 "GeoIntelX" 被拆成「吉奥 Intel X」；"archives" 宜译为「档案」。

按项目既有模式回填 news.json + JSON 覆盖表，再由
scripts/regen_overrides.py 同步到代码层 manual_overrides.py。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

FIX = {
    "Skanska Wins Additional Award for New Georgia Data Center": (
        "斯坎斯卡获佐治亚州新数据中心追加合同",
        "斯坎斯卡（Skanska）于 2026 年 11 月 26 日宣布，从现有客户处获得一份追加合同，将在美国佐治亚州新建一座 48 兆瓦数据中心。该合同价值约 2.75 亿美元（约合 28 亿瑞典克朗），将计入公司 2026 年第四季度的美国订单。这一分类很关键：公告将已签约的工作计入订单簿，而非把全部金额记为已确认收入。",
    ),
    "GeoIntelX to Apply AI to Angola’s National Geological Archives": (
        "GeoIntelX 将用 AI 处理安哥拉国家地质档案",
        "2026 年 11 月 26 日，GeoIntelX 宣布与安哥拉地质研究所及勘探合作方 Ivanhoe Mines 联手，运用人工智能处理安哥拉跨越一个多世纪的历史地质记录。Ivanhoe Mines 正在资助该平台在安哥拉的落地，包括数字化历史地质图、报告及其他保存在该国地质档案中的实体记录。",
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
            changed += 1
            print("[fix]  summary:", en[:60])
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
