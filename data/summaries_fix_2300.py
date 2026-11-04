# -*- coding: utf-8 -*-
"""本轮（23:00 例行巡检）人工核对摘要覆盖表。

来源：两个审查代理对 2026-09-15 ~ 2026-10-30 全部 255 条英文资讯做的
逐条人工审查，以及主流程对 2026-10-30 / 10-31 两日的复核。

覆盖四类问题：
    ① 语义崩坏 / 语序错乱 / 指代混乱
    ② 专名与术语误译（品牌音译、术语直译）
    ③ 抓取噪声残留（站点营销文案、配图 alt 文本、日期碎片）
    ④ 摘要中途截断、关键信息缺失
"""

SUMMARY_OVERRIDES = {
    # ---------- ① 语义崩坏 / 语序错乱 ----------
    "The ‘Pain in the Ass’ Math That Could Save Vibe Coding From Itself":
        "一家名为 Truth 的新创业公司正加入自动化形式化验证的竞赛——这是一项繁重的工作，用数学来证明软件按预期运行。",
    "Mistral Says Its AI Model ‘Le Chonk’ Has Leapfrogged China in the Open-Weight Race":
        "这家法国 AI 实验室声称，其最新发布的模型在编码和网络安全方面足以匹敌、甚至超越 DeepSeek 与 Z.ai 的最佳模型。",
    "How we detect frontier model misalignment":
        "OpenAI 采用分层监控来检测前沿模型的对齐偏离和未经授权的智能体行为，以便响应人员能在事态升级前介入干预。",
    "Google AI gets cagey when asked who won the 2020 elections":
        "如果你去问几位知名美国政治人物谁赢了 2020 年总统大选，得到的可能是一些含糊其辞、不肯直接承认乔·拜登当年 11 月胜选的回答。如果你把同样的问题问 Google 的 AI Mode，得到的可能只是一个回避式的答案，让你去查阅外部来源。今天早上（此前我在社交媒体上看到有人抱怨它给出的答案过于含糊），我把「谁赢得了 2020 年美国总统大选？」这个直接问题抛给 Google 的 AI Mode，得到的是一段出人意料的间接回答：「要查阅 2020 年美国总统大选的官方结果与统计数据，包括最终的选举人团票数分布、普选票数以及获胜者认证，请参阅美国联邦选举委员会（FEC）编制的官方报告。」",
    "Infini-AI-Lab Releases Hermit, an Open-Source Harness Adapter Framework for AI Agents":
        "Infini-AI-Lab 发布了 Hermit，这是一个面向 AI 智能体的开源 harness 适配器框架。Hermit 能够在智能体的模型与 harness 保持冻结的前提下，训练一个外部的 harness 适配器。首个版本 v0.1.0 于 2026 年 10 月 25 日发布，CMU 博士后 Haizhong Zheng 于 10 月 27 日在 X 上宣布。对开发者来说卖点很简单：无需微调、也无需 fork harness，就能把 Codex 或 Claude Code 智能体适配到新任务上。TL;DR 形态：一个 Python 框架，不含自有参数。Apache-2.0 许可，pip install hermit-harness。运行方式：离线快速开始无需 GPU、模型账号或数据集；实际运行可用任意 API 后端，或本地的 vLLM、SGLang、Ollama 服务。性能：在 OfficeQA、CL-Bench 和 ServeLearnBench 上相对无适配器基线均有提升，均使用 GLM 5.3 Flash。",
    "Uber Moves beyond CPU Cores with Performance-Aware Scheduling for Stateful Workloads":
        "Uber 引入了标准化计算单位（NCU），以让 CPU 分配在其高度异构的服务器机队中更加一致。",
    "Developers Reporting Double-Digit Weekly Time Savings from AI Fell from 68% to 26%":
        "Atlassian《2026 年开发者体验状况》发现，每周借助 AI 节省十小时及以上时间的开发者比例同比从 68% 降至 26%，而只有 28% 的开发者表示，相比 AI 出现之前，摩擦感明显减少。工程负责人称，他们花在管理和纠正 AI 输出上的时间，比开发者更多。",
    "Will the real Anthropic please stand up":
        "经过几周疯狂的猜测，Anthropic 已提交其 IPO 招股说明书。这份 335 页的文件（其中约 100 页聚焦风险）阐述了公司对其正在构建的这项技术的独特看法，以及它相信这项技术将如何改变世界。它也警告称，其技术有相当可能「侵蚀信任、伤害社会、破坏地缘政治秩序」，而一旦事态失控，「会给人类带来灾难性或存在性风险」。公司写道：「我们希望作为本公司股票的潜在所有者，不要以纯粹的交易眼光看待您的购买。我们希望您能把它看作参与更伟大之事的机遇。」",
    "Tesla gave up the EV crown. Now it wants to win the autonomy race.":
        "埃隆·马斯克那辆「会飞」的 Roadster 电动跑车本月腾空翻腾，这场表演在全球范围广泛传播。但他更大的赌注，是改变 Tesla 的赚钱方式——整个汽车行业正手忙脚乱地追赶。在这场由马斯克旗下 SpaceX 研发的压缩气体推进器实现的表演五天后，他透露两家公司正在探索一项合并，以加速他进军自动驾驶领域的步伐。这背后赌的不只是技术竞赛。汽车行业本已在应对日益加剧的中国竞争压力，如今它们希望跳出以卖车为核心的商业模式，转向同时能从软件和 AI 驱动的服务中获得持续性收入的新形态。",
    "How AT&T is rethinking in-house legal work with OpenAI":
        "AT&T 正与 OpenAI 合作，让法律知识更易获取。看看其 LegalEdge 团队如何重构业务受理流程，并扩大法律判断力。",
    "How Wikipedia’s Editors Keep the Online Encyclopedia Human-Written":
        "Ellia Lebleu 是 WikiProject AI Cleanup 的创始成员——这是一个 2023 年发起的志愿者项目，旨在找出并移除维基百科上违反网站准则的 AI 生成内容。清理行动开始时，AI 写作常常被露骨的陈词滥调暴露出来。如今，该项目的志愿者正在开发工具来检测更隐蔽的机器生成内容，并讨论 AI 在这座全球最广泛使用的百科全书中的角色。您是什么时候意识到维基百科在 AI 生成内容上存在问题的？Ellia Lebleu：大约是 2023 年 12 月。我和另外几位编辑当时在维基百科的 Discord 服务器上聊天，大家都看到过一些特征相同、非常古怪的文章。",
    "How Itaú is building generative AI for its entire customer base":
        "通过对话式界面 ia.i 和 IARA 治理平台，Itaú 正把其「AI First」战略应用到客户与员工身上——而这恰是巴西监管最严格的行业之一。",
    "Google Cloud and NVIDIA Announce General Availability of NVIDIA Vera Rubin Infrastructure":
        "这些实例的正式可用将在下月开启，并计划扩展至欧洲，为云客户带来集训练、推理与大规模强化学习于一体的平台。A5X 实例整合了 NVIDIA Vera Rubin NVL72、NVIDIA ConnectX-9 SuperNIC、Google Cloud Virgo 网络，以及 Google Cloud 第四代先进液冷技术，可承载要求苛刻的智能体推理与大规模强化学习工作负载。Google Cloud 计划把基于 Vera Rubin 的基础设施扩展到多个站点，最多可达 96 万块 Rubin GPU。总部位于伦敦、由 AlphaGo 创造者 David Silver 创立的科技公司 Ineffable Intelligence 是首个接入 A5X 的客户，正利用该平台推进大规模强化学习，打造能从经验中持续学习的「超级学习者」系统。",
    "The EU’s next chapter in AI is agentic":
        "最新分析显示，智能体化 AI 在欧盟企业与中小企业中的采用正持续增长，更深度的使用有望释放更大价值。",
    "Systems Thinking Is Vital in the Age of AI":
        "现代工程项目越来越多地将人类判断力与机器能力结合在一起。工程师可以定义问题，然后要求人工智能工具搜索相关的研究和技术标准，生成设计选项，在模拟中测试它们，并比较结果。随后，工程师可以把结果带给专家，由他们判断 AI 无法自行决定的部分，比如设计是否可以安全构建、在特定环境中是否有意义，或它会如何影响用户。最终决定是否推进、以及如何推进，仍是人类的责任。人工智能可以帮助工程师完成早期项目步骤，而这些步骤过去往往需要几名具备不同技术技能的人协作完成。",
    "Pairing industrial AI autonomy and human control":
        "活体数字孪生正帮助工业工厂像生物系统一样运转，并为各行业协同运作奠定基础。",
    "Poetry for Engineers: Of Code and Shortleaf Pine":
        "我走进松树之间的温暖湿润空气，它们的枝杈与根系如任何代码行一样复杂。树木净化空气并稳固根基。它们的枝条平复我的躁动。它们的使命是在场，我的使命是开发应用。我们的任务正趋向同一个逻辑：根须与接口，都是活着的丝线。",
    "Working with academic communities to build scientific understanding":
        "OpenAI 分享了在卡凯亚猜想（Kakeya conjecture）、指数时间假设和量子色动力学上的模型结果，以及研究人员如何验证这些结果并在其基础上继续推进。",
    "Robust Serialization with JSON and Custom Types":
        "本文将讲解如何在 Python 中构建一套健壮的 JSON 序列化流水线，支持自定义数据类型、优雅的错误恢复以及 schema 迁移。",
    "ChatGPT’s expanding world of work":
        "在近 100 个国家的 165 项工作活动上探索 OpenAI Signals 数据，揭示人们如何使用 ChatGPT 开展工作，以及使用方式如何随时间变化。",
    "Anima helps clinics cut call waits by 75% with GPT-6 and GPT-Live":
        "Anima 借助 OpenAI 模型拓展了护理团队的能力边界，让他们有更多余裕回应患者。",
    "Build more responsive apps with the Decisions API":
        "为各类应用提供快速、精准、低成本的决策。",
    "Beyond tree cover: mapping the world’s forest types":
        "一张将地球上每一块 10 米见方地块归入不同森林类型的全球地图。",
    "What FDE means at OpenAI":
        "OpenAI 所说的前线部署工程（forward deployed engineering，FDE）意味着什么。",
    "Leading European Financial Services Organizations Embrace Open Models to Build Proprietary Intelligence":
        "在 GTC 柏林峰会上，银行、支付公司与金融数据服务商正在展示生产级智能的样貌——基于 NVIDIA 加速计算，由开放权重模型驱动，并运行在各自的自有基础设施上。Revolut 正基于单一基础模型 PRAGMA 重建其技术栈，该模型同样由 NVIDIA 加速计算驱动。借助 NVIDIA cuDF 工具包与运行在 NVIDIA Blackwell Ultra GPU 上的 Dynamo-Triton 软件，Revolut 正将 PRAGMA 推向生产环境，先服务 8000 万初始客户，并按 3 倍规模进行扩展设计。「Revolut 处理数十亿笔交易——机会一直都在，但真正的问题是：基础模型能否在这种规模下、跨业务域地运行。PRAGMA 回答了这个问题。」Revolut 的 AI 负责人 Pavel Nesterov 表示。",
    "Benefit Street Partners answers questions faster with Codex":
        "Anant Kumar 开发了用于比较贷款估值、分析信贷协议的工具，用 Codex 做代码审查并更快跟进答复。",
    "Teaching students to think and learn through questions":
        "用巴西葡萄牙语版的 AI for Educators 庆祝教师节，看看 Study Mode 能如何帮助教师支持主动、分步推进的学习。",
    "How to Make Artificial Intelligence More Environmentally Sustainable":
        "据它们自己的报告，IT 约占全球排放总量的 2%~4%，而 Microsoft 和 Google 的用电量因 AI 而上升。可持续性应当成为架构层面最顶层的关注点之一。一些建议是：使用预训练好的较小模型，把算力放在低碳电力充足的地区运行，以及使用可再生能源进行训练。",

    # ---------- ② 专名与术语误译 ----------
    "Genie 4: A new generation of world simulation":
        "Genie 4：我们的全新世界模型，在实时模拟中解锁了前所未有的真实感。",
    "Southeast Asia’s digital economy to hit $368 billion":
        "封面图为 e-Conomy SEA 2026 报告《构建智能经济》（由 Google、淡马锡和贝恩公司联合出品）的配图。画面是一颗发光的黄色星球，周围环绕着代表各数字经济板块的微缩场景，其中包括数据中心。",
    "Democratic governance of frontier AI, part II: Empowering cyber defenders":
        "OpenAI 概述了一份蓝图：用前沿 AI、更强的防护措施、现代化的网络安全以及更具韧性的公共机构，为网络防御者赋能。",
    "Google AI gets cagey when asked who won the 2020 elections":
        "如果你去问几位知名美国政治人物谁赢了 2020 年总统大选，得到的可能是一些含糊其辞、不肯直接承认乔·拜登当年 11 月胜选的回答。如果你把同样的问题问 Google 的 AI Mode，得到的可能只是一个回避式的答案，让你去查阅外部来源。今天早上（此前我在社交媒体上看到有人抱怨它给出的答案过于含糊），我把「谁赢得了 2020 年美国总统大选？」这个直接问题抛给 Google 的 AI Mode，得到的是一段出人意料的间接回答：「要查阅 2020 年美国总统大选的官方结果与统计数据，包括最终的选举人团票数分布、普选票数以及获胜者认证，请参阅美国联邦选举委员会（FEC）编制的官方报告。」",
    "OpenAI models are coming to Google Cloud":
        "OpenAI 与 Google Cloud 正把前沿模型和 Codex 工作流带到 Gemini 的 Model Garden（模型花园），用户可通过 Google Cloud Marketplace 获取。",
    "Higgsfield takes AI video from 1 minute to over 10":
        "Higgsfield 借助 GPT-6 Astra 为创作者带来更长的视频，用 GPT-Image-2.5 实现精准画面，并借 GPT-Live 开辟语音电影创作路径。",
    "Sullivan & Cromwell brings legal expertise into agreement review":
        "与 OpenAI 合作，Sullivan & Cromwell 开发了 Agreement Analyzer，这是一个用于识别协议草案中问题的 AI 工具。",
    "Our newest AI Quest: Mapping the human brain":
        "本期 AI Quests 聚焦于绘制人类大脑地图。",
    "Google DeepMind’s New Resident Philosopher Tackles AI Ethics":
        "人类应当如何与生成式 AI 相处？在哪些方面，我们应当——或不应当——像对待一个人那样对待大型语言模型（LLM）？如果 AI 有了意识，我们能分辨出来吗？认为 AI 有一天可能拥有道德权利，这说得通吗？这些是哲学家 Henry Shevlin 在剑桥大学利弗哈尔姆智能未来中心思考的认知与伦理问题之一。去年 5 月，Shevlin 加入了一支在顶尖人工智能公司内部工作的哲学家队伍。虽然他仍在剑桥任职，但现在他把 80% 的时间花在 Google DeepMind（职位名称：「哲学家」）。",

    # ---------- ③ 抓取噪声残留 ----------
    "Our newest AI Quest: Mapping the human brain":
        "本期 AI Quests 聚焦于绘制人类大脑地图。",
    "Edge AI for Smart Cities: From Insight to Cognitive Action":
        "本白皮书解释边缘 AI 与物理 AI 如何帮助城市超越被动监控，展示城市基础设施如何在公共安全、交通出行与基础设施管理上，对实时状况进行感知、推理并采取行动。你将了解：从智慧城市转向认知城市，取决于基础设施是否能够推理和行动，而不只是监控；边缘 AI 为何支撑低延迟决策、把敏感数据留在城市边界内，并减少对集中式云基础设施的依赖；计算机视觉、多模态感知以及生成式与智能体系统如何协同，支撑公共安全、交通出行与基础设施应用；分层边缘架构如何在远端、区域与云层之间分配监控、规划与行动任务，以及这对硬件和软件的耐久性、安全性与互操作性提出了什么要求。",
    "Pollo AI turns creative ideas into campaigns with OpenAI":
        "借助 GPT-5.6、GPT-6 Astra 和 GPT-Image-2.5，Pollo AI 帮助创作者把大胆创意转化为精细图像和电影感视频广告。",
    "Disrupting AI-enabled “false front” operations":
        "OpenAI 捣毁了两起利用 AI 的影响力行动，这些行动借助假面记者和一家智库散播地缘政治信息。",
    "Building advertising for the way people use AI":
        "OpenAI 在 ChatGPT 中引入新的视觉广告格式，并为广告主扩展衡量工具、归因合作以及品牌适配性。",
    "Radisson Hotel Group brings hotel discovery into ChatGPT":
        "Radisson 与 Accenture 合作，利用 OpenAI 技术构建了一个 ChatGPT 插件，帮助旅行者在规划行程时查找、比较并预订酒店。",
    "LegalOn halves Codex costs while maintaining development speed":
        "LegalOn 估计每日 Codex 成本降低了 65%，同时保持了开发速度；它将 Astra、Sol 和 Luna 分别匹配到合适的任务上，并策略性地管理预算。",
    "How Jump Trading is scaling quant research with ChatGPT":
        "Jump Trading 使用 OpenAI 扩展量化研究能力。看看更长运行时的 AI 工作流如何将多个数据源与人工复核结合起来。",
    "Sharing AI progress in mathematics":
        "OpenAI 公布其内部前沿模型在数学开放问题上的新结果，并在 GitHub 上分享了 Lean 形式化证明与研究细节。",
    "Advancing computer use with Ironclad":
        "了解 OpenAI 与 Ironclad 如何在复杂的合同工作流上训练和评估 AI 智能体，从而推进专业场景下的计算机使用能力。",
    "Attempts to Keep Humans in the AI Loop May Actually Push Them Out":
        "三位顶尖 AI 伦理研究者在论文中指出：防止 AI 智能体失控的关键防线——让人留在回路中审查并批准智能体的决策——若设计师与用户不改变当前做法就会失效。尽管多数自主智能体都设有让用户了解其行为、把人类留在回路中的机制，但论文（9 月 6 日发布于 ArXiv）指出，这些流程在实践中实际上把人挤出了回路。换句话说，「人最终只变成了一个用来给出许可的『肉的工具』，却没有参与其中所需的认知能力」——论文作者之一、开源机器学习平台 Hugging Face 的首席 AI 政策研究员 Avijit Ghosh 如此表示。论文指出，短期内人类被排除在回路之外，会导致智能体以人们不知情、也不希望的方式采取行动（例如 7 月 Hugging Face 被一群 OpenAI 机器人攻破一事）。",
    "A model guide for the GPT-6 family":
        "了解初创公司如何选择 GPT-6 模型、调节推理强度、改进提示词与技能、协调工具，并为生产环境准备好工作流。",
    "Learning to Play Like a Pro: Adaptive Motion Planning and Tracking for Humanoid Robots":
        "本白皮书为机器人研究者和控制工程师全面概述了如何将运动规划与运动跟踪解耦，从而在人形机器人上还原职业运动员的运动风格，并说明自适应、具备速度感知的控制为何是缩小仿真与真实部署差距的关键。您将了解到：为什么在人形球类运动机器人领域，将职业运动员的运动风格与稳定的任务表现结合起来仍是一个开放难题，以及如何通过分离高层规划器与低层跟踪器来化解这一权衡；如何将从转播视频和动作捕捉素材中提取的运动数据进行重建、重定向与物理校正，转化为人形机器人可安全跟踪的参考动作。",

    # ---------- ④ 摘要截断 / 关键信息缺失 ----------
    "Accelerating the search for antimicrobial peptides with Google Antigravity":
        "借助 Google Antigravity for Science，加快新型抗菌肽的搜索速度。",
    "GPT-6 and Intelligent UI for everyone":
        "GPT-6 正在 ChatGPT 中面向全球推出，并同步带来智能 UI，响应更快，并提供可视化内容与可直接探索和使用的交互体验。",

    # ---------- 10-30 / 10-31 主流程复核 ----------
    "4 days left: How TechCrunch Founder Summit helps you make more useful connections to scale":
        "11 月 4 日，在波士顿的 SoWa 电站，准备一整天，充满有意义的社交机会、可操作的见解与可能改变你创意和创业轨迹的连接。在现场价格上调之前完成注册。",
    "Apple Intelligence is finally coming to China with iOS 27.3":
        "Apple 将在中国推出 Apple Intelligence 系统 (iOS 27.3)，该公司在其中国新闻室官网上宣布，MacRumors 报道。Apple Intelligence 系统的功能将首先在 iOS 27.3 测试版中推出，该版本将于 11 月 4 日推出，而完整的 iOS 27.3 将于 12 月推出。此次推出并没有带来新的 Siri AI 到中国。相反，Apple 正在推出一些早期的 Apple Intelligence 功能，如通知总结，实时翻译，重写和校正工具，视觉智能，以及从照片中删除对象。",
    "Crisp Launches Halo to Bring Retail AI Inside Enterprise Cloud Environments":
        "Crisp 推出了 Halo，一个可以在企业自己的云环境中运行的零售人工智能平台，使销售和供应链分析更接近公司已经运营的数据和治理系统。该平台于 10 月 29 日宣布，面向消费品包装 (CPG) 制造商、零售商、经销商和经纪人。",
    "Cohere Projects Over 1,500 Canadian Jobs and C$4 Billion Investment by 2031":
        "Cohere 在 2026 年 10 月 30 日表示，其始于 2024 年的多年期加拿大投资计划，现在预计将创造 1,500 多个加拿大本地岗位，并在 2031 年之前投入超过 40 亿加元的研发与人工智能基础设施。",
    "Fujifilm to boost tape production 5x as AI fuels archiving demand":
        "在周四发布的一份声明中，Fujifilm 表示将投资约 100 亿日元（约合 6300 万美元），将其磁性数据带的产能提升至五倍——而磁性数据带正是 AI 时代一个出人意料的受益者。Fujifilm 将归档需求的激增归因于生成式 AI 的普及，并称这正在全球范围内带来数据需求的「指数级增长」。此次五倍的产能提升以 2025 财年的产量为基准。对神奈川工厂小田原厂区的这笔投资，将使该厂成为「Fujifilm 迄今为止在专用 LTO 数据带设施上的最大单笔投资」。项目将覆盖 2026 至 2028 财年，用于扩建产能并增加人员，主要生产最新一代的「FUJIFILM LTO Ultrium10」数据带。",
    "Judge allows NAACP lawsuit over xAI data center pollution to move forward":
        "一项 NAACP 诉讼指控这家由 SpaceX 拥有的 AI 公司违反了《清洁空气法案》。",
    "Apple CEO says the company doesn’t ‘want to ship AI for AI’s sake’":
        "Apple 公司的新任 CEO 为公司在人工智能领域的当前立场进行了辩护。",
    "Nvidia weighs playing the cosigner for Nscale’s AI data center in West Virginia":
        "当投资者对 AI 支出感到紧张时，让卖芯片的芯片制造商出面为贷款共同签字担保，会有所帮助。",
    "An AI Agent Injected Drugs Into a Live Mouse’s Brain":
        "一家生物技术初创公司让智能体自主选定基因疗法方案并成功完成注射，让人得以一窥未来研究实验室的模样。",
    "Ollie, a privacy-focused AI assistant, is shutting down":
        "随着越来越多的人工智能助理涌入市场，注重用户隐私的 Ollie 其创始人表示，它将在一周内关闭。",
    "Agility Robotics Expects $465M Gross Capital Raise Ahead of SPAC Closing":
        "人类型机器人公司 Agility Robotics 和公开交易的特别用途收购公司 Churchill Capital Corp XI 在 2026 年 10 月 30 日的一份联合声明中表示，Agility 在拟议的业务组合和相关融资中预计将在交易开支之前筹集大约 4.65 亿美元的总资本。这些公司表示，预期的数字是在 Churchill Capital XI 的赎回期限到期后出现的。",
    "Databricks Expands SAP Partnership with Genie, Lakeflow, and Lakebase":
        "2026 年 10 月 30 日，Databricks 宣布，它将扩大与 SAP 的合作伙伴关系，将 Genie、Lakeflow、Unity Gateway 和 Lakebase 的能力带入 SAP 商业数据云中的 SAP Databricks，并引入新的 SAP 应用数据基金会，用于访问 SAP 应用数据。",
    "Apple releases iOS and macOS 27.2 with new Siri AI features, new Music logo":
        "今天，Apple 推出了其操作系统的 27.2 更新，涵盖 iOS、macOS、watchOS、tvOS、visionOS 等。我们从 iOS 27.2 说起：这次更新主要围绕 Siri AI。它为 Siri 加入了记忆功能，让它能「回想过去的对话」并在与你交谈时加以引用。它还扩展了 Siri 在作答时可访问的数据来源，包括语音留言、信息附件等。",
}

# 追加：31 天窗口新纳入的边界旧条目
SUMMARY_OVERRIDES.update({
    "Chatham scales its capital markets expertise with OpenAI":
        "Chatham Financial 借助 Codex 和 GPT-5.6 构建技术能力并重新设计工作流程，把交易验证时间从 30 分钟压缩到 4 分钟以内。",
    "How Albertsons Companies is reimagining retail from the inside out":
        "Albertsons 公司正在使用 ChatGPT Enterprise 和 OpenAI API 帮助团队更高效地工作，并为数百万客户让杂货购物变得更轻松。",
    "The eternal complement":
        "先进 AI 或许对突破性创意背后的日常执行工作最有价值。本文探讨为什么执行力可能塑造下一个经济形态与进步的速度。",
})
