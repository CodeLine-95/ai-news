# -*- coding: utf-8 -*-
"""09:00 例行巡检：人工定稿 7 条 NLLB 机翻硬伤。

本轮（08:00 整点调度，进程重启后首轮抓取）新增 7 条，机翻硬伤包括：
- Harbour BioMed→生物医疗港口/港口生物医药（公司名误译，应为「和铂医药」）
- ClickUp→单击、Notion→概念（产品名误译，应保留原名）
- supercomputing bottleneck→超级计算瓶（漏译「颈」）
- AWS Full-Weight Training→全重训练（应为「全权重训练/全量微调」）、FFT→全细调
- TRM Labs' Ardence→TRM 实验室（应保留）、Anchor Probes→安装探测器（应为「支撑/锚定…调查」）
- Perplexity AI teammates→AI 队友、「转移工作」语义不通
- 60K employees buyouts→提供收购（应为「提供买断/自愿离职补偿」）

固化覆盖三层：
1) data/news.json 内条目直接回填
2) data/titles_override.json / data/summaries_override.json（JSON 层）
3) 再运行 scripts/regen_overrides.py 同步到 manual_overrides.py（代码层）
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

FIXES = [
    {
        "match": "ClickUp vs. Notion",
        "title_zh": "ClickUp 与 Notion：哪款更适合你的团队？",
        "summary_zh": (
            "一个项目可能有清晰的任务简报，却依然错过最后期限；也可能每项任务都已分配，"
            "却没人说得清背后的理由。ClickUp 与 Notion 都能解决这两个问题，但组织工作的方式不同。"
            "在协调团队交付方面，ClickUp 是我们的更强选择；当文档、共享知识和灵活数据库成为工作核心时，"
            "Notion 则是我们的首选。两者都出现在我们的最佳 AI 协作工具指南中。"
        ),
    },
    {
        "match": "TRM Labs’ Ardence Will Anchor",
        "title_zh": "TRM Labs 的 Ardence 将支撑新威胁打击中心的调查工作",
        "summary_zh": (
            "美国国土安全特别工作组国家协调中心宣布，将于 2026 年 11 月 18 日启动威胁打击中心，"
            "并选定 TRM Labs 的 Ardence 平台，帮助调查人员绘制犯罪网络图谱，"
            "并针对针对美国民众的诈骗与网络犯罪协调更快速的干预。该协调中心由国土安全部与司法部共同领导。"
        ),
    },
    {
        "match": "Google Cloud brings AI agents to the supercomputing bottleneck",
        "title_zh": "Google Cloud 将 AI 智能体引入超级计算瓶颈",
        "summary_zh": (
            "高性能计算（HPC）正与人工智能加速融合，其速度超出许多研究团队的适应能力。"
            "算力难以获取，工作负载如今跨云端和本地集群运行。真正重要的指标，正从峰值性能转向「获得发现所需的时间」。"
        ),
    },
    {
        "match": "Perplexity Brings Voice-Controlled AI Teammates to Mobile",
        "title_zh": "Perplexity 将语音控制的 AI 队友带到移动端",
        "summary_zh": (
            "Perplexity 于 2026 年 11 月 18 日为其 AI 队友在 iOS 和 Android 上新增语音模式，"
            "让 Max 订阅用户可通过电话分配项目、接收更新并调整正在进行的工作。"
            "此举为 Perplexity Computer 中的个人智能体提供了一个移动端控制点，使用户无需守在办公桌前也能工作。"
            "用户可点按通话按钮开始一项任务，随后回拨电话讨论调整后的优先事项。"
            "AI 队友会规划工作、核查结果，并返回成果供用户审阅。"
        ),
    },
    {
        "match": "Harbour BioMed’s AI-Enabled Obesity Antibody",
        "title_zh": "和铂医药 AI 驱动的肥胖抗体 LET003 获临床试验申请受理",
        "summary_zh": (
            "和铂医药（Harbour BioMed）于 2026 年 11 月 18 日宣布，中国国家药品监督管理局已受理"
            " LET003 的临床试验新药（IND）申请。LET003 是公司利用 Hu-mAtrIx AI 平台开发的首个候选药物。"
            "这款单克隆抗体旨在通过阻断激活素受体 ACVR2A 和 ACVR2B 来治疗超重或肥胖。"
            "这一里程碑意味着进入临床开发的申请获得受理，并非已公布的临床结果。"
        ),
    },
    {
        "match": "AWS Brings Full-Weight Training",
        "title_zh": "AWS 将全权重训练引入无服务器 SageMaker 定制",
        "summary_zh": (
            "亚马逊云科技（AWS）于 2026 年 11 月 18 日宣布为 SageMaker AI 无服务器模型定制"
            "提供全量微调（FFT）支持，并报告在一项使用超过 10 万个训练样本的编码实验中达到 90.0% 的语义正确率，"
            "同时警告称过于激进的参数设置会造成严重的通用知识流失。"
        ),
    },
    {
        "match": "Microsoft CEO Satya Nadella explains why he asked 60K employees",
        "title_zh": "微软 CEO 萨蒂亚·纳德拉解释为何要求 6 万名员工离职",
        "summary_zh": (
            "微软 CEO 萨蒂亚·纳德拉解释了为何在 10 月向 6 万名员工提供自愿离职买断方案，"
            "实质上是敦促他们主动辞职，而非通过又一轮大规模裁员来缩减员工队伍。"
            "简短的答案是人工智能，但原因并非你可能想象的那样。"
        ),
    },
]


def main():
    with open(os.path.join(DATA, "news.json"), encoding="utf-8") as f:
        db = json.load(f)
    items = db["items"] if isinstance(db, dict) else db

    tpath = os.path.join(DATA, "titles_override.json")
    spath = os.path.join(DATA, "summaries_override.json")
    tov = json.load(open(tpath, encoding="utf-8")) if os.path.exists(tpath) else {}
    sov = json.load(open(spath, encoding="utf-8")) if os.path.exists(spath) else {}

    changed = 0
    for fx in FIXES:
        hit = None
        for it in items:
            if fx["match"].lower() in (it.get("title") or "").lower():
                hit = it
                break
        if not hit:
            print("MISS:", fx["match"])
            continue
        en = hit["title"]
        hit["title_zh"] = fx["title_zh"]
        hit["summary_zh"] = fx["summary_zh"]
        hit["translated"] = True
        hit["method"] = "nllb+manual"
        tov[en] = fx["title_zh"]
        sov[en] = fx["summary_zh"]
        changed += 1
        print("fixed:", hit.get("date"), hit.get("time"), en[:70])

    with open(tpath, "w", encoding="utf-8") as f:
        json.dump(tov, f, ensure_ascii=False, indent=2)
    with open(spath, "w", encoding="utf-8") as f:
        json.dump(sov, f, ensure_ascii=False, indent=2)
    with open(os.path.join(DATA, "news.json"), "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    print("changed:", changed, "/", len(FIXES))


if __name__ == "__main__":
    main()
