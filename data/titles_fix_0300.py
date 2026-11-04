# -*- coding: utf-8 -*-
"""2026-11-02 03:00 例行巡检 · 人工核对标题覆盖。

本轮新增条目《Klap vs. Submagic: Which Is Better for Turning Videos Into
Shorts?》（Unite.AI，2026-11-02 02:51）NLLB 原始标题译文存在严重缺陷：

    - 标题后半段被**重复输出**：「Klap vs. Submagic: Which Is Better for
      Turning Videos into Shorts? 视频转换成短片？哪个更好转换视频？」
      英文原题与机翻中文各出现一次，拼接成病句。
    - 语序错乱：「视频转换成短片？哪个更好转换视频？」应为
      「将视频转为短片，哪一个更好？」

定稿策略：产品名 Klap / Submagic 保留英文原名不音译，
疑问句按中文语序重排为「A 还是 B：哪个更好」结构。

键为英文原标题，值为定稿的中文标题。
"""

TITLE_OVERRIDES = {
    'Klap vs. Submagic: Which Is Better for Turning Videos Into Shorts?': (
        'Klap 与 Submagic 对比：哪个更适合把视频转成短片？'
    ),
}
