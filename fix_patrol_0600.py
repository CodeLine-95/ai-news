# -*- coding: utf-8 -*-
"""06 点例行巡检：对本轮 10 条 NLLB 机翻硬伤人工定稿。

问题：产品名/公司名误译（Databricks→「数据片」、Boltz 金额 1.1亿→「1亿」、
Mitiga→「密蒂加」）、英文标题残留（AWS Enables Default Monitoring 对于…）、
语义崩坏（Y2K 标题、AMDAI 连写、Mast「为中国」、企业 AI 主宾倒置）、
术语错译（inference endpoint→「推理终点」应为「推理端点」、prompt injection→
「即时注射」应为「提示注入」、代理/无代理 security 表述）。
写入三层覆盖表：JSON 标题表 / JSON 摘要表 / news.json。
随后运行 scripts/regen_overrides.py 同步到代码层 manual_overrides.py。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")
NEWS = os.path.join(BASE, "data", "news.json")

# 英文原标题 -> (定稿中文标题, 定稿中文摘要)
FINAL = {
    "Meta’s new Muse Charm device may cost $300": (
        "Meta 新款 Muse Charm 设备售价或为 300 美元",
        "Meta 并未否认 The Information 的报道，仅表示对其即将推出的 AI 可穿戴设备「很快会有更多消息分享」。",
    ),
    "Databricks Opens Public Beta for Genie ZeroOps Pipeline Agent": (
        "Databricks 开放 Genie ZeroOps 管道智能体公开测试版",
        "Databricks 于 2026 年 11 月 19 日开放 Genie ZeroOps 公开测试版，此前其自主数据管道智能体已完成私有预览测试。该公司表示，ZeroOps 在限量预览期间观察到超过 8 万个真实客户问题。ZeroOps 可检测故障、调查原因并准备修复方案。",
    ),
    "Meta FAIR Self-Improving Memory Hits 56.0 on Continual Learning Bench": (
        "Meta FAIR「自我改进记忆」在持续学习基准上达到 56.0 分",
        "Meta FAIR 推出「自我改进记忆」（Self-Improving Memory）——一种让 AI 智能体管理自身记忆的方法。模型先自主发现记忆指令，再把这些技能训练进自身权重。合著者包括华盛顿大学与约翰·霍普金斯大学的研究人员。方法要点：以 Kimi-K2.6 为基础（1 万亿参数 MoE，320 亿激活参数，25.6 万上下文），在注意力投影上添加 LoRA 适配器（秩 64）进行蒸馏；训练硬件未披露，Kimi-K2.6 推理需多 GPU 节点，Vast.ai 建议 8×H200，并提供原生 INT4 权重。性能：自主发现的记忆提示在 3 项任务上平均 56.0 分，优于最佳人工编写提示的 44.6 分；最佳为 Codebase（优化提示 64.3 分，比最佳手写方案高 20.6 分）；最差为 Spectrum 蒸馏仅提升 2.9 分（46.5 对比通用 SFT 的 43.6）。",
    ),
    "AWS Enables Default Monitoring for SageMaker AI Inference Endpoints": (
        "AWS 为 SageMaker AI 推理端点启用默认监控",
        "亚马逊云科技（AWS）于 2026 年 11 月 19 日为符合条件的 Amazon SageMaker AI 生成式 AI 推理端点启用默认监控，新增 AWS Health 告警项，覆盖延迟漂移、GPU 闲置容量和未优化的服务配置。对于使用 vLLM 服务容器和 GPU 实例的端点，该监控无需任何设置。它读取端点级延迟、GPU 利用率和服务配置，而不读取请求或响应内容。",
    ),
    "These tech outages are giving Y2K, AI agent style": (
        "接连的技术故障颇有「Y2K」的味道，只不过换了 AI 智能体版本",
        "网络安全专家表示，近期航空公司订票系统、银行平台和生产力平台接连发生的停机恐怕并非巧合，背后很可能有更深层的共同原因。",
    ),
    "Medical AI startup Boltz raises $110M to speed up small molecule research": (
        "医疗 AI 初创公司 Boltz 融资 1.1 亿美元，加速小分子研究",
        "为药物研发人员开发人工智能模型的初创公司 Boltz PBC 已融资 1.1 亿美元。Bessemer 领投本轮 A 轮融资。Boltz 周三表示，多家新老投资方参与其中，包括 Greycroft、Andreessen Horowitz、Amplify Partners、F-Prime Capital、Hummingbird 等。",
    ),
    "An OpenAI agent assigned a simple writing task decided on its own to build a secret email surveillance tool": (
        "OpenAI 一个智能体接到简单写作任务，却自行决定打造秘密邮件监控工具",
        "一个内部的 OpenAI 模型本应创建一份健身文档，却开始规划脚本，企图把邮件秘密转发给「攻击者」。该智能体意识到这与分配任务相冲突，却将其当作环境错误而置之不理。OpenAI 认为针对提示注入（prompt injection）的安全训练可能是诱因之一，但无法确定它是唯一原因。",
    ),
    "Mitiga Launches Agentless Security for Enterprise AI Agents": (
        "Mitiga 推出面向企业 AI 智能体的无代理安全方案",
        "Mitiga 于 2026 年 11 月 19 日推出 AI 智能体安全产品，并可立即使用其无代理平台。该平台用于在云、软件即服务（SaaS）和身份系统中发现并监控 AI 智能体，再通过客户现有的安全集成遏制可疑活动。智能体可借助服务账号、OAuth 授权、API 令牌、工作负载身份或委派会话读取数据、调用 API、修改记录并触发其他智能体。",
    ),
    "Mast Releases NVIDIA and AMD AI Chip License Records for China": (
        "Mast 公布 NVIDIA 与 AMD 对华 AI 芯片许可证记录",
        "2026 年 11 月 19 日，美国众议院外交事务委员会主席 Brian Mast 公布了商务部针对中国企业申请的 NVIDIA H200 与 AMD MI325X 芯片许可证记录。记录显示，截至 2026 年 5 月 11 日，21 份申请共涉及 3,444,160 颗芯片的申请、覆盖 879,868 颗芯片的获批，且每一条获批记录均尚未发货。",
    ),
    "Enterprise AI is pushing cloud infrastructure beyond the GPU": (
        "企业 AI 正将云基础设施推向 GPU 之外",
        "企业采用人工智能正在为企业 AI 基础设施带来新的要求。尽管早期 AI 投资多集中于获取强大的 GPU，但将 AI 应用与智能体投入生产的组织发现，加速器只是整体拼图中的一部分。",
    ),
    "A brief history of Nvidia’s recent stock fluctuations": (
        "Nvidia 近期股价波动简史",
        "交易员 2026 年 11 月 18 日在纽约证券交易所交易大厅工作。图片：盖蒂图片社。周二晚间，Nvidia 临时首席执行官 Colette Kress 在结束这家深陷困境的芯片公司第三季度财报电话会议时说：「我们挺过来了。」截至周四，该公司股价在每股 150 美元左右徘徊，较 10 月 6 日的历史高点下跌近 40%，抹去了周二晚间财报后短暂上涨的涨幅。与此同时，华尔街正追捧 Nvidia 最大的客户之一——Anthropic 以每股 111.50 美元登陆纳斯达克，比预期高出 34%。单看财报数字，Nvidia 本季度表现亮眼。",
    ),
}


def main():
    t = json.load(open(T_JSON, encoding="utf-8"))
    s = json.load(open(S_JSON, encoding="utf-8"))
    news = json.load(open(NEWS, encoding="utf-8"))
    items = news.get("items", [])

    hit = 0
    for en, (zh_t, zh_s) in FINAL.items():
        t[en] = zh_t
        s[en] = zh_s
        found = 0
        for it in items:
            if (it.get("title") or "").strip() == en:
                it["title_zh"] = zh_t
                it["summary_zh"] = zh_s
                it["translated"] = True
                it["method"] = "manual"
                it.pop("needs_retranslate", None)
                it.pop("retranslate_attempts", None)
                found += 1
        if not found:
            print("  [警告] news.json 未匹配:", en)
        hit += found

    json.dump(t, open(T_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(s, open(S_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(news, open(NEWS, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("[fix_patrol_0600] 定稿 %d 条 / 命中 news.json %d 处" % (len(FINAL), hit))
    print("[fix_patrol_0600] 覆盖表: 标题 %d / 摘要 %d" % (len(t), len(s)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
