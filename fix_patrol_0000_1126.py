# -*- coding: utf-8 -*-
"""2026-11-26 00:00 例行巡检：定稿新增 6 条与存量 2 条 NLLB 错译。

本轮错译集中在术语层面：open-weight→「开放模型」、context→「文本」、
Chariot→「卡车」、foundation model→「基金会模型」、neocloud→「新云」。
同引擎重译会复现同类错误，因此沿用人工定稿覆盖表（优先级最高）。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")
NEWS = os.path.join(BASE, "data", "news.json")

FIXES = {
    "Open-weight models are the hottest thing in AI. Are they right for you?": (
        "开放权重模型是当下 AI 最热门的话题，它们适合你吗？",
        "在生成式 AI 热潮的前三年，企业的技术战略遵循一条简单规则：选用最顶尖的前沿基础模型，"
        "把所有提示都通过其商业 API 发送，并支付订阅溢价以获取最先进的技术。",
    ),
    "The Hidden Cost of AI Coding: Why Context Matters More Than Tokens": (
        "AI 编程的隐性成本：为什么上下文比 token 更重要",
        "过去一年，我与技术领导者的对话发生了明显变化。当时我们问的是：大语言模型能否更快、"
        "更好地编写代码、生成文档并运行测试？如今，更值得追问的是：这一切究竟让我们付出了多少成本？"
        "近期报告显示，AI 开支会迅速累积——Uber 到今年 4 月就已耗尽 2026 年全年的 AI 预算。",
    ),
    "Lute Raises $20M Across Pre-Seed and Seed to Scale Physical AI": (
        "机器人初创公司 Lute 完成 Pre-Seed 与 Seed 轮共 2000 万美元融资，加速物理 AI 落地",
        "OTB Ventures 于 2026 年 11 月 25 日宣布，与 FORWARD.one 共同领投机器人初创公司 Lute 的种子轮，"
        "使该公司 Pre-Seed 与 Seed 两轮融资总额达到 2000 万美元。这笔资金将用于扩大触觉数据采集、"
        "改进 Lute 的模型并支持客户部署。Seedcamp、Credo Ventures、Naval Ravikant、Inovo VC、"
        "ff Venture Capital 和 Borusan Ventures 也参与投资。",
    ),
    "AI data centers are becoming harder to build, and neoclouds are feeling it": (
        "AI 数据中心越来越难建，新型云服务商（neocloud）首当其冲",
        "Nvidia 已明确表示，在 AI 数据中心接近可运行之前不会为其兜底；与此同时，新型云服务商正报告"
        "工期延误和债务成本上升。这一信号传递给开发者的是：土地、电力和建成的厂房，比一份演示文稿更重要。"
        "而 Anita Verma-Lallian 一直在做的正是这类生意。",
    ),
    "AI Is Speeding Up Security Disclosures. Patches Still Move at Different Speeds": (
        "AI 正在加速安全漏洞披露，但补丁修复速度仍参差不齐",
        "Eclypsium 11 月报告显示，AI 辅助研究可以加快漏洞披露，但下游固件修复仍需更长时间。",
    ),
    "Chariot Launches Sovereign Foundation Models Under IndiaAI Mission": (
        "Chariot 在 IndiaAI 计划下推出主权基础模型",
        "印度 AI 使命（IndiaAI Mission）于 2026 年 11 月 25 日宣布，电子与信息技术部秘书 S. Krishnan "
        "为 Chariot Artificial Intelligence 的 Chariot-1 基础模型揭幕。该系列模型完全在印度从零研发，"
        "覆盖英语及 10 种印度语言。Chariot 是该计划首批入选、负责构建主权基础模型的四个团队之一。",
    ),
    "What Is Physical AI? How Foundation Models Are Moving Into the Real World": (
        "什么是物理 AI？基础模型如何走进现实世界",
        "物理 AI 将习得的感知、推理与控制能力应用到真实世界中行动的机器上；在这些场景里，"
        "不确定性、物理规律和安全约束都不容忽视。本指南解释了实践中真正重要的机制、权衡、评估方法与管控手段。",
    ),
    "MBZUAI’s IFM Releases PAN 2, an Open 29B World Model for Physical AI": (
        "MBZUAI 旗下 IFM 发布 PAN 2：面向物理 AI 的开放 29B 世界模型",
        "MBZUAI 基础模型研究所（IFM）发布了 PAN 2——面向物理智能的开放世界模型。PAN 2 接收场景与文本动作，"
        "并将结果模拟为视频。IFM 于 2026 年 11 月 10 日在 X 上宣布这一消息。模型权重、训练代码和推理代码"
        "均以 Apache 2.0 许可发布。对机器人与智能体开发者来说，其卖点很简单：先仿真测试方案，再付诸行动。"
        "要点速览：规模为 290 亿参数的稠密扩散 Transformer（MMDiT）；输入为文本加可选的首帧；"
        "输出为 704×1248、24 fps、最长 20 秒的视频；运行于数据中心 GPU；每个工作节点以 BF16 持有完整 29B 模型，"
        "并以分块卸载作为后备方案。性能方面，PAN 2 在完整方案任务上领先 6 个受测模型，"
        "但在单步动作和人类偏好方面落后于 MiniMax-H3；最佳成绩为 100 个多步骤任务上 34.0% 的完整方案完成率，"
        "为所有受测模型中最高（自报数据）。",
    ),
}


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    titles, summaries = load(T_JSON), load(S_JSON)
    for key, (title_zh, summary_zh) in FIXES.items():
        titles[key] = title_zh
        summaries[key] = summary_zh
    save(T_JSON, titles)
    save(S_JSON, summaries)

    news = load(NEWS)
    fixed = 0
    for it in news["items"]:
        fix = FIXES.get(it.get("title"))
        if not fix:
            continue
        it["title_zh"], it["summary_zh"] = fix
        it["translated"] = True
        it["method"] = "manual"
        fixed += 1
    save(NEWS, news)
    print("定稿条目数:", fixed)


if __name__ == "__main__":
    main()
