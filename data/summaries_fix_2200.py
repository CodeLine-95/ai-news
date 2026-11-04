# -*- coding: utf-8 -*-
"""2026-11-01 22:00 例行巡检 · 人工核对摘要覆盖表。

本轮聚焦全量 255 条中英对照审查发现的**结构性崩坏**条目——
这类问题不是单词替换能解决的（规则层改完仍然不成句、
或漏掉整段关键信息），必须逐条基于英文原文人工重写定稿。

分组说明：

【A. 术语级误译但句意尚完整】（规则层已在 translate.py 加确定性规则处理，
    此处仅对无法用规则覆盖的整句重写）
  - DoorDash：LLM 被译成「法律法规」，整句语义被带偏
  - DoorDash 收益通话 / 表格等专名直译
  - Starbucks：drive-thru 译成「车站」、More Perfect Union 意译
  - Intel 股价：末句「导致 PC 价格上。」被截断
  - Sapan Pandya：master's degree 译成「学士学位」
  - OpenAI 机器人协助项目：ChatGPT for Teens 直译

【B. 整段语义崩坏 / 主谓错位】（必须人工重写）
  - Tesla EV 冠军：「路德斯特跳过了空中」「这是一项流传的戏」
  - NVIDIA DSX：「从子站到架子」「电力现在是基础设施中最大的瓶」
  - Anthropic 心智模型：缺主语，「Claude 编码团队现在在…如何审查代码」
  - AI Adoption ROI：「在被压力迫以展示」
  - 机器人安全功能：两句粘连，谓语悬空
  - 未来公司：「人工智能如何进入 org 图表下，旁边和我们之间。」
  - 青少年 AI：「学院规划师即将到达青少年 ChatGPT」
  - Oracle：「转化为与 ChatGPT Work 和 Codex 的快速，可重复的工作流程」
  - ServiceNow：「带入 ServiceNow 和 ServiceNow 工作流入 ChatGPT」

【C. 抓取噪声残留 + 逐句直译】（The Verge 系正文混入站点元素）
  - AI Tamagotchi：「链接查看」（原文 View Link）、「5G 移动电台」、
    「可爱的形图像」、「远程摄像头查看器」、「它真的与 Muse 谈话」
  - IEEE Capitol Hill：「阅读更多」（原文 as he read more about...，
    此处 read more 是正文动词，非样板语，但中文读感歧义）

【D. 长文本退化 / 断句丢失】
  - Kazakhstan NVIDIA：正文中间混入「23,」日期碎片、「公共火聊天」
  - Revolut 欧洲金融：「普拉格马」、引号破碎
  - Vibe genes：结尾混入「拥」字碎片
  - Prime Intellect：规格段缺失 Performance 数据
  - ChatGPT 在线存储：multi-tenancy 译成「多租金」

【E. 专名误译】
  - Fujifilm：「富士电影公司」
  - Atlassian：「亚特拉斯人」
  - Genie 4：resting on its laurels 译成「依靠自己的荣誉」
  - open source：译成「公开源」
  - honor robots.txt：译成「授予」
  - robots.txt：译成「网站的机器人内部」
  - NBC News：译成「美国广播公司新闻」
  - Apple Brings First Apple Intelligence：品牌还原残留「果表示」
  - C-BRAIN：「人智能联盟」
  - multi-tenancy / single digits / laurels / drive-thru / administrator
  - on net / Princeton / College Planner / 等等

键为英文原标题（与 server.py 的 apply_summary_overrides 约定一致）。
"""

