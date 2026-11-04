# -*- coding: utf-8 -*-
"""2026-11-02 03:00 例行巡检 · 人工核对摘要覆盖。

本轮新增条目《Klap vs. Submagic: Which Is Better for Turning Videos Into
Shorts?》（Unite.AI，2026-11-02 02:51）NLLB 原始摘要译文存在缺陷：

    - "a regular supply of long recordings"
      → 「定期提供长长录音工作」（"长长" 重复字 + "工作" 冗余）
    - "supporting footage" → 「支持片段」（误译，实为「辅助画面/补充素材」）
    - "when the captions, supporting footage, and pace of the edit are
      what bring a short to life"
      → 「当字幕，支持片段和编辑的速度使短片生动时」
      （英文原句是并列主语，译文处理成状语前置，语义漂移）

定稿重写为通顺中文，保留原文全部事实点：
播客/访谈中找出值得分享的瞬间、配上竖屏画幅、变成独立成片的视频；
Klap 与 Submagic 都覆盖这些环节但各有侧重；Klap 适合素材量大的创作者
（长录音持续供给）；Submagic 在字幕、辅助素材与剪辑节奏决定成片表现时更有优势。

键为英文原标题，值为定稿的中文摘要。
"""

SUMMARY_OVERRIDES = {
    'Klap vs. Submagic: Which Is Better for Turning Videos Into Shorts?': (
        '一段优秀的播客或访谈里往往藏着大量值得分享的瞬间。真正的工作是从中'
        '找出这些瞬间，给它们配上干净的竖屏画幅，再把它们做成能够独立成片的'
        '视频。Klap 与 Submagic 把这些环节整合到了一起，但两者的侧重点不同。'
        '对于能够持续积累大量长录音素材的创作者，Klap 的理由相当充分；而当字幕、'
        '辅助素材与剪辑节奏才是决定一条短片表现好坏的关键时，Submagic 就格外有吸引力。'
    ),
}
