# -*- coding: utf-8 -*-
"""2026-11-26 02:00 巡检：定稿本轮整点新增的 7 条 NLLB 机翻。

本轮新增覆盖 Gemini Robotics 2.5、Anthropic 用 Claude 把 Messages API
从 Python 迁移到 Rust、机器人从他人示范中学习、MIGNOW COO 访谈、
各州检察长反对 Character.AI 拍卖用户隐私聊天、FCC 批准 SpaceX 一百万颗
数据中心卫星入轨（含 Starmind 附条件授权）等主题。机翻在专有名词、
数值关系与语义上偏差明显（如 Anthropic 被译成「人文」、dexterous 被译成
「品质」、COO 被译成「首席执行官」），统一以人工定稿回填数据文件与
三层覆盖表。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

FIXES = [
    {
        "title": "DeepMind's Gemini Robotics 2.5 Aims to Make Robots Safer, More Dexterous, and Faster Learners",
        "title_zh": "DeepMind 的 Gemini Robotics 2.5 旨在让机器人更安全、更灵巧、学习更快",
        "summary_zh": (
            "Google DeepMind 推出 Gemini Robotics 2.5——一个视觉-语言-动作（VLA）模型，"
            "旨在提升机器人的灵巧性、可靠性与学习速度，同时使其能在非结构化的真实世界中更安全地运作。"
        ),
    },
    {
        "title": "Anthropic Details Claude-Assisted Rust Migration of Messages API",
        "title_zh": "Anthropic 详解如何借助 Claude 将 Messages API 迁移至 Rust",
        "summary_zh": (
            "Anthropic 于 2026 年 11 月 25 日表示，Claude 智能体帮助其将 Messages API 从 Python 迁移至 Rust，"
            "期间服务未中断，功能开发也未停摆。每次请求的 CPU 与内存占用分别下降约 70% 与 80% 以上，"
            "客户使用 Claude Code 时首个响应 token 的平均等待时间缩短约 20%。"
        ),
    },
    {
        "title": "When One Robot Learns, Can a Thousand Others Follow?",
        "title_zh": "当一个机器人学会，千台机器人能跟着学会吗？",
        "summary_zh": (
            "第一人称视角（自我中心）视频仍是机器人训练数据的重要来源。但研究人员正在超越这一路径，"
            "探索机器人如何从第三人称示范以及其他机器人系统的经验中学习。目标是让机器人通过观察人类与"
            "其他机器来获得新技能。但我们离这一目标还有多远？又有哪些技术挑战仍横亘在前？"
        ),
    },
    {
        "title": "Guilherme Joventino, Co-Founder & COO of MIGNOW – Interview Series",
        "title_zh": "MIGNOW 联合创始人兼首席运营官 Guilherme Joventino——访谈系列",
        "summary_zh": (
            "Guilherme Joventino 是 MIGNOW 的联合创始人兼首席运营官（COO），曾在 Philips、Sandoz 与 Bayer 的"
            "全球 SAP 团队任职。在 MIGNOW，他致力于通过分阶段交付、自动化与持续的系统演进，"
            "让企业现代化更具可预测性，同时保留关键 ERP 环境所需的业务专业能力与问责机制。"
        ),
    },
    {
        "title": "State AGs fight Character AI’s plan to auction off users’ private chats",
        "title_zh": "各州检察长反对 Character.AI 拍卖用户私密聊天记录的计划",
        "summary_zh": (
            "各州检察长表示，拟议中的 Character.ai 破产出售包含来自超过 2100 万个美国账户的敏感个人数据，"
            "其中 210 万个账户注册人为未成年人。"
        ),
    },
    {
        "title": "FCC signs off on SpaceX’s plan to put up to 1 million data center satellites into space",
        "title_zh": "FCC 批准 SpaceX 将多达一百万颗数据中心卫星送入太空的计划",
        "summary_zh": (
            "在周三的公告中，美国联邦通信委员会（FCC）表示，已授权 SpaceX 部署多达一百万颗搭载 AI 芯片的卫星，"
            "作为这家埃隆·马斯克旗下公司「Starmind」计划的一部分。包括 Google 与蓝色起源在内的多家公司也在"
            "探索把 AI 数据中心搬上太空，而这是该机构首次批准完整的 AI 卫星「星座」。FCC 的批准要求 SpaceX "
            "在 2033 年前至少部署一颗卫星，并在 2040 年前达成一百万颗卫星的里程碑。"
        ),
    },
    {
        "title": "FCC Space Bureau Authorizes SpaceX’s Starmind with Conditions",
        "title_zh": "FCC 太空局附条件批准 SpaceX 的 Starmind 计划",
        "summary_zh": (
            "2026 年 11 月 25 日，FCC 太空局授予 Space Exploration Holdings（SpaceX）附条件授权，"
            "推进 Starmind——一个由多达一百万颗卫星组成、作为数据中心运行的近地轨道星座计划，"
            "同时暂缓处理该申请的部分内容。FCC 的公告称，此举是美国首次采取此类行动。"
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
