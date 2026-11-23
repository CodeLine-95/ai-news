# -*- coding: utf-8 -*-
"""2026-11-23 13:00 巡检：本轮重启后首轮抓取新增 1 条，NLLB 硬伤人工定稿。

  Unite.AI《Visa CLI Adds Card Verification for AI Agents and OUSD Task Payouts》
       * "Visa" 被译成「维萨」「签证」（应为支付机构名「Visa」，原文保留）；
       * "Visa Crypto Labs" 译成「维萨加密实验室」（应为「Visa 加密实验室」）；
       * "verify AI agents with eligible Visa cards" 译成「验证符合条件的 Visa 卡的 AI 智能体」
         （语义错乱，应为「通过符合条件的 Visa 卡验证 AI 智能体」）；
       * "签证 CLI 产品页面" 明显错译（应为「Visa CLI 产品页面」）。

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
        "47895949acc72afc5b0db37c2995212b",
        "Visa CLI 为 AI 智能体新增卡片验证与 OUSD 任务支付",
        "Visa 加密实验室（Visa Crypto Labs）负责人 Cuy Sheffield 于 2026 年 11 月 22 日宣布推出新版 "
        "Visa CLI——一款智能体钱包，允许美国用户通过符合条件的 Visa 卡验证 AI 智能体，并通过创意任务"
        "与其协作赚取美元稳定币 OUSD。Visa CLI 产品页展示了三步流程：连接现有智能体、通过持卡人的卡片"
        "完成验证、接收任务付款。",
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
