# -*- coding: utf-8 -*-
"""2026-11-22 19:00 巡检：本轮新增 2 条 NLLB 机翻硬伤人工定稿。

Marktechpost 两条：
  1) Best Personal AI Agents in 2026 —— 标题「与记忆，安全和成本相比」为
     硬伤（compared on ... 应译为「在……方面的对比」）；摘要「保持内存」
     「该类别开始小」等为生硬机翻，需定稿。
  2) Google AI Previews Tool Retrieval —— 标题「预览在大型工具库的…中检索工具」
     语序错乱；摘要「染色扩展」「互动 API」「0 个额外的循环访问」为硬伤。

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
        "720294235d3936827b46946393150db8",
        "2026 年最佳个人 AI 智能体横评：OpenClaw、Hermes Agent、Gemini Spark 等，在记忆、安全与成本方面的对比",
        "一个个人 AI 智能体可以持续运行，在整个会议过程中保持记忆，并在你的各类应用中发挥作用。你可以在聊天应用里、通过电子邮件或语音与它交谈；即使关闭窗口，它也会继续工作。这一品类起初规模很小：OpenClaw 于 2025 年 11 月以 Clawdbot 之名问世，是 Peter Steinberger 的一个周末项目。12 个月后，Google、OpenAI、Meta 和 Perplexity 都推出了自己的版本。产品分为两大阵营：自托管智能体运行在你自己的机器或服务器上，可使用你选择的任意模型；托管智能体运行在供应商的云虚拟机上，并附带订阅服务。我们的排名方法是对每个智能体在三个维度上评分——一旦智能体掌握了你的收件箱和凭证，这三点就至关重要。记忆：保存哪些内容、存储在哪里，以及你能否阅读、编辑或删除它。安全：默认权限、隔离边界、审批关卡与公开事件日志。成本：订阅或算力开支，以及长期使用下的总体花费。",
    ),
    (
        "683d47f35ae815c78b981be912f39cf3",
        "Google AI 在 Gemini API 中预览工具检索功能，面向大型工具库",
        "Google 推出了 Gemini API 中的工具检索（Tool Retrieval）功能，目前在互动 API（Interactions API）中提供预览。Gemini API 工具检索让智能体能够使用庞大的工具库，而不必在每次提示中都发送每个参数方案——模型只会在任务确实需要某个工具时才加载相应的方案。对于连接了数十个函数或 MCP 服务器的智能体来说，这直接针对一项现实成本：工具定义本身。要点速览：该功能是没有工具数量声明限制的 API 特性；Google 建议对 20 个以内的稳定工具采用静态加载。运行方式既可以是 Google 的服务器（服务器端检索），也可以是你自己的注册表（客户端检索）。API 互动目前仅提供 v1beta 版本。性能方面，检索、方案加载与函数调用在服务器模式下可在一次 API 请求中完成。最佳场景：零额外往返，且服务器端检索无需自建索引。",
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
