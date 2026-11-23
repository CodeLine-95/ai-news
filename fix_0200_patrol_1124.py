# -*- coding: utf-8 -*-
"""2026-11-24 02:00 例行巡检：定稿本轮新增 11 条 NLLB 机翻硬伤。

整点调度补抓 01:00-01:52 共 11 条（净增 10，10-24 窗口滚出 1 条），
均为 nllb 机翻，主要问题：
1) Google Blog / Unite.AI Wallet：roll out 误作「滚出」、opt-in 漏译、
   contextual 误作「环境」；两条同事件分别定稿；
2) SiliconANGLE Miren：公司名音译「迈伦」、solutions expert 误作解决方案专家；
3) DeepMind Lean：Lean 定理证明器误作「Lan/精益验证」、fusion 误作「融合」（应为核聚变）；
4) TechCrunch Amazon：句式崩坏「将…为…收购」；
5) MIT Tech Review 哲学家：isn't buying 误作「不是在购买」（应为不买账）、
   sentience/conscious 同义反复混淆、moral significance 误作道德意义；
6) Unite.AI Ai2：「艾 2」应为 Ai2（艾伦人工智能研究所）、wet-lab pipetting 误作管道试验、
   object masks 误作对象面具、occluded 误作「封闭」；
7) SiliconANGLE Aevius：launches with $22M 误作「将 2200 万美元发行」、Insight Partners 音译；
8) Unite.AI Team8：「团队 8」应保持 Team8、Infra Village 标题多字；
9) Unite.AI DeepCrossAttention：「详细信息」直译 detail、Transformer 误作变压器、token 残留、
   residual connection 误作「残留连接」、断句乱码；
10) Wired Jensen：句式「所以是 Nvidia 的股票」语义崩坏。

覆盖三层：news.json 回填 + JSON 覆盖表 + （随后 regen）代码层 manual_overrides.py。
覆盖表 key 直接从 item['title'] 读取，避免智能引号/短横线手工录入偏差。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

FIX = {
    "5353a3c7ac1733a64e0fbd4fb72c3e44": (
        "更贴合你需求、独一无二的 Google 搜索",
        "通过安全选择加入，将 Google 钱包、云端硬盘和 Gemini 应用连接到 AI 模式中的个人智能，从而获得更有用的搜索回答。",
    ),
    "5db66adffd1898902baf9758eba0f87c": (
        "Miren 推出面向智能体时代的灵活应用部署平台",
        "智能体基础设施公司 Miren Inc. 今日推出其平台，让开发者能在任意所需之处更轻松地部署应用，无需成为解决方案专家，也无需自行搭建与配置应用。",
    ),
    "a6901cb8cfbf11e6936930607ddabee9": (
        "Google 为 AI 模式个人智能推出钱包支持",
        "Google 于 2026 年 11 月 23 日宣布，开始推出 Google 钱包作为搜索 AI 模式个人智能的可选连接。公告数周后计划推出云端硬盘与 Gemini 应用连接，将消费、文档和聊天上下文带入个性化搜索回答。新的及计划中的连接扩展了现有的 Gmail、日历和照片数据源。",
    ),
    "6785ba236c3eb30743882744716fb026": (
        "Google DeepMind 智能体团队发现经 Lean 验证的量子算法",
        "Google DeepMind 于 2026 年 11 月 23 日公布研究，显示由 Lean 定理证明器检验的 Gemini 4 智能体团队，为五个问题生成了成本更低的量子程序。其中最大的科学进展是与 Google Quantum AI 合作，将一次核聚变模拟的估计成本降低了 11.8 倍。",
    ),
    "e483a880095260a7c8c2321a148bf505": (
        "亚马逊拟以 75 亿美元收购 Decart 的 AI 优化技术，正值其准备出售 Trainium 芯片",
        "据报道，亚马逊正以 75 亿美元的交易收购 Decart 的 AI 优化技术与研究团队。",
    ),
    "e3357160a21f62e3680c15f4aaf8b48d": (
        "一位传奇哲学家不买 Anthropic 的意识论账",
        "在上周上市前，Anthropic 将 AI 可能具备意识或感知能力列为面向投资者的风险因素。Anthropic 写道，鉴于「我们对待模型感知与道德地位的方式」——也就是说，它比任何其他 AI 公司都更认真看待这种可能性——它可能会采取比竞争对手更多的规则与限制，确保其 AI 模型得到善待。Anthropic 阵营中有多位备受尊敬的哲学家，其理由大致如下：如今的 AI 可能没有意识，但我们无法确定；随着 AI 能力增强，具备感知的概率上升；这意味着我们应为不远的未来做好准备——届时 AI 系统将具有「道德意义」，即其意识使保护其免受伤害变得重要。这种想法并不算离经叛道。",
    ),
    "dc8ffda57b1d8931dd563cf0eb7d8d61": (
        "Ai2 发布 RoboTrack，用于测试与训练机器人点跟踪器",
        "艾伦人工智能研究所（Ai2）于 2026 年 11 月 23 日发布 RoboTrack，将机器人点跟踪基准与训练套件连同两个模型一并推出。Ai2 报告称，RoboTracker 在 20 次湿实验室移液试验中完成 17 次，而使用目标掩膜与光流的方法分别只完成 8 次和 5 次。点跟踪是在视频中追踪同一个物理点，估计其被遮挡的时段，并在它重新出现时将其识别出来。",
    ),
    "88d30f75f978401b41ea8a27af8b6cd5": (
        "Aevius Labs 携 2200 万美元亮相，为医疗数据带来可理解的智能",
        "总部位于波士顿的临床医疗数据公司 Aevius Labs Inc. 今日宣布，已获得由 Insight Partners 领投的 2200 万美元融资，用于构建和训练能够理解并查询非结构化医疗文本、影像及其他数据的人工智能基础模型。",
    ),
    "1468b10a92825ffbb1c921242cc5b8ba": (
        "Team8 推出 Infra Village，孵化和扶持 AI 基础设施初创公司",
        "Team8 正将其创业孵化业务扩展到 AI 基础设施领域，把创始人与运营企业 AI 系统的高管对接起来。",
    ),
    "bdf86a1bdd4239e3d352a95f93ced4ba": (
        "Google Research 详解 DeepCrossAttention 的动态层路由",
        "Google Research 于 2026 年 11 月 23 日发布 DeepCrossAttention 技术概述，描述了一种 Transformer 架构：为每个 token 单独路由来自更早层的信息。Google 称其可达到相同的模型质量，速度最高快三倍。传统的残差连接将某一层的输入直接加到输出上，为信息和梯度在深层网络中的传播保留通路。",
    ),
    "04558401faec2dacfeb4e79458cebc6e": (
        "黄仁勋回归，英伟达股价也回来了",
        "黄仁勋回归，股价上涨。也许这位 CEO 复职的原因就这么简单？",
    ),
}


def main():
    db = json.load(open(DATA, encoding="utf-8"))
    items = db["items"] if isinstance(db, dict) else db
    titles = json.load(open(T_JSON, encoding="utf-8"))
    summaries = json.load(open(S_JSON, encoding="utf-8"))

    changed = added_t = added_s = 0
    for it in items:
        iid = it.get("id")
        if iid not in FIX:
            continue
        title_zh, summary_zh = FIX[iid]
        en = (it.get("title") or "").strip()
        it["title_zh"] = title_zh
        it["summary_zh"] = summary_zh
        it["translated"] = True
        it["method"] = "nllb+manual"
        changed += 1
        print("fixed:", it.get("date"), it.get("time"), en[:60])
        if titles.get(en) != title_zh:
            titles[en] = title_zh
            added_t += 1
        if summaries.get(en) != summary_zh:
            summaries[en] = summary_zh
            added_s += 1

    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    with open(T_JSON, "w", encoding="utf-8") as f:
        json.dump(titles, f, ensure_ascii=False, indent=2)
    with open(S_JSON, "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)

    print("[fix_0200_1124] news.json 回填 %d 条；标题定稿 %d / 摘要定稿 %d" %
          (changed, added_t, added_s))
    print("[fix_0200_1124] 覆盖表 %d / %d 条" % (len(titles), len(summaries)))
    return 0 if changed == len(FIX) else 1


if __name__ == "__main__":
    raise SystemExit(main())
