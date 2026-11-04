# -*- coding: utf-8 -*-
"""本轮（23:00 例行巡检）人工核对标题覆盖表。

来源：两个审查代理对 2026-09-15 ~ 2026-10-30 全部 255 条英文资讯做的
逐条人工审查，以及主流程对 2026-10-30 / 2026-10-31 两日的复核。

只收录确实存在问题的条目。专有名词保留英文原写法。
"""

TITLE_OVERRIDES = {
    # ---- 语义崩坏 / 指代混乱 ----
    "The ‘Pain in the Ass’ Math That Could Save Vibe Coding From Itself":
        "可能让 Vibe 编程自我救赎的那道「数学难题」",
    "Mistral Says Its AI Model ‘Le Chonk’ Has Leapfrogged China in the Open-Weight Race":
        "Mistral 说其 AI 模型 Le Chonk 在开放权重竞争中超越了中国",
    "How we detect frontier model misalignment":
        "我们如何检测前沿模型的对齐偏离",
    "Google AI gets cagey when asked who won the 2020 elections":
        "被问谁赢得了 2020 年大选时，Google AI 含糊其辞",
    "Uber Moves beyond CPU Cores with Performance-Aware Scheduling for Stateful Workloads":
        "Uber 突破 CPU 核心限制，为有状态工作负载引入性能感知调度",
    "Developers Reporting Double-Digit Weekly Time Savings from AI Fell from 68% to 26%":
        "报告 AI 每周带来两位数时间节省的开发者比例从 68% 降至 26%",
    "Will the real Anthropic please stand up":
        "真正的 Anthropic，请站起来",
    "Our newest AI Quest: Mapping the human brain":
        "我们最新的 AI Quest：绘制人类大脑地图",
    "Tesla gave up the EV crown. Now it wants to win the autonomy race.":
        "Tesla 放弃了电动车王座，现在它要赢下自动驾驶之战",
    "Robust Serialization with JSON and Custom Types":
        "使用 JSON 与自定义类型实现健壮的序列化",
    "ChatGPT’s expanding world of work":
        "ChatGPT 不断扩张的工作版图",
    "Anima helps clinics cut call waits by 75% with GPT-6 and GPT-Live":
        "Anima 借助 GPT-6 和 GPT-Live 将诊所来电等待时间缩短 75%",
    "Build more responsive apps with the Decisions API":
        "用 Decisions API 构建响应更快的应用",
    "Beyond tree cover: mapping the world’s forest types":
        "不止林地覆盖：绘制全球森林类型地图",
    "What FDE means at OpenAI":
        "OpenAI 的 FDE 意味着什么",
    "Leading European Financial Services Organizations Embrace Open Models to Build Proprietary Intelligence":
        "欧洲领先的金融服务机构采用开放模型构建自有智能",
    "How AT&T is rethinking in-house legal work with OpenAI":
        "AT&T 如何借助 OpenAI 重塑内部法律工作",
    "How Wikipedia’s Editors Keep the Online Encyclopedia Human-Written":
        "维基百科编辑如何让在线百科全书保持人工撰写",
    "Google Cloud and NVIDIA Announce General Availability of NVIDIA Vera Rubin Infrastructure":
        "Google Cloud 与 NVIDIA 宣布 NVIDIA Vera Rubin 基础设施正式可用",
    "Southeast Asia’s digital economy to hit $368 billion":
        "东南亚数字经济将达 3680 亿美元",
    "Democratic governance of frontier AI, part II: Empowering cyber defenders":
        "前沿 AI 的民主治理，第二部分：赋能网络防御者",
    "How Itaú is building generative AI for its entire customer base":
        "Itaú 如何为整个客户群体构建生成式 AI",
    "Benefit Street Partners answers questions faster with Codex":
        "Benefit Street Partners 用 Codex 更快地回答问题",
    "Teaching students to think and learn through questions":
        "教学生通过提问来思考与学习",
    "Sullivan & Cromwell brings legal expertise into agreement review":
        "Sullivan & Cromwell 将法律专业能力带入协议审查",
    "The EU’s next chapter in AI is agentic":
        "欧盟 AI 的下一章是智能体化",
    "Google DeepMind’s New Resident Philosopher Tackles AI Ethics":
        "Google DeepMind 新任驻场哲学家探讨 AI 伦理",
    "Higgsfield takes AI video from 1 minute to over 10":
        "Higgsfield 把 AI 视频时长从 1 分钟延长到 10 分钟以上",
    "Systems Thinking Is Vital in the Age of AI":
        "在 AI 时代，系统思维至关重要",
    "Pairing industrial AI autonomy and human control":
        "让工业 AI 自主性与人类控制相结合",
    "Poetry for Engineers: Of Code and Shortleaf Pine":
        "工程师的诗歌：关于代码与短叶松",
    "Edge AI for Smart Cities: From Insight to Cognitive Action":
        "面向智慧城市的边缘 AI：从洞察走向认知行动",
    "Edge AI for Smart Cities: From Insight to Cognitive Action ":
        "面向智慧城市的边缘 AI：从洞察走向认知行动",

    # ---- 品牌名 / 专名保留原文 ----
    "Infini-AI-Lab Releases Hermit, an Open-Source Harness Adapter Framework for AI Agents":
        "Infini-AI-Lab 发布 Hermit：面向 AI 智能体的开源 harness 适配器框架",
    "Genie 4: A new generation of world simulation":
        "Genie 4：新一代世界模拟",
    "OpenAI models are coming to Google Cloud":
        "OpenAI 模型将登陆 Google Cloud",
    "Higgsfield takes AI video from 1 minute to over 10 minutes":
        "Higgsfield 把 AI 视频时长从 1 分钟延长到 10 分钟以上",

    # ---- 标题语病 / 直译腔 ----
    "Radisson Hotel Group brings hotel discovery into ChatGPT":
        "Radisson Hotel Group 将酒店搜索接入 ChatGPT",
    "GPT-6 and Intelligent UI for everyone":
        "GPT-6 与智能 UI，人人可用",
    "Paper on AI hiring shows a hiring market that hasn't changed":
        "AI 招聘论文：一个并未改变的招聘市场",
    "Apple releases iOS and macOS 27.2 with new Siri AI features, new Music logo":
        "Apple 发布 iOS 与 macOS 27.2，新增 Siri AI 功能与全新音乐标识",

    # ---- 10-30 / 10-31 主流程复核 ----
    "Apple CEO says the company doesn’t ‘want to ship AI for AI’s sake’":
        "Apple CEO：公司不会为了 AI 而发布 AI",
    "Judge allows NAACP lawsuit over xAI data center pollution to move forward":
        "法官允许 NAACP 关于 xAI 数据中心污染的诉讼继续推进",
    "Nvidia weighs playing the cosigner for Nscale’s AI data center in West Virginia":
        "英伟达考虑为 Nscale 位于西弗吉尼亚州的 AI 数据中心担任联合担保方",
    "Apple Intelligence is finally coming to China with iOS 27.3":
        "Apple Intelligence 终于将在 iOS 27.3 带到中国",
    "Fujifilm to boost tape production 5x as AI fuels archiving demand":
        "AI 推动归档需求，Fujifilm 将磁带产能提升 5 倍",
    "Crisp Launches Halo to Bring Retail AI Inside Enterprise Cloud Environments":
        "Crisp 推出 Halo，将零售 AI 带进企业自有云环境",
    "Agility Robotics Expects $465M Gross Capital Raise Ahead of SPAC Closing":
        "Agility Robotics 预计在 SPAC 完成前募集 4.65 亿美元总资本",
    "Cohere Projects Over 1,500 Canadian Jobs and C$4 Billion Investment by 2031":
        "Cohere 预计到 2031 年创造 1,500 多个加拿大岗位、投资 40 亿加元",
}

# 追加：31 天窗口新纳入的边界旧条目
TITLE_OVERRIDES.update({
    "Chatham scales its capital markets expertise with OpenAI":
        "Chatham 借助 OpenAI 扩展其资本市场专业能力",
    "How Albertsons Companies is reimagining retail from the inside out":
        "Albertsons 如何从内部重塑零售业",
})
