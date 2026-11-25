# -*- coding: utf-8 -*-
"""2026-11-26 01:00 例行巡检：定稿整点新增 6 条 NLLB 错译。

本轮错译集中在术语与语序层面：
- supply chain 标题被译成「下一个瓶是供应链 AI」（漏「颈」、语序颠倒）
- humanoid→「人类化剂/人类型」（应为「人形机器人」）
- background 未翻译直接保留英文
- Amazon/Muse 摘要尾部混入源站推广句（重复标题）
- Callimacus Magic 品牌名被意译为「卡利马库斯魔术」
同引擎重译会复现同类错误，因此沿用人工定稿覆盖表（优先级最高）。
品牌名译法与既有覆盖表保持一致：XPENG→小鹏、humanoid→人形机器人。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")
NEWS = os.path.join(BASE, "data", "news.json")

FIXES = {
    "AI’s Next Bottleneck Is the Supply Chain": (
        "AI 的下一个瓶颈是供应链",
        "当人们谈论 AI 基础设施热潮时，话题通常集中在芯片和数据中心的电力消耗上。这些确实是现实的制约因素，"
        "但它们只是更长链条的末端。每一座新建的 AI 数据中心背后，都有一个由制造商构成的庞大网络："
        "生产机架、机箱、冷却系统、配电设备、连接器、线缆、紧固件、精密加工零件，以及制造这一切所需的工具。",
    ),
    "Callimacus Magic Builds AI Websites That Change With Each Visit": (
        "Callimacus Magic 打造每次访问都不同的 AI 网站",
        "Callimacus Magic 可将现有网站转化为由 AI 编排界面的预览。此次发布把个性化从「页面推荐」推进到「页面本身」。",
    ),
    "XPENG Debuts IRON Humanoid and Outlines Store Training Plan": (
        "小鹏发布 IRON 人形机器人，并公布门店培训计划",
        "2026 年 11 月 25 日，小鹏汽车在广州举办的第八届 AI 日上发布面向汽车与机器人的共享物理 AI 架构，"
        "并公开亮相 IRON——一款拥有 76 个自由度的人形机器人，计划于 2027 年第一季度开始在小鹏零售门店作为助理接受训练。"
        "这套图灵物理 AI 架构（也称 VLA 3.0）将认知、实时决策与物理执行分配到三个相互连接的系统中。",
    ),
    "Amazon and Meta are in talks to end the block on Meta's AI shopping agent Muse in Amazon's online store.": (
        "Amazon 与 Meta 谈判，拟解除对 Meta AI 购物智能体 Muse 在 Amazon 在线商店的封锁",
        "Amazon 与 Meta 正在谈判，希望让 Meta 的 AI 购物智能体 Muse 重返平台——Muse 于今年 9 月被 Amazon 从平台下架。"
        "双方在广告收入以及谁掌控搜索结果上陷入僵局。这一点至关重要：Amazon 的广告业务每年创造 686 亿美元收入，"
        "而 Muse 已占据全部智能体购物订单的 51%。",
    ),
    "Elisa Seghetti, Co-Founder & CEO of Saturn Dynamics – Interview Series": (
        "Saturn Dynamics 联合创始人兼 CEO Elisa Seghetti——访谈系列",
        "Elisa Seghetti 是 Saturn Dynamics 的联合创始人兼 CEO，拥有横跨生物技术、计算化学与企业 AI 的背景。"
        "她此前创立了 AiGot，将工程团队从 3 人扩展到 35 人以上，并与《财富》500 强企业合作制定 AI 战略。"
        "她在 Saturn Dynamics 的工作重点是帮助物理 AI 学会与人类安全、可靠地协同运作。"
        "Saturn Dynamics 开发基于物理的世界模型，面向机器人技术与具身 AI。",
    ),
    "Ars Live recap: Don’t expect military attacks on data centers to stop": (
        "Ars Live 回顾：别指望针对数据中心的军事攻击会停止",
        "无人机袭击数据中心。今年 Amazon 数据中心在中东首次遭到军事攻击，俄罗斯与乌克兰也对彼此的数据中心"
        "发动了前所未有的密集无人机打击。为探讨这类攻击对所有现代社会所依赖的云服务的未来意味着什么，Ars 举办了一场线上讨论。"
        "在与 Ars Technica 科技记者 Jeremy Hsu 的对话中，英国皇家联合军种研究所（RUSI）的 Joseph Jarnecki "
        "首先谈及为何公共云数据中心在 2026 年伊朗战争与俄罗斯持续全面入侵乌克兰期间日益成为军事目标："
        "「我们看到，人们越来越认识到并接受两用性这一事实——尤其是在公共云领域，但整个私有云数据中心同样如此。」",
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
