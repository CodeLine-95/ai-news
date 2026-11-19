# -*- coding: utf-8 -*-
"""08:00 例行巡检：人工定稿本轮 NLLB 机翻硬伤（8 条中 8 条），回填 news.json 并写入三层覆盖表。

对英文标题做精确匹配定稿：标题译名/断句/语义硬伤一次性修正，
摘要同步修正关键错译。键为英文原标题，写入 JSON 覆盖表后由
scripts/regen_overrides.py 同步到代码层 manual_overrides.py。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

# 英文原标题 -> (定稿中文标题, 定稿中文摘要 or None 表示保留原摘要)
FIX = {
    "Google upgrades Gemini’s agentic Task mode with new model, e-commerce features": (
        "Google 升级 Gemini 智能体任务模式：新增模型与电商功能",
        "Google 正在为其 Gemini AI 助手推出新版本，提升多步骤任务执行能力。负责 Gemini 应用的副总裁 Josh Woodward 在周四的博客文章中详述了此次更新。该 AI 助手提供两种模式，可通过独立界面标签访问。",
    ),
    "Anthropic’s record-breaking IPO priced at $83 per share, higher than expected": (
        "Anthropic 创纪录 IPO 定价每股 83 美元，高于预期",
        None,
    ),
    "Amidst fears of AI cyberattacks, Satya Nadella says lots of critical infrastructure is ‘unpatchable’": (
        "担忧 AI 网络攻击之际，萨蒂亚·纳德拉称大量关键基础设施「无法修补」",
        "微软 CEO 淡化了近期的 Outlook 中断事件，同时指出 AI 正带来机遇，也为保障大部分互联网世界的安全带来新挑战。",
    ),
    "Nadella Backs NVIDIA Team Led by Interim CEO Colette Kress": (
        "纳德拉支持临时 CEO Colette Kress 领衔的 NVIDIA 团队",
        "微软 CEO 萨蒂亚·纳德拉在 2026 年 11 月 18 日于纽约市举行的 DealBook 峰会上表示，他信赖 NVIDIA 临时 CEO Colette Kress 的团队。据 TechCrunch 报道，黄仁勋在执掌公司 33 年后辞任。纳德拉称他认识克雷斯已久，并指出她此前在微软任职。",
    ),
    "Elon Musk says ousting Jensen Huang is like ‘kicking Michael Jordan off your team’": (
        "埃隆·马斯克称罢黜黄仁勋如同「把迈克尔·乔丹踢出你的团队」",
        "马斯克表示：「我不认为[黄仁勋]对美国不忠。」",
    ),
    "AWS Adds Training Validation and Hung-Job Detection to HyperPod": (
        "AWS 为 HyperPod 新增训练校验与挂起作业检测",
        "亚马逊云科技于 2026 年 11 月 18 日宣布为 Amazon SageMaker HyperPod 推出三项可靠性功能，针对数值训练故障、Kubernetes 故障以及停滞的 Slurm 作业——这些作业会在单个节点看似健康的情况下占用 GPU 算力。HyperPod 已可监控硬件错误、运行深度诊断检查并测试实例间通信，自动恢复故障节点。",
    ),
    "The nation’s largest school districts consider ditching Google Search": (
        "美国最大几个学区考虑弃用 Google 搜索",
        "据《纽约时报》报道，纽约、洛杉矶和芝加哥的学校正考虑 Google 的替代方案；该公司表示将屏蔽拒绝其 AI 功能的学校的搜索服务。从明年起，学校将无法在保留搜索的同时禁用 Gemini 驱动的功能。Google 教育副总裁 Chris Phillips 告诉该报：「搜索与 AI 已深度集成。」",
    ),
    "Microsoft CEO Satya Nadella remains confident in Nvidia after Huang’s exit": (
        "黄仁勋卸任后，微软 CEO 萨蒂亚·纳德拉仍对英伟达有信心",
        "微软 CEO 萨蒂亚·纳德拉对黄仁勋的继任者、现任英伟达临时 CEO Colette Kress 表示信心。",
    ),
}


def main():
    db = json.load(open(os.path.join(DATA, "news.json"), encoding="utf-8"))
    items = db["items"] if isinstance(db, dict) else db

    tpath = os.path.join(DATA, "titles_override.json")
    spath = os.path.join(DATA, "summaries_override.json")
    tov = json.load(open(tpath, encoding="utf-8")) if os.path.exists(tpath) else {}
    sov = json.load(open(spath, encoding="utf-8")) if os.path.exists(spath) else {}

    changed = 0
    for it in items:
        en = it.get("title") or ""
        if en not in FIX:
            continue
        title_zh, summary_zh = FIX[en]
        if it.get("title_zh") != title_zh:
            it["title_zh"] = title_zh
            it["translated"] = True
            it["method"] = "nllb+manual"
            changed += 1
            print("[fix] title:", en[:50], "->", title_zh)
        if summary_zh is not None and it.get("summary_zh") != summary_zh:
            it["summary_zh"] = summary_zh
            print("[fix]  summary:", en[:50])
        tov[en] = title_zh
        sov[en] = summary_zh if summary_zh is not None else (it.get("summary_zh") or "")

    json.dump(tov, open(tpath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(sov, open(spath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(db, open(os.path.join(DATA, "news.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("[fix] 标题变更:", changed, "| 覆盖表 标题:", len(tov), "摘要:", len(sov))


if __name__ == "__main__":
    main()
