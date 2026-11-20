# -*- coding: utf-8 -*-
"""2026-11-20 15:00 巡检：定稿本轮新增 2 条 + 历史硬伤 3 条 NLLB 机翻错误。

本轮 15:00 整点调度新增 2 条（2447→2449）：
1) InfoQ AI《AWS Releases a Free Local Emulator of AWS Built Entirely by
   Agents》（14:53）——"The docs say" 误译「医生说」、"fidelity scores"
   误译「忠诚度分数」；
2) Wired《This 16-Year-Old Founded an AI Missile Startup. He's Targeting
   'Cost per Kill'》（15:00）——标题截断「他正在准每次杀伤的成本」。

历史硬伤 3 条（全库 fidelity/Fidelity 误译扫描发现）：
3) Fidelity 公司名误译「忠诚度」+ Anthropic 误译「人类」（11-11 标题）；
4) AWS 开源模拟器摘要 fidelity→「忠诚度分数」（11-16）；
5) AWS Emulator 本地副本摘要 fidelity→「忠诚度测试」（11-13）。

覆盖三层：news.json 回填 + JSON 覆盖表 + manual_overrides.py（regen）。
运行后需 curl -X POST /api/refresh 让在线生效并重生成报告。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

AWS_TITLE = "AWS Releases a Free Local Emulator of AWS Built Entirely by Agents"
MISSILE_TITLE = "This 16-Year-Old Founded an AI Missile Startup. He’s Targeting ‘Cost per Kill’"
FIDELITY_TITLE = "Fidelity Sets Retail Participation Terms for Anthropic’s Planned IPO"
AWS_OPEN_TITLE = "AWS Open-Sources Emulator for Local Testing of 200+ Services by Coding Agents"
AWS_COPY_TITLE = "AWS Releases AWS Emulator: A Local Copy of 200+ AWS Services Built by AI Agents"

# 标题整段定稿
TITLE_FIX = {
    AWS_TITLE: "AWS 发布完全由智能体构建的免费 AWS 本地模拟器",
    MISSILE_TITLE: "这名 16 岁少年创办了一家 AI 导弹初创公司，主打「单次杀伤成本」",
    FIDELITY_TITLE: "富达（Fidelity）为 Anthropic 计划中的 IPO 设定散户参与条款",
}

# 摘要整段定稿（仅短摘要；长摘要用 SUMMARY_PATCH 定点替换以保留 TL;DR 事实）
SUMMARY_FIX = {
    AWS_TITLE: (
        "AWS 发布了 AWS Emulator——一款免费、采用 CC0 许可的本地替代方案，"
        "可模拟其 200 多项服务，由公开 API 模型生成，面向编码智能体的测试循环。"
        "AWS 称全部代码均由智能体编写和维护，并随每个版本发布保真度评分。"
        "文档说明它不评估 IAM（身份与访问管理），从业者对于是否信任一个无人审查的模拟器看法不一。"
    ),
    MISSILE_TITLE: (
        "Henrijs Dandzbergs 从高中辍学，加入创业加速器 Y Combinator。"
        "他希望凭借一种新型导弹，让美国及其军事盟友尽可能高效地实现「杀伤」——"
        "把每一发弹药的成本压到最低。"
    ),
}

# 摘要定点替换（保留原有 TL;DR 长摘要结构）
SUMMARY_PATCH = {
    AWS_OPEN_TITLE: [("忠诚度分数", "保真度分数")],
    AWS_COPY_TITLE: [("忠诚度测试", "保真度测试")],
}


def main():
    # 1) 回填 news.json
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

    # 2) 写入 JSON 覆盖表
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
    # 历史长摘要：对覆盖表中已存在的条目做同样定点替换
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

    print("[fix_1500] news.json 回填 %d 条；标题定稿 %d 条 / 摘要定稿 %d 条" %
          (changed, added_t, added_s))
    print("[fix_1500] 覆盖表 %d 条 / %d 条" % (len(titles), len(summaries)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
