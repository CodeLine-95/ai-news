# -*- coding: utf-8 -*-
"""22:00 例行巡检：定稿本轮 NLLB 新增条目的机翻误译。

22:00 整点抓取净新增 2 条：
- The Decoder / FCC 批准 SpaceX 部署 Starmind 卫星：Starmind 专有名词
  前后译成「星脑」「星心」两个名字，需统一为原文品牌名 Starmind；
  orbital data centers 译为「轨道数据中心」。
- Unite.AI / SIMMTECH 两项永久债券：SIMMTECH 被音译为「辛姆泰克」
  且摘要里写成「SIMMTECHs」；KRW（韩元）被误译为「克罗瓦」；
  bond-with-warrants 被译为「保证券/证券」，应为「附认股权证债券」；
  unsecured 应为「无担保」，detachable 相关表述需准确。

按项目既有模式回填 news.json + JSON 覆盖表，再由
scripts/regen_overrides.py 同步到代码层 manual_overrides.py。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

FIX = {
    "FCC clears SpaceX to deploy up to 1 million Starmind satellites for orbital AI data centers by 2040": (
        "美国联邦通信委员会批准 SpaceX 到 2040 年部署多达 100 万颗 Starmind 卫星，用于轨道 AI 数据中心",
        "美国联邦通信委员会（FCC）已批准 SpaceX 部署多达 100 万颗 Starmind 卫星，将其作为轨道数据中心处理 AI 数据。SpaceX 计划于 2027 年首次发射，整个星座预计在 2040 年前投入运行。Google 与蓝色起源也在推进太空 AI 基础设施，但波士顿咨询集团估计，目前太空数据中心的成本仍将远高于地面数据中心。",
    ),
    "SIMMTECH Approves Two KRW 150B Perpetual Bonds for AI Substrate Expansion": (
        "SIMMTECH 批准两项 1500 亿韩元永久债券，用于扩产 AI 基板",
        "SIMMTECH 董事会于 2026 年 11 月 26 日批准发行两项各 1500 亿韩元的私人永久债券，用于扩大面向 AI 的 SOCAMM 模组基板与高层 MSAP 基板产能。相关可转换债券及附认股权证债券决议已通过韩国 DART 公司披露系统提交。第 11 期证券为无担保的私人永久可转换债券；第 12 期为无担保、不可分离的私人永久债券。",
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
    matched = set()
    for it in items:
        en = it.get("title") or ""
        if en not in FIX:
            continue
        matched.add(en)
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

    missing = set(FIX) - matched
    if missing:
        print("[warn] 未匹配到条目:", missing)

    json.dump(tov, open(tpath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(sov, open(spath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(db, open(os.path.join(DATA, "news.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("[fix] 变更 %d 处 | 覆盖表 标题 %d 条 / 摘要 %d 条"
          % (changed, len(tov), len(sov)))


if __name__ == "__main__":
    main()
