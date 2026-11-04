# -*- coding: utf-8 -*-
"""2026-11-01 21:00 例行巡检 · 人工核对摘要覆盖表。

本轮聚焦四类缺陷（均为「术语规则修完仍不通顺」或「内容缺失」，
必须逐条人工重写定稿，不能靠规则批量修）：

1. **整段语义崩坏**（b4fe7198 / dbbf75dd / cd240cd3 / 4c59753c / 19a48959）：
   离线模型在长句上把固定搭配拆开重组，产出「风险损失机构背景」
   「执法提议」「统一登录」「带你自己的提供商密钥」这类中文不成话的短语。
   规则层只能替换被点名的错误片段，无法还原整句语义，故人工重写。

2. **内容缺失**（73ca8e79 DoorDash）：
   英文原文 3 句（285 字符），中文只剩首句 43 字符，
   「预计算复购需求 / 批量 LLM 推理 / 确定性校验 / 实时目录解析 /
   可编辑购物界面」等关键技术细节全部丢失。补齐全部要点。

3. **专名形态错误**（19a48959 Boston Dynamics）：
   公司名被译成「波士顿动态公司」「波士顿动力学」（正确为「波士顿动力」），
   机器形态被译成「四旋翼机器人」（quadruped = 四足），
   合同金额 $1.3 million 被截断成 100 万美元（应为 130 万美元）。
   注：数值修复与四足机器人已同时在 translate.py 里加了确定性规则，
   此处再人工定稿一份，确保存量与后续调度都稳定。

4. **语义走样但句子完整**（62efadaf / fa5b0957 / 9fe039a8）：
   「deceptively cute」译成「欺骗性可爱」（实为「看着可爱实则暗藏玄机」）、
   「propose fixes for review」译成「提出修复问题」（应为「提出修复方案供审查」）、
   「data pipelines」译成「数据管道」（中文技术语境应为「数据管线」）。

键为英文原标题（与 server.py 的 apply_summary_overrides 约定一致）。
"""

