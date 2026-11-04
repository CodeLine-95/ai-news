"""本轮（17:00 例行巡检）人工核对结果：标题级覆盖。

覆盖标准：
    1) 标题语义与英文原文不符（主语/数字/术语错位）；
    2) 术语规则无法修复的整句崩坏；
    3) 专有名词意译失真且不在 BRAND_TERMS 触发词覆盖范围内。

键为英文原标题（严格一致），值为人工核对后的中文标题。
"""

TITLE_OVERRIDES = {
    # ---- 数字量级错位：$1T = 1 万亿美元，原译「1 万美元」差 4 个数量级 ----
    "AWS will be a $1T business, Jassy says — but first, it will spend big":
        "Jassy 称 AWS 将成长为 1 万亿美元营收的业务，但首先它得继续大笔投入",
    # ---- 标题截断 / 主语丢失 ----
    "Can AI data centers be mass-produced like cars? This startup aims to find out":
        "AI 数据中心能否像汽车一样量产？这家初创公司想找到答案",
    "Meta’s Muse Could Upend All Kinds of Businesses. It Hasn’t Yet":
        "Meta 的 Muse 可能颠覆各类商业模式，但目前尚未做到",
    "Google’s satellite AI server transmits its first response to Earth":
        "Google 的卫星 AI 服务器首次向地球回传响应",
    "AI Adoption Is Up. But Is Business Performance?":
        "AI 采用率在上升。但业务表现真的跟上了吗？",
    "Google admits AI search makes less money, but it's fixing that with more ads":
        "Google 承认 AI 搜索赚钱不如自然搜索，正打算用更多广告来弥补",
    "The EU’s next chapter in AI is agentic":
        "欧盟 AI 的下一章是智能体化",
    "Could Treating AI as Conscious Make It More Dangerous?":
        "把 AI 当作有意识的存在，会不会让它更危险？",
    # ---- 术语错位 ----
    "How AI Is Changing the Pace of Discovery for Millions Living With Dementia":
        "AI 正在如何改变数百万痴呆症患者的疾病研究节奏",
    "I Gave My Blood to the AI Death Clock":
        "我把我的血献给了 AI 死亡时钟",
    "Franchisee reconciles cash in 94% less time with ChatGPT Work":
        "加盟商用 ChatGPT Work 将现金核对时间缩短了 94%",
    "How Third Moment Research runs 10,000 agents for 36+ hours":
        "Third Moment Research 如何让 1 万个智能体连续运行 36 小时以上",
    "How Ropes & Gray is developing AI for transactional diligence":
        "Ropes & Gray 如何与 OpenAI 合作开发用于交易尽职调查的 AI",
    "Securing our frontier model training environment":
        "守护我们的前沿模型训练环境",
    "How we built ChatGPT’s novel ad stack for user trust and relevance":
        "我们如何构建 ChatGPT 的全新广告技术栈，以兼顾用户信任与相关性",
    "How Fanatics and OpenAI streamline the fan experience":
        "Fanatics 与 OpenAI 如何让球迷观赛体验更顺畅",
    "Jen Vescio, President of Empiric Earth – Interview Series":
        "Empiric Earth 总裁 Jen Vescio 访谈系列",
    "Cracks are emerging in the AI spending boom":
        "AI 支出热潮正出现裂痕",
    "Why Token Costs Don’t Tell You Whether Enterprise AI Is Working":
        "为什么 token 成本说明不了企业 AI 是否真的见效",
    "Context Managers Beyond Opening Files in Python":
        "Python 中打开文件之外的上下文管理器",
    "Master AI Chip Principles With New IEEE Design Program":
        "用全新 IEEE 设计课程掌握 AI 芯片核心原则",
    "Google DeepMind and Singapore Government collaborate to build fine-tuned AI model for scam detection":
        "Google DeepMind 与新加坡政府合作构建用于诈骗检测的微调 AI 模型",
    "How Localiza reorganized work around generative AI":
        "Localiza 如何围绕生成式 AI 重构工作方式",
    "Amp puts AI agents to work beyond code with OpenAI models":
        "Amp 借助 OpenAI 模型让 AI 智能体在代码之外也投入实战",
    "Skip the small talk: Make game-changing connections at TechCrunch Founder Summit with Braindate":
        "别再寒暄：在 TechCrunch 创始人峰会上用 Braindate 建立真正有价值的连接",
    "Anthropic VS code extension on Cursor backdoored for nearly 12 hours":
        "Anthropic 的 VS Code 扩展在 Cursor 上被植入后门近 12 小时",
    "Dartmouth's provost warned us about AI cheating—but his own AI use cost him his job":
        "达特斯学院教务长曾警告我们 AI 作弊问题，但他自己的 AI 使用却让他丢了工作",
    "OpenAI and Poland’s NASK partner to advance AI safety and security":
        "OpenAI 与波兰 NASK 携手推进 AI 安全与网络安全",
    "Anthropic expected to receive high ‘junk’ rating from credit agencies following IPO, FT report says":
        "据《金融时报》报道，Anthropic 在 IPO 后预计将获得信用机构较高的“垃圾”评级",
    # 注意：源站标题本身被截断为 "...Open-Source Infere"（Inference 缺尾），
    # 覆盖键必须与 data/news.json 中的原标题严格一致，否则不会命中。
    "QCon AI New York 2026 Program Committee Picks: Agent Identity, Context Costs, and Open-Source Infere":
        "QCon AI 纽约 2026 组委会精选议题：智能体身份、上下文成本与开源推理",
    "Infini-AI-Lab Releases Hermit, an Open-Source Harness Adapter Framework for AI Agents":
        "Infini-AI-Lab 开源 Hermit：面向 AI 智能体的框架适配器",
    "A Defense Contractor Gave Their Personal AI Agent Access to a Secure Pentagon System":
        "国防承包商让个人 AI 智能体接入了五角大楼机密系统",
    "How a Contractor’s Claude Agent Got Into the Pentagon":
        "承包商的 Claude 智能体如何进入五角大楼？",
    "5 days left: Your last chance to connect, scale, and save at TechCrunch Founder Summit 2026":
        "仅剩 5 天：在 TechCrunch 创始人峰会 2026 连接、扩张并省钱",
    "How we detect frontier model misalignment":
        "我们如何检测前沿模型失配",
    "Meet Factory Droid 1.0: A Model-Independent Coding Agent Harness Built on Script Mode":
        "认识 Factory Droid 1.0：一个基于脚本模式、与模型无关的编码智能体框架",
    "Samaya AI Releases Sterling: A 3B-Active Finance Research Agent Model that Beats Claude Fable 5.1 on FrontierFinance at 11x Lower Cost":
        "Samaya AI 发布 Sterling：3B 激活参数的金融研究智能体模型，在 FrontierFinance 上以 1/11 成本击败 Claude Fable 5.1",
    "NVIDIA Cosmos Opens New Tools to Train, Evaluate and Deploy World Models":
        "NVIDIA Cosmos 开放训练、评估和部署世界模型的新工具",
    "How Fanatics and OpenAI streamline the fan experience":
        "Fanatics 与 OpenAI 如何让球迷观赛体验更顺畅",
    "Book Review: Investing in AI: Six Mental Models to Tell Moats from Traps by Rob May":
        "书评：投资 AI——辨别护城河与陷阱的六种思维模型（Rob May 著）",
    "What Is Flow Matching? A Faster Path for Generative AI":
        "什么是流匹配（Flow Matching）？生成式 AI 的更快路径",
    "Google’s first data center satellite is online and writing poetry":
        "Google 首颗数据中心卫星已上线，开始写诗",
    "Cisco Talos Details VOLTA Infostealer’s LLM Victim-Ranking Stage":
        "Cisco Talos 详解 VOLTA 信息窃取器的 LLM 受害者资产排序阶段",
}
