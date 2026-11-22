# -*- coding: utf-8 -*-
"""2026-11-23 03:00 巡检：03:00 整点调度新增 5 条，NLLB 硬伤人工定稿。

  * TechCrunch《Why data centers are at the center of the Big Tech backlash》——
    "Paris Marx" 被误译「巴黎马克思」（人名应为帕丽斯·马克思）；摘要仅一句却译得生硬。
  * Unite.AI《Musk Allocates AI5 to Optimus...》——「超人驾驶」「留在 AI4」生硬；
    "10.3 billion active parameters" 在 Sarvam 条目被误作「1050 亿活跃参数」（应为 103 亿）。
  * Marktechpost《NVIDIA Releases Alpamayo 2 Edge...》——标题「为了驱动 Thor」生硬。
  * Unite.AI《OpenAI Proposes Shared AI Development Limits...》——
    术语 "perplexity"（困惑度）又被当成公司名 Perplexity，标题/摘要均需定稿。

三层覆盖：news.json 回填 + JSON 覆盖表 + (regen) report.main()。
"""
import json
import os
import report

BASE = os.path.dirname(os.path.abspath(__file__))
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")
N_JSON = os.path.join(BASE, "data", "news.json")

FIXES = [
    (
        "9d8fa306d2196715c96b8c32009942ff",
        "为何数据中心成为大型科技公司遭到反弹的焦点",
        "记者帕丽斯·马克思（Paris Marx）在新书《Hyperscale》（超大规模）中剖析了这一议题。",
    ),
    (
        "6c23520caea148f6d7a3a9e717aba9e8",
        "马斯克将 AI5 芯片用于 Optimus，特斯拉汽车继续搭载 AI4",
        "埃隆·马斯克在 2026 年 11 月 22 日的 X 回复中表示，特斯拉的 AI5 计算机将用于 Optimus，"
        "汽车将继续使用 AI4，而 AI4 已足以实现「超人级驾驶」。他是在回应一位车主的提问——"
        "新车何时能用上 AI5、是否值得在从 AI3 升级前再等等。该回复承接同一讨论中早前的一篇技术帖，"
        "马斯克在其中解释了特斯拉的 Reality View 可视化如何适配 AI4。这一解释背后是两类车载工作负载："
        "一个生成驾驶动作的模型，以及一个生成界面可视化的独立生成式模型。",
    ),
    (
        "0ea03b92d1e8409d2e582a6a07a9d1e3",
        "Sarvam AI 发布面向企业智能体的开放权重 105B 检查点",
        "Sarvam AI 于 2026 年 11 月 22 日发布 Sarvam-105B-1711，这是一个面向客户支持、语音智能体"
        "及其他高负载企业场景的新开放权重检查点。该版本包含可用于进一步训练的 BF16 权重，"
        "以及一款紧凑的 4 位 NVFP4 版本，可在单张工作站 GPU 上运行。模型卡显示，它采用与 "
        "Sarvam-105B 相同的 1050 亿参数混合专家基座，其中激活参数为 103 亿。",
    ),
    (
        "6cd7eace6c6d5b3b86cf8895a62650ec",
        "英伟达发布 Alpamayo 2 Edge：面向 DRIVE Thor 的 2B 推理 VLA 模型",
        "英伟达发布了 Alpamayo 2 Edge，这是一款面向自动驾驶的紧凑型推理视觉-语言-动作（VLA）模型。"
        "Alpamayo 2 Edge 是一个 20 亿参数模型，可在车内规划行驶轨迹并给出解释。它面向 NVIDIA "
        "DRIVE AGX Thor，而非数据中心 GPU，目标是在车载算力与延迟预算内实现基于推理的规划。"
        "你可通过 GPULeaderboard.com 的 Chrome 扩展查看部署选项与规格。要点速览：规模为 2B 级，"
        "模型构成为 2.45B 主干 + 0.2B 动作专家（约 20 亿 + 2 亿参数；HuggingFace 元数据标为 3B），"
        "上下文长度未披露（实测提示为 3,236 个 token）。运行平台：NVIDIA DRIVE AGX Thor，"
        "采用 FP8 + TensorRT Edge-LLM 方案；BF16 PyTorch 需要 16 GB 以上显存，已在 1× H100 80GB 上验证。"
        "性能方面：以该体量而言是强劲的闭环驾驶模型，推理问答处于中游水平。",
    ),
    (
        "0edf8a40f1fd3823cb9627f11d985292",
        "OpenAI 提议将共享的 AI 研发限制与安全里程碑挂钩",
        "OpenAI 首席科学家 Jakub Pachocki 于 2026 年 11 月 22 日公布了内部困惑度（perplexity）"
        "测量结果，并提议对前沿 AI 研发设定共享限制，警告称若预训练进展在 2027 年之前加速，"
        "对齐与监测研究可能跟不上步伐。此次披露涉及对数困惑度（log-perplexity），即困惑度的对数，"
        "也称交叉熵损失。困惑度衡量模型平均预测下一个词元（token）的能力，数值越低表示预测越准确。",
    ),
]


def main():
    titles = json.load(open(T_JSON, encoding="utf-8"))
    summaries = json.load(open(S_JSON, encoding="utf-8"))
    news = json.load(open(N_JSON, encoding="utf-8"))
    by_id = {it["id"]: it for it in news["items"]}

    ok = 0
    for iid, zh_t, zh_s in FIXES:
        it = by_id.get(iid)
        if not it:
            print("[WARN] id 未找到:", iid)
            continue
        en = (it.get("title") or "").strip()
        titles[en] = zh_t
        summaries[en] = zh_s
        it["title_zh"] = zh_t
        it["summary_zh"] = zh_s
        it["method"] = "manual"
        it["translated"] = True
        ok += 1
        print("[FIX]", iid[:8], "->", zh_t)

    json.dump(titles, open(T_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(summaries, open(S_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(news, open(N_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("[OK] 定稿 %d 条；覆盖表 标题=%d 摘要=%d；news.json=%d 条"
          % (ok, len(titles), len(summaries), len(news["items"])))

    report.main()
    print("[OK] 报告已重生成")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
