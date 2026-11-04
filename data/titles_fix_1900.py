"""2026-11-01 19:00 例行巡检 —— 人工核对标题覆盖表。

键为英文原标题（与 data/titles_override.json 保持同一约定）。
只收录自动翻译后语义明显走样、需要人工定稿的标题。
"""

TITLE_OVERRIDES = {
    # 原文品牌名 Boom 被模型意译成「勃起」，标题里改回品牌 + 事件
    "Supersonic airliner in doubt as company shifts to powering AI data centers":
        "超音速客机前景存疑：Boom 转向为 AI 数据中心供电",
    # 「获得意识」应为「产生自我意识」
    "Anthropic IPO warns its AI could blackmail people, become sentient, end humanity":
        "Anthropic IPO 警告：其 AI 可能勒索人类、产生自我意识乃至终结人类",
    # 「信任性」不通顺
    "Meet the Anthropic Engineer Keeping Its AI Agent Trustworthy":
        "认识那位让 Anthropic AI 智能体保持可信的工程师",
    # 「带来……到」句式冗余
    "Bringing GPT-Rosalind to academic research labs":
        "将 GPT-Rosalind 带入学术研究实验室",
    # 补主语与量词
    "Thousands of “ghost students” use AI to steal millions in student loans, DOJ says":
        "司法部称：数以千计的“幽灵学生”利用 AI 窃取数百万美元学生贷款",
    # 「AI 工厂」前缺主语，句尾标点风格不统一
    "NVIDIA Unveils Minerva to Bring End-to-End Observability for AI Factories":
        "NVIDIA 发布 Minerva，为 AI 工厂带来端到端可观测性",
    # 「引领徒步旅行者」漏译「带偏」的语义
    "Chatbots Are Leading Hikers Astray, With Dangerous Consequences":
        "聊天机器人正把徒步者带偏，后果危险",
    # 补「后来发生了什么」
    "I Used AI to Fake a Scientific Paper. Here’s What Happened":
        "我用 AI 伪造了一篇科学论文，后来发生了什么",
    # 「何时该调 sklearn 头」表述不清
    "Fine-Tuning vs. Frozen Embeddings: When to Adapt the LLM vs. the Sklearn Head":
        "微调还是冻结嵌入：何时该改 LLM，何时该改 sklearn 分类头",
    # 「在规模上提供 LLMs」是生硬直译
    "Presentation: Serving LLMs at Scale: The Hidden KV Cache Advantage":
        "演讲：规模化服务 LLM——被忽视的 KV 缓存优势",
    # 「闪烁其词」误作「闪烁」类动词
    "Google AI gets cagey when asked who won the 2020 elections":
        "被问谁赢得了 2020 年大选时，Google AI 含糊其辞",
    # 「达特斯学院」应为「达特茅斯学院」
    "Dartmouth's provost warned us about AI cheating—but his own AI use cost him his job":
        "达特茅斯教务长警告我们 AI 作弊问题，但他自己的 AI 使用让他丢了工作",
    # 「被用于广告」表述更准确
    "Updated Google privacy policy says your Gmail might be used for advertising":
        "Google 更新隐私政策：你的 Gmail 可能被用于广告",
    # 「国会山」语义在标题中更准确
    "Why Engineers Should Brave Capitol Hill":
        "工程师为何应该勇闯国会山",
    # 「论证……的必要性」尚可，但统一为「价值」
    "Making the case for context-aware AI":
        "论证上下文感知 AI 的价值",
    # 「文本来源规则」应为「文本溯源规则」
    "Our approach to EU text provenance rules":
        "我们应对欧盟文本溯源规则的方法",
    # 「攻克」比「解决」更贴合「unsolved math problem」
    "AI Solves a Major Unsolved Math Problem. Not Everyone Is Happy":
        "AI 攻克了一个重大未解数学问题，但不是所有人都高兴",
    # 补版本空格与产品定性
    "EmbeddingGemma 2: an open, lightweight multimodal embedding model":
        "EmbeddingGemma 2：一款开放、轻量的多模态嵌入模型",
    # 「专用矢量数据库」术语错误 + 缺空格
    "pgvector vs. Dedicated Vector Databases: A Production Benchmark":
        "pgvector vs. 专用向量数据库：生产环境基准对比",
    # 「培训控制」表述不清，实际是 robots.txt 中的共享训练控制信号
    "Google Plans Support for Shared Robots.txt AI Training Control":
        "Google 计划在 robots.txt 中支持共享的 AI 训练控制信号",
    # 「AI 领域巨头正支持」漏掉「共同」
    "The biggest names in AI are backing a new way to opt out of scraping":
        "AI 领域巨头共同支持一种新的退出抓取机制",
    # 「让网站更容易表达」语序生硬
    "Making it easier for websites to express AI training preferences":
        "让网站更轻松地表达 AI 训练偏好",
    # 「铁甲」类意译，实际是产品名 Ironclad
    "Advancing computer use with Ironclad":
        "与 Ironclad 一起推进计算机使用能力",
    # 标题「说明」应为「解释」
    "Speculative Decoding Explained: How to Get 3× Faster Inference from Any LLM":
        "投机解码详解：如何让任意 LLM 的推理快 3 倍",
}
