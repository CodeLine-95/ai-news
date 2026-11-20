# -*- coding: utf-8 -*-
"""09:00 例行巡检（2026-11-20）：人工定稿本轮 NLLB 机翻硬伤（3 条），回填 news.json 并写入三层覆盖表。

键为英文原标题的关键词片段（规避弯引号精确匹配问题），写入时以数据中的真实英文标题为键。
写入 JSON 覆盖表后由 scripts/regen_overrides.py 同步到代码层 manual_overrides.py。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

# 英文原标题关键词片段 -> (定稿中文标题, 定稿中文摘要)
FIX = {
    "Sparky AI Usage Jumps": (
        "沃尔玛上调全年业绩展望，AI 购物助手 Sparky 使用量飙升 129%",
        "沃尔玛在 2026 年 11 月 19 日第三季度营收增长 5.2% 至 1888 亿美元后，上调了全年销售与利润展望。这家零售商在财报电话会上表示，其 AI 购物助手 Sparky 在美国的用量同比增长 129%，不过受投资结果由盈转亏影响，GAAP 每股收益降至 0.62 美元。首席执行官约翰·弗纳（John Furner）表示，随着顾客发现更多商品，与 Sparky 相关的购物篮金额增长了 40%，Sparky 也在持续增加功能并拓展市场。",
    ),
    "Apple may be developing its own AI agent": (
        "苹果或正研发可操控用户 Mac 的自家 AI 智能体",
        "这家 iPhone 制造商似乎正在打造能够与 Meta Muse、Instinct、Claude 和 OpenAI Dots 等产品竞争的 AI 智能体。",
    ),
    "7 founders cashed out": (
        "Anthropic 7 位创始人在创纪录 IPO 中套现近 20 亿美元",
        "在上调至每股 83 美元的 IPO 定价下，Anthropic 的七位创始人每人套现约 2.8 亿美元，而公司本身则募得近 1050 亿美元。",
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
        key = next((k for k in FIX if k in en), None)
        if not key:
            continue
        title_zh, summary_zh = FIX[key]
        if it.get("title_zh") != title_zh:
            it["title_zh"] = title_zh
            it["translated"] = True
            it["method"] = "nllb+manual"
            changed += 1
            print("[fix] title:", en[:55], "->", title_zh)
        if it.get("summary_zh") != summary_zh:
            it["summary_zh"] = summary_zh
            print("[fix]  summary:", en[:55])
        tov[en] = title_zh
        sov[en] = summary_zh

    json.dump(tov, open(tpath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(sov, open(spath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(db, open(os.path.join(DATA, "news.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("[fix] 标题变更:", changed, "| 覆盖表 标题:", len(tov), "摘要:", len(sov))


if __name__ == "__main__":
    main()
