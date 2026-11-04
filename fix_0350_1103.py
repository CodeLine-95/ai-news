# -*- coding: utf-8 -*-
"""2026-11-03 03:50 巡检：修复 03:35 周期新抓取/回补条目中的 3 条译文缺陷。

A) Unite.AI 03:21 —— Anthropic Launches Message Threads Beta for Long-Running Agents
   1) 标题「Anthropic」被音译替换成「人类发射」——Anthropic 是公司名，
      而 Launches（推出）被译成「发射」，标题因此完全不可读。
   2) 摘要「intended for active sessions where latency matters」
      译成「延迟重要的活跃会议」——latency（延迟）在此指「时延敏感」，
      不是「重要」；active sessions 也不是「会议」。
   3)「computer-use agents whose screenshots remain with the thread」
      译成「其截图仍然与线程保持」——中文语序与用词均不通。

B) TechCrunch 03:19 —— New York Times and other outlets sue web browser Brave
   1) 标题「over alleged content scraping」被截断成「因涉嫌的内容除」，
      「除」为无意义残字，且信息缺失。
   2) 摘要「scraping the outlet's copyrighted [content] and unlawfully
      distributing it」被译成「删除了其版权保护的网站」——
      scrape（抓取）错译为「删除」，copyrighted 被错配为「网站」。

C) OpenAI 08:00 —— Qodo builds context into AI code review with Codex
   1) 标题「builds context into」译成「构建了文本」，context 错译为「文本」，
      句意崩塌。
   2) 摘要「catch P0 issues across repositories before opening a pull request」
      译成「在打开拉取请求之前在存储库中捕获 P0 问题」——「存储库」
      应为「代码仓库」。

D) 附带修正：TechCrunch 11-01 10:22「Data centers are now a midterm issue,
   even in Brooklyn」标题把 Brooklyn 误作「布鲁克林」（应为「布鲁克林区」），
   摘要「每一场对话都回到了人工智能和数据中心」漏译「与政治」。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

TITLE_FIX = {
    "Anthropic Launches Message Threads Beta for Long-Running Agents":
        "Anthropic 推出消息线程 Beta，面向长时运行的智能体",
    "New York Times and other outlets sue web browser Brave over alleged content scraping":
        "《纽约时报》等媒体起诉隐私浏览器 Brave，指其涉嫌抓取内容",
    "Qodo builds context into AI code review with Codex":
        "Qodo 将上下文引入基于 Codex 的 AI 代码审查",
    "Data centers are now a midterm issue, even in Brooklyn":
        "数据中心如今已成为中期选举议题，布鲁克林区也不例外",
}

SUMMARY_FIX = {
    "Anthropic Launches Message Threads Beta for Long-Running Agents":
        "2026 年 11 月 2 日，Anthropic 推出消息线程（message threads）公测，"
        "Claude 平台上的 Messages API 应用在完成首次全量对话请求后，"
        "后续只需发送新增消息。"
        "该功能面向对时延敏感的活跃会话场景，"
        "包括长时间运行的编码智能体、截图需随会话保留的计算机使用智能体，"
        "以及文档与图像密集型的工作流。",
    "New York Times and other outlets sue web browser Brave over alleged content scraping":
        "《纽约时报》起诉以隐私保护为卖点的浏览器公司 Brave，"
        "指其未经授权抓取该报受版权保护的内容，"
        "并非法分发给自家客户，其中包括 Anthropic 和 Perplexity。",
    "Qodo builds context into AI code review with Codex":
        "Qodo 将公司内部知识与编码规范引入 Codex，"
        "帮助开发者在提交拉取请求之前，就能在各个代码仓库中捕获 P0 级问题。",
    "Data centers are now a midterm issue, even in Brooklyn":
        "在选举日前五天举行的布鲁克林区中期选举集会上，"
        "从议员之间激烈的交锋，到围绕民主党的辩论，"
        "几乎每一场对话都绕回了人工智能与数据中心这一议题。",
}


def main():
    with open(os.path.join(DATA, "news.json"), encoding="utf-8") as f:
        db = json.load(f)
    items = db["items"] if isinstance(db, dict) else db

    hit_t = hit_s = 0
    for it in items:
        t = it.get("title", "")
        if t in TITLE_FIX:
            it["title_zh"] = TITLE_FIX[t]
            it["translated"] = True
            it["method"] = "nllb+manual"
            hit_t += 1
            print("fix title:", it["date"], it["time"], it["source"], "|", t[:48])
        if t in SUMMARY_FIX:
            it["summary_zh"] = SUMMARY_FIX[t]
            it["translated"] = True
            it["method"] = "nllb+manual"
            hit_s += 1
            print("fix summary:", it["date"], it["time"], it["source"])

    with open(os.path.join(DATA, "news.json"), "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    for name, fix in (("titles_override.json", TITLE_FIX),
                      ("summaries_override.json", SUMMARY_FIX)):
        path = os.path.join(DATA, name)
        cur = {}
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                cur = json.load(f)
        cur.update(fix)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cur, f, ensure_ascii=False, indent=2)

    print("fixed titles:", hit_t, "/", len(TITLE_FIX))
    print("fixed summaries:", hit_s, "/", len(SUMMARY_FIX))


if __name__ == "__main__":
    main()
