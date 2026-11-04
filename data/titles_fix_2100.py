# -*- coding: utf-8 -*-
"""2026-11-01 21:00 例行巡检 —— 人工核对标题覆盖表。

键为英文原标题（与 data/titles_override.json 保持同一约定）。
只收录自动翻译后语义明显走样、需要人工定稿的标题。

本轮收录 1 条：
  - "Last-minute Halloween costumes for tech nerds"：
    模型把 "last-minute"（临时赶制的、当天现凑的）译成「最后一分钟」，
    中文读者会理解成「最后一刻的时间」，语义完全跑偏；
    正确译法是「临时赶制」或「现凑的」。
"""

TITLE_OVERRIDES = {
    "Last-minute Halloween costumes for tech nerds":
        "临时赶制的万圣节装扮，科技宅的救急方案",
}
