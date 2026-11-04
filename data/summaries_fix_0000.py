# -*- coding: utf-8 -*-
"""2026-11-02 00:00 例行巡检 —— 人工核对摘要定稿（增量）。

来源：独立审查代理对全库 258 条的增量抽检（重点 2026-10-31 及之后的
最新条目 53 条 + 早期随机抽样 25 条），再由主流程逐条比对英文原文后定稿。
本轮共修复摘要 20 处，问题类型：
    · 语义崩坏（否定倒置、指代错位、并列成分残缺、across 误作「之间」）
    · 术语与专名误译（endpoint 误作「终点」、Brian Niccol 误拼、
      physical AI 双译、petaflop 未本地化、fulfillment 未译、
      教宗/教皇称谓不统一、misalignment 生造词）
    · 抓取噪声残留（白皮书配图 alt 文本、营销 CTA「立即注册」「在现场价格
      上调之前完成注册」、票务促销句）
    · 摘要截断与信息缺失（Google 卫星俳句条丢失三个关键事实）
    · 语序混乱（同位语断裂、并列结构错位、半角标点混用）

键为英文原标题（与既有覆盖表同构，server.py 以英文标题做匹配）。
"""

SUMMARY_OVERRIDES = {
    # 语义崩坏：religious exemption from using AI = 获准免于使用 AI，
    # 原译「宗教豁免，禁止在工作场所使用人工智能」把豁免对象完全倒置
    'You don’t need to believe in a god to get a religious exemption from using AI at work':
        '肯塔基大学的管理者戴维·达尔曼最近获准在工作中免于使用 AI。',
    # 语义崩坏：across multiple AI providers = 向多家提供商表达，
    # 原译「多家人工智能提供商之间」把关系词方向搞反
    'Google Plans Support for Shared Robots.txt AI Training Control':
        '2026 年 10 月 30 日，Google 宣布计划在 robots.txt 中支持共享的 AI 训练控制信号，'
        '为网站所有者提供一种统一方式，一次性向多家 AI 提供商表达训练偏好。'
        '这一承诺与 Microsoft 和 OpenAI 在同一天发布的公告同步提出。'
        '该计划由 Google 搜索中心博客的一篇文章披露，作者是 Google 搜索倡导者约翰·穆勒（John Mueller）。',
    # 术语：Autodox/doxxing 双关需保留「人肉」含义；
    # Infostealer 统一本地化为「信息窃取」
    'Spooky New Infostealer Malware Uses AI to ‘Autodox’ Victims':
        '这款新近曝光的恶意软件名为「Volta-Autodoxer」，利用 AI 工具批量收集受害者数据，'
        '涵盖登录凭据、信用卡号、Discord 会话与 UberEats 收据。',
    # 语义崩坏：并列成分残缺，「审查发现和建议的修复」缺「问题」与「修复方案」
    'GPT-6.1 Sol helps CodeRabbit strengthen security across complex codebases':
        'CodeRabbit 使用 GPT-6.1 Sol 在复杂代码库中排查安全风险。'
        '其安全智能体可帮助开发者审阅发现的问题与建议的修复方案。',
    # 语义崩坏：Rob May 是作者而非自评者，角色错置
    'Book Review: Investing in AI: Six Mental Models to Tell Moats from Traps by Rob May':
        '本文由作者 Rob May 亲自评述其面向投资者与创业者的实用思维模型，'
        '帮助他们在打造可持续的 AI 业务时区分护城河与陷阱。',
    # 语义崩坏：looking past = 不再满足于；并修正 appositive 语序
    'Consumer Appetite for Personal AI Goes Mainstream':
        '对于许多消费者而言，人工智能的承诺与吸引力在很大程度上是个人化的。'
        '他们已经不再满足于通用工具，而是想了解这些技术将如何融入自己的日常生活。'
        '这些趋势与新一代可穿戴设备的出现同步发生——这些设备除了能调用强大的前沿模型，'
        '还内置了能够理解用户情境的智能。它们在哪里？它们看到和听到了什么？'
        '它们的习惯、偏好与日程是怎样的？这是一次令人惊叹的转向：从主要用来向用户推送'
        '手机通知的被动配件，转为主动的智能伙伴。智能手机不再是这一宇宙的中心；'
        '它依然极其重要，但在这个个人 AI 范式中，AI 就是用户界面。'
        '重心也随之转向你——用户本身。这些新技术令人兴奋。',
    # 专名误拼：Brian Niccol（原文），原译误作 Brian Nicicol；
    # 另修「识别参与会员」不成句
    'Starbucks wants to use AI to show you a ‘personalized digital menu’ at the drive-thru':
        '未来当你驶入得来速通道时，星巴克可能会为你展示一份个性化数字菜单。'
        '在周四的财报电话会议上，星巴克 CEO Brian Niccol 表示，'
        '公司将探索「在顾客抵达时识别其会员身份、展示个性化数字菜单、'
        '并让支付更加便捷」的体验——这一说法最早由 More Perfect Union 披露。'
        '这听起来与塔可钟正在试验的技术类似：该技术可以「按每一辆车」'
        '改变数字菜单屏上的布局、内容与视觉效果。',
    # 术语：endpoint = 端点，非「终点」；并修正语序
    'Cisco Talos Details VOLTA Infostealer’s LLM Victim-Ranking Stage':
        '2026 年 10 月 31 日，Cisco Talos 研究员 Ryan Fetterman 发表了针对 '
        'VOLTA-AUTODOXER 的分析。这是一款可自我删除的 Windows 信息窃取器，'
        '在大范围凭据窃取之后接续一个大型语言模型阶段，用于对每位受害者的'
        '可变现资产进行分级排序。Talos 将 VOLTA 描述为一款成熟的窃取器植入体，'
        '带有可选的 AI 集成层，并表示所观测到的每一个端点均由第三方掌控，'
        '不存在攻击者自有基础设施。',
    # 术语：教宗称谓统一为「十四世」；「为人工智能解除武装」是硬译
    'Pope Leo XIV Calls to “Disarm” AI, Urges Ban on Lethal Autonomous Weapons':
        '2026 年 10 月 30 日，教宗利奥十四世在梵蒂冈宗座宫枢机团会议厅发表讲话，'
        '呼吁解除人工智能的武装，并敦促 11 月齐聚日内瓦的各国采取具体步骤，'
        '推动禁止致命自主武器。',
    # 术语：physical AI 统一译作「物理 AI」（与 54a5bb0b、709a71b7 一致）
    'Jen Vescio, President of Empiric Earth – Interview Series':
        'Jen Vescio 是 Empiric Earth 的总裁，负责产品战略、企业发展与商业化。'
        '她此前担任 Uber 首席商务发展官，在 Uber 主导全球业务拓展以及出行与自动驾驶'
        '领域的新合作。她的经历还涵盖对新兴科技公司的投资与咨询，'
        '专注于推动物理 AI 从研究走向商业落地。',
    # 术语：physical AI 统一译作「物理 AI」
    'NVIDIA Cosmos Opens New Tools to Train, Evaluate and Deploy World Models':
        '为帮助开发者快速构建世界模型——让物理 AI 系统理解并模拟真实世界——'
        'NVIDIA 扩展了 Cosmos 平台，加入新的训练工具、模拟检查点和 '
        'Cosmos Data Factory 蓝图。NVIDIA Cosmos 平台在六个不同的开放模型排行榜上'
        '均位列前五，为世界模型构建者提供前沿开放模型，以及数据、训练与优化工具和配方，'
        '用于扩展训练数据、适配模型、测试行为并在部署前优化性能。'
        '构建更好的训练数据：构建世界模型始于多模态、多感官数据。'
        'NVIDIA Cosmos Data Factory 汇集了标注、筛选、增强和大规模评估数据的工具与方法，'
        '用于训练物理 AI。',
    # 术语：fulfillment 未译；并修正标点
    'NVIDIA Transforms European Retail, From Digital Discovery to Physical Operations':
        '欧洲零售商正把开放模型与物理智能应用于各类场景——从把推理成本降低 90% 的'
        '电商平台，到在数字孪生中模拟多支机器人车队协同作业的履约中心。'
        '开放模型带来的前沿成果：欧洲各地的零售企业与科技公司正借助 NVIDIA 加速的'
        '开放模型与前沿模型，推进智能体化商业、数字商品发现与零售研发。'
        'Shopify 对开放模型进行后训练，以极低的成本达到前沿级精度；'
        '其工程师使用 NVIDIA Megatron Bridge 库实现更快的微调，'
        '并用 NVIDIA NeMo RL 进行强化学习。Shopify 已为集成进 Sidekick'
        '（Shopify 面向商家的 AI 助理）的 GraphQL 子智能体，'
        '后训练了 NVIDIA Nemotron 3.5 Lightning。',
    # 术语：petaflop 未本地化；「一个单个」冗赘；顿号与半角逗号混用
    'Thin, Light and Built for Everything: NVIDIA RTX Spark Windows Laptops Gain New Models, Agent Tools and Games':
        'NVIDIA RTX Spark 支持开发人员、创作者和游戏玩家所需的轻薄笔记本电脑。'
        'RTX Spark 笔记本现已由 ASUS、Dell、HP、Lenovo、Microsoft 和 MSI 提供。'
        '这些强大的系统将 NVIDIA Blackwell RTX GPU 与 NVIDIA Grace CPU '
        '整合为单一超级芯片，最高配备 128GB 统一内存，并提供高达 1 PFLOPS'
        '（千万亿次浮点运算）的 FP4 AI 算力。这让 NVIDIA CUDA 平台、'
        'RTX 图形以及个人 AI 超算的能力，尽在可随身携带的高端 Windows 笔记本中。'
        '即将推出的 RTX Spark 更新包括：NVIDIA Nemotron 3.5 Transcribe，'
        '一个用于转录、说话人归属与翻译的开放权重语音模型，已可在 RTX Spark 上使用。'
        '此外还有 LFM3 开放模型家族，提供首日支持。',
    # 术语：misalignment = 对齐失配
    'How we detect frontier model misalignment':
        'OpenAI 采用分层监控来检测前沿模型的对齐失配和未经授权的智能体行为，'
        '以便响应人员能在事态升级前介入干预。',
    # 术语与标点：教宗称谓统一；半角引号与逗号位于中文引号后
    'Pope Leo calls for the disarmament of AI: ‘Machines are tools, not persons’':
        '教宗利奥十四世表示，人工智能系统应当被「解除武装」，并补充说，'
        '人类「有责任去引导、改变，并在必要时拒绝其应用」。'
        '在周五的教宗文告中，利奥鼓励联合国成员国在下个月日内瓦举行的会议上'
        '「采取具体措施禁止致命自主武器」。该演讲与利奥在 5 月份第一份重要'
        '教宗文件中提出的许多主张相呼应，那份文件强调了「保护人工智能时代的人类」。',
    # 语序与标点：闭合引号后误用半角逗号
    'Sam Altman sympathizes with mathematicians, but says OpenAI’s math onslaught won’t stop':
        '几个月来，OpenAI 以源源不断的 AI 生成结果轰炸数学家，'
        '首席执行官萨姆·阿尔特曼（Sam Altman）表示，他很同情那些'
        '疲于理清这一切的研究者。但他完全没有停下来的意思，'
        '反而暗示公司手中的「发现储备」里可能还有更多。'
        '「总体而言，我认为这个世界应当理解宇宙是如何运作的，」'
        '阿尔特曼在周四发布的 Cheeky Pint 播客节目中说道。'
        '「但我对这种方式确实抱有同理心。」',
    # 标点：句末多余逗号
    '"No human at the helm": Delaware plan would let AI agents run entire businesses':
        '美国众议员 James Comer（肯塔基州共和党）昨日在一封信中告诉特拉华州州长 '
        'Matt Meyer，特拉华州一项允许公司由 AI 智能体运营的提案，'
        '将帮助这些企业的人类所有者免于为 AI 所采取的鲁莽且有害行为承担法律责任。'
        '担任众议院监督与政府改革委员会主席的 Comer 对 Meyer 表示，'
        '该委员会「正寻求协助获取与州政府推动建立一种名为『人工智能公司』'
        '（Artificial Intelligence Company，AIC）的新型企业形式相关的文件」。'
        'Comer 说，这项提案极易被滥用。「我们担心特拉华州的 AIC 提案'
        '可能被用来保护实力强大的 AI 公司及其投资者，使其免于为鲁莽且有害的行为负责，'
        '同时也为那些躲在州级 AI 倡议背后、寻求反竞争性监管俘获的不透明力量提供保护」，'
        'Comer 在信中写道。',
    # 语序：同位语结构断裂，「注重用户隐私的 Ollie 其创始人」不成句
    'Ollie, a privacy-focused AI assistant, is shutting down':
        '随着越来越多的人工智能助理涌入市场，注重保护用户隐私的 AI 助理 Ollie '
        '的创始人表示，该产品将在一周内关停。',
    # 语序：同位语被误译成定语谓语
    'OpenAI to Honor Shared Robots.txt Signal for AI Training Preferences':
        '2026 年 10 月 30 日，OpenAI 宣布将遵循 robots.txt'
        '（网站用于表达其内容使用偏好的文件）中的共享信号，'
        '使网站运营者能够一次性向多家参与的提供商传达同一个 AI 训练偏好。',
    # 语序与标点：介词缺失；「把…带到」句式硬译
    'Apple Intelligence is finally coming to China with iOS 27.3':
        'Apple 将在中国推出 Apple Intelligence，该公司在其中文新闻室官网上宣布，'
        'MacRumors 报道。Apple Intelligence 的相关功能将首先在 11 月 4 日推出的 '
        'iOS 27.3 测试版中上线，完整的 iOS 27.3 正式版则计划于 12 月发布。'
        '此次发布并未将新版 Siri AI 带到中国。相反，Apple 正在推出一些'
        '早期的 Apple Intelligence 功能，如通知摘要、实时翻译、重写与校正工具、'
        '视觉智能，以及从照片中移除对象。',
    # 术语：law enforcement referrals 生造为「举报转介」
    'OpenAI Announces Community Safety Report and New Teen Weapons Limits':
        '2026 年 10 月 30 日，OpenAI 宣布发布首份聚焦暴力预防的社区安全报告，'
        '并将每半年更新一次；同时推出一系列新防护措施，限制青少年获取武器相关信息，'
        '并收紧 ChatGPT 对过往大规模袭击相关提问的处理。'
        '公司表示，2026 年第三季度共向执法部门转介了 200 多起案件线索。',
    # 抓取噪声：整段摘要为《e-Conomy SEA 2026》封面图 alt 文本译文，非新闻摘要
    'Southeast Asia’s digital economy to hit $368 billion':
        'Google 与淡马锡、贝恩公司联合发布的《e-Conomy SEA 2026》报告'
        '《构建智能经济》显示，东南亚数字经济规模预计将达 3680 亿美元，'
        '增长主要由 AI 普及、电子商务扩张与数字支付普及推动。',
    # 抓取噪声：营销 CTA「在现场价格上调之前完成注册」入正文；
    # 另修语序与专名（SoWa Power Station）
    '4 days left: How TechCrunch Founder Summit helps you make more useful connections to scale':
        '11 月 4 日，在波士顿的 SoWa Power Station（SoWa 电站），'
        '准备好迎接一整天，尽享有意义的社交机会、可落地的见解，'
        '以及可能改变你创意与创业走向的人际连接。',
    # 抓取噪声：营销 CTA「立即注册。」入正文
    '5 days left: Your last chance to connect, scale, and save at TechCrunch Founder Summit 2026':
        'TechCrunch 创始人峰会 2026 将于 11 月 4 日在波士顿举行，'
        '门票最高可省 100 美元，并可多获一张免费票。',
    # 抓取噪声：票务促销句入正文
    'Skip the small talk: Make game-changing connections at TechCrunch Founder Summit with Braindate':
        '在 11 月 4 日于波士顿 SoWa Power Station 举办的 TechCrunch 创始人峰会 2026 上，'
        '由 Braindate 驱动的社交功能让 1:1 或小组现场交流的匹配变得更容易。',
    # 摘要截断：26 字对 92 字，丢失「太空中首个 TPU」「Gemma 4 模型」
    # 「俗气的诗」三个关键事实，且把「数据中心卫星」误作「卫星」
    'Google’s first data center satellite is online and writing poetry':
        '太空中首个 TPU 已开始运行 Google DeepMind 的 Gemma 4 模型，并写起了颇为俗气的诗。',
}
