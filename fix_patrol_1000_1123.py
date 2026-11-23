# -*- coding: utf-8 -*-
"""2026-11-23 10:00 巡检：本轮重启后首轮抓取新增 2 条，NLLB 硬伤人工定稿。

  1) TechCrunch《How Notable Capital, GIC, and Baillie Gifford bet big on
     Anthropic before its IPO》——
       * "Notable Capital" 被译成「值得注意的资本」（应为机构名「Notable Capital」）；
       * "bet big on Anthropic" 被译成「对人类进行了大投注」（Anthropic 被误译为「人类」，
         应为「押注 Anthropic」）；
       * "significant backers ... bet billions on ..." 译成「有意义的支持者……投注数十亿美元的人类」，
         语义错乱（应为「重要投资方……向 Anthropic 投入数十亿美元的信心」）。

  2) Unite.AI《XPENG Moves Public NGP Rides Into Its Paris Retail Store》——
       * "Next Generation Pilot (NGP)" 被译成「下一代飞行员」（应为「下一代领航辅助驾驶 NGP」）；
       * "public test rides" 译成「公共测试车程」（应为「公众试乘」）；
       * "localization" 译成「定位化」（应为「本地化」）；
       * 地址 "10 boulevard Gouvion-Saint-Cyr" 译成「10 丁目 ... Boulevard」（应为「古维翁-圣西尔大道 10 号」）。

三层覆盖：news.json 回填 + JSON 覆盖表 + (regen) manual_overrides.py。
"""
import json
import os
import report

BASE = os.path.dirname(os.path.abspath(__file__))
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")
N_JSON = os.path.join(BASE, "data", "news.json")

FIXES = [
    (
        "ca5d392ce76c8966b263d58c05e81b1b",
        "Notable Capital、GIC 与 Baillie Gifford 如何在 Anthropic IPO 前重金押注",
        "三家重要投资方——Notable Capital、GIC 与 Baillie Gifford——分享了是什么让他们确信，"
        "在 Anthropic 上市前向其投入数十亿美元。",
    ),
    (
        "f2fa3481b6d41275f72b75b502b008c0",
        "小鹏将公众 NGP 试乘引入巴黎零售店",
        "小鹏汽车（XPENG）于 2026 年 11 月 22 日宣布，客户可在其巴黎门店预约下一代领航辅助驾驶"
        "（NGP）的公众试乘，将这项技术从临时的车展演示推向真实运营，作为公司持续推进欧洲测试与"
        "本地化的一部分。试乘从位于古维翁-圣西尔大道 10 号的门店出发，覆盖真实城市道路，包括密集"
        "城市交通、复杂路口等具有挑战性的环境。",
    ),
]


def main():
    titles = json.load(open(T_JSON, encoding="utf-8"))
    summaries = json.load(open(S_JSON, encoding="utf-8"))
    news = json.load(open(N_JSON, encoding="utf-8"))
    by_id = {it["id"]: it for it in news["items"]}

    ok = 0
    for iid, zh_t, zh_s in FIXES:
        it = by_id.get(iid)
        if not it:
            print("[WARN] id 未找到:", iid)
            continue
        en = (it.get("title") or "").strip()
        titles[en] = zh_t
        summaries[en] = zh_s
        it["title_zh"] = zh_t
        it["summary_zh"] = zh_s
        it["method"] = "manual"
        it["translated"] = True
        ok += 1
        print("[FIX]", iid[:8], "->", zh_t)

    json.dump(titles, open(T_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(summaries, open(S_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(news, open(N_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("[OK] 定稿 %d 条；覆盖表 标题=%d 摘要=%d；news.json=%d 条"
          % (ok, len(titles), len(summaries), len(news["items"])))

    report.main()
    print("[OK] 报告已重生成")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
