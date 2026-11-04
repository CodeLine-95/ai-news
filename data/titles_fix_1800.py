"""2026-11-01 18:00 例行巡检 —— 人工核对标题覆盖表。

本轮定位到两类标题缺陷：

1) **「代理」直译残留**：离线模型把 agent 一律译成「代理」，
   组合词（QA 代理 / 浏览器代理 / 个人代理权 / 代理工具…）无法靠
   通用规则穷举，故对受影响条目标题逐条人工定稿。
2) **标题语义走样**：如「获得新模式」（New Models 实为新机型）、
   「AI,ML」（应为 AI、ML）、句末多余句点等。

键为英文原标题（与 data/titles_override.json 保持同一约定）。
"""

TITLE_OVERRIDES = {
    # ---- 「代理」→「智能体」类 ----
    "Bug0 Releases QA Agent to Automate Regression Testing with Cached Playwright Replays":
        "Bug0 发布 QA 智能体，用缓存的 Playwright 重放自动化回归测试",
    "An AI Agent Injected Drugs Into a Live Mouse’s Brain":
        "一个 AI 智能体向活体小鼠的大脑注入了药物",
    "GPT-6.1 Sol helps CodeRabbit strengthen security across complex codebases":
        "GPT-6.1 Sol 帮助 CodeRabbit 强化复杂代码库的安全性",
    "Thin, Light and Built for Everything: NVIDIA RTX Spark Windows Laptops Gain New Models, Agent Tools and Games":
        "轻薄全能：NVIDIA RTX Spark Windows 笔记本新增机型、智能体工具与游戏",
    "AI Agents vs. Copilots vs. Workflows: What’s the Difference?":
        "AI 智能体 vs. Copilot vs. 工作流：区别是什么？",

    # ---- 标题语义走样类 ----
    # "New Models" 指新增机型（笔记本型号），不是「获得新模式」。
    # 另：原文标题尾部无句点，中文标题不应保留句号。
    "TBC Launches Mischief, a Neuron-Derived AI Video Model Built on Wan 2.2":
        "TBC 发布 Mischief：基于 Wan 2.2 的神经元衍生 AI 视频模型",
    # "AI, ML" 在中文里应拆成顿号，避免读成一个词。
    "Article: InfoQ AI, ML and Data Engineering Trends Report - 2026":
        "文章：InfoQ AI、ML 与数据工程趋势报告 2026",
    "Podcast: AI, ML, and Data Engineering InfoQ Trends Report 2026":
        "播客：InfoQ AI、ML 与数据工程趋势报告 2026",
    # "frontier AI model" 此前被译成「新型 AI 模型」，丢失「前沿」义。
    "Google announces Gemini 4 Carbon, its latest frontier AI model that you can't use":
        "Google 发布 Gemini 4 Carbon：最新前沿 AI 模型，但你暂时还用不了",
    # "AI training preferences" 中的 training 是「训练」而非「培训」。
    "Making it easier for websites to express AI training preferences":
        "让网站更容易表达 AI 训练偏好",
    # 「midterms」指中期选举，「revolt」在此是选民的强烈反弹。
    "Maine’s data center revolt will decide who controls the Senate":
        "缅因州的数据中心反弹潮将决定参议院归属",
    # "Edge AI for Smart Cities" 的主语是 Edge AI，不是「智慧城市」。
    "Edge AI for Smart Cities: From Insight to Cognitive Action":
        "面向智慧城市的边缘 AI：从洞察走向认知行动",
    # "keep humans in the loop" 是 AI 治理的固定说法「人在回路中」，
    # 译成「人类循环中」会让人误解为循环往复。
    "Attempts to Keep Humans in the AI Loop May Actually Push Them Out":
        "试图把人类留在回路中，实际却可能把人挤出回路",
}
