# -*- coding: utf-8 -*-
"""2026-11-24 18:00 例行巡检：定稿本轮新增 4 条 NLLB 机翻硬伤。

18:00 整点调度新增 4 条（total 2695 -> 2699），均为 NLLB 原始机翻，存在明确硬伤：
1) Non-Determinism 误译为「非定制主义」（应为「非确定性」），Evals/Grounding/Release
   Gates 分别误作「平衡/地面积/释放门」（应为「评测/事实依据/发布门禁」）；
2) ASRock Industrial 音译混乱（亚斯洛克/亚斯罗克，应为「华擎工业」），
   "launches ... kit" 误作「发起了」，Physical AI 宜作「具身 AI」；
3) 公司名 Trustly 误译为「信任性/托拉斯利」，应保留品牌名；
4) Genspark 误译为「斯帕克」，Dictation 误作「测试」（应为「语音听写」），
   "CNC-machined aluminum body" 误作「CNC 机械化的体」。

覆盖三层：news.json 回填 + JSON 覆盖表 + 代码层 manual_overrides.py（regen）。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

FIXES = [
    {
        "title": "Article: Engineering Around Non-Determinism: Evals, Grounding, and Release Gates for AI-Drafted Suspicious Reports",
        "title_zh": "文章：应对非确定性——面向 AI 起草可疑报告的评测、事实依据与发布门禁",
        "summary_zh": (
            "将生成式 AI 投入高风险生产环境，需要把非确定性当作工程问题来对待。"
            "这份架构蓝图展示了工程负责人与架构师如何利用知识图谱、双层评测裁判、"
            "CI/CD 发布门禁，以及针对黄金数据集的回归测试，构建可信的智能体工作流——"
            "在自动化起草的同时保持零幻觉的合规要求。"
        ),
    },
    {
        "title": "ASRock Industrial Launches RBK-100 Physical AI Development Kit",
        "title_zh": "华擎工业推出 RBK-100 具身 AI 开发套件",
        "summary_zh": (
            "华擎工业（ASRock Industrial）于 2026 年 11 月 24 日宣布推出 RBK-100"
            "「机器人套装」（Robotics-in-a-Box）——一个集成的物理 AI（具身智能）开发平台，"
            "结合了基于 Intel 的边缘计算设备、RGB-D 深度相机、配套机械臂，"
            "以及为研究人员、教育工作者和开发者预装的软件。"
            "华擎工业表示，该套件旨在减少机器人 AI 开发中的集成工作。"
        ),
    },
    {
        "title": "Trustly Raises $60M in Equity to Accelerate AI Product Development",
        "title_zh": "Trustly 通过股权融资 6000 万美元，加速 AI 产品开发",
        "summary_zh": (
            "Trustly Holding AB 在 2026 年 11 月 24 日的监管公告中宣布，"
            "母公司 Trustly AB 将通过股东资本募集约 6000 万美元，"
            "用于加速开发 AI 驱动的产品，把支付活动转化为面向企业的财务智能。"
            "Trustly 的主要股东 Nordic Capital 与 Alfvén & Didrikson 在 2026 年 10 月 2 日"
            "披露的不可撤销、具有法律约束力的股权承诺中，提供了超过 4000 万美元资金。"
        ),
    },
    {
        "title": "Genspark Launches SecondBrain VoicePad for Dictation and AI Agents",
        "title_zh": "Genspark 推出 SecondBrain VoicePad，用于语音听写与 AI 智能体",
        "summary_zh": (
            "Genspark 于 2026 年 11 月 24 日推出 SecondBrain VoicePad——"
            "一款面向 Windows 和 macOS 的五键桌面控制器，可进行语音听写、"
            "打开应用程序并触发 AI 工作流。该公司表示，预订现已开放，"
            "首批量产产品计划于 2027 年 1 月发货。"
            "这款 85 克重的设备采用 CNC 加工铝制机身、双麦克风，并支持蓝牙连接。"
        ),
    },
]


def main():
    db = json.load(open(DATA, encoding="utf-8"))
    items = db["items"] if isinstance(db, dict) else db
    titles = json.load(open(T_JSON, encoding="utf-8"))
    summaries = json.load(open(S_JSON, encoding="utf-8"))

    by_title = {fx["title"].strip(): fx for fx in FIXES}

    changed = 0
    for it in items:
        key = (it.get("title") or "").strip()
        fx = by_title.get(key)
        if not fx:
            continue
        it["title_zh"] = fx["title_zh"]
        it["summary_zh"] = fx["summary_zh"]
        it["translated"] = True
        it["method"] = "nllb+manual"
        changed += 1
        print("fixed:", it.get("date"), it.get("time"), key[:60])

    for fx in FIXES:
        titles[fx["title"]] = fx["title_zh"]
        summaries[fx["title"]] = fx["summary_zh"]

    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    with open(T_JSON, "w", encoding="utf-8") as f:
        json.dump(titles, f, ensure_ascii=False, indent=2)
    with open(S_JSON, "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)

    print("[fix_1800_1124] news.json 回填 %d 条；覆盖表 %d / %d 条"
          % (changed, len(titles), len(summaries)))
    return 0 if changed == len(FIXES) else 1


if __name__ == "__main__":
    raise SystemExit(main())
