# -*- coding: utf-8 -*-
"""2026-11-23 21:00 例行巡检：定稿本轮新增 7 条 NLLB 机翻硬伤。

本轮 21:00 整点抓取新增 7 条，逐条核对原文后人工定稿：
1) Marlowe Raises $277M Seed... : 标题「种子」缺「轮」、「多化工」应为「多芯片」。
2) Arm CEO Rene Haas... : 标题漏主语 Arm，摘要「供应自己的 AI 数据中心」缺宾语「芯片」。
3) Sierra Raises $1.75B... at $30B Valuation : 数字硬伤——$1.75B=17.5亿美元(非1.75亿)、
   $30B=300亿美元(非30亿)、$950M=9.5亿美元(非9.5亿)；Series F=F 轮；Sierras=所有格误写。
4) Mach7 and Rad AI... : 「马赫7」「拉德人工智能」为公司名音译硬伤，viewer 应为「影像浏览器」。
5) GPT-6.2 Astra... : 「证据」应为「证明」、「差距定理」为 Smoktunowicz 间隙定理、
   「文章 GPT-6」为结尾截断残留，需删除。
6) Claude Code Adds Experimental Code Mode... : 「Claude 代码」应为产品名 Claude Code、
   「过 Bash」应为「筛选 Bash」、「克如何」为 hooks 误译。
7) CrowdStrike Agrees to Acquire Zscaler... : 「克劳德斯特莱克」为公司名音译硬伤、
   「猎平台」应为 Falcon 平台、「出发的...股票」应为「流通在外的每股」。

覆盖三层：news.json 回填 + JSON 覆盖表（regen 时复用）。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

TITLE_FIX = {
    "Marlowe Raises $277M Seed to Build Multi-Silicon AI Factories":
        "Marlowe 完成 2.77 亿美元种子轮融资，建设多芯片 AI 工厂",
    "Arm CEO Rene Haas Extends Tenure with New SoftBank Leadership Role":
        "Arm CEO Rene Haas 任期延长，兼任软银新领导职务",
    "Sierra Raises $1.75B in Series F Funding at $30B Valuation":
        "Sierra 完成 17.5 亿美元 F 轮融资，估值达 300 亿美元",
    "Mach7 and Rad AI Plan Viewer-to-Report Integration for Radiologists":
        "Mach7 与 Rad AI 计划为放射科医生打通影像浏览到报告的集成",
    "GPT-6.2 Astra solved a math theorem no other AI could crack, then invented its own proof strategy":
        "GPT-6.2 Astra 攻克其他 AI 无解的数学定理，还自创证明策略",
    "Claude Code Adds Experimental Code Mode to Orchestrate Tool Calls with JavaScript":
        "Claude Code 新增实验性代码模式，用 JavaScript 编排工具调用",
    "CrowdStrike Agrees to Acquire Zscaler to Secure AI Agent Connections":
        "CrowdStrike 同意收购 Zscaler，强化 AI 智能体连接安全",
}

SUMMARY_FIX = {
    "Marlowe Raises $277M Seed to Build Multi-Silicon AI Factories": (
        "Marlowe 于 2026 年 11 月 23 日宣布完成 2.77 亿美元种子轮融资，并详述其建设与运营 AI 工厂的"
        "计划——这些工厂专为跨多种芯片类型的推理工作负载而设计。公布的机构投资者包括 Accel、"
        "Bessemer、Altimeter、Atreides 和 Eclipse，以及其他风险投资机构和天使投资人。Dan Lewis 与 "
        "Kutta Srinivasan 于 2026 年 5 月联合 Lior Susan、Ido Susan 和 Chris Ré 创立了 Marlowe。"
    ),
    "Arm CEO Rene Haas Extends Tenure with New SoftBank Leadership Role": (
        "Arm 于 2026 年 11 月 23 日宣布，CEO Rene Haas 已签署新协议，将其领导任期延长至 2033 年，"
        "并将于 2026 年 12 月 1 日出任软银集团副董事长。他将留任 Arm CEO，同时公司正从授权处理器"
        "技术扩展到自研 AI 数据中心芯片。软银另行发布的人事公告将 Haas 列为董事、副董事长，并确认"
        "他将继续领导 Arm。"
    ),
    "Sierra Raises $1.75B in Series F Funding at $30B Valuation": (
        "Sierra 于 2026 年 11 月 23 日宣布，在由 Greenoaks 和 Lightspeed Venture Partners 领投的一轮"
        "融资中，以 300 亿美元估值募集 17.5 亿美元 F 轮资金。该公司构建 AI 智能体，为大型企业处理"
        "客户交互并执行业务任务。此前 Sierra 于 2026 年 5 月 4 日宣布，由 Tiger Global 和 GV 领投、"
        "以超过 150 亿美元估值募集 9.5 亿美元。"
    ),
    "Mach7 and Rad AI Plan Viewer-to-Report Integration for Radiologists": (
        "Mach7 Technologies 与 Rad AI 于 2026 年 11 月 23 日宣布合作，将 Mach7 的 Flamingo Worklist "
        "与 eUnity 企业级影像浏览器同 Rad AI Reporting 打通，目标是在影像判读与放射报告之间传递测量"
        "数据和病例上下文，无需人工重新录入。即便影像、AI 与报告系统彼此相连，测量数据等临床信息仍"
        "常常无法自动流转——两家公司正是要解决这一交接难题。"
    ),
    "GPT-6.2 Astra solved a math theorem no other AI could crack, then invented its own proof strategy": (
        "据 Vals AI 称，OpenAI 的 GPT-6.2 Astra 独立给出了 Smoktunowicz 间隙定理的机器可验证 Lean "
        "证明，属首个此类成果。由于 Mathlib 缺少关键基础库，该模型自行选择了证明路径。在 "
        "Autoform-Hard 基准上，Astra 以 56 道题解出 49 道的成绩登顶排行榜。"
    ),
    "Claude Code Adds Experimental Code Mode to Orchestrate Tool Calls with JavaScript": (
        "Anthropic 的实验性代码模式让 Claude Code 能够编写 JavaScript，串联、并行执行并筛选 Bash、"
        "Read 和 Edit 调用，同时改变了自动模式与 hooks 审查这些调用的方式。"
    ),
    "CrowdStrike Agrees to Acquire Zscaler to Secure AI Agent Connections": (
        "CrowdStrike 与 Zscaler 于 2026 年 11 月 23 日宣布达成最终收购协议，CrowdStrike 将以全股票"
        "交易收购 Zscaler，对后者的企业估值约为 439 亿美元。该交易将为 CrowdStrike 的 Falcon 平台"
        "增加网络控制与 AI 智能体连接安全能力。每股 Zscaler 股票将换取 1.135 股 CrowdStrike 股票，"
        "按 CrowdStrike 2026 年 11 月 20 日收盘价计算约为每股 260.41 美元，较 Zscaler 当日收盘价溢价"
        "约 34%。双方董事会均一致批准该协议。交易完成后，现有 CrowdStrike 与 Zscaler 股东预计将分别"
        "持有合并后公司约 84.1% 和 15.9% 的股份。"
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

    print("[fix_2100_1123] news.json 回填 %d 条；标题定稿 %d / 摘要定稿 %d" %
          (changed, added_t, added_s))
    print("[fix_2100_1123] 覆盖表 %d / %d 条" % (len(titles), len(summaries)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
