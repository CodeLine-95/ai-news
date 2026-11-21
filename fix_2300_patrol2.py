# -*- coding: utf-8 -*-
"""2026-11-20 23:00 巡检第二批：定稿 refresh 追抓的 1 条 + 全库扫描发现的历史硬伤。

新增 1 条：
1) The Decoder《Apple joins the race for AI agents ...》(23:03)——
   「果」= Apple 品牌截断；摘要同。

历史硬伤（全库 term 扫描）：
2) 11-17《Apple is testing daily usage limits ...》「果正在测试」截断；
3) 11-05《Apple is reportedly cutting budgets ...》「果正在削减」截断；
4) 11-10《The AI Safety Debate Has Lost the Plot ...》
   「真正的梦是什么」错译 real nightmares、「间们」错译 spies；
5) 11-10《MIT-led team ... weed killers》「杂草杀手」「草药」错译
   weed killers / herbicides（应为除草剂）、ARPA-H 全称误译；
6) 11-17《Ian Buck Kicks Off NVIDIA's Week ...》
   「击了 NVIDIAs 周」错译 kicks off / NVIDIA's Week。

覆盖三层：news.json 回填 + JSON 覆盖表 + manual_overrides.py（regen）。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

T1 = "Apple joins the race for AI agents that control your device while raising new barriers for competitors"
T2 = "Apple is testing daily usage limits for more complex Siri AI interactions"
T3 = "Apple is reportedly cutting budgets for its internal AI usage"
T4 = "The AI Safety Debate Has Lost the Plot. We Asked 10 Experts What the Real Nightmares Are"
T5 = "MIT-led team receives funding to develop next-generation alternatives to modern weed killers"
T6 = "Ian Buck Kicks Off NVIDIA’s Week at SC26 as Science Enters the Age of Agents"

TITLE_FIX = {
    T1: "苹果加入控制设备的 AI 智能体竞赛，同时为竞争对手设立新的门槛",
    T2: "苹果测试针对更复杂 Siri AI 交互的每日使用限制",
    T3: "据报道，苹果正削减其内部 AI 使用预算",
    T4: "AI 安全辩论已偏离主题：我们询问了 10 位专家真正的噩梦是什么",
    T5: "麻省理工学院团队获资助，研发现代除草剂的下一代替代品",
    T6: "科学迈入智能体时代，伊恩·巴克拉开 NVIDIA 在 SC26 活动周序幕",
}

SUMMARY_FIX = {
    T1: (
        "在 Meta、OpenAI、Anthropic 和 Google 相继推出各自的 AI 智能体后，苹果如今也在打造自己的智能体——"
        "同时让竞争对手更难访问其设备。"
    ),
    T3: (
        "据称，这家公司正大幅削减其工程团队在 AI 上的支出。"
    ),
    T4: (
        "核灾难的风险真实存在，中美主导权博弈的后果同样真实（间谍就在眼前）。但无需对「天网」恐慌。"
    ),
}

# 长摘要用定点替换，保留事实结构
SUMMARY_PATCH = {
    T2: [("根据 MacRumors 的说法，果今天发布了", "据 MacRumors 报道，苹果今天发布了")],
    T5: [
        ("现代杂草杀手的下一代替代品", "现代除草剂的下一代替代品"),
        ("STREAM（Systems 对于有效农业输入管理的追踪和弹性）计划",
         "STREAM（高效农业投入管理的追踪与韧性系统）计划"),
        ("美国高级研究项目卫生署（ARPA-H）", "美国高级研究计划局健康分部（ARPA-H）"),
        ("帮助农民和保护人类健康的杀虫剂", "帮助农民并保护人类健康的除草剂"),
        ("对草药的接触可能导致癌症", "接触除草剂可能增加癌症风险"),
        ("由于经常使用草药而受到影响", "因经常使用除草剂而受到影响"),
    ],
    T6: [
        ("伊恩·巴克周一在芝加哥 SC26 上启动了公司的周", "伊恩·巴克周一在芝加哥 SC26 上拉开了公司活动周的序幕"),
        ("Nemotron 为了科学", "Nemotron for Science（面向科学的 Nemotron）"),
    ],
}


def main():
    db = json.load(open(DATA, encoding="utf-8"))
    items = db["items"] if isinstance(db, dict) else db
    changed = 0
    for it in items:
        en = (it.get("title") or "").strip()
        touched = False
        if en in TITLE_FIX:
            it["title_zh"] = TITLE_FIX[en]
            touched = True
        if en in SUMMARY_FIX:
            it["summary_zh"] = SUMMARY_FIX[en]
            touched = True
        if en in SUMMARY_PATCH:
            s = it.get("summary_zh") or ""
            for old, new in SUMMARY_PATCH[en]:
                s = s.replace(old, new)
            it["summary_zh"] = s
            touched = True
        if touched:
            it["translated"] = True
            it["method"] = "nllb+manual"
            changed += 1
            print("fixed:", it.get("date"), it.get("time"), en[:55])
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    titles = json.load(open(T_JSON, encoding="utf-8"))
    summaries = json.load(open(S_JSON, encoding="utf-8"))
    added_t = added_s = 0
    for k, v in TITLE_FIX.items():
        if titles.get(k) != v:
            titles[k] = v
            added_t += 1
    for k, v in SUMMARY_FIX.items():
        if summaries.get(k) != v:
            summaries[k] = v
            added_s += 1
    for en, patches in SUMMARY_PATCH.items():
        s = summaries.get(en)
        if s:
            for old, new in patches:
                s = s.replace(old, new)
            summaries[en] = s
            added_s += 1
    with open(T_JSON, "w", encoding="utf-8") as f:
        json.dump(titles, f, ensure_ascii=False, indent=2)
    with open(S_JSON, "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)

    print("[fix_2300b] news.json 回填 %d 条；标题定稿 %d 条 / 摘要定稿 %d 条" %
          (changed, added_t, added_s))
    print("[fix_2300b] 覆盖表 %d 条 / %d 条" % (len(titles), len(summaries)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