SUMMARY_OVERRIDES = {
    # ---- 1. DoorDash：摘要只剩首句，技术细节全部丢失 ----
    "DoorDash Cuts Grocery Reorder Latency from 16 to 2 Seconds with AI Agents":
        "DoorDash 通过批量 LLM 推理与确定性校验预先计算复购需求，"
        "把零售补货延迟从 16 秒压缩到 2 秒。"
        "实时目录解析让商品选择始终保持最新，"
        "而可编辑的购物界面则避免了不必要的模型调用。",

    # ---- 2. OpenAI 社区安全报告：「执法提议」+「过去大规模袭击问题」语义崩坏 ----
    "OpenAI Announces Community Safety Report and New Teen Weapons Limits":
        "2026 年 10 月 30 日，OpenAI 宣布发布首份社区安全报告，"
        "聚焦暴力预防，并将每半年更新一次；"
        "同时推出一系列新防护措施，限制青少年获取武器相关信息，"
        "并收紧 ChatGPT 对过往大规模袭击相关提问的处理。"
        "公司表示，2026 年第三季度共向执法部门提交了 200 多条举报转介。",

    # ---- 3. 工程梯队演讲：「风险损失机构背景」「工程管道」整段崩坏 ----
    "Presentation: The Ladder Is Missing Rungs: Engineering Progression When AI Ate the Middle":
        "阿拉斯代尔·艾伦解读了 METR 与 Anthropic 关于 AI 编码采用情况的研究成果。"
        "他提出了「监督悖论」：依赖 AI 工具会打乱初级工程师的技能成长路径，"
        "有导致机构性上下文丢失的风险，"
        "并威胁到支撑自主系统有效监管所需的长期工程人才梯队。",

    # ---- 4. Cloudflare Web Search API：「统一登录」「发票」「带你自己的提供商密钥」 ----
    "Cloudflare Introduces Web Search API for AI Applications":
        "Cloudflare 最近通过 AI Gateway 推出测试版 Web 搜索 API。"
        "该接口可通过 REST API 与 Cloudflare Workers 调用，"
        "提供统一的日志记录、访问控制与计费能力，并支持自带服务商密钥。",

    # ---- 5. Credit Saison：句号半角 +「将结果转化为全公司的采用」语序生硬 ----
    "Credit Saison achieves 954% ROI in a ChatGPT Enterprise pilot":
        "Credit Saison 的 ChatGPT 企业版试点带来了 954% 的投资回报率。"
        "看看管理者与员工如何将这些成果推广为全公司范围内的采用。",

    # ---- 6. Boston Dynamics / ICE：专名形态错误 + 金额被截断 + 结尾语义崩坏 ----
    "ICE plan to buy robot dogs spurs protest from hundreds of Boston Dynamics employees":
        "美国机器人公司波士顿动力的数百名员工签署请愿书，"
        "要求公司高管叫停向美国移民与海关执法局出售机器人狗的交易；"
        "但高管仍坚持该协议，同时声明这些机器人不会被武器化。"
        "9 月 25 日，国土安全部将一份价值 130 万美元的合同授予"
        "康涅狄格州一家名为 Radeco 的公司，"
        "由其向 ICE 提供波士顿动力四足机器人的改装版本。"
        "9 月初，波士顿动力的员工已联名将这封请愿信递交公司高管，"
        "签名超过 300 个、其中一半匿名，并将副本发送给"
        "《波士顿环球报》和 WBUR 公共广播电台。"
        "请愿书中写道：许多同事都收到了亲友发来的消息，"
        "震惊与难以置信地问我们这条消息是否属实，"
        "以及如果属实，我们该如何面对自己。",

    # ---- 7. 万圣节装扮：「deceptively cute」译成「欺骗性可爱」 ----
    "Last-minute Halloween costumes for tech nerds":
        "还没想好万圣节装扮？当一个看着呆萌实则别有用途的 AI 智能体图标、"
        "一个 PHP 漏洞，或者「困意上头的布莱恩·约翰逊」都行。",

    # ---- 8. Cloudflare + OpenAI Daybreak：「propose fixes for review」译成「提出修复问题」 ----
    "Cloudflare links vulnerability discovery to defense with OpenAI":
        "Cloudflare 使用 OpenAI Daybreak 调查漏洞并提出修复方案供审查。"
        "其开发者则借助 Codex 更快地编写代码并提升代码质量。",

    # ---- 9. AI 治理六原则：「data pipelines」译成「数据管道」 ----
    "6 Guidelines for Governing AI":
        "职业生涯的前 10 年，我独自从事产品管理与数据分析工作："
        "编写从企业系统中提取数字的数据库查询，"
        "构建统计模型来预测客户会买什么，"
        "并交付在业务系统之间搬运信息的数据管线。"
        "我在 Best Buy 和 Target 建立并扩展了分析团队，"
        "研究顾客如何购物、门店应当备什么货。"
        "如今我负责《财富》100 强家居装修零售商 Lowe's 的企业 AI 转型。"
        "目标不是兜售人工智能，而是在客户需要时用它交付有用的专业知识。"
        "在零售及其他面向客户的行业，"
        "虚拟助理可以帮助人们解决日常问题——比如如何修理漏水的水龙头——"
        "同时引导他们找到相关产品、服务或下一步。",

    # ---- 10. Powerlattice：引号语义错位 +「power delivery chiplet」译成「发电芯片」 ----
    "Powerlattice Raises $86M in Equity Offering, SEC Filing Shows":
        "根据这家居于华盛顿州温哥华的初创公司 2026 年 10 月 30 日"
        "向美国证券交易委员会提交的 Form D 豁免发行通知，"
        "Powerlattice Technologies Inc. 已在一轮 111,010,000 美元的"
        "股权发行中出售了 86,009,965 美元。"
        "该公司正在为 AI 处理器开发供电芯粒，"
        "并报告首次出售日期为 2026 年 10 月 15 日。",
}
