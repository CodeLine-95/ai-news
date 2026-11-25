# -*- coding: utf-8 -*-
"""本轮（04:00 例行巡检）人工核对结果：摘要级覆盖。

针对 NLLB 机翻在专有名词、量级单位、句法上的硬伤做人工定稿。
键为英文原标题（严格一致），值为人工核对后的中文摘要。
"""

SUMMARY_OVERRIDES = {
    "Nvidia GPU Sellers Seek Buyers After U.S. Remote-Access Rule":
        "CNBC 于 2026 年 11 月 25 日报道，在美国收紧对中国关联方远程访问先进 AI 算力的限制后，英伟达 GPU 卖家正在寻找新买家。报道提到的报价中，包括涉及数千颗 B300 GPU 的潜在交易。",
    "Want to buy your kid an AI toy this Christmas? Not in New York":
        "纽约已对 AI 聊天机器人玩具实施为期五年的禁令。此前 Common Sense Media 的新研究揭示了令人担忧的安全问题，包括接触不当内容以及对儿童情感发育的风险。",
    "OpenAI wants companies to trust it with sensitive work by promising not to look at their data":
        "OpenAI 正在测试一项名为「私密推理」（Private Inference）的新功能，允许企业在自己强大的模型上运行查询，而 OpenAI 本身无法访问相关数据。",
    "OpenAI Begins Limited Customer Trials of Alpha Private Inference":
        "OpenAI 首席执行官 Sam Altman 于 2026 年 11 月 25 日在 X 上宣布，公司正与一小批客户测试「私密推理」（Private Inference），作为 OpenAI Private Intelligence——其面向企业使用前沿 AI 的隐私框架——的一部分。Altman 表示，更强的隐私保护将使前沿 AI 能胜任更多工作，并把企业隐私视为健康生态系统的重要一环。",
    "Ulys Raises $4M to Market Its Investing App and Train AI Models":
        "总部位于纽约的 AI 投资应用 Ulys 于 2026 年 11 月 25 日宣布，在 Streamlined Ventures 领投的一轮融资中再获 400 万美元，累计融资额达 1700 万美元。Fundstrat 的 Tom Lee、BitMine 与 XBTO Ventures 也参与投资。此轮融资发生在应用于 2026 年 11 月 10 日正式登陆 App Store 之后，资金将主要用于市场推广以及训练支撑产品的 AI 模型。",
    "A Stranger Broke Our AI Agent’s Guardrails. Here Is What It Taught Us":
        "几周前，我们发布了一篇技术解析，讨论一个在几乎所有接手项目中都会遇到的问题：如何阻止 AI 智能体读取本不该读取的数据。简要做法是：为智能体分配独立的数据库角色，只授予其所需的列，通过行级安全把每条查询限定到单一客户，并编写试图造成数据泄露的测试。这是我们推荐的模式，发布前我们也逐一验证了每段代码。",
    "Perplexity Launches Time Machine for Point-in-Time Web Retrieval":
        "Perplexity 于 2026 年 11 月 25 日为其 Search API 与 Context API 推出「时间机器」（Time Machine），让开发者与智能体能够检索、阅读指定时间点或之前保存的网页快照。上线之初，历史截止点最早可回溯至 365 天前。新增的 snapshot_as_of 参数面向评估等场景——在这些场景下，后续的信息会干扰结果。",
    "Anthropic’s Dario Amodei calls accusations of surrendering human control to AI ‘absurd’":
        "Anthropic 首席执行官达里奥·阿莫迪（Dario Amodei）反驳了竞争对手的指控——对方称他主张把人类自主权交给 AI。与此同时，头部 AI 公司正越来越多地将自身的研究与模型开发流程自动化。",
    "Jensen Huang broke Nvidia’s code of conduct, and his employees may not forget it":
        "多数行为准则都是企业文化的反映。就英伟达而言，这可能带来实实在在的后果。",
    "Three insights you may have missed from theCUBE’s coverage of the Fully Connected event":
        "AI 基础设施经济学越来越取决于「生产智能」的成本，而非获取算力的成本。随着推理需求增长超过训练，基础设施供应商及其客户必须在运营成本不相应上升的前提下，提高有效计算时间。持续学习的智能体与物理 AI 应用的兴起，进一步让这道等式变得复杂。",
}
