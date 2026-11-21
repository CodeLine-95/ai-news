# -*- coding: utf-8 -*-
"""2026-11-21 10:00 巡检：定稿 orchestration 机翻硬伤。

NLLB 将 AI 语境下的 orchestration / orchestrator 误译为「管弦乐/管弦乐器/
管弦乐员」，正确术语应为「编排 / 编排器」。本轮定稿 4 条：
1) Unite.AI《AWS Quick Adds Chat-Built Flows and Multi-Agent Orchestration》
   —— 标题「多智能体管弦乐」；摘要「调整/汇集」语义偏差。
2) Ambience Healthcare《Adds Care Orchestration to Inpatient AI Suite》
   —— 标题「护理管弦乐器在患者」语义崩坏；摘要「护理管弦功能/排放障碍」。
3) Kubernetes《Agents idling ... hand back unused resources》
   —— 摘要「管弦乐员」错译 orchestrator（应为编排器/调度器）。
4) Rafay《Adds Confidential AI Orchestration for Kubernetes Pods》
   —— 标题「机密人工智能管弦乐」；摘要「机密装箱」等瑕疵。

覆盖三层：news.json 回填 + JSON 覆盖表 + manual_overrides.py（regen）。
运行后需 curl -X POST /api/refresh 让在线生效并重生成报告。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

TITLE_FIX = {
    "AWS Quick Adds Chat-Built Flows and Multi-Agent Orchestration":
        "AWS Quick 新增聊天式构建流程与多智能体编排",
    "Ambience Healthcare Adds Care Orchestration to Inpatient AI Suite":
        "Ambience Healthcare 为住院 AI 套件新增护理编排功能",
    "Agents idling while they wait on humans push Kubernetes to hand back unused resources":
        "智能体因等待人工而闲置，促使 Kubernetes 归还闲置资源",
    "Rafay Adds Confidential AI Orchestration for Kubernetes Pods":
        "Rafay 为 Kubernetes Pod 新增机密 AI 编排能力",
}

SUMMARY_FIX = {
    "AWS Quick Adds Chat-Built Flows and Multi-Agent Orchestration": (
        "亚马逊云科技于 2026 年 11 月 20 日发布 AWS Quick 的一次广泛更新，新增通过聊天构建的业务工作流，"
        "以及可汇集多个专业智能体输出的编排能力。重新设计的网页应用、新连接器与扩展的管理控制，"
        "支撑其推动 AI 辅助流程在团队间可重复执行。"
    ),
    "Ambience Healthcare Adds Care Orchestration to Inpatient AI Suite": (
        "Ambience Healthcare 于 2026 年 11 月 17 日宣布为其住院 AI 套件推出两项护理编排功能——"
        "Rounding Assistant（查房助手）与 Discharge Readiness（出院准备），"
        "为医院工作流增加任务优先级排序与更早识别出院障碍的能力。这些功能在已支持住院病历记录与编码的软件之上，"
        "新增了一层协调机制。"
    ),
    "Agents idling while they wait on humans push Kubernetes to hand back unused resources": (
        "智能体 AI 负载正让 Kubernetes 迎来意想不到的第二春。"
        "这个曾被认为可靠但乏味的编排器，如今成为企业规划运行自主软件的核心。"
    ),
    "Rafay Adds Confidential AI Orchestration for Kubernetes Pods": (
        "Rafay Systems 与 Fortanix 于 2026 年 11 月 11 日宣布，Rafay 平台现已编排运行在 "
        "CNCF 机密容器（CoCo）上的 Fortanix 机密 AI 工作负载，"
        "将其既有的机密虚拟机集成扩展到 Kubernetes Pod。该联合方案现已面向新云服务商、主权 AI 云与企业开放，"
        "补足了传统加密方案的空白。"
    ),
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
        if touched:
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

    print("[fix_1121_1000] news.json 回填 %d 条；标题定稿 %d 条 / 摘要定稿 %d 条" %
          (changed, added_t, added_s))
    print("[fix_1121_1000] 覆盖表 %d 条 / %d 条" % (len(titles), len(summaries)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
