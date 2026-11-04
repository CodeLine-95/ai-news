# -*- coding: utf-8 -*-
"""2026-11-02 02:00 例行巡检 · 人工核对标题覆盖。

本轮新增条目《Affle Signs Definitive Agreement to Acquire Ad Tech Company
Perion》（Unite.AI，2026-11-02 01:06）NLLB 原始标题译文存在缺陷：

    - "Affle" → 「艾弗尔」  （音译生造，且与摘要中的「阿弗尔」不一致）
    - "Ad Tech Company" 漏译「广告技术公司」的完整语义，标题读起来像产品名

定稿策略：Affle / Perion 均为公司注册名（Affle 为纳斯达克上市公司），
按科技资讯惯例保留英文原名，不做音译；标题其余部分逐词对齐。

键为英文原标题，值为定稿的中文标题。
"""

TITLE_OVERRIDES = {
    'Affle Signs Definitive Agreement to Acquire Ad Tech Company Perion': (
        'Affle 签署最终协议，收购广告技术公司 Perion'
    ),
}
