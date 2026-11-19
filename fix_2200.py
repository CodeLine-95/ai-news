# -*- coding: utf-8 -*-
"""22 点巡检：本轮 9 条 NLLB 机翻硬伤人工定稿。

- 英文标题 -> 中文标题 写入 titles_override.json
- 英文标题 -> 中文摘要 写入 summaries_override.json
- 按 id 精确回填 data/news.json 的 title_zh / summary_zh，method 标记 manual
- 重生成 Markdown 摘要报告

纯确定性处理，不加载翻译模型，避免与后台调度争内存。
"""
import json
import os
import report

BASE = os.path.dirname(os.path.abspath(__file__))
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")
N_JSON = os.path.join(BASE, "data", "news.json")

# (id, 英文原标题, 定稿中文标题, 定稿中文摘要)
FIXES = [
    ("02881da1b9dcfa485d2c1fe45f0d16e3",
     "Superhuman pushes its Go assistant everywhere",
     "Superhuman 将 Go 助手推向全平台",
     "Superhuman 正将 Go 打造为核心智能体，并让其覆盖 Docs 和 Mail。"),
    ("8f87f7f5a092431a5e96e7d435f7248f",
     "Metano Raises $12M Seed to Secure AI Agents Across the Enterprise",
     "Metano 完成 1200 万美元种子轮融资，为企业 AI 智能体提供安全防护",
     "Metano 于 2026 年 11 月 19 日宣布结束隐身状态，推出面向企业 AI 智能体的通用安全与治理平台，并获得由 Sierra Ventures 领投的 1200 万美元种子轮融资。Correlation Ventures、High Alpha 和 360 ONE 也参与了本轮投资。"),
    ("6546cce88650635981f08180d8feb6e9",
     "Salesforce Details Sovereign SI Package for U.S. Export Program",
     "Salesforce 详述面向美国出口计划的主权 SI 方案",
     "Salesforce 于 2026 年 11 月 19 日详细介绍了其指定超级智能（SI）出口方案所包含的云、数据、AI 模型、安全与应用组件。此前美国商务部将该公司的联盟列为美国 SI 出口计划首批 33 个预选联盟之一，并于 2026 年 11 月 16 日公布了首批名单。"),
    ("394780dd6ce9072efe33993fe3e751a9",
     "Google Plans Orbital AI Satellite Launch on Blue Origin\u2019s New Glenn",
     "Google 计划借助蓝色起源「新格伦」火箭发射轨道 AI 卫星",
     "Google 于 2026 年 11 月 19 日宣布，蓝色起源的「新格伦」火箭将执行「日光捕获者计划」（Project Suncatcher）的首次专属重型发射任务，目标时间为 2029 年第一季度。双方的发射服务协议涵盖将搭载 Google 张量处理单元（TPU）的太阳能卫星部署至太阳同步轨道。每颗卫星的设计算力约相当于一个数据中心机架的规模。"),
    ("7ee0b27e6945f91f693a76fa7e1bf16c",
     "OpenAI's own researchers now say they value their AI tools more than nearly half their colleagues",
     "OpenAI 自家研究员如今表示，他们对自己 AI 工具的重视程度超过近半数同事",
     "OpenAI 内部对编程智能体的使用正快速增长，理论上消耗的 token 成本如今已超过研究员的基本工资。尽管团队不愿在没有这些工具的情况下工作，但模型在日常任务之外仍会产生大量「AI 垃圾内容」（AI slop）。"),
    ("6331103e71ca915409b71208872a744e",
     "Metano launches with $12M to help enterprises secure AI agents",
     "Metano 携 1200 万美元正式亮相，助力企业保护 AI 智能体",
     "AI 智能体安全初创公司 Metano Inc. 今日正式亮相，获得 1200 万美元融资，帮助企业保护其端点、云基础设施和软件即服务（SaaS）应用中的 AI 智能体。Metano 的平台旨在让企业对其 AI 智能体保持一致的可视性和控制力，将智能体发现、上下文感知的威胁检测和实时处置整合到同一层。"),
    ("ac973a9bff8663358f17f3b8c3c9ff6e",
     "I let Apple\u2019s always-listening AI summarize my life for two weeks",
     "我让 Apple 的「常听」AI 为我总结了两周的生活",
     "Siri Recap 可在手腕上手动开启或关闭。它值得吗？过去一个月，我在 Apple Watch Ultra 4 上同时试用 Amazon Bee Frontier 和 Siri Recap 时，一直反复问自己这个问题。两者都能让可穿戴设备环境式地聆听你的对话，并用 AI 为你生成总结。为什么？为了让你记得更牢，也希望能更专注当下。主要区别在于：Amazon 的 Bee 采取的是「最大化」（坦率说，近乎扭曲现实）的路线，而 Apple 则走更简约、隐私优先的路线。"),
    ("e0251703f1d12de0a23ab55aaf7a4740",
     "Topview Adds AI Relighting and Editing Tools for Hybrid Filmmaking",
     "Topview 为混合影视制作新增 AI 重新布光与剪辑工具",
     "Topview 正在扩展其混合影视制作工具集，新增用于重新布光、选择性编辑、新机位、背景替换以及其他实拍素材调整的 AI 后期制作控制功能。该套件的灯光组件 Video Relight 将于 11 月 19 日推出。这一方法以电影人已拍摄的素材为起点。"),
    ("fc03dd93ac31281d8050a2253efe5f52",
     "QCon San Francisco 2026: Use AI to Multiply Your Team as a Staff Engineer",
     "QCon 旧金山 2026：作为资深工程师，如何用 AI 让团队效能倍增",
     "在 QCon 旧金山 2026 大会上，Pinterest 高级资深工程师兼 Web 平台技术负责人 Jordan Cutler 介绍了当每位工程师都能使用相同的 AI 工具时，资深工程师（Staff Engineer）这一角色将如何变化。"),
]


def main():
    titles = json.load(open(T_JSON, encoding="utf-8"))
    summaries = json.load(open(S_JSON, encoding="utf-8"))
    news = json.load(open(N_JSON, encoding="utf-8"))
    by_id = {it["id"]: it for it in news["items"]}

    ok = 0
    for iid, en, zh_t, zh_s in FIXES:
        titles[en] = zh_t
        summaries[en] = zh_s
        it = by_id.get(iid)
        if not it:
            print("[WARN] id 未找到:", iid)
            continue
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
