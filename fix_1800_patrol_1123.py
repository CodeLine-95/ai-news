# -*- coding: utf-8 -*-
"""2026-11-23 18:00 例行巡检：定稿本轮新增 2 条 NLLB 机翻硬伤。

1) Unite.AI《Coprod Raises $6M Pre-Seed to Bring Modular Robot Hardware
   to Market》(17:18)：NLLB 把公司名 coprod 误译为「科普罗德」、
   pre-seed 误作「预售资金」、prototyping facility 误作「原型设备」。
2) Unite.AI《Agon Raises $70M Series A at $450M Valuation to Build
   Defence AI Lab》(17:29)：金额错译 10 倍——$70M→「7 亿美元」、
   $450M→「4 亿美元」；投资机构 Northzone 误作「北区」；
   「种子轮流」语句不通。按原文逐项定稿。

覆盖三层：news.json 回填 + JSON 覆盖表 + MANUAL_OVERRIDES（regen）。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

TITLE_FIX = {
    "Coprod Raises $6M Pre-Seed to Bring Modular Robot Hardware to Market":
        "Coprod 完成 600 万美元种子前轮融资，将模块化机器人硬件推向市场",
    "Agon Raises $70M Series A at $450M Valuation to Build Defence AI Lab":
        "Agon 以 4.5 亿美元估值完成 7000 万美元 A 轮融资，筹建国防 AI 实验室",
}

SUMMARY_FIX = {
    "Coprod Raises $6M Pre-Seed to Bring Modular Robot Hardware to Market": (
        "瑞士机器人初创公司 Coprod 于 2026 年 11 月 23 日宣布完成 600 万美元种子前轮"
        "（pre-seed）融资，用于资助其首条商业化组件产品线以及在洛桑建立的原型制造设施。"
        "该公司正在开发模块化硬件与软件，旨在缩短为特定任务制造机器人所需的时间并降低成本。"
    ),
    "Agon Raises $70M Series A at $450M Valuation to Build Defence AI Lab": (
        "Agon 于 2026 年 11 月 23 日宣布，已以 4.5 亿美元估值完成 7000 万美元 A 轮融资。"
        "本轮由 Northzone 领投，资金将用于支持该公司建立一所欧洲国防 AI 实验室，"
        "提供主权基础设施与基础模型。此轮融资使 Agon 累计融资额达到 1 亿美元——"
        "此前该公司已于 2026 年初完成 3000 万美元种子轮。现有投资方 Lakestar、XYZ、"
        "Lux Capital、Global Founders Capital 与 Speedinvest 参与本轮。"
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

    print("[fix_1800_1123] news.json 回填 %d 条；标题定稿 %d / 摘要定稿 %d" %
          (changed, added_t, added_s))
    print("[fix_1800_1123] 覆盖表 %d / %d 条" % (len(titles), len(summaries)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
