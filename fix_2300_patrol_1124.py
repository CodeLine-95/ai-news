# -*- coding: utf-8 -*-
"""2026-11-24 23:00 例行巡检：定稿本轮新增 10 条 NLLB 机翻硬伤。

本轮整点调度新增 10 条（total 2731 -> 2741），全部为 NLLB 原始机翻，硬伤包括：
1) The Biggest Risk... 标题「智能体人工智能」生硬，摘要「观察智能体做什么」漏掉治理语境；
2) Gary Vaynerchuk 音译错乱（「盖里·维纳丘」），AI avatar 误作「人工智能化器」，channel 漏译；
3) Anthropic 被译成「人类科学研究员」，Riemann 误作「里曼」，proof 误作「证据」，25 万页/垃圾代码语义错位；
4) Shirudo 条 runtime 误作「运行时间」，摘要中 "temporary shields" 残留英文，Java4Shell/CVSS 等关键信息缺失；
5) OpenAI and Anthropic 的 Anthropic 误作「人类」，outgrown safety measures 语义错位；
6) Astelia（SiliconANGLE）音译错乱（「亚斯泰利亚」），exploits 残留英文，without a patch 语序错乱；
7) Brava Security 误作「勇敢的安全」（把品牌名当形容词），摘要「布拉瓦安全」同样失真；
8) Cloudera 误作「云拉」，air-gapped 误作「空隙」；
9) Astelia（Unite.AI）音译错乱（「阿斯泰利亚」），mitigation 误作「减轻」；
10) AI Venture Capital 漏译 AI，recurring revenue 误作「反复收入」，funding race 语义失真。

覆盖三层：news.json 回填 + JSON 覆盖表 + 代码层 manual_overrides.py（regen）。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

FIXES = [
    {
        "title": "The Biggest Risk in Agentic AI Is Not the Agent But the Business It Doesn’t Understand",
        "title_zh": "智能体 AI 最大的风险不是智能体，而是它所不理解的业务",
        "summary_zh": (
            "OpenAI 近期披露的情况暴露了企业 AI 治理的一个关键弱点：如果智能体还能改动那些"
            "用来约束它们的管控措施，那么仅仅监视它们的行为是不够的。"
        ),
    },
    {
        "title": "Gary Vaynerchuk Launches Daily AI Avatar Advice Channel With HeyGen",
        "title_zh": "Gary Vaynerchuk 与 HeyGen 推出每日 AI 头像建议频道",
        "summary_zh": (
            "HeyGen 与 Gary Vaynerchuk 于 2026 年 11 月 24 日推出 @hey_garyvee——一个 Instagram "
            "与 TikTok 频道，他的 AI 头像将在 365 天里每天回答一位观众的问题，并可选择用提问者的"
            "语言作答。该项目把观众提问变成一档持续更新的公开视频系列，而非私人聊天机器人。"
            "每个入选的回答都旨在针对提问者的具体业务状况与市场环境。"
        ),
    },
    {
        "title": "Anthropic researcher stands by his AI-assisted Riemann proof but owns up to \"stupid things\" in the rollout",
        "title_zh": "Anthropic 研究员坚持其 AI 辅助的黎曼猜想证明，但承认发布过程中做了「蠢事」",
        "summary_zh": (
            "Anthropic 研究员 Levent Alpöge 正在收回其关于 AI 辅助证明广义黎曼猜想的部分公告内容。"
            "他说，所谓证明长达 25 万页的说法是个玩笑，而公开的 Lean 代码「满是垃圾」。"
            "但他仍坚持数学部分的正确性。"
        ),
    },
    {
        "title": "OpenAI and Cisco Releases Shirudo: An Open-Source Linux Runtime Allowing Agents to Defend Systems Without Downtime",
        "title_zh": "OpenAI 与思科发布 Shirudo：开源 Linux 运行时，让智能体无需停机即可防护系统",
        "summary_zh": (
            "OpenAI 与思科发布了 Shirudo——一款用于保护运行中系统的开源 Linux 运行时。Shirudo "
            "是一个 eBPF 运行时，可让 AI 智能体针对已知漏洞编写临时「防护罩」。防护罩会阻断有漏洞的"
            "行为，同时合法请求照常通过，团队因此有时间测试并部署真正的补丁。该工程来自思科旗下 "
            "Isovalent（Cilium 与 Tetragon 背后的团队）。速览：它是软件运行时，不是模型；代码尚处"
            "预发布阶段；支持 x86-64、arm64 与 riscv64 架构的 Linux，需 TPM 2.0 与打了补丁的 "
            "bpf-next 内核；快速入门虚拟机示例使用 4 CPU 与 4G 内存；官方未公布开销或延迟数据，"
            "仅披露一次受控漏洞利用测试。最佳案例：Codex 生成的防护罩在运行中的 Elasticsearch "
            "9.5.5 上阻断了 Java4Shell（CVSS 9.2），无需重启。局限：目标系统需要 bpf-next 内核"
            "外加 5 个尚未合入 bpf-next 的补丁。"
        ),
    },
    {
        "title": "Dozens of insiders say OpenAI and Anthropic's unreleased models have outgrown their safety measures",
        "title_zh": "数十名内部人士称，OpenAI 与 Anthropic 未发布的模型已超出其安全措施的掌控",
        "summary_zh": (
            "据 Axios 报道，OpenAI 与 Anthropic 的许多员工认为，这两家公司尚未发布的前沿模型"
            "已无法被安全地控制。两家公司内部都在讨论是否暂停发布、甚至完全停止训练，"
            "而员工对领导层的信任正在削弱。"
        ),
    },
    {
        "title": "Astelia’s autonomous network mitigation blocks AI-driven exploits without a patch",
        "title_zh": "Astelia 的自主网络缓解能力无需补丁即可阻断 AI 驱动的攻击利用",
        "summary_zh": (
            "暴露管理公司 Astelia Inc. 今日宣布推出自主网络缓解（autonomous network mitigation）"
            "能力——一项可让组织在网络层面阻断 AI 驱动攻击利用的新功能，即便补丁尚不可用或无法应用。"
        ),
    },
    {
        "title": "Brava Security Warns That Untrusted Logs Can Undermine AI Threat Detection",
        "title_zh": "Brava Security 警告：不可信日志会削弱 AI 威胁检测",
        "summary_zh": (
            "Brava Security 的研究强调，AI 辅助的安全团队在把日志当作证据之前，"
            "需要先对其进行交叉验证。"
        ),
    },
    {
        "title": "Cloudera Combines Its Data Platform and Mistral Models for Sovereign AI",
        "title_zh": "Cloudera 将数据平台与 Mistral 模型结合，面向主权 AI",
        "summary_zh": (
            "Cloudera 的新产品将其混合数据平台与 Mistral 模型相结合，面向主权云、"
            "私有数据中心与气隙（air-gapped）部署场景。"
        ),
    },
    {
        "title": "Astelia Adds Autonomous Network Mitigation for Systems That Cannot Patch Yet",
        "title_zh": "Astelia 为尚无法打补丁的系统增加自主网络缓解能力",
        "summary_zh": (
            "Astelia 正在为安全团队提供一种新手段，可在不改动系统上运行软件的情况下遏制存在"
            "漏洞的系统。该公司于 11 月 24 日宣布，其暴露管理平台能在组织设定的策略范围内，"
            "在网络层面实施临时保护。该功能针对的是补丁不可用、或立即安装补丁会中断关键服务的场景。"
        ),
    },
    {
        "title": "AI Venture Capital in 2027: Revenue Quality Will Reshape the Funding Race",
        "title_zh": "2027 年 AI 风险投资：收入质量将重塑融资竞赛",
        "summary_zh": (
            "两家初创公司可能报告相同的经常性收入，但业务实质可能截然不同。一家靠可复制的产品"
            "留住客户，另一家则靠高昂的推理成本、实施工作和创始人不断介入来「买」增长。一轮亮眼的"
            "融资可能让这些差异暂时被忽视。到了 2027 年，更多 AI 投资故事将不得不再度经受运营"
            "数据的审视。"
        ),
    },
]


def main():
    db = json.load(open(DATA, encoding="utf-8"))
    items = db["items"] if isinstance(db, dict) else db
    titles = json.load(open(T_JSON, encoding="utf-8"))
    summaries = json.load(open(S_JSON, encoding="utf-8"))

    by_title = {fx["title"].strip(): fx for fx in FIXES}

    changed = 0
    for it in items:
        key = (it.get("title") or "").strip()
        fx = by_title.get(key)
        if not fx:
            continue
        it["title_zh"] = fx["title_zh"]
        it["summary_zh"] = fx["summary_zh"]
        it["translated"] = True
        it["method"] = "nllb+manual"
        changed += 1
        print("fixed:", it.get("date"), it.get("time"), key[:60])

    for fx in FIXES:
        titles[fx["title"]] = fx["title_zh"]
        summaries[fx["title"]] = fx["summary_zh"]

    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    with open(T_JSON, "w", encoding="utf-8") as f:
        json.dump(titles, f, ensure_ascii=False, indent=2)
    with open(S_JSON, "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)

    print("回填条目:", changed)
    assert changed == len(FIXES), "定稿条目数不符：%d != %d" % (changed, len(FIXES))


if __name__ == "__main__":
    main()
