# -*- coding: utf-8 -*-
"""2026-11-01 22:00 例行巡检 —— 人工核对标题覆盖表。

键为英文原标题（与 data/titles_override.json 保持同一约定）。
本轮收录 3 条（均为整句语义崩坏，规则层无法安全还原）：

1. "What Is Chunking in RAG? How Document Splitting Shapes Answer Quality"：
   模型把 "chunking" 译成「碎」、「document splitting」译成「分化文件」、
   "shapes answer quality" 译成「形状答案质量」，整句中文完全不成话。
   正确译法：「RAG 中的分块是什么？文档切分如何影响答案质量」。

2. "Pope Leo calls for the disarmament of AI: 'Machines are tools, not persons'"：
   "disarmament"（解除武装）在 AI 治理语境指"给 AI 解除武装 / 收缴自主能力"，
   模型译成「消除人工智能」会让人理解为"消灭 AI"，
   正确译法：「教宗利奥呼吁为 AI 解除武装：『机器是工具，而非人』」。

3. "Leading European Financial Services Organizations Embrace Open Models..."：
   标题本身译文正确，仅摘要需重写（见 summaries_fix_2200.py），此处不重复收录。
"""

TITLE_OVERRIDES = {
    "What Is Chunking in RAG? How Document Splitting Shapes Answer Quality":
        "RAG 中的分块是什么？文档切分如何影响答案质量",

    "Pope Leo calls for the disarmament of AI: ‘Machines are tools, not persons’":
        "教宗利奥呼吁为 AI 解除武装：「机器是工具，而非人」",
}
