# -*- coding: utf-8 -*-
"""2026-11-25 02:00 巡检：定稿整点新增的 15 条 NLLB 机翻。

本轮新增覆盖 Meta Muse 进入 Instagram DMs、OpenAI Noam Brown 劝退学生、
黄仁勋复职后道歉、GPT-6.2 Astra 破解历史谜题、Tidal 下架 AI 音乐、
Anorak 视频加速、Epochal Time Portal、Google Workspace 智能体接口、
Cloudera 数字主权等主题。机翻在专有名词、数值与语义关系上偏差明显，
统一以人工定稿回填数据文件与三层覆盖表。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

FIXES = [
    {
        "title": "Meta brings its Muse AI assistant directly into Instagram DMs",
        "title_zh": "Meta 将 Muse AI 助手直接接入 Instagram 私信",
        "summary_zh": (
            "新的集成让用户与 AI 智能体互动时，无需在 Instagram 与 Muse 应用之间来回切换。"
        ),
    },
    {
        "title": "OpenAI o1 co-creator Noam Brown urges promising students to drop out as AI enters a \"very steep rate of progress\"",
        "title_zh": "OpenAI o1 共同缔造者 Noam Brown 敦促优秀学生退学，称 AI 正进入「进展极其迅猛」阶段",
        "summary_zh": (
            "OpenAI 研究员 Noam Brown 正敦促有潜力的学生退学，称「现在不是袖手旁观的好时机」。"
            "这位 o1 的共同缔造者表示，AI 仍处于「半人马时代」，在规划与自我纠错方面仍有困难，"
            "但他预计很快会出现「非常陡峭的进步速度」。Brown 称，语言模型已经被用于构建下一代模型。"
        ),
    },
    {
        "title": "Jensen Huang Apologizes to Nvidia Employees in First All-Hands Since His Return",
        "title_zh": "黄仁勋复职后首次全员大会上向 NVIDIA 员工道歉",
        "summary_zh": (
            "这位重新上任的 NVIDIA CEO 承认违反了公司的行为准则，"
            "并说自己犯下了「非常严重的个人错误」。"
        ),
    },
    {
        "title": "GPT 6.2 Astra Solves a Historical Mystery",
        "title_zh": "GPT 6.2 Astra 破解一桩历史谜题",
        "summary_zh": (
            "历史学教授 Mark Humphries 分享了一个用 GPT-6.2 Astra 做历史研究的有趣案例："
            "只需极少的提示，该模型就能自主识别出耶鲁大学拜内克图书馆收藏的一本 1808 年"
            "匿名速写簿的作者。它仅用 22 分钟，借助公开的一手与二手资料就完成了这一工作。"
            "为此，它在报纸档案中发现了一份鲜为人知的资料，并预测若对其加以查验便能证实自己的"
            "假设——结果确实如此。不仅如此，这份新资料本身就是一项重要发现，"
            "会引起加拿大研究者与毛皮贸易史学者的浓厚兴趣。"
        ),
    },
    {
        "title": "Tidal announces ban on AI-generated music; 27 million tracks will be deleted",
        "title_zh": "Tidal 宣布封禁 AI 生成音乐，将删除 2700 万首曲目",
        "summary_zh": (
            "大多数流媒体音乐服务商都选择对平台上的 AI 生成内容进行标注，Tidal 此前也是如此。"
            "但该公司即将采取更强硬的立场。Tidal 宣布，由于 AI 音乐对人类艺术家造成伤害，"
            "未来数周将全面封禁此类音乐。Tidal 于 2026 年 7 月首次推出 AI 政策，"
            "包括对完全由 AI 创作的歌曲进行标注并取消变现。然而这并不足以遏制 AI 垃圾内容的泛滥。"
            "Tidal 称，过去 90 天里，新上传内容中有 43% 完全由 AI 生成；"
            "11 月 6 日，新上传内容中 AI 生成比例高达 60%。目前 Tidal 上有 2700 万首被标注为 AI 的"
            "曲目，显然都是近两年添加的，占其曲库总量的 6.3%。12 月 9 日，Tidal 将删除所有这些歌曲。"
        ),
    },
    {
        "title": "Anorak Speeds Up Reference-Guided AI Video Without Retraining the Model",
        "title_zh": "Anorak 无需重训模型即可加速参考引导式 AI 视频生成",
        "summary_zh": (
            "Anorak 的 PCRG 技术减少了参考引导视频生成中的重复计算，"
            "在 MiniMax-H3 上的测试中实现了 1.49 至 1.57 倍的加速。视频生成模型在遵循参考素材时，"
            "可能会把相当一部分时间花在几乎不变的细节上：空荡的天空、平坦的墙壁或一段道路。"
            "Anorak 在 11 月 24 日发布消息称，其 AI 实验室开发出一种减少此类重复工作的方法。"
            "团队研究预印本显示，该方法在两个基准上将端到端生成速度提升约 1.5 至 1.6 倍，"
            "且无需重新训练底层模型。另一项实验中，该方法与其他优化手段结合后，速度提升超过两倍。"
        ),
    },
    {
        "title": "Interhuman AI Tests How Models Read Social Signals Beyond the Transcript",
        "title_zh": "Interhuman AI 推出 Social Signal Bench，测试模型能否读懂文字记录之外的社交信号",
        "summary_zh": (
            "Social Signal Bench 用于测试多模态模型如何解读音频与视频中可观察到的线索，"
            "同时不把人类的判断视为绝对标准。"
        ),
    },
    {
        "title": "Epochal Launches Time Portal to Test Forecasting AI on Web History",
        "title_zh": "Epochal 推出 Time Portal，用网页历史测试 AI 的预测能力",
        "summary_zh": (
            "新成立的 AI 公司 Epochal 于 2026 年 11 月 24 日亮相，并发布 Time Portal——"
            "一个面向 AI 智能体的「时间点」网页环境。该公司称，这一档案库涵盖超过 1 万亿个页面，"
            "旨在训练系统在不接触未来结果的前提下进行预测。公布的团队成员包括 xAI 创始团队的"
            "核心成员 Guodong Zhang、Zihang Dai 与 Manuel Kroiss，以及 Alex Bocharoff 和 Frank Luan。"
            "Time Portal 是 Epochal 的首款产品，仅用 90 天便打造完成。"
        ),
    },
    {
        "title": "Leash Biosciences Raises $11M to Build Scientific AI Training Worlds",
        "title_zh": "Leash Biosciences 融资 1100 万美元，构建科学 AI 训练环境",
        "summary_zh": (
            "Leash Biosciences 于 2026 年 11 月 24 日宣布完成 1100 万美元融资，"
            "用于基于湿实验室测量数据构建科学 AI 训练环境。Innovation Endeavors 与 Insight Partners "
            "共同参与投资，支持 Leash 让 AI 智能体从物理实验中获得可复用的经验。"
            "Innovation Endeavors 称，Leash 的收藏已涵盖 630 万个分子、440 亿条实验测量数据和"
            "1200 多种蛋白质。"
        ),
    },
    {
        "title": "Google Requires Workspace AI Agents to Use Managed Interfaces",
        "title_zh": "Google 要求 Workspace AI 智能体使用受管接口",
        "summary_zh": (
            "Google 于 2026 年 11 月 24 日宣布，其 Workspace 模型上下文协议（MCP）服务器与"
            "Workspace 命令行界面（CLI）已正式可用，同时出台规则，要求 AI 智能体使用这些接口"
            "而非现有的 REST API。技术层面的强制执行将从 2027 年 2 月 1 日开始。"
            "Google 表示，Workspace API 每月处理超过 2.8 万亿次调用，"
            "公开的 Drive API 流量已是 2022 年的两倍多。"
        ),
    },
    {
        "title": "Meta Adds Muse AI Agent to Instagram DMs for Saved-Content Planning",
        "title_zh": "Meta 将 Muse AI 智能体加入 Instagram 私信，用于规划收藏内容",
        "summary_zh": (
            "Meta 于 2026 年 11 月 24 日将其 Muse 个人 AI 智能体加入 Instagram 私信，"
            "并通过 Muse 已认证的 Instagram 账号宣布，用户可以直接给它发私信，"
            "把「收藏内容变成真正的计划」，示例是一次一直想去的旅行。"
            "此举让 Muse 在 Instagram 内部获得了一个对话入口，与其现有的其他聊天界面并行。"
        ),
    },
    {
        "title": "Rahul Pangam, Co-Founder & CEO of RapidCanvas – Interview Series",
        "title_zh": "RapidCanvas 联合创始人兼 CEO Rahul Pangam 访谈",
        "summary_zh": (
            "Rahul Pangam 是 RapidCanvas 的联合创始人兼 CEO，"
            "致力于帮助企业把 AI 应用从概念推进到生产。创办 RapidCanvas 之前，"
            "他曾联合创办 Simility，该公司后来被 PayPal 收购。他的工作重点是构建契合真实业务流程的 "
            "AI 系统，使其在数据、需求与运营条件变化时依然有用。"
        ),
    },
    {
        "title": "Peptone Advances AI-Developed Prostate Cancer Candidate and Names CSO",
        "title_zh": "Peptone 推进 AI 研发的前列腺癌候选药物，并任命首席科学官",
        "summary_zh": (
            "Peptone 于 2026 年 11 月 24 日宣布，其借助 AI 与生物物理学研发的前列腺癌候选药物 "
            "PEP-5089 已进入支持新药临床试验申请（IND）的研发阶段，"
            "即用于支撑人体试验申请的临床前阶段。公司同时任命 Deepak Sampath 为首席科学官。"
        ),
    },
    {
        "title": "The Next Insider Threat Will Be an Employee’s Personal AI Agent",
        "title_zh": "下一个内部威胁将是员工的个人 AI 智能体",
        "summary_zh": (
            "员工把个人智能体接入工作邮箱和 Slack 的速度，远超安全团队的追踪能力。"
            "本文提出四个问题，帮助管理层提前应对。未来一年内，员工的个人 AI 智能体将在大多数"
            "大公司内部运行，而多数安全团队并不知道有哪些智能体。信号出现在 9 月："
            "安全研究员 Patrick Wardle 演示了 Mac 上的恶意软件如何劫持 Meta 新推出的 Muse 助手会话，"
            "并在受害者的设备间操控它。"
        ),
    },
    {
        "title": "Cloudera launches digital sovereignty platform spanning AI and infrastructure",
        "title_zh": "Cloudera 推出覆盖 AI 与基础设施的数字主权平台",
        "summary_zh": (
            "Cloudera Inc. 今日发布一套数字主权方案，称无论工作负载运行在何处，"
            "该方案都能让组织保持对自身数据、AI 模型和计算基础设施的控制。"
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
