# -*- coding: utf-8 -*-
"""2026-11-03 06:00 巡检：修复 05:40—05:54 抓取的 4 条 Unite.AI 条目译文缺陷。

A) 05:40 —— OpenAI's LifeVal Evaluation Tests AI on Practical Everyday Tasks
   1) 标题语序崩坏：「评估测试人工智能在实际的日常任务上」——主谓宾错位。
   2) 「个人智能体人的帮助」多出一个「人」字（personal agents 译出冗余）。
   3) 「以追踪人工智能模型在实践工作上随着时间的推移的表现」长定语套嵌，
      读者无法解析。
   4) 「包括寻找照顾，制定预算和订购杂货」用逗号并列，应为顿号；
      "finding childcare" 译成「寻找照顾」语义错误（应为育儿照护）。
   5) 「3995 名受访者」缺千分位分隔。

B) 05:42 —— LongCat-2.5 Debuts With 1.6T Parameters and Native Visual Tokens
   1) 标题「采用 1.6T 参数和原生视觉 token 的 LongCat-2.5 首发」中文语序倒置。
   2) 「原始多模态」——natively multimodal 应为「原生多模态」，
      「原始」是 raw/original 的直译，语义完全不同。
   3) 「长视野」「长视线」——long-horizon 是「长时程」，
      NLLB 按「视线/视野」直译，AI 论文语境下完全不通。
   4) 「它的培训包括」——training 是「训练」不是「培训」。
   5) 「智能体编码」——agentic coding 是「智能体编程」。

C) 05:54 —— Omen AI Buys Aquatic Labs for Cooling-Fluid Sensor Development
   1) 公司名 Omen AI 被音译成「欧门 AI」；Aquatic Labs 被意译成「水力实验室」。
   2) 人名 Allan Adams 被写成「Alan Adams」——漏掉一个 l，不是同一人。
   3) 摘要「收购 Aquatic Labs.Aquatic Labs 创始人」——句点粘连 + 机构名重复。
   4) 「并通过收购将他的团队，知识产权和传感器研究带入旧金山的公司」
      ——逗号误用作并列，且丢了「这家总部位于旧金山」的限定。
   5) 「Adams 将领导 Omen AI 的传感器技术的研发和开发」——
      "lead research and development across Omen AI's sensing technologies"
      是「主导传感技术的研发」，不是「领导传感技术的研发和开发」。

D) 05:54 —— DeepSeek Harness Adds Plugin-Creation Entry for Creator Mode
   1) 产品名 DeepSeek Harness 被音译成「深度搜索带」。
   2) 「插件-创建入口」中英混排带连字符，应为「插件创建入口」。
   3) 「预测版本」——prerelease 是「预发布版本」。
   4) 「添加了 Let Agent 创建插件进入插件管理」——原文是插件管理里新增一个
      名为 "Let Agent create a plugin" 的入口项，不是动作。
   5) 「选择它将现有的草稿输入创作者模式」——carries the existing draft into
      是「把已有草稿带入」，不是「输入」。
   6) 结尾「这个 v0.1.6-alpha。」为源站截断句，中文应写成版本号结尾。

同时把根因规则补进 translate.py：
  BRAND_TERMS  + DeepSeek Harness / Omen AI / Aquatic Labs / LongCat
  TERM_FIXES   + prerelease / long-horizon / natively multimodal / agentic coding
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

TITLE_FIX = {
    "OpenAI’s LifeVal Evaluation Tests AI on Practical Everyday Tasks":
        "OpenAI 发布 LifeVal 评估，检验 AI 在日常实际任务中的表现",
    "LongCat-2.5 Debuts With 1.6T Parameters and Native Visual Tokens":
        "LongCat-2.5 发布：1.6T 参数与原生视觉 token",
    "Omen AI Buys Aquatic Labs for Cooling-Fluid Sensor Development":
        "Omen AI 收购 Aquatic Labs，开发冷却液传感器",
    "DeepSeek Harness Adds Plugin-Creation Entry for Creator Mode":
        "DeepSeek Harness 为创作者模式新增插件创建入口",
}

SUMMARY_FIX = {
    "OpenAI’s LifeVal Evaluation Tests AI on Practical Everyday Tasks":
        "OpenAI 于 2026 年 11 月 2 日发布了 LifeVal，"
        "这是一项部分基于 3,995 名受访者调查的评估，"
        "用于持续追踪 AI 模型在日常实际工作上的表现，"
        "涵盖寻找育儿照护、制定预算和订购杂货等场景。"
        "LifeVal 覆盖的正是用户希望 AI 与个人智能体提供帮助的领域。"
        "过去一年里，OpenAI 一直用这项评估监测模型表现，"
        "并指导日常任务方向的改进。",
    "LongCat-2.5 Debuts With 1.6T Parameters and Native Visual Tokens":
        "LongCat 于 2026 年 11 月 1 日推出 LongCat-2.5，"
        "这是一款面向长时程智能体任务的原生多模态混合专家模型，"
        "总参数达 1.6 万亿，每 token 激活约 480 亿参数。"
        "LongCat 表示，本次发布在 LongCat-2.0 的基础上进一步强化了"
        "原生视觉理解与智能体编程能力。"
        "其训练过程引入了更多长时程轨迹，以及面向复杂代码库开发"
        "与整项目构建的大规模长时程强化学习。",
    "Omen AI Buys Aquatic Labs for Cooling-Fluid Sensor Development":
        "Omen AI 于 2026 年 11 月 2 日宣布，"
        "已以 1,600 万美元的现金和股票收购 Aquatic Labs。"
        "Aquatic Labs 创始人 Allan Adams 将加入 Omen AI 担任首席科学官，"
        "此次收购也把他的团队、知识产权与传感器研究纳入这家总部位于旧金山的公司。"
        "Adams 将主导 Omen AI 传感技术的研发。",
    "DeepSeek Harness Adds Plugin-Creation Entry for Creator Mode":
        "2026 年 10 月 3 日，DeepSeek 发布了 DeepSeek Harness 的 "
        "v0.2.1-alpha.1 预发布版本，"
        "在插件管理中新增了一个名为「Let Agent create a plugin」的入口项。"
        "选中该入口会把已有草稿带入创作者模式，"
        "执行过程则要等用户提交插件创建请求后才开始。"
        "插件管理变更方面，创作者模式在此次预发布之前就已有文档说明。"
        "版本号为 v0.1.6-alpha。",
}


def main():
    with open(os.path.join(DATA, "news.json"), encoding="utf-8") as f:
        db = json.load(f)
    items = db["items"] if isinstance(db, dict) else db

    hit_t = hit_s = 0
    for it in items:
        t = it.get("title", "")
        if t in TITLE_FIX:
            it["title_zh"] = TITLE_FIX[t]
            it["translated"] = True
            it["method"] = "nllb+manual"
            hit_t += 1
            print("fix title:", it["date"], it["time"], it["source"], "|", t[:52])
        if t in SUMMARY_FIX:
            it["summary_zh"] = SUMMARY_FIX[t]
            it["translated"] = True
            it["method"] = "nllb+manual"
            hit_s += 1
            print("fix summary:", it["date"], it["time"], it["source"])

    with open(os.path.join(DATA, "news.json"), "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    for name, fix in (("titles_override.json", TITLE_FIX),
                      ("summaries_override.json", SUMMARY_FIX)):
        path = os.path.join(DATA, name)
        cur = {}
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                cur = json.load(f)
        cur.update(fix)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cur, f, ensure_ascii=False, indent=2)

    print("fixed titles:", hit_t, "/", len(TITLE_FIX))
    print("fixed summaries:", hit_s, "/", len(SUMMARY_FIX))


if __name__ == "__main__":
    main()
