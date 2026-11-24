# -*- coding: utf-8 -*-
"""2026-11-24 08:00 例行巡检：定稿本轮新增 5 条 NLLB 机翻硬伤。

08:06 引擎加载完成后首轮自动抓取新增 5 条，均含明显硬伤：
1) The Verge「Jensen Huang」未译（作「詹森」），「Steven Cheung」截断为「史蒂文·」；
2) Unite.AI「running Linux systems」误作「运行 Linux 系统」，表述生硬；
3) Simon Willison「Loop Transformer」误作「环变压器」，「looped」架构术语错乱；
4) SiliconANGLE「closes $1.75B investment」误作「关闭了 17.5 亿美元的投资」（应为「完成融资」）；
5) Marktechpost「Claude Ship」误作「Claude·船发射了」，产品名与动词全错。

覆盖三层：news.json 回填 + JSON 覆盖表 + 代码层 manual_overrides.py（regen）。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

FIX = {
    "White House brags that Trump was \u2018totally involved\u2019 in getting Jensen reinstated": (
        "白宫炫耀特朗普「全程参与」让黄仁勋复职",
        "唐纳德·特朗普总统在黄仁勋重返英伟达 CEO 一事中所起的作用显而易见——如今白宫要让所有人都知道这一点。白宫通讯主任史蒂文·张（Steven Cheung）在一份声明中表示：「特朗普总统全程参与，这是英伟达董事会的英明决定。」该声明最早由 Semafor 报道。「我们必须保护我们的天才。」特朗普随后在 CNBC 上发表了类似言论，他在节目中说：「我们必须保护我们的天才。」他还表示自己「非常坚定地」认为黄仁勋应当复职。",
    ),
    "OpenAI Launches Shirudo to Protect Running Linux Systems": (
        "OpenAI 推出 Shirudo，保护运行中的 Linux 系统",
        "OpenAI 与思科于 2026 年 11 月 23 日推出开源项目 Shirudo，为运维人员提供运行时保护手段：在永久性修复方案开发与部署期间，可对 Linux 系统施加临时防护。这个预发布项目结合了 eBPF 控制与面向智能体的设计，用于开发名为「防护罩（shields）」的定向保护措施，瞄准从发现漏洞到补丁部署完成之间的空窗期。",
    ),
    "GLM-5.4: Toward Generalized Coding with Our First Loop Transformer": (
        "GLM-5.4：以首个循环 Transformer 迈向通用编程",
        "GLM 5.4 现已由中国 AI 实验室 Z.ai 发布，这是其首个采用循环 Transformer 架构的模型。他们的描述如下：在标准 Transformer 中，每一层在每次前向传播中运行一次；而在循环 Transformer 中，一组共享权重的层会多次迭代运行，利用上一次传播的隐藏状态不断精炼。这让网络可以更深，却不增加参数量。这是我在过去一周内第二次看到循环 Transformer——第一次是 11 月 20 日 Thinking Machines Lab 的 Inkling 2 Mini，他们称：Inkling 2 Mini 是一个循环 Transformer，对每个 token 将模型的中间层运行三次。",
    ),
    "AI agent provider Sierra closes $1.75B investment amid rapid revenue growth": (
        "AI 智能体服务商 Sierra 完成 17.5 亿美元融资，营收快速增长",
        "距上一轮融资仅六个月，AI 创业公司 Sierra Technologies Inc. 今日宣布完成 17.5 亿美元后期融资。Greenoaks 与 Lightspeed 领投本轮 F 轮融资，回归的投资方还包括 Alphabet Inc. 旗下的 GV 基金。",
    ),
    "Anthropic Launches Claude Ship for GitHub Pull Request Review and Fixes": (
        "Anthropic 推出 Claude Ship，用于 GitHub Pull Request 审查与修复",
        "Anthropic 刚刚发布 Claude Ship——这是一套将 GitHub Pull Request 从审查推进到批准的智能体集合。它包含 3 个智能体：代码审查（Code Review）、PR 管家（PR Steward）和 Claude 批准（Claude Approvals）。最终是否合并仍由你的 GitHub 分支规则决定。速览：包含 3 个智能体，配有本地 /ship 命令；Code Review 与 PR Steward 运行在 Anthropic 云端，/ship 在本地 Claude Code CLI 中运行；大多数代码审查在 6 至 10 分钟内完成，约为研究预览版的 3 倍速；Claude Code 团队在 6 月至 9 月间合并的 PR 数量翻了一倍以上（自报数据）。根据 Claude Ship 文档，每个智能体各司其职：Code Review 负责查找逻辑错误、安全漏洞和失效的边界情况，发现的问题会以内联评论形式按严重程度排序呈现；PR 管家则处理失败的检查、合并冲突和审查意见。",
    ),
}


def main():
    db = json.load(open(DATA, encoding="utf-8"))
    items = db["items"] if isinstance(db, dict) else db
    titles = json.load(open(T_JSON, encoding="utf-8"))
    summaries = json.load(open(S_JSON, encoding="utf-8"))

    changed = added_t = added_s = 0
    for it in items:
        en = (it.get("title") or "").strip()
        if en not in FIX:
            continue
        title_zh, summary_zh = FIX[en]
        it["title_zh"] = title_zh
        it["summary_zh"] = summary_zh
        it["translated"] = True
        it["method"] = "nllb+manual"
        changed += 1
        print("fixed:", it.get("date"), it.get("time"), en[:55])
        if titles.get(en) != title_zh:
            titles[en] = title_zh
            added_t += 1
        if summaries.get(en) != summary_zh:
            summaries[en] = summary_zh
            added_s += 1

    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    with open(T_JSON, "w", encoding="utf-8") as f:
        json.dump(titles, f, ensure_ascii=False, indent=2)
    with open(S_JSON, "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)

    print("[fix_0800_1124] news.json 回填 %d 条；标题定稿 %d / 摘要定稿 %d" %
          (changed, added_t, added_s))
    print("[fix_0800_1124] 覆盖表 %d / %d 条" % (len(titles), len(summaries)))
    return 0 if changed == len(FIX) else 1


if __name__ == "__main__":
    raise SystemExit(main())
