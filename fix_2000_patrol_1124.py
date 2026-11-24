# -*- coding: utf-8 -*-
"""2026-11-24 20:00 例行巡检：定稿本轮新增 8 条 NLLB 机翻硬伤。

本轮整点调度新增 8 条（total 2701 -> 2709），均为 NLLB 原始机翻，硬伤包括：
1) Anthropic 被误译为「人类」（3 条：股票/员工质疑/Claude Ship）；
2) Exein（意大利公司）被误译为「埃克森」，Ray 被误译为「雷」；
3) Nasdaq premarket 被误译为「纳斯达克预售市场」（应为「盘前交易」）；
4) Security Posture Management 被误译为「安全姿势管理」（应为「安全态势管理」）；
5) Kenyans' Speech 条把 Swahili/English/Sheng 错译成中文混杂，语义严重失真；
6) CT scan 被误译为「脑电图扫描」；domain ontology 被误译为「域名解剖学」。

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
        "title": "Exein launches Ray AI agent to show manufacturers which firmware weaknesses to fix first",
        "title_zh": "Exein 推出 Ray AI 智能体，帮助制造商确定固件漏洞修复优先级",
        "summary_zh": (
            "意大利实体 AI 网络安全公司 Exein SpA 今日推出名为 Ray 的 AI 智能体，"
            "称其能帮助制造商找出联网设备固件中最值得关注的安全弱点。Ray 内置于该公司的"
            "固件安全平台 Exein Analyzer，该平台可检查固件中的漏洞、安全弱点与合规问题。"
        ),
    },
    {
        "title": "Why Does Voice AI Still Struggle With Kenyans\u2019 Speech?",
        "title_zh": "为什么语音 AI 仍难以识别肯尼亚人的口语？",
        "summary_zh": (
            "当人们朗读准备好的文本时，AI 转录斯瓦希里语的错误率极低，斯瓦希里语语音识别"
            "似乎已接近攻克。2026 年 3 月一篇由哈佛大学研究人员参与的预印本报告称，在 Mozilla "
            "Common Voice 志愿者录音数据集上词错误率仅为 3.24%。但肯尼亚人的日常说话方式与志愿者"
            "截然不同：他们会句中切换斯瓦希里语和英语、夹杂随街区变化的 Sheng 俚语、带着受母语"
            "影响的口音，还要在低端手机上面临公共交通噪音。另一篇 2026 年预印本覆盖 20 种非洲语言，"
            "指出这种自然、嘈杂、重叠的语音暴露了一种泛化差距——基于英语建立的缩放定律并未填补它。"
        ),
    },
    {
        "title": "CGI Brain-Hemorrhage AI Receives EU Medical Device Certification",
        "title_zh": "CGI 脑出血 AI 获欧盟医疗器械认证",
        "summary_zh": (
            "CGI 于 2026 年 11 月 24 日宣布，其与赫尔辛基大学医院和 Planmeca 合作开发的 "
            "CGI AI Head Analysis 已获得欧盟《医疗器械法规》IIb 类认证。该软件通过分析头部"
            "计算机断层扫描（CT）影像，检测非创伤性、自发性颅内出血，并标记疑似急性出血区域供医生复查。"
        ),
    },
    {
        "title": "Anthropic Shares Fall Below IPO Price in Nasdaq Premarket",
        "title_zh": "Anthropic 股价跌破 IPO 发行价，纳斯达克盘前交易承压",
        "summary_zh": (
            "2026 年 11 月 24 日，Anthropic 股价在纳斯达克盘前交易中跌破每股 83 美元的 IPO "
            "发行价。纳斯达克盘前报价显示，这家 AI 公司的 A 类普通股于美国东部时间 6:35 报 "
            "82.40 美元，较前一交易日收盘价下跌 5.98%，较发行价低约 0.7%。盘前最低价 81.28 美元、"
            "最高价 86.46 美元，当时约有 402 万股成交。"
        ),
    },
    {
        "title": "Anthropic's Claude Ship lets AI agents review, fix, and approve pull requests on their own",
        "title_zh": "Anthropic 推出 Claude Ship：AI 智能体可自主审查、修复并批准拉取请求",
        "summary_zh": (
            "Anthropic 推出处于测试阶段的新工具 Claude Ship，可根据团队指南自动审查、修正并批准代码变更建议。"
        ),
    },
    {
        "title": "Why AI Workloads Need Their Own Security Posture Management",
        "title_zh": "为什么 AI 工作负载需要专属的安全态势管理？",
        "summary_zh": (
            "云安全团队发现一个存有敏感训练数据的存储桶：访问控制配置正确、加密已启用、基础设施"
            "通过配置检查。但连接到该存储桶的 AI 应用所获权限，远远超出其预期任务所需；一名员工还把"
            "未经批准的 AI 服务接入了同一数据集。传统的云安全检查往往不会审查这两类问题。"
        ),
    },
    {
        "title": "Anthropic and OpenAI Staff Question Releasing Advanced AI Models",
        "title_zh": "Anthropic 与 OpenAI 员工质疑发布先进 AI 模型",
        "summary_zh": (
            "Axios 于 2026 年 11 月 24 日报道称，部分 Anthropic 与 OpenAI 员工不再相信某些尚未发布的 "
            "AI 模型能够安全发布。报道援引了二十多位知情人士，他们熟悉公司内部围绕限制部署以及是否继续训练的争论。"
        ),
    },
    {
        "title": "Presentation: Inferencing for Enterprises",
        "title_zh": "演讲：企业级推理的落地实践",
        "summary_zh": (
            "Dio Rettori 探讨企业 AI 推理的运营现实。他超越「快速生成 token」这一层面，剖析推理为何需要"
            "专门的系统工程，讨论 GPU 利用率的陷阱，对比本地部署与云端的总拥有成本（TCO），并分析多智能体"
            "延迟的确定性。他还分享了团队为何应把领域本体直接嵌入模型，而非仅仅依赖 RAG。"
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


if __name__ == "__main__":
    main()
