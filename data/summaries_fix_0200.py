# -*- coding: utf-8 -*-
"""2026-11-02 02:00 例行巡检 · 人工核对摘要覆盖。

本轮修复 1 条译文质量缺陷：

《Affle Signs Definitive Agreement to Acquire Ad Tech Company Perion》
（Unite.AI，2026-11-02 01:06）

NLLB 原始译文存在多处误译、语义崩坏与关键财务信息丢失：
    - "Affle"                       → 「阿弗尔」（音译，且与标题「艾弗尔」不一致）
    - "step-down subsidiary"        → 「下一步子公司」（控股结构术语误译）
    - "implied equity value"        → 「暗示股权价值」（财务术语生造）
    - "closing share price"         → 「关闭额」（股价术语误译）
    - "34.5% premium"               → 「其股票价格的关闭额为 34.5%」（溢价信息丢失）
    - "valued at"                   → 「估值……的」（主谓错位）
    - "Perion announced on ..."      → 「Perion 宣布于……」（状语位置不当）

定稿重写为通顺中文，保留原文全部事实点：
Affle 3iL Ltd. 为以色列注册、隶属 Affle 3i Limited 的阶梯式控股子公司；
每股 11.70 美元全现金收购 Perion Network Ltd.；隐含股权估值约 4.2 亿美元；
2026 年 11 月 1 日宣布；较 2026 年 10 月 30 日（协议签署前最后交易日）
收盘价溢价 34.5%。

键为英文原标题，值为定稿的中文摘要。
"""

SUMMARY_OVERRIDES = {
    'Affle Signs Definitive Agreement to Acquire Ad Tech Company Perion': (
        'Affle 3iL Ltd.（总部位于以色列，是 Affle 3i Limited 名下的阶梯式控股子公司）'
        '于 2026 年 11 月 1 日宣布，已签署最终协议，将以每股 11.70 美元的全现金交易'
        '收购 Perion Network Ltd.，对该广告技术公司的隐含股权估值约为 4.2 亿美元。'
        'Perion 表示，这一价格较 2026 年 10 月 30 日（最终协议签署前的最后一个交易日）'
        '的收盘价溢价 34.5%。'
    ),
}
