# -*- coding: utf-8 -*-
"""17:00 例行巡检（第二批）：人工定稿本轮新增的高受损条目译文。

问题条目（均为 2026-11-02 新增）：
  1) 'EASE Raises $9.5M Equity to Scale AI Medical Devices in South Africa, Ghana'
     （Unite.AI, 16:38）
     - 标题把公司名 EASE 意译成「易 ASE」，公司名彻底丢失；
     - equity（股权/股本次融资）被译成「资产」，在融资语境下完全错误；
     - 中文顿号错用：「南非，加纳」应为「南非、加纳」。

  2) 'RWS Closes £22.4M Enterprise-Value Deal For Acolad Parent Acogroup'
     （Unite.AI, 16:26）
     - 货币单位被截断：「2240 万英」应为「2240 万英镑」；
     - 标题语序生硬：「为 Acolad Parent Acogroup」。

  3) 'NVIDIA Releases Auto Ontology: An Open Semantic Layer That Grounds AI Agent SQL'
     （MarkTechPost, 15:47）
     - 产品名 Auto Ontology 被意译成「自动解读」；
     - open library 被译成「开放的图书馆」（软件语境应为「开源库」）；
     - context layer 被译成「文本层」（应为「上下文层」）；
     - against 误解为「相反」，语义反转：「写 SQL 与认证的商业定义相反」；
     - harness 被译成「运势」，完全不通；
     - 结构标签中英混杂（Runs on: / Performance: / Best: / Worst: 未译）。

  4) 'Meet qwenGPU: Qwen3.5-2B With 45 Compiled GPU Layers That Run CUDA'
     （MarkTechPost, 15:28）
     - weights（权重）被译成「重量」；
     - Apple 被意译成单字「果」，中文不通；
     - 结构标签中英混杂（Size: / Context: / Runs on: 等）。

根因修复（translate.py）：
     - TERM_FIXES 补入上述术语（易 ASE→EASE、万美元的资产→万美元的股权、
       自动解读→Auto Ontology、开放的图书馆→开源库、文本层→上下文层、
       运势→测试框架、重量→权重、相反→针对…编写 SQL 等）；
     - 新增 _fix_currency_units：原文含货币符号时补全被截断的中文单位；
     - 新增 _fix_struct_labels：把残留英文结构标签统一译为中文；
     - 新增 _fix_bare_apple：还原被意译成单字「果」的 Apple 品牌。

处理：写入人工定稿标题 + 摘要覆盖，并回写数据。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

FINAL = {
    # ---- EASE ----
    "EASE Raises $9.5M Equity to Scale AI Medical Devices in South Africa, Ghana": {
        "title": "EASE 融资 950 万美元，扩展南非、加纳的人工智能医疗设备业务",
        "summary": (
            "荷兰医疗设备即服务提供商 EASE Holdings BV 已从新兴市场资产支持融资"
            "投资方 AAFC Group Inc（一家美国公司）获得 950 万美元新增股权融资，"
            "用于扩大其在南非和加纳的业务规模，该公司于 2026 年 11 月 2 日宣布。"
            "本轮融资后，EASE 的股权总额达到 2400 万美元。"
        ),
    },
    # ---- RWS ----
    "RWS Closes £22.4M Enterprise-Value Deal For Acolad Parent Acogroup": {
        "title": "RWS 完成 2240 万英镑企业价值交易，收购 Acolad 母公司 Acogroup",
        "summary": (
            "RWS 于 2026 年 11 月 2 日宣布，已完成对 Acogroup 的收购。"
            "Acogroup 是语言与内容服务提供商 Acolad 的母公司，本次交易的企业价值为"
            " 2240 万英镑，公司层面已完成社会协商程序并取得全部监管批准。"
        ),
    },
    # ---- NVIDIA Auto Ontology ----
    "NVIDIA Releases Auto Ontology: An Open Semantic Layer That Grounds AI Agent SQL": {
        "title": "NVIDIA 发布 Auto Ontology：为智能体 SQL 提供语义依据的开放语义层",
        "summary": (
            "NVIDIA 发布了 Auto Ontology，这是一个基于 Apache 2.0 许可的开源库。"
            "NVIDIA Auto Ontology 是一个语义层框架，可从企业元数据构建上下文层，"
            "智能体借此层针对经过认证的业务定义编写 SQL。该仓库把要解决的问题讲得很直白："
            "如果数字是错的，再快的营收答案也毫无价值。"
            "速览——库：默认 LLM 为 nvidia/nemotron-3-nano-30b-a3b，"
            "并搭配 Nemotron 嵌入与重排模型。运行方式：本地可用 Docker Compose 部署，"
            "或通过 Helm 部署到 Kubernetes。推理：可使用托管的 NVIDIA NIM 端点，也可自托管 NIM。"
            "表现：工程实现扎实，但公开证据有限。最佳：据 NVIDIA 自测，本体创建时间缩短 90%。"
            "最差：未公布任何 text-to-SQL 准确率分数——评测仓库只提供评测框架，未发布结果。"
        ),
    },
    # ---- qwenGPU ----
    "Meet qwenGPU: Qwen3.5-2B With 45 Compiled GPU Layers That Run CUDA": {
        "title": "认识 qwenGPU：Qwen3.5-2B 搭载 45 层可运行 CUDA 的编译 GPU 层",
        "summary": (
            "qwenGPU 是一个实验性模型，可将 SIMT GPU 直接编译进 Qwen3.5-2B 的权重中。"
            "开发者 Vixhal（@TheVixhal）已在 GitHub 上以 MIT 许可发布该项目。"
            "该模型在自身的前向传播中运行真实的 CUDA 代码，编译目标为 NVIDIA PTX。"
            "对开发者而言，它验证了一个想法：在预训练 LLM 内部做精确计算，而不是在模型旁边计算。"
            "速览——规模：Qwen3.5-2B（24 层）加上 45 层编译 GPU 层，共 69 层。"
            "上下文：262,144 token（基础模型）。运行方式：Apple Silicon、NVIDIA GPU 或 CPU，"
            "需约 16 GB 空闲内存。未提供量化版本。表现：开发者运行中的每次启动均为精确计算，"
            "文本漂移约为 7e-4 的 KL。最佳：参考解释器在 49 个内核中有 49 个与真实 NVIDIA Tesla T4 结果一致。"
            "最差：在 Apple MPS 上约为每秒 10 至 15 token；Qwen 写出的 CUDA 通过了 5 项中的 4 项。"
        ),
    },
}


def main():
    for path, key in ((T_JSON, "title"), (S_JSON, "summary")):
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
        changed = 0
        for en, vals in FINAL.items():
            if d.get(en) != vals[key]:
                d[en] = vals[key]
                changed += 1
        with open(path, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
        print("[fix_1700] 已更新覆盖表:", os.path.basename(path), "改动", changed, "条")

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    hit = 0
    for it in data.get("items", []):
        vals = FINAL.get(it.get("title"))
        if not vals:
            continue
        it["title_zh"] = vals["title"]
        it["summary_zh"] = vals["summary"]
        it["translated"] = True
        hit += 1
        print("[fix_1700] 已回写:", it["title"][:58])
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("[fix_1700] 已回写数据 %d 条" % hit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
