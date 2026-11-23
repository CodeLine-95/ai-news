# -*- coding: utf-8 -*-
"""2026-11-23 16:00 例行巡检：定稿本轮新增 2 条 NLLB 机翻硬伤。

1) Unite.AI《Bureau Veritas Buys Topo Solutions to Expand AI Supply Chain
   Services》(15:16)：NLLB 把 Bureau Veritas（必维国际检验集团）音译成
   「维里塔斯」，与摘要自我指代不一致；标题与摘要需按官方通稿定稿。
2) Unite.AI《Ant Group Begins Open-Weight Release of LingSante Medical AI
   Models》(15:47)：NLLB 把 Ant Group 译成「团」（漏译 Ant/蚂蚁），
   Open-Weight Release 译成「重量发布」（应为「开放权重发布」）；
   Afu 应为「阿福」，Ling 基础模型应为「百灵/Ling」；据中文官方通稿定稿。

覆盖三层：news.json 回填 + JSON 覆盖表 + manual_overrides.py（regen）。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

TITLE_FIX = {
    "Bureau Veritas Buys Topo Solutions to Expand AI Supply Chain Services":
        "必维国际检验集团收购 Topo Solutions，扩展 AI 供应链服务",
    "Ant Group Begins Open-Weight Release of LingSante Medical AI Models":
        "蚂蚁集团开始开放 LingSante 医疗 AI 模型权重",
}

SUMMARY_FIX = {
    "Bureau Veritas Buys Topo Solutions to Expand AI Supply Chain Services": (
        "必维国际检验集团（Bureau Veritas）于 2026 年 11 月 23 日宣布收购 Topo Solutions——"
        "一家总部位于香港、提供 AI 驱动的端到端供应链管理平台的公司。这笔交易扩大了这家"
        "全球测试、检验与认证（TIC）集团为消费品公司和零售商提供的数字服务；Topo 2025 年"
        "营收约 300 万欧元。收购让必维获得一个覆盖从产品开发到发货的供应链信息统一平台，"
        "也为其 AI 战略带来落地场景——客户数据可支撑自动化、分析与决策。该交易属于必维"
        "「LEAP | 28」战略下的补强收购，并与其 2030 年 AI 驱动业务收入达 10 亿欧元的目标相呼应。"
    ),
    "Ant Group Begins Open-Weight Release of LingSante Medical AI Models": (
        "蚂蚁集团于 2026 年 11 月 23 日宣布，其阿福（Afu）健康应用推出 LingSante（百灵）"
        "医疗 AI 模型家族，该家族基于蚂蚁 Ling 基础模型构建。首批两款模型以 MIT 许可证开放，"
        "更广泛家族的权重将分阶段发布。模型卡将 LingSante-3.1-air-VL 定位为面向影像与个人"
        "健康评估的多模态系统，将 LingSante-3.1-flash 定位为面向证据综合与多阶段医疗工作流的"
        "更大规模推理模型；前者面向个人用户与小型机构，后者面向复杂病例分析与专业医疗智能体。"
        "蚂蚁称阿福服务 1.5 亿用户、日均处理近 2000 万次健康咨询。此外，LingSante-Pulse 可评估"
        "150 余种疾病风险，LingSante-MedGuard 用于识别与降低医疗安全、合规及伦理风险，"
        "LingSante-Live 已集成进阿福用于实时视频交互。模型卡明确这些可下载系统仅供研究与评估，"
        "不得用于独立诊断、开具处方或治疗决策。"
    ),
}


def main():
    db = json.load(open(DATA, encoding="utf-8"))
    items = db["items"] if isinstance(db, dict) else db
    changed = 0
    for it in items:
        en = (it.get("title") or "").strip()
        if en not in TITLE_FIX:
            continue
        it["title_zh"] = TITLE_FIX[en]
        it["summary_zh"] = SUMMARY_FIX[en]
        it["translated"] = True
        it["method"] = "nllb+manual"
        changed += 1
        print("fixed:", it.get("date"), it.get("time"), en[:60])
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
    with open(T_JSON, "w", encoding="utf-8") as f:
        json.dump(titles, f, ensure_ascii=False, indent=2)
    with open(S_JSON, "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)

    print("[fix_1600_1123] news.json 回填 %d 条；标题定稿 %d / 摘要定稿 %d" %
          (changed, added_t, added_s))
    print("[fix_1600_1123] 覆盖表 %d / %d 条" % (len(titles), len(summaries)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
