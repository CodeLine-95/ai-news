"""08 点巡检：对 08:04 补抓的 9 条 NLLB 译文逐条人工定稿并沉淀到覆盖表。

做法与既往巡检一致：以英文原标题为键写入 data/titles_override.json 与
data/summaries_override.json，同时回填 data/news.json，再重生摘要报告。
重启服务时 apply_manual_overrides_on_startup() 会再次确保定稿生效。
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
STAMP = "0800patrol1125"

FIXES = {
    "Marlowe raises $277M to build inference clusters with chips from Nvidia rivals": (
        "Marlowe 融资 2.77 亿美元，用英伟达竞争对手的芯片构建推理集群",
        "人工智能基础设施初创公司 Marlowe AI Inc. 已完成由 Accel 领投的 2.27 亿美元种子轮融资（原文标题与正文金额存在出入）。Bessemer、Altimeter、Emergence Capital 等多家机构投资方也参与了本轮融资。",
    ),
    "Dell and HP beat expectations, but their fortunes are diverging as AI dynamics crush the PC market": (
        "戴尔与惠普业绩超预期，但 AI 浪潮冲击 PC 市场令两家公司前景分化",
        "戴尔科技与惠普今日公布最新财报，盈利与营收均超出预期。然而，随着两家公司所处的 AI 服务器与个人电脑市场走势分化，它们未来的前景也大不相同。",
    ),
    "Jensen Huang’s Return Shows Nvidia Is Too Big to Police": (
        "黄仁勋回归凸显英伟达已大到难以监管",
        "国家安全与外交政策专家表示，英伟达在美国经济中的核心地位，可能已超过外界对其首席执行官与疑似中国情报人员存在关联的担忧。",
    ),
    "Perplexity Guide Details Permission and Citation Tests for AI Search": (
        "Perplexity 指南详解 AI 搜索的权限与引用测试",
        "Perplexity 于 2026 年 11 月 24 日发布内部搜索指南，主张对 AI 生成的答案分别进行权限与引用测试，并援引《每日经济新闻》（Maeil Business Newspaper）报道称，出版商加入 AI 答案后搜索量增加了 44.3%，使用搜索的人数增加了 22.6%。该指南涵盖两种场景：访客搜索企业网站，以及员工检索政策、合同和会议记录等工作场所材料。",
    ),
    "OpenTable Agrees to Acquire Me&u for Voice AI and Venue Software": (
        "OpenTable 同意收购 Me&u，加码语音 AI 与门店软件",
        "OpenTable 于 2026 年 11 月 24 日宣布，已同意收购澳大利亚餐厅技术公司 me&u，后者提供语音 AI、预订及点单支付等产品。该交易预计于 2027 年上半年完成，尚需获得监管批准并满足其他惯例条件。",
    ),
    "Together AI Launches Preemptible GPU Compute at Half On-Demand Rates": (
        "Together AI 推出抢占式 GPU 算力，价格仅为按需实例一半",
        "Together AI 于 2026 年 11 月 24 日宣布，在 Together GPU 集群中全面提供抢占式 GPU 算力，覆盖所有区域的 Kubernetes 与 Slurm 部署。这些可中断节点采用与标准节点相同的 NVIDIA 加速计算硬件，价格固定为按需费率的 50%。客户可在创建集群或为现有集群添加抢占式容量。这些节点利用闲置资源，当其他地方需要这部分容量时可被回收。",
    ),
    "Meet Facebook’s Your Algorithm: How Meta Turns Plain-Language Preferences Into Ranking": (
        "认识 Facebook「Your Algorithm」：Meta 如何把自然语言偏好转化为排序",
        "Meta 发布了一篇工程深度解析，介绍 Facebook 的「Your Algorithm」功能。该功能让用户用自然语言告诉 Facebook 自己希望在 Feed 和 Reels 中看到什么内容，于 2026 年 10 月 13 日上线。新文章展示了大语言模型（LLM）如何嵌入生产级推荐系统。对开发者而言，这是难得一见的、将显式偏好接入隐式信号排序技术栈的案例。核心要点：这是一个端到端系统，旨在解决推荐在适应性与细微差异上的局限；运行于 Meta 服务端排序技术栈，并结合 Facebook 应用内的设备端缓存失效机制；显式兴趣会接入 4 个召回来源，并同时作用于 Feed 与 Reels。结论是，这是一份用 LLM 驱动排序的清晰蓝图。「Your Algorithm」是一个由 AI 驱动的 Facebook Feed 与 Reels 偏好设置页面。",
    ),
    "Three LLM inflection points in twelve months": (
        "十二个月里的三个 LLM 拐点",
        "几周前，我在 AI Engineer Code Summit 上发表主题演讲，围绕过去十二个月里 LLM 与编程智能体能力出现的三个重要拐点展开。这是演讲视频。本文将提炼其中的主要拐点主题并做更深入的探讨。2025 年 11 月的编程智能体：今天（2026 年 11 月 24 日）恰逢 Claude Opus 4.5 发布一周年。事后看来，这是一个影响深远的模型。在 Opus 4.5 的发布公告中，Anthropic 表示：测试人员指出，Claude Opus 4.5 能在不依赖手把手指导的情况下处理模糊性并权衡取舍。他们告诉我们，当指向一个复杂的多系统缺陷时，Opus 4.5 能找出修复方案。他们说，几周前对 Sonnet 4.5 来说几乎不可能完成的任务，如今已触手可及。事实证明了这一点。",
    ),
    "Clay helps sales teams win with Codex and ChatGPT": (
        "Clay 借助 Codex 与 ChatGPT 帮助销售团队赢得客户",
        "ChatGPT 与 Codex 的集成帮助 Clay 的用户调研交易机会，并把数据转化为上市策略，其中推理由 GPT-6 模型承担。",
    ),
}


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
    applied = 0
    for it in data["items"]:
        en = (it.get("title") or "").strip()
        fix = FIXES.get(en)
        if not fix:
            continue
        zh_title, zh_summary = fix
        titles[en] = zh_title
        summaries[en] = zh_summary
        it["title_zh"] = zh_title
        it["summary_zh"] = zh_summary
        it["translated"] = True
        it["method"] = "manual"
        applied += 1
        print("定稿: %s -> %s" % (en[:55], zh_title[:45]), flush=True)

    save(DATA, data)
    save(T_OVR, titles)
    save(S_OVR, summaries)
    print("本轮定稿 %d 条，覆盖表 %d/%d 条" % (applied, len(titles), len(summaries)), flush=True)
    if applied != len(FIXES):
        print("警告：并非全部目标条目都命中", file=sys.stderr, flush=True)
    report.main()
    print("报告已重生", flush=True)


if __name__ == "__main__":
    main()
