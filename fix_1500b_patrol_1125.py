# -*- coding: utf-8 -*-
"""2026-11-25 15:00 巡检第二轮：人工定稿整点抓取的 3 条 NLLB 硬伤译文。

重启后引擎预热竞态导致 3 条新条目先以未翻译入库，补译后译文出现术语硬伤：
- "Spark 升级"被译成"火升级"
- "形式化验证（formal verification）"被译成"正式验证"
- "operational playbook"被译成"操作书"

沿用惯例：以英文原标题为键写入 JSON 覆盖表并回填 news.json，
随后由 scripts/regen_overrides.py 固化到 manual_overrides.py（随发布生效）。
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
STAMP = "1500bpatrol1125"

FIXES = {
    "QCon San Francisco 2026: Automating Spark Upgrades with Codex Agents at OpenAI": (
        "QCon 旧金山 2026：OpenAI 用 Codex 智能体自动化 Spark 升级",
        "在 QCon 旧金山 2026 大会上，OpenAI 数据基础设施工程经理 Mouli Mukherjee 提出，"
        "AI 智能体最有价值的应用场景并非重建数据平台，而是处理那些难以写成固定操作手册的"
        "开放式运维工作。",
    ),
    "Certis Partners with SUTD to Test Physical AI in Live Operations": (
        "Certis 与 SUTD 合作，在真实运营场景中测试物理 AI",
        "Certis 与新加坡科技设计大学（SUTD）于 2026 年 11 月 25 日宣布签署一份为期三年的"
        "谅解备忘录，将在真实的安防与设施运营场景中联合开发并测试物理 AI、机器人与无人机技术。"
        "该备忘录还涵盖工程人才培养以及商业化部署的规划。",
    ),
    "Formal verification startup Sequent raises $2.2M to prove code obeys its safety rules": (
        "形式化验证初创公司 Sequent 融资 220 万美元，用数学证明代码遵守安全规则",
        "形式化验证初创公司 Sequent Inc. 今日宣布完成 220 万美元新融资，"
        "将其 Alan 证明平台从早期访问阶段推向正式可用。Sequent 于今年 1 月在伦敦成立，"
        "提供了一个利用人工智能寻找数学证明的平台，用于验证代码是否遵守工程师设定的安全规则。",
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
