# -*- coding: utf-8 -*-
"""19:00 巡检：修复历史遗留的 13 条 "Adds" 逐词机翻硬伤。

这些条目 method=nllb，标题把英文动词 Adds/Launches/Raises 原样保留，
形成「AWS Adds XXX 到 YYY」式中英断裂。人工定稿标题+摘要，写入覆盖表并回填。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

FIXES = [
    {
        "en": "Amazon SageMaker AI Adds Generally Available Regional Failover Router",
        "title_zh": "Amazon SageMaker AI 正式推出跨区域故障转移路由器",
        "summary_zh": "亚马逊云科技于 2026 年 11 月 19 日在 Amazon SageMaker AI 中正式推出跨区域推理路由功能，应用只需调用一个路由器，即可在本地容量不足时访问 AWS 各区域和账户中现有的模型服务资源。SageMaker AI 端点通常运行在单一区域和账户内；当自动扩容无法增加所需实例类型时，即使相同模型在其他地方有空闲容量，请求也可能被限流并超时。",
    },
    {
        "en": "AWS Adds PolyAI Dialog-RSN-1 to SageMaker JumpStart Catalog",
        "title_zh": "AWS 将 PolyAI Dialog-RSN-1 纳入 SageMaker JumpStart 目录",
        "summary_zh": "AWS 于 2026 年 11 月 19 日宣布，PolyAI 的 Dialog-RSN-1 已加入 Amazon SageMaker JumpStart 目录，为这款原生语音客服模型提供一键部署、评估工具和四种优化配置。端点运行在客户自己的 AWS 账户内。此次新进展在于目录工作流，此前 PolyAI 已有两次发布。",
    },
    {
        "en": "Clay Adds Sales Workflow Building and Previews to ChatGPT Plugin",
        "title_zh": "Clay 为 ChatGPT 插件新增销售工作流构建与预览功能",
        "summary_zh": "Clay 于 2026 年 11 月 17 日宣布，其重新推出的 MCP 插件可直接在 ChatGPT 内构建和预览销售工作流，涵盖潜客筛选、数据丰富和营销活动发布。该插件将 Clay 的市场进入工具接入 ChatGPT。此前的集成主要让销售人员运行队友已创建并共享的功能。",
    },
    {
        "en": "AWS Adds Managed NVIDIA Dynamo to SageMaker HyperPod Inference",
        "title_zh": "AWS 为 SageMaker HyperPod 推理新增托管式 NVIDIA Dynamo 支持",
        "summary_zh": "亚马逊云科技于 2026 年 11 月 17 日宣布，Amazon SageMaker HyperPod Inference 现已支持 NVIDIA Dynamo，可实现托管式多节点与分离式模型服务；基准结果显示，在 AWS 延迟目标下，每 GPU 聚合输出 token 吞吐量达到最高合格值的 2.05 倍。",
    },
    {
        "en": "Meta Launches Muse AI Agent in Australia with Local Connectors",
        "title_zh": "Meta 在澳大利亚推出 Muse AI 智能体及本地连接器",
        "summary_zh": "Meta 于 2026 年 11 月 17 日宣布，其 Muse 个人 AI 智能体已在澳大利亚上线，面向创意、购物、房产、健身和娱乐的本地连接器体验将逐步推出。Meta 称 Muse 旨在执行工作而非仅回答问题，帮助用户掌握待办、管理任务与项目，并把长期目标转化为行动计划。",
    },
    {
        "en": "Hitachi Vantara Adds In-Place Lakehouse Queries to VSP One Object",
        "title_zh": "Hitachi Vantara 为 VSP One Object 新增原地湖仓查询能力",
        "summary_zh": "Hitachi Vantara 于 2026 年 11 月 11 日宣布，VSP One Object 可直接在存储平台上查询受支持的开放格式数据，以四节点起步配置简化部署。此次更新还为面向企业 AI 应用与智能体的 Hitachi iQ Studio 增加治理功能，将对象存储、湖仓分析与 AI 应用开发治理软件连接起来。",
    },
    {
        "en": "Zum Adds Zoe Conversational AI to School Transportation Operations",
        "title_zh": "Zum 将 Zoe 对话式 AI 引入校车交通运营",
        "summary_zh": "Zum 于 2026 年 11 月 10 日推出 Zoe，向校车交通团队、运营商和管理员在 Zum CMX 内提供对话式 AI 助手。它分析学区运营数据并提出下一步建议，但线路变更、司机调度和家校沟通仍由员工掌控。Zum 称 19 个州已有超过 7500 所学校使用 CMX。",
    },
    {
        "en": "Otter.ai Adds 13 Languages and Previews Automatic Language Switching",
        "title_zh": "Otter.ai 新增 13 种语言并预览自动语言切换",
        "summary_zh": "Otter.ai 于 2026 年 11 月 10 日宣布将其会议转录服务扩展至 27 种语言，其中新增 13 种即刻可用，另有 14 种即将上线。公司还预览了一种多语言模式，可在同一场会议中随参与者切换受支持语言自动转录，无需手动更改设置。",
    },
    {
        "en": "AWS Adds Single-Shot RAG and Retrieval-Only Mode to Bedrock",
        "title_zh": "AWS 为 Bedrock 新增单次 RAG 与仅检索模式",
        "summary_zh": "亚马逊云科技于 2026 年 11 月 9 日宣布，Amazon Bedrock 托管知识库现通过 AgenticRetrieveStream 支持单次检索增强生成（RAG）和仅返回段落的请求。maxAgentIteration 的 0–5 范围扩展让应用可选择仅检索源、单次搜索作答或服务现有的多步智能体检索。",
    },
    {
        "en": "Meta Adds Custom Spaces to Personalize the Muse App Experience",
        "title_zh": "Meta 新增自定义 Spaces 以个性化 Muse 应用体验",
        "summary_zh": "Meta 于 2026 年 11 月 6 日宣布，Spaces 现已在 Muse 所有可用地区上线，用户可通过描述想法并用 Muse 优化结果，在应用内创建 persists 的定制体验。每个 Space 都会成为应用中已保存的部分，可支持日常安排、目标、兴趣、实际工作或娱乐。",
    },
    {
        "en": "AWS Adds NVIDIA GPU Partitioning to SageMaker Inference Endpoints",
        "title_zh": "AWS 为 SageMaker 推理端点新增 NVIDIA GPU 分区支持",
        "summary_zh": "亚马逊云科技（AWS）于 2026 年 11 月 6 日宣布，为 Amazon SageMaker Inference 引入 NVIDIA 多实例 GPU 支持，让多个硬件隔离的模型在实时端点上共享一个加速器，而无需为每次部署分配整块 GPU。该功能解决了整块 GPU 分配的两项限制。",
    },
    {
        "en": "AT&T Adds Gemini Video Search and Daily Summaries to Connected Life",
        "title_zh": "AT&T 为 Connected Life 新增 Gemini 视频搜索与每日摘要",
        "summary_zh": "AT&T 于 2026 年 11 月 4 日宣布，其 Connected Life 家庭安防服务推出 Gemini for Home 功能，可描述录制事件、支持对话式视频搜索并把家庭活动生成每日摘要。AT&T 称 Connected Life 是首款集成 Google Home Premium 高级能力的家庭安防产品，并作为新客户安防服务的一部分提供。",
    },
    {
        "en": "Phaze Raises $8.75M Seed Led by a16z for Human and AI Agent Remote Access",
        "title_zh": "Phaze 完成 a16z 领投的 875 万美元种子轮，为人类与 AI 智能体提供远程计算访问",
        "summary_zh": "Phaze 完成由 a16z 领投的 875 万美元种子轮融资，为员工和 AI 智能体提供对高性能远程计算机的访问。公司于 11 月 4 日宣布该轮融资，Indie、NextView、Makers Fund 和 Lerer Hippeau 参投。这家总部位于犹他州的初创公司计划扩充工程团队、开发产品并支持客户增长。其创始人此前打造了远程访问业务 Parsec，该业务于 2021 年被 Unity 收购。",
    },
]


def main():
    for path, key, label in ((T_JSON, "title_zh", "标题"), (S_JSON, "summary_zh", "摘要")):
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
        for fx in FIXES:
            if d.get(fx["en"]) != fx[key]:
                d[fx["en"]] = fx[key]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=1)
        print("[fix_history] %s覆盖表写入 %d 条" % (label, len(FIXES)))

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    hit = 0
    for it in data.get("items", []):
        en = (it.get("title") or "").strip()
        for fx in FIXES:
            if en == fx["en"]:
                it["title_zh"] = fx["title_zh"]
                it["summary_zh"] = fx["summary_zh"]
                it["translated"] = True
                it["method"] = "nllb+manual"
                hit += 1
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print("[fix_history] 回写条目 %d" % hit)


if __name__ == "__main__":
    main()
