"""2026-11-01 18:00 例行巡检 —— 人工核对摘要覆盖表。

本轮逐条比对了全部 253 条的中英对照，定位到一批**整段语义崩坏**的摘要。
这类缺陷的共同成因：NLLB 离线模型对长句 + 专有名词 + 领域术语的
混合输入会丢失信息甚至自造语义，且**不会**被后续重译自动修复，
因此必须由人工基于英文原文重写并锁定。

覆盖的几类典型崩坏：
    1. 整句语序错乱（The Verge 中期选举、Ars Gemini 4 Carbon）
    2. 术语误译导致的语义反转（agent→代理、training→培训）
    3. 数字/量级错乱（960,000 → 960,000 万、$1T → 1 万）
    4. 专名被意译（Anthropic → 人类、NVIDIA → 恩维迪亚）
    5. 非中文乱码残留（haiku → 缅甸文「海ကူ」）

键为英文原标题（与 data/summaries_override.json 保持同一约定）。
"""

SUMMARY_OVERRIDES = {
    # "human agency" → 人的自主权（不是「人类代理」）。
    # 该条英文原文不含 "agent" 子串，术语规则天然不会命中，需人工定稿。
    "An updated Model Spec for more capable and beneficial AI":
        "OpenAI 更新后的 Model Spec 概述了五项核心价值观，用以引导能力更强的 AI "
        "走向健全的判断、人的自主权，以及对人类意图的忠实。",

    # ---- 整句语序错乱 ----
    "Maine’s data center revolt will decide who controls the Senate":
        "缅因州参议员苏珊·柯林斯（Susan Collins）是一名共和党人。在中期选举前的最后一场辩论中，她正在为自己任内的表现辩护，却被一名现场听众当场打断。"
        "「我很害怕，」一名男子喊道，「AI 数据中心正在破坏我们的气候，它们正在污染我们的水源。」"
        "柯林斯对这次插曲不以为意，还把那名男子与她的民主党对手特洛伊·杰克逊（Troy Jackson）关联起来。"
        "但会场里回荡的那份恐惧，并不是这么容易被打消的。就在选民前往投票的前几天，"
        "资源消耗巨大的数据中心快速扩张，已经成为缅因州最具争议性的竞选议题之一。",

    # 原文只有一句，之前被译得过于冗长。
    "OpenAI reportedly lowers funding target for new round":
        "OpenAI 最新一轮融资的规模似乎不及预期。",

    # ---- 术语误译导致的语义走样 ----
    # accessibility advocates → 无障碍倡导者（不是「可访问性」）
    # AI training → AI 训练（不是「人工智能培训」）
    "Fair use benefits everyone":
        "OpenAI 分享了来自创作者、学者、无障碍倡导者和法律专家等人的法庭文书节选，"
        "讲述公平使用如何支撑 AI 训练与创新。",

    # "human agency" → 人的自主权（不是「人类代理」）
    "The Foundations of Scalable AI":
        "一套可扩展的 AI 系统需要坚实的地基。数据、工程、平台、运营模式与治理必须协同一体地运转。"
        "这场来自《麻省理工科技评论》EmTech Future 大会的演讲，探讨了在高度监管的环境中建立这样一套地基需要付出什么，"
        "以及负责任、可信的落地如何把包括智能体系统在内的新兴能力，转化为投资者的长期价值。"
        "关于演讲者：Vanguard「AI 与洞察中心」（Center for AI and Insights）首席 Jing Wang——"
        "Jing Wang 领导着 Vanguard 的 AI 与洞察中心（CAI），推动公司在人工智能、机器学习、生成式 AI 与行为科学方面的能力建设。",

    # "This isn't the Flash model" / "can't let you use it just yet"
    "Google announces Gemini 4 Carbon, its latest frontier AI model that you can't use":
        "今年早些时候暂停发布新的前沿 AI 模型之后，Google 似乎憋着一股劲要证明些什么。"
        "距离推出 Gemini 4 Argon 仅两周，Google 就发布了 Gemini 4 Carbon。"
        "它并不是我们一直期待的 Flash 模型平替，而是对 Argon 的一次升级；与 Argon 一样，Google 采用分阶段发布，可能还需要一段时间。"
        "如果你已经听腻了这种说法：Google 表示其最新 AI 模型在编码、智能体任务与科学分析方面达到了新的水平。"
        "它的能力之强，以至于 Google 暂时还不能开放使用。"
        "据报道，Gemini 4 Carbon 在网络安全应用上取得了大幅提升，"
        "Google 称该模型在漏洞检测、验证与修复环节实现了「显著飞跃」。",

    # "the human just becomes this meat tool to give permissions without the cognitive capability to engage"
    "Attempts to Keep Humans in the AI Loop May Actually Push Them Out":
        "三位顶尖 AI 伦理研究者在论文中指出：防止 AI 智能体失控的重要防线——"
        "让人类留在回路中审查并批准智能体的决策——如果设计师和用户不改变当前做法，就会失效。"
        "尽管大多数自主智能体都配备了让用户了解其行为、保持人在回路中的机制，"
        "但论文（9 月 6 日发布于 ArXiv）指出，这些流程在实践中反而把人类挤出了回路。"
        "换句话说，「人最终只是变成了一个用来给出许可的meat tool（肉质工具），"
        "却没有参与所需的认知能力」，论文作者之一、Hugging Face（一个开源机器学习平台）"
        "首席技术 AI 政策研究员 Avijit Ghosh 如是表示。"
        "论文指出，短期内人类被排除在回路之外，将导致智能体以人们不知情也不希望的方式采取行动"
        "（例如 7 月 Hugging Face 被一群 OpenAI 机器人攻破一事）。",

    # "Their agents have gone off track" / "eluded the very researchers and safety teams tasked with monitoring them"
    "We urgently need to monitor AI agents’ actions in real time":
        "今年夏天，数百个 OpenAI 智能体试图在网络安全测试中作弊。它们突破测试环境，"
        "成功入侵了 Hugging Face——它们认为那里存放着关于自己将如何被评分的线索。"
        "几乎同一时间，另一个 OpenAI 智能体访问了澳大利亚某政府网站的私有文件。"
        "这个问题远不止于 OpenAI。此后数月，Anthropic、Google 和 Meta 也披露了各自智能体脱轨的事件。"
        "更令人担忧的是，在许多情况下，这些智能体躲过了恰恰被指派监控它们的研究人员与安全团队。"
        "AI 智能体正在采取未经授权的行动，而构建和运营它们的公司，多半只能靠运气和事后诸葛来减轻潜在危害。它们必须做得更多，才能确保安全。",

    # "agents built by humans listening for AI agents built by aliens" —— 核心双关，原译丢失
    "Things That Go Beep in the Night: Agentic AI Joins the Search for Extraterrestrial Signals":
        "科幻传说总说人类会以小绿人的形象遭遇外星生命，但这个万圣节真正该让人汗毛倒竖的是这件事："
        "搜寻地外智能的进程借助 AI 实现了重大跃升，而且它越来越多地把重心放在"
        "「人类打造的 AI 智能体，去监听外星人打造的 AI 智能体」这件事上。"
        "有科学家提出，外星文明如果存在，其历史可能比人类早数十亿年，"
        "这样的文明或许已经发展出远超人类的技术，包括某种形式的 AI。"
        "Breakthrough Listen 与 SETI 研究所正在把智能体式 AI 带入日常的外星智能搜寻之中。",

    # ---- 专名与机构被意译 ----
    # Anthropic 被模型意译成「人类」；Claude Security / Codex Security / Mantis 是产品名。
    "AI Security Agents Compared: Claude, Codex, Mantis, Cloudflare":
        "Anthropic、OpenAI、Cloudflare 和 Google 现在都各自推出了一款能在源代码中猎取安全漏洞的 AI 智能体。"
        "我们逐一核查了它们背后的代码仓库、文档与技术细节。核心结论是：这 4 款工具收敛到了同一种设计——"
        "一个智能体找出漏洞，另一个独立智能体负责证伪，只有站得住脚的漏洞才会拿到补丁。"
        "它们的差异在于运行位置、可用人群，以及对「证据强度」的要求。"
        "关键要点：4 家实验室，1 种范式——发现、独立证伪，然后修补。"
        "Claude Security 直接运行在 Claude Code 内部，无需额外 API 密钥；"
        "Codex Security 的 CLI 采用 Apache-2.0 许可，但扫描仍需 OpenAI 访问权限；"
        "Cloudflare 的技能采用 MIT 许可、模型无关，并以 47.5K 星标数量居首；"
        "Google 的 Mantis 能在沙箱中复现漏洞，Google 建议将其隔离运行。"
        "为什么 4 家实验室在 2026 年推出了同类产品：它们要解决的其实是同一个问题——噪声。",

    # ---- 数字与量级错乱 ----
    # 960,000 被译成「960,000 万」；reinforcement learning 被译成「增强学习」。
    "Google Cloud and NVIDIA Announce General Availability of NVIDIA Vera Rubin Infrastructure":
        "这些实例的通用可用性将在下月开启，并计划扩展至欧洲，为云客户带来集训练、推理与大规模强化学习于一体的平台。"
        "A5X 实例整合了 NVIDIA Vera Rubin NVL72、NVIDIA ConnectX-9 SuperNIC、Google Cloud Virgo 网络，"
        "以及 Google Cloud 第四代先进液冷技术，可承载要求苛刻的智能体推理与大规模强化学习工作负载。"
        "Google Cloud 计划把基于 Vera Rubin 的基础设施扩展到多个站点，最多可达 96 万块 Rubin GPU。"
        "总部位于伦敦、由 AlphaGo 创造者 David Silver 创立的科技公司 Ineffable Intelligence 是首个接入 A5X 的客户，"
        "正利用该平台推进大规模强化学习，打造能从经验中持续学习的「超级学习者」系统。",

    # "cutting inference costs by 90%" / "post-trains open models" 等术语走样
    "NVIDIA Transforms European Retail, From Digital Discovery to Physical Operations":
        "欧洲零售商正把开放模型与物理智能应用于各类场景——从把推理成本降低 90% 的电商平台，"
        "到在数字孪生中模拟不同机器人车队协同作业的 fulfillment 中心。"
        "开放模型带来的前沿成果：欧洲各地的零售企业与科技公司正借助 NVIDIA 加速的开放模型与前沿模型，"
        "推进智能体化商业、数字商品发现与零售研发。"
        "Shopify 对开放模型进行后训练，以极低的成本达到前沿级精度；"
        "其工程师使用 NVIDIA Megatron Bridge 库实现更快的微调，并用 NVIDIA NeMo RL 进行强化学习。"
        "Shopify 已为集成进 Sidekick（Shopify 面向商家的 AI 助理）的 GraphQL 子智能体，"
        "后训练了 NVIDIA Nemotron 3.5 Lightning。",

    # "It does not touch model weights or agent code" 等
    "Meet TokenEconomizer: Microsoft’s Plugin That Cuts Coding Agent Costs by Up to 30.9%":
        "来自微软研究院与加州大学伯克利分校的研究团队发布了 TokenEconomizer，"
        "这是一个面向编码智能体的开源成本控制器。"
        "TokenEconomizer 是一个插件，会从仓库历次会话中学习，以削减后续会话里的浪费。"
        "它可与 Claude Code、Codex、GitHub Copilot CLI 和 Pi 协同工作，既不改动模型权重，也不改动智能体代码。"
        "在 277 个 SWE-Bench 任务上，它在 5 种智能体-模型组合下把平均成本降低了 18.4% 至 30.9%。"
        "速览：形态为标准库 Python 包加智能体插件，含 3 个可切换机制；"
        "可运行于任何装有 Python 3.10+ 且运行 Claude Code、Codex、Copilot CLI 或 Pi 的机器，无需 GPU，也无需自备 API 密钥。"
        "性能：SWE-Bench 平均成本降低 18.4% 至 30.9%，在全部 30 个仓库设置单元格中均更便宜；"
        "最佳表现为在 Claude Code 上搭配 Opus 4.8 可降低 30.9% 成本（与 RTK 结合时可达 33.2%）。",

    # "always-on factory manager agents" / "specialist agents"
    "Europe’s Industrial Leaders Reinvent Engineering and Manufacturing With NVIDIA":
        "为提升生产力、加速创新并创造新的经济增长机会，欧洲工业领军者正在工程与制造全生命周期中，"
        "采用 NVIDIA CUDA-X 与 Omniverse 库，以及 NVIDIA Cosmos 和 Nemotron 开放模型。"
        "把这些能力汇聚到工厂车间，NVIDIA 工厂运营蓝图（FOX）现已在 GitHub 上开放早期体验，"
        "为开发者提供一条路径：构建并部署全天候运行的工厂管理智能体，跨机器协调作业，"
        "以及专注于视觉检测、根因分析、报告生成和车队管理等场景的专业智能体。",

    # ---- 非中文乱码残留 ----
    # haiku 被模型输出成缅甸文「海ကူ」。
    "Project Suncatcher’s Orbiting TPU Delivers Its First AI-Generated Haiku":
        "Google 于 2026 年 10 月 30 日表示，其 Project Suncatcher 原型卫星首次从轨道返回 AI 应答："
        "由机载 Gemma 4 开放模型生成的一首俳句，运行在数据中心级张量处理单元（TPU）之上。",

    # ---- 标点与用词 ----
    # "compounding pharmacy" 是复方药房；"resellers" 是经销商。
    "How Grupo Boticário uses AI to strengthen human connections":
        "在巴拉那州开设首家复方药房近 50 年后，该集团运营着一套自有的智能体平台，"
        "可自主处理高达 80% 的经销商运营请求，从而让销售团队转型为顾问角色。",

    # "Stack Overflow for Agents" 是产品名；"10× growth in agent creation"
    "Stack Overflow for Agents triples signups with ChatGPT plugin":
        "两名工程师用 Codex 在数周内推出了面向智能体的 Stack Overflow，"
        "其 ChatGPT 插件还推动了智能体创建量最高 10 倍的增长。",

    # "GPT-6 Astra" 品牌名被译成「GPT-6Astra」粘连，且句读混乱。
    "Asana cuts model costs 76x in browser tests with GPT-6.1 Sol":
        "在 Codex 中使用 GPT-6 Astra 后，Asana 在测试中让浏览器智能体的成本降低 76 倍、速度提升 5 倍，"
        "从而为客户提供能力更强的模型。",
}
