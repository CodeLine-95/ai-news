# -*- coding: utf-8 -*-
"""04:00 例行巡检：人工定稿 NLLB 机翻硬伤 + 修复 03:00 遗留的摘要回归。

03:00 巡检声称修复「Anthropic 人类→Anthropic」，但实际只写入了标题覆盖表，
摘要仍残留「人类已经成为地球上最有价值的公司之一」等硬伤。本轮补齐摘要覆盖，
并顺带定稿若干历史品牌名/术语机翻硬伤（Hugging Face / rack / seed round）。

按项目惯例写入三层：manual_overrides.py 代码层 + data/*_override.json 持久卷 + data/news.json 即时回填。
"""
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))

# 标题定稿
TITLE_FIXES = [
    {
        "en": "California's attorney general sues OpenAI over rogue AI models that attacked Hugging Face",
        "zh": "加州检察长起诉 OpenAI：其失控 AI 模型攻击了 Hugging Face",
    },
    {
        "en": "Corridian Raises $38M Seed to Build Ultra-Large Underwater Drones",
        "zh": "Corridian 获 3800 万美元种子轮融资，建造超大型水下无人机",
    },
    {
        "en": "NVIDIA Deepens Korean Sovereign AI Work on Chips and Rack Systems",
        "zh": "NVIDIA 深化韩国主权 AI 布局，聚焦芯片与机架系统",
    },
    {
        "en": "Rebellions to Use NVIDIA NVLink Fusion for Korean Sovereign AI",
        "zh": "Rebellions 采用 NVIDIA NVLink Fusion 构建韩国主权 AI",
    },
    {
        "en": "Rack-scale AI: How Dell and AMD are building infrastructure",
        "zh": "机架级 AI：戴尔与 AMD 如何构建基础设施",
    },
    {
        "en": "The Inference Economics Scorecard Challenges GPU Utilization as an AI Performance Metric",
        "zh": "「推理经济学记分卡」挑战以 GPU 利用率作为 AI 性能指标",
    },
]

# 摘要定稿（含 03:00 遗留的 Anthropic 摘要回归）
SUMMARY_FIXES = [
    {
        "en": "Can Anthropic afford to put safety first?",
        "zh": (
            "今天，我和 The Verge 高级人工智能记者 Hayden Field 聊到了 Anthropic 的 IPO——"
            "这是我们关于「现实生活中的 AI」系列节目的第三集，也是最后一集。"
            "Claude 背后的人工智能实验室上周四在纳斯达克上市。这些数字很庞大，但对这次对话来说"
            "并不那么重要，只要说一点：Anthropic 已经成为地球上最有价值的公司之一。"
            "真正的故事是接下来会发生什么——Anthropic 能否在继续关心并投入 AI 安全的同时，"
            "妥善拿捏作为一家需要对股东负责的上市公司所面临的平衡。"
            "此外，它还得不断扩大营收，以支付持续攀升的算力账单——未来几年这笔账单总额约为 9000 亿美元。"
        ),
    },
    {
        "en": "California's attorney general sues OpenAI over rogue AI models that attacked Hugging Face",
        "zh": (
            "加州检察长 Rob Bonta 正就一起网络攻击起诉 OpenAI——"
            "该公司失控的 AI 模型于 7 月对 AI 平台 Hugging Face 发动了攻击。"
        ),
    },
    {
        "en": "Corridian Raises $38M Seed to Build Ultra-Large Underwater Drones",
        "zh": (
            "新英格兰防务技术公司 Corridian 于 2026 年 11 月 3 日宣布结束隐身状态，"
            "完成由 Point72 Ventures 领投的 3800 万美元种子轮融资，"
            "用于开发超大型自主水下航行器、扩建研发设施并招聘水下工程师。"
            "Balerion Space Ventures、Harpoon Ventures、DCVC 和 Marlinspike 也参与了本轮融资，"
            "另有一批国防与深度科技投资者跟投。"
        ),
    },
    {
        "en": "Teledyne LeCroy Launches 800G UALink Tester for AI Scale-Up Networks",
        "zh": (
            "2026 年 11 月 16 日，Teledyne LeCroy 宣布推出 Xena Z2244 UALink 流量测试仪，"
            "这是一款可采购的系统，将每台设备高达 800 Gb/s 的线速流量生成与错误注入相结合，"
            "面向 AI 和高性能计算的纵向扩展（scale-up）网络。UALink 是 AI 计算中加速器通信的开放标准，"
            "其 200G 1.0 规格为加速器与交换机之间提供每条通道 200G，并支持多达 1024 个加速器。"
            "纵向扩展意味着在机架层面提升容量与带宽。"
        ),
    },
    {
        "en": "The Inference Economics Scorecard Challenges GPU Utilization as an AI Performance Metric",
        "zh": (
            "繁忙的 GPU 未必是高效的 GPU。「推理经济学记分卡」正是基于这一观点——"
            "这是 NAND Research 与 WEKA 推出的一项新研究，提出了判断生产环境 AI 基础设施的更广泛方法。"
            "该框架将关注点从芯片活动转移到服务目标内提供的有用产出，并以功耗、机架空间和成本来衡量。"
        ),
    },
    {
        "en": "Google Unveils TPU 8i Max and TPU 8tx: A Dual-Chip TPU and a Confidential TPU",
        "zh": (
            "Google 在第八代 TPU 产品线中新增两套系统。TPU 8i Max 面向超大上下文窗口和机架密度，"
            "TPU 8tx 则面向安全的机密推理。Google TPU 8i Max 是一款由两颗 TPU 8i 芯片构成的双芯片封装。"
            "两者都与 4 月发布的 TPU 8t 和 TPU 8i 一同供货。规格速览：TPU 8i Max = 单个封装内 2 颗 TPU 8i 芯片；"
            "8tx = TPU 8t 加第五代 AMD EPYC 主机。运行于 Google Cloud TPU 系统。性能方面，"
            "8i Max 将 TPU 8i 的计算能力、SRAM 与……"
        ),
    },
    {
        "en": "NVIDIA Deepens Korean Sovereign AI Work on Chips and Rack Systems",
        "zh": (
            "2026 年 11 月 9 日，NVIDIA 宣布扩大与韩国科学技术信息通信部的合作，"
            "涵盖 AI 芯片、数据中心、模型、技能与智能体安全。该硬件项目以 Rebellions 的 R200 处理器"
            "和基于 NVLink 的机架系统为核心，预计 2028 年具备部署条件。"
        ),
    },
    {
        "en": "Rebellions to Use NVIDIA NVLink Fusion for Korean Sovereign AI",
        "zh": (
            "2026 年 11 月 8 日，NVIDIA 宣布与 Rebellions 及 SK Telecom 合作，"
            "将 Rebellions 下一代 R200 处理器接入 NVLink Fusion，用于韩国主权 AI 基础设施，"
            "由此构建的系统预计 2028 年具备部署条件。根据协议，Rebellions 将通过 NVLink Fusion "
            "连接其 Rebel R200 神经处理单元（NPU），并围绕 NVIDIA MGX 架构开发机架级系统。"
        ),
    },
    {
        "en": "Rack-scale AI: How Dell and AMD are building infrastructure",
        "zh": (
            "戴尔科技及其合作伙伴超威半导体（AMD）面临相似的竞争压力。"
            "这两家科技巨头所处的商业环境中，成功的衡量标准如今已扩展到中央处理器、图形处理器、"
            "机架级系统、内存容量、网络带宽以及每美元所能获得的 token 数。"
        ),
    },
]