SUMMARY_OVERRIDES = {

    # ---------- A. 术语级误译（整句重写）----------

    "Basically no one is using AI agents for their DoorDash orders":
        "随着 AI 工具与智能体持续渗透数字生活的方方面面，"
        "许多公司正试图用大语言模型（LLM）改善人们在互联网上购买商品与服务的体验。"
        "但迄今为止，真正用上这些能力的人少之又少——"
        "至少在「用外部 AI 智能体点外卖配送应用 DoorDash」这件事上如此。"
        "在周四的第三季度财报电话会议上，"
        "DoorDash 联合创始人兼 CEO Tony Xu 回答分析师提问时提到，"
        "「这些 AI 智能体上线运行以来，一共只产生了数百笔订单。」"
        "Xu 用了极为克制的说法，把这称为一家"
        "「仅在 2026 年第三季度就处理了近 10 亿笔订单」的公司而言"
        "「非常低的使用场景」。",

    "Sapan Pandya, Senior Software Engineer and IEEE Senior Member – Interview Series":
        "Sapan Pandya 是一名常驻新泽西州的高级软件工程师、IEEE 高级会员，"
        "在弹性分布式事务系统领域有十余年经验。"
        "他的工作横跨事务完整性、软件与物理设备之间的集成、"
        "生产环境故障排查，以及受监管环境下的部署验证。"
        "他拥有 Stevens Institute of Technology 计算机科学硕士学位，"
        "并参与学术评审与技术研究工作。",

    "Apple Brings First Apple Intelligence Features to China in iOS 27.3":
        "在一份日期为 2026 年 10 月 31 日、发布于 Apple 中国新闻室的新闻稿中，"
        "Apple 宣布首批 Apple Intelligence 功能即将面向中国用户开放。"
        "这些功能将于 2026 年 11 月 4 日随最新 iOS 开发者测试版开放测试，"
        "并于 2026 年 12 月随 iOS 27.3 正式版公开发布。"
        "Apple 表示，在取得必要批准之后，其他平台也将陆续获得支持。",

    "Intel’s stock crashes, knocking $12B from government’s stake":
        "随着 AI 行业大量吞噬内存等零部件、推高 PC 价格，"
        "Intel 正受到 PC 销量下滑的冲击。",

    "Helping teens learn, plan, and shape the future of AI":
        "升学规划助手（College Planner）即将上线 ChatGPT 青少年版，"
        "帮助学生管理大学申请；同时还将新增闪卡、小测验，"
        "并成立青少年 AI 委员会。",

    "Starbucks wants to use AI to show you a ‘personalized digital menu’ at the drive-thru":
        "未来当顾客驶入星巴克的得来速通道时，"
        "星巴克可能会为其展示一份个性化数字菜单。"
        "在周四的财报电话会议上，星巴克 CEO Brian Nicicol 表示，"
        "公司将探索「在顾客到店时识别参与会员、展示个性化数字菜单、"
        "并让支付更加轻松」的体验——"
        "这一说法最早由 More Perfect Union 披露。"
        "这听起来与塔可钟正在试验的技术类似："
        "该技术可以「按每一辆车」改变数字菜单屏上的布局、内容与视觉效果。",

    # ---------- B. 整段语义崩坏（人工重写）----------

    "Tesla gave up the EV crown. Now it wants to win the autonomy race.":
        "埃隆·马斯克那辆「会飞」的 Roadster 电动跑车本月腾空翻腾，"
        "这场表演在全球范围内 viral 传播。"
        "但他更大的赌注，是改变 Tesla 的赚钱方式——整个汽车行业正手忙脚乱地追赶。"
        "在这场由马斯克旗下 SpaceX 研发的压缩气体推进器实现的表演五天后，"
        "他透露两家公司正在探索一项合并，"
        "以加速他进军自动驾驶领域的步伐。"
        "这背后赌的不只是技术竞赛。"
        "汽车行业本已在应对日益加剧的中国竞争压力，"
        "如今它们希望跳出以卖车为核心的商业模式，"
        "转向同时能从软件和 AI 驱动的服务中获得持续性收入的新形态。",

    "How Companies Are Using NVIDIA DSX to Break the Power Bottleneck":
        "全球各地的企业正基于 NVIDIA DSX AI 工厂平台，"
        "把电网与 AI 工厂当作一个整体系统来规划、仿真和运行，"
        "覆盖从变电站到机架的每一个环节。"
        "它们之所以采用该平台，是因为正面临一个尖锐的现实问题："
        "电力已经成为基础设施领域最大的瓶颈。"
        "超过 3000 亿美元的设备处于积压待交付状态，"
        "美国并网排队队列中还积压着超过 200 吉瓦的项目。"
        "造成这一瓶颈的一个根本原因，是系统之间长期相互割裂："
        "电网、厂房设施与其中的算力长期以来被各自独立设计，"
        "从而为延期、风险与产能搁浅埋下了条件。",

    "Anthropic Says Nobody Needs a Mental Model of Claude Code. Practitioners Are Testing That":
        "Anthropic 公布了 Claude Code 团队如今如何审查代码——"
        "在 Claude 已能编写约 90% 代码的情况下。"
        "其中有一个说法是：没有人会在脑中保留整个代码库的完整心智模型。"
        "该文记录了一次拉取请求（pull request），"
        "它在一夜之间经历了超过五十轮审查；"
        "其中一名评审者把大部分精力都花在已有代码上；"
        "以及一项团队自称目前尚未具备的控制手段。",

    "AI Adoption Is Up. But Is Business Performance?":
        "企业正努力把 AI 投入转化为有意义的回报。"
        "使用量在增长，但只有 13% 的组织报告从 AI 中获得了显著的转型价值。"
        "这种落差应当促使管理者退一步反思："
        "自己衡量的究竟是「活动量」，还是「真实改变」。"
        "在需要展示明确 AI ROI 的压力下，"
        "组织往往转而采用那些容易汇报的指标，"
        "比如工具使用量、活跃用户数或采用率。",

    "Your Robot’s Safety Functions Already Work. What If the Input Lies?":
        "移动机器人在走廊里为行人减速，协作机械臂在工人靠近时放缓动作，"
        "人形机器人会停下让路人先行。"
        "每一种反应都依赖关于机器人或其周边环境的信息："
        "距离读数、位置估计，或停止信号。"
        "但如果其中某个输入是错的，而机器人依然按设计做出反应，会怎样？"
        "移动机器人把走廊判断为通畅，此时仍有人站在其中；"
        "机械臂误判工人距离更远；"
        "人形机器人在有人横穿其路径时没有收到停止信号。"
        "每一种情形下，一次故障都可能造成这种错配，蓄意操纵同样可以。"
        "在 VicOne LAB R7 中，我们考察被操纵的输入如何改变机器人行为，"
        "以及这对那些本应保障人身安全的系统意味着什么。",

    "The future of the firm":
        "AI 将如何进入组织架构图——位于我们之下、身旁，还是之间。",

    "How Oracle turns days of work into minutes with ChatGPT and Codex":
        "在招聘、工程与运营等各个领域，"
        "Oracle 正借助 ChatGPT Work 与 Codex，"
        "把专家知识转化为快速、可重复执行的工作流。",

    "OpenAI and ServiceNow expand partnership across enterprise workflows":
        "OpenAI 与 ServiceNow 扩大合作，"
        "既把 OpenAI 的模型与智能体引入 ServiceNow，"
        "也把 ServiceNow 的工作流带入 ChatGPT 与 Codex。",

    "Bringing the Spark to Europe: Local Intelligence Powers Next Wave of Agents":
        "在 GTC 柏林峰会上，NVIDIA 正展示其全套本地 AI 硬件。"
        "上周发布的 RTX Spark 可在 Windows PC 上运行个人智能体；"
        "DGX Spark 支持开发者在 Linux 上构建并扩展应用；"
        "DGX Station 则服务于在 Linux 上运行前沿工作负载的企业团队，"
        "其 Windows 版本将于 12 月推出。"
        "同期发布的还有：Underdog Desktop Agent 现已支持 RTX Spark；"
        "64GB 版本的 DGX Spark 将于 10 月 15 日（周五）开售。",

    # ---------- C. 抓取噪声残留 + 逐句直译 ----------

    "I built an AI Tamagotchi before Meta could":
        "扎克伯格的 Meta 给 AI 配上了一张软乎乎的小脸，"
        "让它看起来可爱至极——这个节日季，他想卖给你一枚 Muse Charm 挂件，"
        "让你像携带拓麻歌子一样随身带着自己的欢乐 AI 助手。"
        "但我不会买，因为我们家已经有一个 Muse Charm 了。"
        "它只花了 50 美元，而我认定这次体验值回票价。"
        "我做的这个版本没有摄像头，也没有 5G 蜂窝通信模块，"
        "但它确实能和 Muse 对话，也有可爱的头像。"
        "它还能当口袋手表和远程取景器，"
        "并且（理论上）能控制我的智能家居——"
        "只要我给它塞进足够多的 vibe 代码。",

    "Why Engineers Should Brave Capitol Hill":
        "常驻圣安东尼奥的软件工程师 Nikhil Jathar 第一次前往华盛顿特区，"
        "为联邦政府支持技术教育与科研经费发声时，对这个机会感到受宠若惊。"
        "那是 2025 年春天——他落脚美国不久之后，"
        "便收到了 IEEE-USA 组织的年度国会参观日邀请。"
        "「我的第一反应是，『哇，我要去参观国会了，』"
        "Jathar 说道。他是商业软件公司 AvanSaber 的 CTO，"
        "该公司由他于 2014 年联合创办。"
        "当时他并没有代表公司的具体游说诉求，"
        "但这个面向全体美国 IEEE 会员发出的邀请吸引了他——"
        "随着他读到更多关于国会参观的信息，他的动机愈发强烈。"
        "他意识到：「我得试试。我想看看它能走到哪一步。」"
        "那么，你的诉求是什么？国会工作人员期待倡导者给出清晰的诉求。",

    # ---------- D. 长文本退化 / 断句丢失 ----------

    "Kazakhstan Expands Compute for Its AI Future":
        "哈萨克斯坦的 AI 生态正在从基础设施规划走向实际部署，"
        "这一转变贯穿 AI 技术栈的每一层——从基础设施到模型再到应用。"
        "以下这批公告与 NVIDIA 创始人兼 CEO 黄仁勋访问阿斯塔纳同期发布，"
        "显示出该国加速算力供给的持续增长，"
        "以及由此带来的对下一代算力需求的攀升。"
        "10 月 23 日（周五），NVIDIA 创始人兼 CEO 黄仁勋访问阿斯塔纳，"
        "在阿科尔达总统宫会见总统卡西姆-约马特·托卡耶夫，"
        "并与哈萨克斯坦人工智能与数字发展部部长、"
        "副总理扎斯兰·马季耶夫一同参加 Alem.AI 项目的公开炉边对话。",

    "Leading European Financial Services Organizations Embrace Open Models to Build Proprietary Intelligence":
        "在 GTC 柏林峰会上，银行、支付公司与金融数据服务商"
        "正在展示生产级智能的样貌——基于 NVIDIA 加速计算，"
        "由开放权重模型驱动，并运行在各自的自有基础设施上。"
        "Revolut 正基于单一基础模型 PRAGMA 重建其技术栈，"
        "该模型同样由 NVIDIA 加速计算驱动。"
        "借助 NVIDIA cuDF 工具包与运行在 NVIDIA Blackwell Ultra GPU 上的 "
        "Dynamo-Triton 软件，Revolut 正将 PRAGMA 推向生产环境，"
        "先服务 8000 万初始客户，并按 3 倍规模进行扩展设计。"
        "「Revolut 每天处理数十亿笔交易——机会一直都在，"
        "但真正的问题是：基础模型能否在这种规模下、跨业务域地运行。"
        "PRAGMA 回答了这个问题。」Revolut 的 AI 负责人 Pavel Nesterov 表示。",

    "Vibe genes? Natural(ish) language comes to protein, genome design software":
        "蛋白质设计工具或许正变得越来越精密，"
        "但要让它们真正发挥作用，你仍然需要对蛋白质结构有精细的理解。"
        "这可能包括把酶的作用机制了解透彻，精确到特定氨基酸的位置，"
        "以及同样占据催化区域的水分子位置。"
        "一旦指定了这些，工具便能围绕该目标搭建出蛋白质的其余部分。"
        "不过，一个总部位于中国的大型研究团队决定把蛋白质设计带给大众，"
        "他们做出了一款可用自然语言提示来生成指定功能蛋白质的工具。"
        "如果你以「做出能工作的蛋白质」为成功标准，"
        "那成功率恐怕不算高——但他们确实把活干成了。"
        "在另一则公告中，Hugging Face 宣布它现在托管着一款"
        "在 DNA 层面做类似事情的工具。",

    "Prime Intellect Releases Prime Mega MoE: Trainable Fused MoE Kernel, 3.11x Faster Forward Pass":
        "Prime Intellect 发布了 Prime Mega MoE，"
        "这是对 DeepSeek 融合式 Mega MoE 内核的训练扩展。"
        "DeepSeek 的内核只能执行前向传播，"
        "Prime Intellect 补上了快速的重叠反向传播，"
        "使这一融合内核不仅可用于推理，也可用于训练。"
        "在其 prime-rl 训练器中，Qwen3 MoE 模型的完整训练步最高提速 34%；"
        "相比 TorchTitan，收益可达 55%。"
        "对于训练混合专家（MoE）模型的团队而言，"
        "这意味着 GPU 时长的直接削减。"
        "TL;DR 形态：一个 GPU 内核，而非模型。"
        "测试模型：Qwen3-30B-A3B 与 Qwen3-235B-A22B（128 专家、top-8 路由）。"
        "运行平台：NVIDIA Hopper（分块式 FP8）与 Blackwell（MXFP8）GPU，两者均支持 BF16。"
        "公布的数字基于 8×H200 节点、32 至 128 块 GPU。"
        "性能：相比 prime-rl 基线，完整训练步快 32% 至 34%；相比 TorchTitan 快 48% 至 55%。",

    "Rapidly scaling online storage to serve over 1 billion ChatGPT users (Part II)":
        "了解 OpenAI 如何借助可靠的多租户架构、全局缓存与 Azure Cosmos DB "
        "扩展 Habitat 的规模，为超过 10 亿 ChatGPT 用户提供快 12 倍的读取速度。",

    # ---------- E. 专名误译 ----------

    "Fujifilm to boost tape production 5x as AI fuels archiving demand":
        "在周四发布的一份声明中，富士胶片表示将投资约 100 亿日元"
        "（约合 6300 万美元），"
        "将其磁性数据带的产能提升至五倍——"
        "而磁性数据带正是 AI 时代一个出人意料的受益者。"
        "富士胶片将归档需求的激增归因于生成式 AI 的普及，"
        "并称这正在全球范围内带来数据需求的「指数级增长」。"
        "此次五倍的产能提升以 2025 财年的产量为基准。"
        "对神奈川工厂小田原厂区的这笔投资，"
        "将使该厂成为「富士胶片迄今为止在专用 LTO 数据带设施上的最大单笔投资」。"
        "项目将覆盖 2026 至 2028 财年，用于扩建产能并增加人员，"
        "主要生产最新一代的「FUJIFILM LTO Ultrium10」数据带。",

    "Atlassian and OpenAI expand partnership to turn enterprise knowledge into action":
        "Atlassian 与 OpenAI 扩大合作，"
        "把前沿模型与企业知识连接起来，"
        "帮助团队规划、构建并交付工作。",

    "DeepMind unveils Genie 4 world model promising more realistic physics and humans":
        "去年，Google DeepMind 推出 Genie 3 世界模型，"
        "一度令游戏类股票重挫。"
        "此后，世界模型成为全球 AI 实验室的重点方向之一，"
        "但 Google 并未躺在功劳簿上。"
        "研究人员一直在打造升级版模型，几乎在每个方面都优于 Genie 3。"
        "而且只要付给 Google 足够多的钱，你或许很快就能用上 Genie 4。"
        "Genie 4 的输出看起来仍然像一款电子游戏，"
        "这正是 Genie 3 当初在游戏行业引发巨大震动的原因。"
        "不过 DeepMind 并不这么看。"
        "按照 Google 的说法，世界模型是迈向通用人工智能（AGI）的关键一环："
        "它构建出一个虚拟世界，却不需要预渲染环境，"
        "也不需要为交互元素编写程序。",

    "Patch the Planet: global response coordination as agents uncover critical vulnerabilities":
        "Patch the Planet 把安全研究员、维护者与事件响应人员连接起来，"
        "共同应对开源生态中的关键漏洞。",

    "The biggest names in AI are backing a new way to opt out of scraping":
        "据 Search Engine Roundtable 此前报道，"
        "OpenAI、Google、Microsoft 与 Anthropic 表示将采用一项新标准，"
        "出版商可借此选择退出被 AI 抓取。"
        "借助这一机制，出版商可以在多家 AI 公司上一次性声明自己的"
        "AI 训练偏好，而不必逐家单独设置。"
        "这项共享的「policy token」信号由 Anthropic 标准技术负责人 Kevin Kelley 提出，"
        "是互联网工程任务组（IETF）推动的一项工作。"
        "它将以网站 robots.txt 文件的一部分形式存在。",
    "Making it easier for websites to express AI training preferences":
        "OpenAI 将遵循共享的 robots.txt 信号，"
        "帮助网站运营者向参与的服务商传达自己的 AI 训练偏好。",

    "Highway thieves are spoofing GPS to steal millions in data center-bound cargo":
        "公路窃贼正在使用精心设计的数字手段，"
        "调查人员担心，这让盗取满载数百万美元数据中心设备的货车变得轻而易举。"
        "NBC News 采访了「多位为执法部门提供建议的行业领袖、顾问与调查人员」，"
        "他们正在侦破迄今规模最大的几起案件，"
        "并报道称自 6 月以来，窃贼已「劫走超过 1 亿美元的数据中心货物」。"
        "他们的作案手法如下：首先，窃贼入侵货运经纪人在运单发布网站上的账户，"
        "发布虚假运单以吸引真实报价，"
        "随后向任何响应的承运公司发送恶意链接。"
        "一旦受害者点击，窃贼便植入软件控制其账户，"
        "开始对真实的货运订单出价。",

    "Pope Leo XIV Calls to “Disarm” AI, Urges Ban on Lethal Autonomous Weapons":
        "2026 年 10 月 30 日，教宗利奥十四号在梵蒂冈宗座宫枢机团会议厅发表讲话，"
        "呼吁为人工智能解除武装，"
        "并敦促 11 月齐聚日内瓦的各国采取具体步骤，"
        "推动禁止致命自主武器。",

    "How AI Is Changing the Pace of Discovery for Millions Living With Dementia":
        "如今全球有 5700 万人与痴呆症共处。"
        "对于致力于帮助他们的研究者而言，"
        "障碍不在于不够努力——"
        "而是数据过多、能够综合这些数据的专家太少，"
        "加上研究发现的节奏已无法跟上疾病进展。"
        "神经退行性疾病生物医学研究与人工智能联盟（C-BRAIN）"
        "正与 NVIDIA 合作，用 AI 改变这一局面。"
        "阿尔茨海默病是当今最突出的全球健康挑战之一，"
        "每年新确诊痴呆症病例超过 1000 万例。"
        "尽管过去 15 年美国国立卫生研究院的资助增长了 7 倍、"
        "达到每年 39 亿美元，"
        "但迄今仍未找到能够阻止、预防或逆转这种疾病的治疗方法。",

    "Beyond the AI Pilot: Turning Customer Data into Personalized Commerce That Scales":
        "企业对 AI 的热情已经跑在企业实际成果的前面。"
        "斯坦福《2026 AI 指数》报告显示，"
        "2025 年有 88% 的组织用上了 AI，"
        "但 AI 智能体在几乎每一个业务职能中的采用率仍停留在个位数。"
        "试验与价值之间的距离依然很大，"
        "而且在客户体验上尤为明显、具体。"
        "要理解这一落差为何存在，有两个关键点值得考虑。"
        "第一是组织在 AI 方面的成熟度。",

    "How Oracle turns days of work into minutes with ChatGPT and Codex":
        "在招聘、工程与运营等各个领域，"
        "Oracle 正借助 ChatGPT Work 与 Codex，"
        "把专家知识转化为快速、可重复执行的工作流。",

    "pgvector vs. Dedicated Vector Databases: A Production Benchmark":
        "在一台典型的笔记本电脑上运行这套测试，"
        "两个系统报告的延迟都在个位数到数十毫秒之间，"
        "具体数字很大程度上取决于你的 CPU、可用内存，"
        "以及当时机器上还在跑的其他负载。",

    "Airbnb Cuts Recommendation Staleness from 2 Days to Seconds with Chronon":
        "Airbnb 为其 Chronon 特征平台增加了 Push Mode 与 "
        "Near Real-Time Model Transform，"
        "可在数秒内更新基于序列的推荐嵌入。"
        "该架构把嵌入陈旧度从接近两天降至不到一分钟，"
        "离线 NDCG 提升 1.67%，"
        "线上测试中未取消的订单量则增加了约三分之一个百分点。",

    "The focus on AI safety disasters ignores everyday harms":
        "想想技术政策中被当作成功的东西。"
        "一家 AI 公司承诺它的聊天机器人不会鼓励自杀；"
        "一个社交平台让儿童更难买到芬太尼。"
        "这些都是重要的保护措施，本就应该一直存在。"
        "但企业可以在满足这些低门槛的同时，"
        "继续制造那些让年轻人依赖模拟陪伴、"
        "或困在以让人不断下滑为设计目标的信息流里的产品。"
        "长期以来，我们允许关于技术的争论被产品最坏的可能后果所定义，"
        "却极少讨论它每天都在造成的那些隐性伤害。"
        "当我们进入一个由强大 AI 产品定义的时代，"
        "就应当要求科技行业做得不止于处理灾难性伤害。",

    "What Is Chunking in RAG? How Document Splitting Shapes Answer Quality":
        "分块（Chunking）把源材料切分成可检索的单元，"
        "这些单元的边界与元数据强烈影响 RAG 系统能够找到哪些证据、"
        "以及能把哪些证据一并呈现出来。"
        "本文梳理了在实际落地中真正重要的机制、权衡取舍、评估方法与管控手段。",

    "Into the Omniverse: How Developers Turn Ideas Into Simulations With Frontier AI Agents":
        "把一个仿真创意变成可运行的应用，"
        "意味着组装资产、连接物理与渲染，并检查场景表现是否符合预期。"
        "开发者正将前沿 AI 模型与 NVIDIA Omniverse 库结合起来完成这项工作——"
        "用于探索场景、排查故障并改进设计。"
        "开发者通过自然语言指令引导 AI 智能体，复核结果并指导修改。"
        "Omniverse 库提供 GPU 加速的物理、渲染与传感器仿真能力。"
        "探索下方项目，看看 GPT-6 Astra 等前沿 AI 模型如何落地实践，"
        "并关注 NVIDIA 团队和整个生态开发者带来的新案例。",
}
