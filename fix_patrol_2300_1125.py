# -*- coding: utf-8 -*-
"""2026-11-25 23:00 例行巡检：定稿本轮 8 条新增资讯的 NLLB 生硬/错译译文。"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")
NEWS = os.path.join(BASE, "data", "news.json")

FIXES = {
    "Amazon and Meta reportedly in talks to lift blockade on AI agent Muse": (
        "据报道，Amazon 与 Meta 正就解除对 AI 智能体 Muse 的封锁进行谈判",
        "Amazon 与 Meta 正在讨论一项潜在协议，以结束对 Muse 长达两个月的封锁。",
    ),
    "Amazon is reportedly in talks to end Muse AI shopping block": (
        "据报道，Amazon 正就结束对 Muse AI 购物的封锁进行谈判",
        "据《财富》报道，Amazon 已就允许 Meta 的 Muse AI 智能体在其在线市场购物举行谈判。"
        "这些讨论可能终结 Amazon 对 Muse 的封锁，据报道聚焦于该 AI 智能体推荐的商品类型，"
        "以及对这家电商巨头广告收入的潜在影响。Amazon 担心允许 Muse 进入其网站会损失广告收入，"
        "因为其收入依赖于真实用户在平台上看到广告。",
    ),
    "DoorDash Scales Dispatch 10x While Maintaining 99.99% Peak Availability": (
        "DoorDash 将调度系统扩容 10 倍，同时保持 99.99% 的峰值可用性",
        "DoorDash 重新设计了其实时调度平台，用将协调与计算分离的分布式架构取代了单一优化引擎。"
        "新系统吞吐量提升 10 倍，峰值可用性超过 99.99%。"
        "它还支持混合机器学习推理与多智能体强化学习，以动态优化配送任务分配。",
    ),
    "Vercel Launched Experimental Board to Coordinate Tasks Across Humans and Coding Agents": (
        "Vercel 推出实验性 Board，协调人类与编码智能体之间的任务",
        "Vercel 的实验性 Board 是一个无头消息存储，人类与编码智能体可在其中领取租约任务、"
        "声明依赖关系，并与 Slack、GitHub 和 Linear 同步讨论线程。",
    ),
    "Nexent Capital Launches Fund for Quantum-Ready AI and Energy Assets": (
        "Nexent Capital 设立基金，投向适配量子时代的 AI 与能源资产",
        "Nexent Capital IFSC Private Limited 在 2026 年 11 月 25 日的公告中表示，"
        "已推出 Nexent Capital ADGM Fund I——一只封闭式基金，目标募资 10 亿美元，"
        "投向适配量子时代的 AI 基础设施与先进能源，其中 Tyagi 家族办公室承诺出资 2000 万美元作为锚定投资。"
        "该目标金额并非已募集资金。基金规模上限可扩至 16 亿美元，面向机构投资者与家族办公室，"
        "最低投资额为 50 万美元。",
    ),
    "Mental Health AI in 2027: The Human Handoff Becomes the Deciding Feature": (
        "2027 年心理健康 AI：人工转接成为决定性功能",
        "一段支持性的对话能让难熬的夜晚不那么孤独，但它也可能触及软件无法提供的照护边界。"
        "下一步的质量——用户是否真的能联系到合格的专业人士——可能比助手说话有多自然更重要。"
        "到 2027 年，心理健康 AI 将越来越多地依据对话之外的配套服务来评判。",
    ),
    "Against the Coming Industrial Scale of AI Fraud": (
        "应对即将到来的工业化规模 AI 欺诈",
        "利用 AI 实施网络欺诈很难建模，因为最有意义的测试必须让真实的人在不知情的情况下参与——"
        "这显然违背伦理与法律准则。",
    ),
    "Cloudflare Launches Automatic Website Search for AI Agents": (
        "Cloudflare 推出面向 AI 智能体的网站自动搜索功能",
        "Cloudflare 于 2026 年 11 月 25 日推出 Search for Agents，包括免费版在内的所有套餐均可使用这一测试功能。"
        "如今，通过仪表板开关或 API 控制即可自动完成网站索引，并暴露一个 API 供 AI 智能体在网站自有域名下发现。"
        "此前，客户必须手动创建并配置 AI Search 实例，将其搜索端点与域名集成，并告知智能体索引的位置。",
    ),
}


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    titles, summaries = load(T_JSON), load(S_JSON)
    for key, (title_zh, summary_zh) in FIXES.items():
        titles[key] = title_zh
        summaries[key] = summary_zh
    save(T_JSON, titles)
    save(S_JSON, summaries)

    news = load(NEWS)
    fixed = 0
    for it in news["items"]:
        fix = FIXES.get(it.get("title"))
        if not fix:
            continue
        it["title_zh"], it["summary_zh"] = fix
        it["translated"] = True
        it["method"] = "manual"
        fixed += 1
    save(NEWS, news)
    print("定稿条目数:", fixed)


if __name__ == "__main__":
    main()
