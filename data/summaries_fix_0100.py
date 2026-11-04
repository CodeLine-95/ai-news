# -*- coding: utf-8 -*-
"""2026-11-02 01:00 例行巡检 · 人工核对摘要覆盖。

本轮修复 1 条译文质量缺陷：

《Guarding the Gates of Knowledge》（IEEE Spectrum AI，2026-11-01 22:00）

NLLB 原始译文存在多处语义崩坏与生造词：
    - "About half my feed" → 「我的料中」          （feed 误作"料"）
    - "AI slop"          → 「人工智能条」          （slop 即"垃圾内容"，未译）
    - "the embarrassment of the rube" → 「让……感到尬的」（rube 生造为"尬"）
    - "the delight of the poster"    → 「分享它故意的海报的快乐」（poster 误作"海报"）
    - "sowing confusion" → 「种植混乱」（误作农业动作）
    - "GPT-3"            → 「GPT-3」（保留，正确）
    - "Claude or Gemini" → 「Claude 或双胞胎」（Gemini 被误译为"双胞胎"）
    - "hallucination"    → 「词语」（关键术语丢失）
    - "Trust but verify" → 「信任但验证」（可保留，但需补足语义）

定稿重写为通顺中文，保留原文全部事实点（社交媒体 AI 垃圾内容、
GPT-3 幻觉一词的由来、Claude/Gemini 仍不可全信、"信任但验证"的结论）。

键为英文原标题，值为定稿的中文摘要。
"""

SUMMARY_OVERRIDES = {
    'Guarding the Gates of Knowledge': (
        '最近刷社交媒体时，我开始思考信任这件事。我的信息流里大约有一半是 AI 生成的垃圾内容'
        '（AI slop），明眼的用户会指出这些是机器生成的；这常常让不知情而转发了它们的人感到尴尬，'
        '有时也让那些故意转发的人暗自得意——他们觉得好玩，或者觉得这样有助于制造混乱。'
        '还记得 GPT-3 的那些好日子吗？那时我们向聊天机器人提问，它几乎立刻、并且极其自信地吐出一个'
        '看似合理却完全错误的答案。正是那时，「幻觉」一词被用来形容 AI 的回答，并进入了大众词汇表。'
        '六年过去，几款不同的聊天机器人也迭代了多个版本，但我依然无法完全信任它们给出的答案——'
        '尽管 Claude 或 Gemini 确实常常能帮我完成有用的工作。这就是当下 AI 的真实状态：'
        '信任，但也要验证。而验证，是必须做的。'
    ),
}
