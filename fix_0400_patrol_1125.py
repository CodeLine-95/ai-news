# -*- coding: utf-8 -*-
"""2026-11-25 04:00 巡检：定稿整点新增的 6 条 NLLB 机翻。

本轮新增覆盖 Cognition SWE-2.1、Anthropic MCP 下载量、MIT TangiMap
物理控制、Google DeepMind HFE 一致性基准，以及两条旧时间戳新入库的
OpenAI 条目。机翻在专有名词（Cognition→「认知」、Apple→「果」）、
撇号与语义关系上偏差明显，统一人工定稿，并回填数据文件与三层覆盖表。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

FIXES = [
    {
        "title": "How Intentful uses dots to make more time for growth",
        "title_zh": "Intentful 如何用「点」为增长腾出更多时间",
        "summary_zh": (
            "Marina Petrova 的 dot Aria 可帮助调研网站、撰写提案，"
            "同时主动标记消息并解决问题。"
        ),
    },
    {
        "title": "Searching for distant planets with Astra",
        "title_zh": "用 Astra 搜寻遥远的行星",
        "summary_zh": (
            "看看两位业余天文学家如何利用 Codex 和 Astra，"
            "从 NASA 开普勒与 TESS 太空望远镜的公开数据中寻找潜在系外行星。"
        ),
    },
    {
        "title": "Cognition Releases SWE-2.1 With Major Coding and Cybersecurity Gains",
        "title_zh": "Cognition 发布 SWE-2.1，编程与网络安全能力大幅提升",
        "summary_zh": (
            "Cognition 于 2026 年 11 月 24 日发布 SWE-2.1，"
            "其 Terminal-Bench 4.1 得分达 50.0，较 SWE-2 的 24.2 分大幅提升。"
            "除基础模型外，还推出了由 Cerebras 支持的 Lightning 变体，"
            "以及更宽松的 SWE-2.1 Cyber 版本，正向 Devin Security 推送。"
            "与 SWE-2 一样，新模型基于 Kimi K3 通过纯强化学习训练而成。"
            "Cognition 将编程能力的大幅提升主要归因于针对通用智能和长周期工作流的优化；"
            "其 FrontierCode 2.0 成绩达到 41.3，而 SWE-2 为 24.1。"
            "同一榜单中，Claude Opus 5.5 在 FrontierCode 上取得 47.3、"
            "在 Terminal-Bench 上取得 65.8——尽管 SWE-2.1 较 SWE-2 进步明显，"
            "但在这两项测试中仍落后于该模型。"
        ),
    },
    {
        "title": "Anthropic tops 700 million monthly MCP SDK downloads and expands the protocol for more autonomous AI agents",
        "title_zh": "Anthropic MCP SDK 月下载量突破 7 亿次，并扩展协议以支持更自主的 AI 智能体",
        "summary_zh": (
            "MCP 接口标准发布两年后，Anthropic 宣布其月下载量已超过 7 亿次。"
            "后台任务、向用户追问以及文件上传等新功能，旨在让 Claude 能够更独立地工作。"
        ),
    },
    {
        "title": "Agentic system personalizes physical controls to help users “DJ their art”",
        "title_zh": "智能体系统个性化物理控制，帮助用户「DJ」自己的作品",
        "summary_zh": (
            "2017 年，Apple 从 iPhone 上移除了 Home 键。"
            "用户失去了一个便捷、可触摸的控制方式——这正是更大范围转向数字按钮、旋钮和滑块的一部分，"
            "类似的转变也出现在汽车（如收音机预设和空调）与厨房（如智能冰箱）中。"
            "不过，我们并不能完全抛弃物理控制：它们往往更方便、更高效——"
            "比如你无需看就能使用游戏手柄——有时还更精准，例如用旋钮把音量调到刚刚好。"
            "但实体控制通常被预先设定为执行特定操作，这限制了它的用途。"
            "由 MIT 一名研究生与麻省理工学院计算机科学与人工智能实验室（CSAIL）研究员共同开发的"
            "新系统 TangiMap，帮助把可触摸的控制带回软件之中。"
        ),
    },
    {
        "title": "Google DeepMind’s 544-Prompt HFE Test Exposes LLM Consistency Gaps",
        "title_zh": "Google DeepMind 的 544 题 HFE 测试揭示大模型一致性差距",
        "summary_zh": (
            "2026 年 11 月 24 日，Google DeepMind 在 Kaggle 上推出 Humanity’s First Exam"
            "（人类第一场考试）——一项由 544 个基础文本与图像提示组成的基准测试，"
            "用于检验大语言模型能否稳定一致地回答常规问题，而非只答对一次。"
            "随附的技术报告评估了 18 个前沿及快速档模型。"
        ),
    },
]


def main():
    db = json.load(open(DATA, encoding="utf-8"))
    items = db["items"] if isinstance(db, dict) else db
    titles = json.load(open(T_JSON, encoding="utf-8"))
    summaries = json.load(open(S_JSON, encoding="utf-8"))

    by_title = {fx["title"].strip(): fx for fx in FIXES}
    changed = 0
    for it in items:
        fx = by_title.get((it.get("title") or "").strip())
        if fx:
            it["title_zh"] = fx["title_zh"]
            it["summary_zh"] = fx["summary_zh"]
            it["translated"] = True
            it["method"] = "nllb+manual"
            changed += 1
            print("fixed:", it.get("date"), it.get("time"), it.get("title", "")[:60])

    for fx in FIXES:
        titles[fx["title"]] = fx["title_zh"]
        summaries[fx["title"]] = fx["summary_zh"]

    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    with open(T_JSON, "w", encoding="utf-8") as f:
        json.dump(titles, f, ensure_ascii=False, indent=2)
    with open(S_JSON, "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)

    print("回填条目:", changed)
    assert changed == len(FIXES), "定稿条目数不符：%d != %d" % (changed, len(FIXES))


if __name__ == "__main__":
    main()
