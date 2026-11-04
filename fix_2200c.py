# -*- coding: utf-8 -*-
"""2026-11-02 22:00 例行巡检第二批修复（重启后新抓到的 2 条）。

服务重启后 22:13 那轮又抓到 2 条，其中 2 条译文有硬伤：

1. 「LinearB Launches Agentic Studio to Give Coding Agents Engineering Context」
   → 「工程背景」在软件工程语境里应为「工程上下文」（已加术语规则），
     但标题「以提供编码智能体工程上下文」仍不成句，摘要里
     「可以使用的背景来做决策」也是逐词硬翻 —— 本条人工定稿。
2. 「Uber Builds MCP Gateway to Govern Access to 800+ Servers and 5,000+ AI Agent Tools」
   → 「优步」是 Uber 的音译（已加品牌规则还原为 Uber），
     「MCP 门户」应为「MCP 网关」（已加术语规则），
     但标题「以管理访问…的访问」重复冗长；
     摘要末尾「和响应过。」明显被 NLLB 截断（原文 response filtering），
     且整句语序断裂 —— 本条人工定稿。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

TITLE_FIX = {
    "LinearB Launches Agentic Studio to Give Coding Agents Engineering Context":
        "LinearB 推出 Agentic Studio，为编码智能体提供工程上下文",
    "Uber Builds MCP Gateway to Govern Access to 800+ Servers and 5,000+ AI Agent Tools":
        "Uber 构建 MCP 网关，统一管控 800 多个服务器与 5,000 多个 AI 智能体工具的访问",
}

SUMMARY_FIX = {
    "LinearB Launches Agentic Studio to Give Coding Agents Engineering Context":
        "LinearB 推出 Agentic Studio，把软件交付数据转化为工程负责人和编码智能体"
        "可用于决策的上下文。该平台于 11 月 2 日发布，将自然语言分析与工程上下文层"
        "相结合，覆盖团队用于规划、编写、审查和发布软件的各类工具。"
        "这次发布反映出 AI 辅助开发中一个日益突出的问题："
        "写出更多代码，并不会自动帮组织更快地交付有用的软件。",
    "Uber Builds MCP Gateway to Govern Access to 800+ Servers and 5,000+ AI Agent Tools":
        "Uber 构建了一套 MCP 网关，用于标准化 AI 智能体在 800 多个 MCP 服务器"
        "和 5,000 个工具中发现并调用内部服务的方式。该网关把工具注册与运行时执行"
        "相分离，并包含自动化 API 发现、访问控制、敏感数据脱敏、"
        "通过 Omni MCP 实现的增量式工具发现，以及响应过滤等能力。",
}


def main():
    with open(os.path.join(DATA, "news.json"), encoding="utf-8") as f:
        db = json.load(f)
    items = db["items"] if isinstance(db, dict) else db

    hit = 0
    for it in items:
        t = it.get("title", "")
        if t in TITLE_FIX:
            it["title_zh"] = TITLE_FIX[t]
            it["translated"] = True
            it["method"] = "nllb+manual"
            hit += 1
            print("title fixed:", it["date"], it["time"], it["source"])
        if t in SUMMARY_FIX:
            it["summary_zh"] = SUMMARY_FIX[t]
            it["translated"] = True
            it["method"] = "nllb+manual"

    with open(os.path.join(DATA, "titles_override.json"), encoding="utf-8") as f:
        tov = json.load(f)
    tov.update(TITLE_FIX)
    with open(os.path.join(DATA, "titles_override.json"), "w", encoding="utf-8") as f:
        json.dump(tov, f, ensure_ascii=False, indent=2)

    with open(os.path.join(DATA, "summaries_override.json"), encoding="utf-8") as f:
        sov = json.load(f)
    sov.update(SUMMARY_FIX)
    with open(os.path.join(DATA, "summaries_override.json"), "w", encoding="utf-8") as f:
        json.dump(sov, f, ensure_ascii=False, indent=2)

    with open(os.path.join(DATA, "news.json"), "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    print("fixed items:", hit, "/ expected", len(TITLE_FIX))


if __name__ == "__main__":
    main()
