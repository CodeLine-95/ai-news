# -*- coding: utf-8 -*-
"""2026-11-18 21:00 例行巡检 —— 人工核对标题覆盖表。

键为英文原标题（与 data/titles_override.json 保持同一约定）。
本轮收录 5 条 NLLB 机翻明显走样的标题。
"""

TITLE_OVERRIDES = {
    "Startup Makes Headway Towards Formalizing All of Math With AI":
        "初创公司借助 AI 推动数学形式化取得进展",
    "Nvidia clarifies when it will — and won’t —keep financing neoclouds":
        "英伟达澄清何时会、何时不会继续为新型云服务商提供资金",
    "Unsiloed AI Raises $7.5M Seed to Grow Research, Engineering and Sales":
        "Unsiloed AI 完成 750 万美元种子轮融资，扩充研究、工程与销售团队",
    "Humyn Labs raises $47M to bridge the gap between AI training and real-world robotics":
        "Humyn Labs 融资 4700 万美元，弥合 AI 训练与真实机器人应用之间的差距",
    "Stalled data center buildouts send inference chips hunting for space in telco and colo sites":
        "数据中心建设停滞，推理芯片转向电信机房与托管站点寻找空间",
}
