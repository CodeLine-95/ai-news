# -*- coding: utf-8 -*-
"""12:00 例行巡检修复：回填 2 条 NLLB 西里尔字母误译标题。

问题：NLLB 把专有名词 "Anthropic" 误译为「安тропо」、「Compass」误译为
「компас」，且标题混入未翻译英文。通过人工覆盖表（代码层，随发布生效）
回填权威中文译文，优先级高于模型译文，避免线上被覆盖回去。

用法：python3.11 fix_1200_cyrillic.py && python3.11 scripts/regen_overrides.py
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
T_JSON = os.path.join(BASE, "data", "titles_override.json")

FIXES = {
    "Amazon and Google will together own nearly 30% of Anthropic after its IPO":
        "Amazon 和 Google 将在 Anthropic IPO 后合计持有近 30% 股份",
    "Cohere Adds Timestamped Video Retrieval to Compass for AI Agents":
        "Cohere 为 Compass 增加带时间戳的视频检索，面向 AI 智能体",
}


def main():
    with open(T_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    n = 0
    for en, zh in FIXES.items():
        if data.get(en) != zh:
            data[en] = zh
            n += 1
            print("[fix] 写入覆盖:", en, "->", zh)
    with open(T_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("[fix] 标题覆盖表写入 %d 条，现共 %d 条" % (n, len(data)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
