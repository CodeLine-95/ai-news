# -*- coding: utf-8 -*-
"""2026-11-22 23:00 巡检：本轮新增 2 条（22:20 The Decoder / 22:00 Unite.AI×2 中 1 条），
加上 22:00 周期入库但尚未定稿的 2 条 Unite.AI，共 3 条 NLLB 硬伤人工定稿。

  * The Decoder《Perplexity's new Monitor API turns web search ... watchdog》——
    "Perplexity" 被译成「迷」（NLLB 把品牌名当普通词），"watchdog" 译成「监视犬」；
    "filters out unimportant results" 译成「将无关紧要的结果过出来」；
    "stand out from ... interchangeable chatbot business" 译成「脱而出越来越互换的聊天机器人业务」。
  * Unite.AI《monday.com vs. ClickUp: Which Is Better for Managing Work?》——
    "see the launch as a whole" 译成「看到整个启动」（应为「通盘了解发布全局」）；
    "two audiences" 译成「两个观众」（应为「两类用户群」）。
  * Unite.AI《Robotics in 2027: The Winners Will Be Measured in Hours Without Human Help》——
    标题「赢家将在不需要人类的帮助的情况下测量在几个小时内」句式不通；
    "pick / tray / rescued an earlier attempt" 译成「选择 / 重新设置托盘 / 救出之前尝试」。

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
        "044718f9c9dc0f930e5a9aa6fd43da0b",
        "Perplexity 新 Monitor API：把网络搜索从一次性查询变成不间断的监测哨兵",
        "Perplexity 推出 Monitor API：它按计划定时搜索网络，仅在出现相关变化时才通过 webhook 通知智能体，"
        "其自研决策模型会过滤掉不重要的结果。对 Perplexity 而言，该 API 是其更宏观战略的一部分——"
        "借助开发者工具，从日趋同质化的聊天机器人业务中脱颖而出。",
    ),
    (
        "e101e2168da3fc7beac1d9d482b92def",
        "monday.com 对比 ClickUp：哪个更适合管理工作？",
        "项目经理需要通盘掌握整个项目进展，设计师则需要清楚下一项任务、任务简报以及相关讨论。"
        "monday.com 与 ClickUp 都服务这两类用户群，但侧重点不同：monday.com 更适合想要清晰看板与"
        "可复用部门工作流的团队；当任务、文档、聊天和交付细节需要集中在同一处时，我们更推荐 ClickUp。",
    ),
    (
        "19277e0614bb834b1de4c8d073c27e3a",
        "2027 年机器人：赢家将以「无需人工干预的连续运行时长」衡量",
        "机器人完成抓取，观众鼓掌。短视频无法显示的是：重新摆放托盘的工人、挽救上一次失败尝试的远程操作员，"
        "以及机器等待帮助所耗费的小时数。一场演示可以完全真实，却依然无法回答商业上的问题。",
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
