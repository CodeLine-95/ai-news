# -*- coding: utf-8 -*-
"""18:00 巡检质量修复：定稿本轮 2 条新增资讯的 NLLB 生硬译文，
并顺带修正一条存量西门子条目的语义/数字格式缺陷。

写入 JSON 覆盖表 + 回填 news.json，再运行 scripts/regen_overrides.py
同步代码层 manual_overrides.py（部署端持久卷不会随发布更新 JSON 表）。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")
NEWS = os.path.join(BASE, "data", "news.json")

FIXES = {
    "XPENG Positions IRON Humanoid as an Autonomous Work Partner": (
        "小鹏将 IRON 人形机器人定位为自主工作伙伴",
        "在 2026 年 11 月 25 日举行的科技日上，小鹏汽车将 IRON 定位为「合格的工作伙伴」，"
        "介绍了其自主商业作业功能、搭载的 AI 系统与安全系统，并邀请购买或合作咨询。"
        "科技日现场汇聚了 7 台 IRON 机器人，官方活动帖重点展示了其多语言互动能力。"
        "该人形机器人身高 170 厘米、体重 62 公斤，具备 76 个全身自由度。",
    ),
    "Siemens Expands Industrial AI Across Planning and Robot Unpacking": (
        "西门子将工业 AI 扩展至生产规划与机器人拆箱",
        "西门子于 2026 年 11 月 24 日在纽伦堡 SPS 2026 展会上宣布扩展自动化产品组合，"
        "面向 AI 驱动的自主生产，其中包括正在开发中的货物拆箱机器人，"
        "以及用于规划与工程环节的 AI 智能体。西门子预计，规划智能体可将人工规划工作量减少 70%。"
        "该组合围绕「目标导向自动化」构建：制造商只需说明期望的结果，"
        "工业 AI 即可自行确定实现路径，或通过 AI 智能体直接完成任务。",
    ),
    "Siemens Raises Growth Targets on Industrial AI and Data Center Demand": (
        "西门子受工业 AI 与数据中心需求推动上调增长目标",
        "西门子于 2026 年 11 月 12 日上调中期增长目标。截至 2026 年 9 月 30 日的财年，"
        "可比订单增长 25%，达到创纪录的 1082 亿欧元。公司将更高的目标与工业 AI、数字化、"
        "电气化及数据中心需求联系起来。不含西门子医疗（Siemens Healthineers）的集团，"
        "可比营收增速目标由 6%–9% 上调至 7%–11%；扣除 PPA 前的每股收益（EPS pre PPA）"
        "增长目标则从高个位数上调至两位数。",
    ),
}


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    titles = load(T_JSON)
    summaries = load(S_JSON)
    for key, (title_zh, summary_zh) in FIXES.items():
        titles[key] = title_zh
        summaries[key] = summary_zh
    save(T_JSON, titles)
    save(S_JSON, summaries)

    news = load(NEWS)
    fixed = 0
    for it in news["items"]:
        fix = FIXES.get(it.get("title"))
        if not fix:
            continue
        it["title_zh"], it["summary_zh"] = fix
        it["translated"] = True
        it["method"] = "manual"
        fixed += 1
    save(NEWS, news)
    print("定稿条目数:", fixed)


if __name__ == "__main__":
    main()
