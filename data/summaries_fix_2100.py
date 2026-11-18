# -*- coding: utf-8 -*-
"""2026-11-18 21:00 例行巡检 · 人工核对摘要覆盖表。

本轮 5 条缺陷：
  1. Axiom Math：「CFSG 证据」「建筑师」「倒计数」「我...他回忆说」整段语义崩坏；
  2. Nvidia：「新公司」「受到威胁」误译 neocloud / on the hook；
  3. Unsiloed AI：品牌名被音译成「无锡人工智能」，「增长研究」语义走样；
  4. Humyn Labs：品牌名被音译成「哈米恩/汉明实验室」；
  5. inference chips：「发送到电商网站的空间狩猎」整句不通。

键为英文原标题。
"""

SUMMARY_OVERRIDES = {
    "Startup Makes Headway Towards Formalizing All of Math With AI":
        "10 月 25 日（周日），Axiom Math 的 AI 智能体集群正为「有限单群分类」（CFSG，"
        "俗称「庞限定理」）长达 1.5 万页的证明完成自动验证做最后收尾，"
        "公司创始数学家 Ken Ono 无事可做，只能静静观看并感慨这一成就。"
        "作为数学家之子，他从小身边就围绕着 CFSG 证明的部分缔造者——"
        "这份证明被公认为人类写出的最长数学证明。"
        "如今，他正参与对父亲与同行们成果的正式验证。"
        "他回忆道：「我妻子陪在我身边，我们一起看团队倒数验证完成的那一刻。」",

    "Nvidia clarifies when it will — and won’t —keep financing neoclouds":
        "临时首席执行官 Colette Kress 解释说：如果英伟达为某笔数据中心贷款提供兜底担保，"
        "只有在新型云服务商（neocloud）具备独立融资、建成设施并装好英伟达设备的前提下，"
        "英伟达才会承担相应责任。",

    "Unsiloed AI Raises $7.5M Seed to Grow Research, Engineering and Sales":
        "TechCrunch 于 2026 年 11 月 18 日报道，Unsiloed AI 完成由 Felicis 领投的 "
        "750 万美元种子轮融资，用于开发将企业文档转化为 AI 智能体可用的结构化数据的技术。"
        "Y Combinator、Orange Collective、Uncorrelated Ventures 以及天使投资人 "
        "Aarthi Ramamurthy 和 Beth Turner 也参与本轮。"
        "首席执行官 Aman Mishra 表示，资金将用于招聘研究与工程人才、扩大销售团队，"
        "并构建专有数据集以改进技术。",

    "Humyn Labs raises $47M to bridge the gap between AI training and real-world robotics":
        "Humyn Labs 是一家将人类经验转化为机器人与 AI 训练数据的公司。"
        "该公司今日宣布完成 4700 万美元早期融资，"
        "用于加速智能机器人在巴西、韩国和印度真实环境中的部署就绪。",

    "Stalled data center buildouts send inference chips hunting for space in telco and colo sites":
        "推理需求增长已超过新建 AI 数据中心的建设速度——电力、资金和审批延误让新增产能一再推迟。"
        "这一缺口正促使芯片厂商在现有设施中寻找空间。"
        "许多较老的电信机房和托管（colo）站点拥有可用空间与电力。",
}
