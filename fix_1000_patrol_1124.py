# -*- coding: utf-8 -*-
"""2026-11-24 10:00 例行巡检：定稿本轮新增 2 条 NLLB 机翻硬伤。

沙箱 resume 后 10:07 整点抓取新增 2 条（SiliconANGLE），均含明显硬伤：
1) 「Claude Ship」被误译为「Claude 船」（产品名，应保留 Claude Ship）；
2) 「reported $7.5B」误作「报告为 75 亿美元」（应为「据报 75 亿美元」），
   「sources told Bloomberg」被截成「消息人士告诉博社」（应为「彭博社」），
   「funding round」误作「融资轮回」。

覆盖三层：news.json 回填 + JSON 覆盖表 + 代码层 manual_overrides.py（regen）。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

FIX = {
    "Anthropic’s Claude Ship automates the final stage of the software development pipeline": (
        "Anthropic 推出 Claude Ship，自动化软件开发流程的最后阶段",
        "Anthropic 并不满足于让 Claude 只负责编写新软件。在今日发布的一项新更新中，Claude 现在能够告诉开发人员，它生成的代码何时已准备好投入生产环境。这意味着从代码编写、审查到上线的交接环节可以进一步由智能体自动完成，是 Anthropic 面向软件开发流水线「最后一公里」的又一步布局。",
    ),
    "Amazon acquires key assets of AI startup Decart for reported $7.5B": (
        "据报道，Amazon 以 75 亿美元收购 AI 初创公司 Decart 的关键资产",
        "Amazon.com Inc. 今日宣布，计划聘请 AI 初创公司 Decart.AI Inc. 的技术团队，并收购其核心技术。公司未披露交易条款，但消息人士向彭博社（Bloomberg）透露，Amazon 为此支付约 75 亿美元——这几乎是 Decart 今年 5 月最新一轮融资后估值（据报）的两倍。此次交易延续了科技巨头通过「人才收购」补强 AI 能力的趋势。",
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
        print("fixed:", it.get("date"), it.get("time"), en[:60])
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

    print("[fix_1000_1124] news.json 回填 %d 条；标题定稿 %d / 摘要定稿 %d" %
          (changed, added_t, added_s))
    print("[fix_1000_1124] 覆盖表 %d / %d 条" % (len(titles), len(summaries)))
    return 0 if changed == len(FIX) else 1


if __name__ == "__main__":
    raise SystemExit(main())
