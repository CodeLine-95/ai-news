# -*- coding: utf-8 -*-
"""2026-11-25 15:00 巡检：定稿 13:42 新增的 Marktechpost / ByteDance 条目。

NLLB 直译把 ByteDance 音译成「拜特丹斯」、post-training 译成「后培训」，
摘要出现「Laminar.Laminar」「对于团队培训长期，偏差的编码智能体」等硬伤。
沿用既往巡检做法：以英文原标题为键写入 JSON 覆盖表并回填 news.json，
随后由 scripts/regen_overrides.py 固化到代码层 manual_overrides.py（随发布生效）。
"""
import json
import os
import shutil
import sys

import report

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_OVR = os.path.join(BASE, "data", "titles_override.json")
S_OVR = os.path.join(BASE, "data", "summaries_override.json")
STAMP = "1500patrol1125"

TITLE_EN = "ByteDance Researchers Open-Sources Laminar, an Async Reinforcement Learning RL Post-Training Framework"

TITLE_FIX = "字节跳动与香港大学研究人员开源 Laminar：异步强化学习后训练框架"

SUMMARY_FIX = (
    "香港大学与字节跳动 Seed 团队的研究人员开源了 Laminar——一个面向大语言模型和"
    "长周期智能体的异步强化学习后训练框架。核心思路很简单：不再让每条轨迹、每块 GPU "
    "都等待最慢的那一个。对于要训练 rollout 长短不一、分布偏斜的编码智能体的团队来说，"
    "这正是大部分 GPU 时间的消耗所在。TL;DR 要点：这是一个框架；已在 "
    "Qwen3-Coder-30B-A3B-Instruct（总参数 305 亿、激活参数 33 亿）以及 Qwen2.5 的 "
    "7B、32B、72B 版本上测试；运行环境为基于 Ray 与 CUDA 的多节点 NVIDIA GPU 集群，"
    "已在 64 块 H800 乃至最多 1024 块 H800 上验证；推理使用 vLLM，训练使用 "
    "Megatron-LM 或 FSDP2。性能方面：在 SWE 智能体强化学习任务上取得显著的端到端提升，"
    "论文中吞吐量最高提升 5.48 倍；最佳成绩为 SWE-bench Verified 上的 52.2%，"
    "高于基座模型的 46.6%。"
)


def load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def main():
    for path in (DATA, T_OVR, S_OVR):
        shutil.copy2(path, path + ".bak." + STAMP)

    data = load(DATA)
    titles = load(T_OVR)
    summaries = load(S_OVR)

    titles[TITLE_EN] = TITLE_FIX
    summaries[TITLE_EN] = SUMMARY_FIX
    applied = 0
    for it in data["items"]:
        if (it.get("title") or "").strip() != TITLE_EN:
            continue
        it["title_zh"] = TITLE_FIX
        it["summary_zh"] = SUMMARY_FIX
        it["translated"] = True
        it["method"] = "manual"
        applied += 1
        print("定稿: %s -> %s" % (TITLE_EN[:60], TITLE_FIX), flush=True)

    save(DATA, data)
    save(T_OVR, titles)
    save(S_OVR, summaries)
    print("本轮定稿 %d 条，覆盖表 %d/%d 条" % (applied, len(titles), len(summaries)), flush=True)
    if applied != 1:
        print("警告：目标条目命中数不为 1", file=sys.stderr, flush=True)
    report.main()
    print("报告已重生", flush=True)


if __name__ == "__main__":
    main()
