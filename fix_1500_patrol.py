# -*- coding: utf-8 -*-
"""2026-11-19 15:00 巡检：定稿本轮新增条目 Gemini 4 Neon 的 NLLB 机翻硬伤。

本轮 15:00 整点调度新增 2 条（2299→2301，全库 100% 全译）：
1) Marktechpost《Nutrient Data Extraction API...》（11:23 重入）——译文已良好，无需改动。
2) Marktechpost《Google DeepMind Releases Gemini 4 Neon: 1M Context, #1
   on AA Coding Agent Index》（14:52）——NLLB 机翻硬伤：
   - 标题「1M 语境」应为「100 万 token 上下文」；
   - 摘要「开发者比率是近边界的分数」语义崩坏（pitch=宣传卖点，
     near-frontier scores=接近前沿模型水平）；
   - 「TL;DR 尺寸」「统一文本」「关闭权重」「AA 智能指数」等术语误译；
   - 「引领在$3/$15 上」「每 token 比 GPT-6.2 Sol 更贵」句式断裂。

修复：人工定稿标题+摘要，写入 data/titles_override.json 与
data/summaries_override.json，再由 regen_overrides.py 固化到代码层。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

GEMINI_TITLE = (
    "Google DeepMind Releases Gemini 4 Neon: 1M Context, "
    "#1 on AA Coding Agent Index"
)

TITLE_FIX = {
    GEMINI_TITLE: (
        "Google DeepMind 发布 Gemini 4 Neon：100 万 token 上下文，"
        "登顶 AA 编码智能体指数"
    ),
}

SUMMARY_FIX = {
    GEMINI_TITLE: (
        "Google DeepMind 刚刚发布 Gemini 4 Neon。这是一款推理模型，定位介于 "
        "Gemini 4 Carbon 与 Gemini 4 Hydrogen 之间，面向编码智能体、知识工作"
        "与科学研究工作流。官方主打卖点是：以更低的单任务成本达到接近前沿模型的"
        "水平。定价为每 100 万输入 token 3 美元、每 100 万输出 token 15 美元。"
        "核心规格：100 万 token 统一上下文，默认输出 6.4 万 token，通过后台长"
        "解码最高可达 100 万；仅通过 Google 托管运行，权重不开放，因此不支持本地 "
        "GPU、量化或边缘部署。性能方面：在 AA 智能指数上得 61 分，领先 Claude "
        "Opus 5.5（59）与 GPT-6.2 Sol（57）。最佳表现：GraphWalks 基准达 95.2%"
        "（上下文 25.6 万至 100 万），而 GPT-6.2 Sol 为 80.1%；最差表现："
        "FrontierCode 2.0 上为 46.2%，落后于 Claude Opus 5.5 的 47.3%。结论："
        "优势在于以 3 美元/15 美元的价格领跑长上下文与智能体编码；劣势在于权重"
        "封闭、成绩为自报，且单 token 价格高于 GPT-6.2 Sol。"
    ),
}


def main():
    with open(T_JSON, "r", encoding="utf-8") as f:
        titles = json.load(f)
    with open(S_JSON, "r", encoding="utf-8") as f:
        summaries = json.load(f)

    added_t = added_s = 0
    for k, v in TITLE_FIX.items():
        if titles.get(k) != v:
            titles[k] = v
            added_t += 1
    for k, v in SUMMARY_FIX.items():
        if summaries.get(k) != v:
            summaries[k] = v
            added_s += 1

    with open(T_JSON, "w", encoding="utf-8") as f:
        json.dump(titles, f, ensure_ascii=False, indent=2)
    with open(S_JSON, "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)

    print("[fix_1500] 标题定稿 %d 条 / 摘要定稿 %d 条" % (added_t, added_s))
    print("[fix_1500] 覆盖表 %d 条 / %d 条" % (len(titles), len(summaries)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
