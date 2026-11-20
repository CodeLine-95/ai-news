# -*- coding: utf-8 -*-
"""08:00 巡检补充：定稿 3 条历史遗留的 Anthropic IPO 机翻硬伤（"人类 IPO"等）。"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

FIX = {
    "Anthropic IPO Expected to Price Above Preliminary Range": (
        "Anthropic IPO 预计定价高于初步区间",
        "2026 年 11 月 17 日，CNBC 的 David Faber 援引多个消息来源报道称，Anthropic 很可能将其首次公开募股（IPO）定价高于每股 70 至 78 美元的初步区间。这一预期出现在该公司计划于纳斯达克上市之前，并非最终定价决定。消息人士称，Anthropic 计划于 11 月 17 日美东时间下午 4 点结束簿记并锁定总需求。他们要求匿名，因为无权公开发表言论。结束簿记确定了可用于定价的需求情况，但最终定价仍由另行决定。",
    ),
    "Anthropic IPO Could Raise $64 Billion as Orders Reach Six Times": (
        "Anthropic IPO 或募资 640 亿美元，认购订单达六倍",
        "路透社 2026 年 11 月 13 日报道，Anthropic 的首次公开募股在路演第三天已获六倍超额认购，投资者正评估 Claude 能否抵御来自 Google 等竞争对手的挑战。熟悉此次发行的人士称，路演首日结束时订单量约为可售股份的两倍，两天后簿记获六倍超额认购，机构投资者的兴趣超过了 SpaceX 路演初期的水平。",
    ),
    "Anthropic IPO Valuation Expectations Fall After Technology Selloff": (
        "科技股抛售后，Anthropic IPO 估值预期下调",
        "CNBC 2026 年 11 月 6 日报道称，在科技股抛售后，部分 Anthropic 投资者正在下调估值预期，其中一家认为更可能的区间为 1 万亿至 1.25 万亿美元。Anthropic 仍预计在 2026 年 11 月 9 日当周启动 IPO 路演。该区间低于某投资者称为「偏高」的 1.5 万亿美元估值，也低于 Anthropic 近期 2 万亿美元的目标。这一估计可能随市场状况变化。",
    ),
}


def main():
    db = json.load(open(os.path.join(DATA, "news.json"), encoding="utf-8"))
    items = db["items"] if isinstance(db, dict) else db
    tpath = os.path.join(DATA, "titles_override.json")
    spath = os.path.join(DATA, "summaries_override.json")
    tov = json.load(open(tpath, encoding="utf-8"))
    sov = json.load(open(spath, encoding="utf-8"))
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
            print("[fix]", en[:50], "->", title_zh)
        if it.get("summary_zh") != summary_zh:
            it["summary_zh"] = summary_zh
        tov[en] = title_zh
        sov[en] = summary_zh
    json.dump(tov, open(tpath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(sov, open(spath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(db, open(os.path.join(DATA, "news.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("[fix] 变更:", changed, "| 覆盖表 标题:", len(tov), "摘要:", len(sov))


if __name__ == "__main__":
    main()
