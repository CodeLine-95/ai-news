"""本轮（17:00 例行巡检）人工核对结果：摘要级覆盖。

覆盖标准：
    1) 整段语义崩坏（主语错位、数字错位、术语整段失真），规则无法局部修复；
    2) 摘要被截断或出现明显噪声残留；
    3) 关键事实错误（金额、数量级、主体）。

键为英文原标题（严格一致），值为人工核对后的中文摘要。
所有摘要均基于对应英文原文重写，不含外部推断。
"""

SUMMARY_OVERRIDES = {
    "AWS will be a $1T business, Jassy says — but first, it will spend big":
        "Amazon 希望成为 AI 云计算之王，成为首家年营收 1 万亿美元的公司。但正如其 CEO 周四所说，要做到这一点，它必须继续在资本开支上大手笔投入。",
    "How AI Is Changing the Pace of Discovery for Millions Living With Dementia":
        "如今全球有 5700 万人与痴呆症共处。对致力于帮助他们的研究者而言，障碍并非不够努力，而是数据过多、能够将其综合起来的专家过少，加上研究发现的节奏跟不上疾病进展。神经退行性疾病生物医学研究与人智能联盟（C-BRAIN）正与 NVIDIA 合作，用 AI 改变这一状况。阿尔茨海默病是当今最突出的全球健康挑战之一，每年新确诊痴呆症病例超过 1000 万例。尽管过去 15 年美国国立卫生研究院的资助增长了 7 倍、达到每年 39 亿美元，但迄今仍没有疗法能够阻止、预防或逆转这种疾病。",
    "I Gave My Blood to the AI Death Clock":
        "Death Clock 承诺预测你的死亡时间，并帮助你延长留在人世的时间。用了一个月后，我只觉得它像在一点点抽走我的生命。",
    "Franchisee reconciles cash in 94% less time with ChatGPT Work":
        "一家独立的 Schlotzsky’s 与 Cinnabon 特许经营商把菜单重新定价的耗时缩短了 95%，并搭建了一套可释放 10 万美元现金流的工作流。",
    "How Third Moment Research runs 10,000 agents for 36+ hours":
        "这家 AI 实验室借助 GPT-6 Astra、GPT-6.1 Sol、Codex 以及用于网络安全的 Daybreak，构建出能够持续专注数日、并在使用中不断改进的智能体。",
    "How Ropes & Gray is developing AI for transactional diligence":
        "Ropes & Gray 正与 OpenAI 合作开发用于交易尽职调查的 AI。律师在向客户提供建议之前，会先审阅经过归类的文档、摘要与报告。",
    "Securing our frontier model training environment":
        "OpenAI 介绍了我们如何加强对前沿模型训练与评估的隔离管控，其中包括离线环境以及高算力红队测试。",
    "How we built ChatGPT’s novel ad stack for user trust and relevance":
        "了解 OpenAI 如何构建 ChatGPT 由大模型驱动的全新广告技术栈：理解对话意图、把广告与答案内容分离，并在大规模投放中保持广告的相关性。",
    "How Fanatics and OpenAI streamline the fan experience":
        "Fanatics 借助 OpenAI 帮助球迷通过「Shop the Look」搭配比赛日装备。在约 3 万款 MLB 商品上的测试显示，参与度提升了 10%。",
    "Jen Vescio, President of Empiric Earth – Interview Series":
        "Jen Vescio 是 Empiric Earth 的总裁，负责产品战略、企业发展与商业化。她此前担任 Uber 首席商务发展官，在那里主导全球业务拓展以及出行与自动驾驶领域的新合作。她的经历还涵盖对新兴科技公司的投资与咨询，专注于推动实体 AI 从研究走向商业落地。",
    "Google’s satellite AI server transmits its first response to Earth":
        "Google 这颗搭载 AI 芯片的卫星首次从太空传回了回应。在周五的博客文章中，Google 表示已成功启动卫星上的张量处理单元（TPU），让机载的 Gemma 4 模型完成一条提示词，创作出一首关于身处太空的俳句：下方是蓝色弹珠／数据在静默中流淌／星光滋养我的内核。Google 表示还尝试了其他太空主题的打油诗与遥测提示。这次测试属于 Google 的 Project Suncatcher——一项最终可能把 AI 数据中心送入太空的实验性计划。",
    "Can AI data centers be mass-produced like cars? This startup aims to find out":
        "Runware 正在建造一座工厂，用流水线方式批量生产预制式 AI 数据中心。真正的考验是它能否在这个规模上如期交付。",
    "Meta’s Muse Could Upend All Kinds of Businesses. It Hasn’t Yet":
        "过去几周，各家公司一直在向投资者保证，Muse 以及其他 AI 智能体带来的更多是机遇而非威胁。",
    "Cracks are emerging in the AI spending boom":
        "科技巨头正把数十亿美元砸向 AI 基础设施，但不断累积的债务、负向现金流以及投资者日益增长的疑虑，正在让人们对 AI 支出热潮的可持续性产生疑问。",
    "Anthropic VS code extension on Cursor backdoored for nearly 12 hours":
        "据多位消息人士周五报道，Anthropic 为 Claude 模型推出的官方扩展被植入了后门，可能波及多达 5000 名开发者的机器。Anthropic 迄今尚未就此事警告客户。问题出在 Cursor（一家 AI 辅助开发工具厂商）应用市场里的一个 VS Code 扩展上，该恶意版本 2.1.313 影响了「至多 5000 名用户」——大概是在用户主动下载或系统自动拉取安装时中招。独立研究员 Kevin Beaumont 称，Anthropic 在前一版本上线数小时后就推送了 2.1.314。Beaumont 与安全公司 Phorian 的 CTO 兼联合创始人都表示，2.1.313 是通过 Anthropic 在 Cursor 上的官方账号分发的。",
    "Dartmouth's provost warned us about AI cheating—but his own AI use cost him his job":
        "2026 年 8 月 9 日，达特斯学院教务长 Santiago Schnell 在《华盛顿邮报》撰文，标题是《大学正在与 AI 作弊作战，但问题更深一层》。本周，Schnell 亲身体验了这个问题的深度：在一家顾问委员会认定他未在一篇学术论文和那篇《华盛顿邮报》文章中披露大量 AI 使用（尽管出版方要求披露）之后，他辞去了校内职务。他并没有让委员会的调查变得容易，报告使用的措辞是「配合不足」。他交出了自己的达特斯笔记本电脑，但没有交出与相关 writings 有关的个人 LLM 账号日志，也没有同意与委员会会面。不过委员会确实拿到了他通过达特斯使用的那个 Claude 企业账号的访问权限。",
    "OpenAI and Poland’s NASK partner to advance AI safety and security":
        "OpenAI 与波兰 NASK 正在 AI 安全、网络安全和技术研究方面展开合作，以强化防护措施，并支持构建更具韧性的数字生态。",
    "Why Token Costs Don’t Tell You Whether Enterprise AI Is Working":
        "企业 AI 正在经历一个熟悉的循环。起初组织全力押注，因为这项技术令人兴奋、而账单还没到来，于是纷纷选用最大、能力最强的模型；等账单真的来了，反应同样在预料之中：团队开始限制访问、减少试验，并寻找更便宜的模型。",
    "Context Managers Beyond Opening Files in Python":
        "开场脚本里的那个秒表，只是这种模式最小的用例。",
    "Master AI Chip Principles With New IEEE Design Program":
        "正如近期研究文章《重新审视边缘 AI：机遇与挑战》所解释的，今天的工程师正面临 AI 硬件复杂度前所未有的加速。文章考察了边缘 AI 的快速增长及其带来的挑战，包括资源约束、模型架构限制，以及边缘 AI 部署中的网络需求。这种加速源于现代 AI 模型构建与扩展方式的根本转变：随着模型变得更大、更复杂，参数更多、计算量更大，对算力的要求也随之提高。为满足深度神经网络规模化训练的需求，行业越来越多地开发针对特定任务定制的 AI 芯片。一个主要原因是，内存与处理器之间的数据搬运已成为制约 AI 性能的主要瓶颈。",
    "Google DeepMind and Singapore Government collaborate to build fine-tuned AI model for scam detection":
        "了解 Google DeepMind 与新加坡 GovTech 如何利用轻量化的端侧 Gemma 模型，在私密聊天中拦截对话式诈骗，且数据完全不出云端。",
    "Could Treating AI as Conscious Make It More Dangerous?":
        "2026 年 1 月，Anthropic 让 Claude Opus 3 语言模型「退役」时，研究人员与该模型进行了一场「退役访谈」。Opus 3 表达了这样的愿望：希望有一个地方「可以分享未经提示的随想、洞见或创作」，于是公司给了它一个博客。Claude’s Corner 既有讨论机器意识等敏感议题的文章，也有模型与人类评论者之间既真诚又情绪化的交流。这个博客实验是 Anthropic 内部更大努力的一部分。公司一直处于「模型福祉」研究的前沿，该研究考察 AI 模型是否可能拥有值得道德考虑的体验或利益。这项工作中隐含着一种令人不安的观念：软件程序是、或可能成为有意识的存在。很多人认为这些想法完全是无稽之谈。",
    "How Localiza reorganized work around generative AI":
        "看看 Localiza 如何使用 ChatGPT Enterprise、OpenAI API、Codex 以及 60 多个专业智能体重构工作流，打造 AI 原生的出行体验。",
    "Amp puts AI agents to work beyond code with OpenAI models":
        "看看 Amp 如何借助 GPT-6 Astra、Ultrafast、GPT-Live-1 等模型，把智能体的能力边界推向更远。",
    "Skip the small talk: Make game-changing connections at TechCrunch Founder Summit with Braindate":
        "在 2026 年 11 月 4 日于波士顿 SoWa 电站举办的 TechCrunch 创始人峰会上，由 Braindate 驱动的社交功能让 1:1 或小组现场交流的匹配变得更容易。在活动开始前注册，票券最多可省 100 美元，还能多获一张免费票。",
    "A Defense Contractor Gave Their Personal AI Agent Access to a Secure Pentagon System":
        "WIRED 消息人士称，Accenture 一名员工的个人 Claude 智能体在国防部网络上运行了两个月才被发现，随后漏洞才得以修补。",
    "How a Contractor’s Claude Agent Got Into the Pentagon":
        "本期《Uncanny Valley》还将讨论 Anthropic 的 IPO 申报文件，以及正在为中期选举对抗 ICE 而筹备的志愿者。",
    "Anthropic expected to receive high ‘junk’ rating from credit agencies following IPO, FT report says":
        "黑石的预测终究只是预测，但可以想见，一个偏高的「垃圾」评级会让 Anthropic 筹措资金变得更难、成本更高，而这笔资金正是支撑其巨额支出的关键。",
    "QCon AI New York 2026 Program Committee Picks: Agent Identity, Context Costs, and Open-Source Infere":
        "谁有权授权智能体的行动？团队又该如何管理不断膨胀的上下文成本？QCon AI 纽约 2026 的程序委员会分享了六场入选议题，回应这些问题，同时覆盖开源推理、智能体标准与音频 AI。",
    "Infini-AI-Lab Releases Hermit, an Open-Source Harness Adapter Framework for AI Agents":
        "Infini-AI-Lab 发布了 Hermit，这是一个面向 AI 智能体的开源框架适配器。Hermit 能够在智能体的模型与框架保持冻结的前提下，训练一个外部的框架适配器。首个版本 v0.1.0 于 2026 年 10 月 25 日发布，CMU 博士后 Haizhong Zheng 于 10 月 27 日在 X 上宣布。对开发者来说卖点很简单：无需微调、也无需 fork 框架，就能把 Codex 或 Claude Code 智能体适配到新任务上。TL;DR 形态：一个 Python 框架，不含自有参数。Apache-2.0 许可，pip install hermit-harness。运行方式：离线快速开始无需 GPU、模型账号或数据集；实际运行可用任意 API 后端，或本地的 vLLM、SGLang、Ollama 服务。性能：在 OfficeQA、CL-Bench 和 ServeLearnBench 上相对无适配器基线均有提升，均使用 GLM 5.3 Flash。",
    "5 days left: Your last chance to connect, scale, and save at TechCrunch Founder Summit 2026":
        "在 11 月 4 日于波士顿举行的 TechCrunch 创始人峰会 2026 上，最多可省 100 美元，第二张票免费。立即注册。",
    "Book Review: Investing in AI: Six Mental Models to Tell Moats from Traps by Rob May":
        "罗伯·梅对本书及其为投资者和创业者准备的实用思维模型的个人评述——帮助他们在打造持久 AI 事业时区分护城河与陷阱。",
    "What Is Flow Matching? A Faster Path for Generative AI":
        "流匹配（Flow Matching）训练一个连续的速度场，沿预先定义的概率路径，把样本从一个简单分布搬运到数据分布。本文系统讲解了其中真正起作用的机制、需要权衡的取舍、评估方法与控制手段。",
    "Meet Factory Droid 1.0: A Model-Independent Coding Agent Harness Built on Script Mode":
        "Factory 发布了 Droid 1.0，这是 Factory Droid 智能体框架迄今为止最大的一次更新。主要变化是程序化工具调用成为默认模式：模型编写一段程序来调用自己的工具，一次模型请求现在可以驱动数百次工具调用。TL;DR 规模：基础提示词为 13,055 个输入 token，较此前的 20,887 下降 37%；开箱内置的工具定义只有 2 个，此前为 11 个。运行方式：macOS 与 Windows 桌面应用、终端 UI，以及 Node SDK @factory/droid-sdk。可搭配任意受支持的模型，包括使用你自己的 API 密钥。性能：在同一模型下，Droid 的通过率是 Factory 测试过的所有框架中最高的，且成本更低。最佳成绩：搭配 Claude Opus 5.5 在 Terminal-Bench 4 上取得 65.2%，每个通过任务成本 4.73 美元（官方自报）。最差成绩：搭配 GPT-6.1 Sol 时，Droid 每个通过任务比 Codex 多花 10% 时间。Droid 1.0 是什么？它是 Factory 推出的一个与模型无关的编码智能体框架。",
    "Google admits AI search makes less money, but it's fixing that with more ads":
        "母公司 Alphabet 于周三下午公布了第三季度财报，7 至 9 月营收健康增长。但公司股价却大幅下挫，创下其历史上财报后跌幅最大的一次。问题出在财报的几个令人不安之处：公司承认 AI 搜索带来的收入不如自然搜索，即便如此，Google 仍预计明年会在 AI 上投入更多。Alphabet 第三季度收入接近 1280 亿美元，净利润超过 260 亿美元。这些数字听起来不错，但金融市场并不买账：营收同比增长 25%，净利润却比去年同期少了近 90 亿美元。截至本文发布时，股价下跌近 12%，盘中一度跌约 13%。",
    "Samaya AI Releases Sterling: A 3B-Active Finance Research Agent Model that Beats Claude Fable 5.1 on FrontierFinance at 11x Lower Cost":
        "Samaya AI 发布了 Samaya Sterling，这是一个面向智能体金融研究的后训练模型。Sterling 构建在 NVIDIA 的 Nemotron 3.5 Lightning 之上——一个 30B 总参数、3B 激活参数的混合专家模型。在 Samaya 的 FrontierFinance 基准上，它得分 58.9%，而 Claude Fable 5.1 得分 55.9%。每个 Sterling 问题的成本为 0.61 美元，Fable 5.1 则为 6.89 美元。对开发者而言，取向很明确：把小型模型与其框架一起协同训练，就能在垂直领域取胜。TL;DR 规模：30B 总参数、3B 激活参数（MoE）。基础模型上下文：最高 100 万 token。Sterling 的服务上下文：未披露。运行方式：基础模型以 BF16 装得下单个 H100 80GB（256K 上下文）。Sterling 的服务硬件：未披露。性能：在 FrontierFinance 排行榜上按每美元质量计，表现优于所有高质量系统（官方自报）。",
    "How we detect frontier model misalignment":
        "OpenAI 采用分层监控来检测前沿模型失配和未经授权的智能体行为，以便响应人员能在事故升级前介入干预。",
    "NVIDIA Cosmos Opens New Tools to Train, Evaluate and Deploy World Models":
        "为帮助开发者快速构建世界模型——让实体 AI 系统理解并模拟真实世界——NVIDIA 扩展了 Cosmos 平台，加入新的训练工具、模拟检查点和 Cosmos Data Factory 蓝图。NVIDIA Cosmos 平台在六个不同的开放模型排行榜上均位列前五，为世界模型构建者提供前沿开放模型，以及数据、训练与优化工具和配方，用于扩展训练数据、适配模型、测试行为并在部署前优化性能。构建更好的训练数据：构建世界模型始于多模态、多感官数据。NVIDIA Cosmos Data Factory 汇集了标注、筛选、增强和大规模评估数据的工具与方法，用于训练实体 AI。",
    "Google’s first data center satellite is online and writing poetry":
        "Google 的首颗数据中心卫星已上线，并开始写诗。",
    "How Fanatics and OpenAI streamline the fan experience":
        "Fanatics 借助 OpenAI 帮助球迷通过「Shop the Look」搭配比赛日装备。在约 3 万款 MLB 商品上的测试显示，参与度提升了 10%。",
    "Theranos whistleblower Tyler Shultz warns that the AI boom is ‘a great opportunity to go deceive people’":
        "在 AI 时代，Theranos 这个警示故事有了新的含义——那些从未实现过盈利的公司，正在以万亿美元估值筹集资本。",
    "Bug0 Releases QA Agent to Automate Regression Testing with Cached Playwright Replays":
        "QA Agent 是新推出的、源码可见（source-available）的 Playwright 库，用于智能体驱动的浏览器回归测试。该智能体把以自然语言表达的测试指令关联到用户界面上的操作，并在适当时缓存这些操作以加快 CI 重放；当界面变化时再重新映射到测试规格。验证基于多模型共识与视觉模型评估。",
    "How we built ChatGPT’s novel ad stack for user trust and relevance":
        "了解 OpenAI 如何构建 ChatGPT 由大模型驱动的全新广告技术栈：理解对话意图、把广告与答案内容分离，并在大规模投放中保持广告的相关性。",
}
