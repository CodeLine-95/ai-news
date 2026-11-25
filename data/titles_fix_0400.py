# -*- coding: utf-8 -*-
"""本轮（04:00 例行巡检）人工核对结果：标题级覆盖。

覆盖标准：
    1) 标题语义与英文原文不符（主语/数字/术语错位）；
    2) 术语规则无法修复的整句崩坏；
    3) 专有名词音译失真、机翻生硬不符合新闻标题习惯。

键为英文原标题（严格一致），值为人工核对后的中文标题。
"""

TITLE_OVERRIDES = {
    "Nvidia GPU Sellers Seek Buyers After U.S. Remote-Access Rule":
        "美国远程访问新规出台后，英伟达 GPU 卖家寻找新买家",
    "Want to buy your kid an AI toy this Christmas? Not in New York":
        "今年圣诞想给孩子买 AI 玩具？纽约禁止了",
    "OpenAI wants companies to trust it with sensitive work by promising not to look at their data":
        "OpenAI 承诺不查看数据，希望企业放心把敏感工作交给它",
    "OpenAI Begins Limited Customer Trials of Alpha Private Inference":
        "OpenAI 启动 Alpha「私密推理」有限客户测试",
    "Ulys Raises $4M to Market Its Investing App and Train AI Models":
        "AI 投资应用 Ulys 融资 400 万美元，用于推广与训练模型",
    "A Stranger Broke Our AI Agent’s Guardrails. Here Is What It Taught Us":
        "一个陌生人突破了我们的 AI 智能体护栏，我们从中吸取了什么",
    "Perplexity Launches Time Machine for Point-in-Time Web Retrieval":
        "Perplexity 推出「时间机器」，支持按历史时间点检索网页",
    "Anthropic’s Dario Amodei calls accusations of surrendering human control to AI ‘absurd’":
        "Anthropic 的达里奥·阿莫迪驳斥「向 AI 交出人类控制权」指控：荒谬",
    "Jensen Huang broke Nvidia’s code of conduct, and his employees may not forget it":
        "黄仁勋违反英伟达行为准则，员工恐怕不会忘记这件事",
    "Three insights you may have missed from theCUBE’s coverage of the Fully Connected event":
        "theCUBE 对 Fully Connected 大会报道中，你可能错过的三点洞察",
}