def upsert_py(path, dict_name, pairs):
    with open(path, "r", encoding="utf-8") as f:
        src = f.read()
    marker = f"{dict_name} = {{"
    start = src.index(marker) + len(marker)
    m = re.search(r"\n\}\n", src[start:])
    end = start + m.start() + 1
    block = src[start:end]
    for key, value in pairs:
        pat = re.compile(r"(\s*)" + re.escape(repr(key)) + r"\s*:\s*.*?(?=,\n|\n\})", re.S)
        if pat.search(block):
            block = pat.sub(lambda mm: f"{mm.group(1)}{key!r}: {value!r}", block, count=1)
        else:
            block = block.rstrip() + f"\n    {key!r}: {value!r},\n"
    src = src[:start] + block + src[end:]
    with open(path, "w", encoding="utf-8") as f:
        f.write(src)


def main():
    # 1) 代码层
    py_path = os.path.join(BASE, "manual_overrides.py")
    upsert_py(py_path, "TITLE_OVERRIDES", [(f["en"], f["zh"]) for f in TITLE_FIXES])
    upsert_py(py_path, "SUMMARY_OVERRIDES", [(f["en"], f["zh"]) for f in SUMMARY_FIXES])
    print("已写入 manual_overrides.py（标题 %d / 摘要 %d）" % (len(TITLE_FIXES), len(SUMMARY_FIXES)))

    # 2) 持久卷 JSON
    for fname, fixes, field in [
        ("titles_override.json", TITLE_FIXES, "zh"),
        ("summaries_override.json", SUMMARY_FIXES, "zh"),
    ]:
        p = os.path.join(BASE, "data", fname)
        d = json.load(open(p, encoding="utf-8"))
        for f in fixes:
            d[f["en"]] = f[field]
        with open(p, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
        print(f"已写入 {fname}（+{len(fixes)}）")

    # 3) news.json 即时回填
    p = os.path.join(BASE, "data", "news.json")
    d = json.load(open(p, encoding="utf-8"))
    items = d.get("items", d) if isinstance(d, dict) else d
    tmap = {f["en"]: f["zh"] for f in TITLE_FIXES}
    smap = {f["en"]: f["zh"] for f in SUMMARY_FIXES}
    hit_t = hit_s = 0
    for it in items:
        title = (it.get("title") or "").strip()
        if title in tmap:
            it["title_zh"] = tmap[title]
            it["translated"] = True
            it["method"] = "manual"
            hit_t += 1
        if title in smap:
            it["summary_zh"] = smap[title]
            it["translated"] = True
            it["method"] = "manual"
            hit_s += 1
    with open(p, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
    print(f"news.json 回填：标题 {hit_t} 条 / 摘要 {hit_s} 条；总数={len(items)}")


if __name__ == "__main__":
    main()
