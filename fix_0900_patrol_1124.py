# -*- coding: utf-8 -*-
"""2026-11-24 09:00 例行巡检：定稿本轮新增 2 条 NLLB 机翻硬伤。

沙箱 resume 后 09:20 首轮自动抓取新增 2 条，均含明显硬伤：
1) Unite.AI「Supertake」误作「超级公司」，「Ex-Coinbase AI Leaders」误作「前代币库 AI 领导者」，
   「seed round」表述生硬；
2) Unite.AI「GridAI」误作「格里达伊」，「Pronghorn Acquisition」误作「长角收购」，
   「Wyoming AI Power Buildout」误作「怀俄明州人工智能发电建设」。

覆盖三层：news.json 回填 + JSON 覆盖表 + 代码层 manual_overrides.py（regen）。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

FIX = {
    "Supertake Raises $20M Seed, Adds Ex-Coinbase AI Leaders as CEO and CTO": (
        "Supertake 完成 2000 万美元种子轮融资，延揽两名前 Coinbase AI 负责人出任 CEO 与 CTO",
        "Supertake 联合创始人 Michael Mignano 于 2026 年 11 月 23 日宣布，这家 AI 投资初创公司已完成由 Adjacent 领投的 2000 万美元种子轮融资；Lincoln Murr 出任首席执行官，John Peterson 出任首席技术官，两人同时加入成为联合创始人。Murr 此前在 Coinbase 领导 AI 产品，Peterson 负责工程；他们的过往成果包括 x402、Coinbase Advisor、面向智能体的 Coinbase（Coinbase for Agents）以及智能体钱包。",
    ),
    "GridAI Closes Pronghorn Acquisition for Wyoming AI Power Buildout": (
        "GridAI 完成对 Pronghorn 的收购，推进怀俄明州 AI 数据中心电力建设",
        "GridAI Technologies 于 2026 年 11 月 23 日宣布，已完成对 Pronghorn Resources 的全股票收购，由此在怀俄明州粉河盆地（Powder River Basin）获得一项在产天然气业务，用于其规划中的 AI 数据中心电力平台。公司目标是在 2027 年实现首批 300 兆瓦专属电力供应。此次交易交割还使 GridAI 依据与 1st American Nuclear Co.（FANCO）的合资协议，获得怀俄明州范围内的独家经营权。",
    ),
}


def main():
    db = json.load(open(DATA, encoding="utf-8"))
    items = db["items"] if isinstance(db, dict) else db
    titles = json.load(open(T_JSON, encoding="utf-8"))
    summaries = json.load(open(S_JSON, encoding="utf-8"))

    changed = added_t = added_s = 0
    for it in items:
        en = (it.get("title") or "").strip()
        if en not in FIX:
            continue
        title_zh, summary_zh = FIX[en]
        it["title_zh"] = title_zh
        it["summary_zh"] = summary_zh
        it["translated"] = True
        it["method"] = "nllb+manual"
        changed += 1
        print("fixed:", it.get("date"), it.get("time"), en[:55])
        if titles.get(en) != title_zh:
            titles[en] = title_zh
            added_t += 1
        if summaries.get(en) != summary_zh:
            summaries[en] = summary_zh
            added_s += 1

    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    with open(T_JSON, "w", encoding="utf-8") as f:
        json.dump(titles, f, ensure_ascii=False, indent=2)
    with open(S_JSON, "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)

    print("[fix_0900_1124] news.json 回填 %d 条；标题定稿 %d / 摘要定稿 %d" %
          (changed, added_t, added_s))
    print("[fix_0900_1124] 覆盖表 %d / %d 条" % (len(titles), len(summaries)))
    return 0 if changed == len(FIX) else 1


if __name__ == "__main__":
    raise SystemExit(main())
