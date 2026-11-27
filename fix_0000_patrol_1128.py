# -*- coding: utf-8 -*-
"""00 点巡检：定稿 6 条 NLLB 机翻硬伤并写回覆盖表。

本轮（2026-11-28 00:00）整点自动抓取新增 6 条，机翻存在明显缺陷：
  1) 'AI Literacy Is the Missing Layer of Deepfake Defense'
     deepfake 译为「深 fake」中英混杂；awareness 译为「意识」生硬。
  2) 'Next Wave of Payer AI: Managing Regulations, Costs, and Fragmented Systems all at once'
     payer 误译为「付款人」（实为医保支付方）；context 误译为「文本」。
  3) 'Rockstar's AI dilemma: Can GTA 6's staggered release model survive coding agents?'
     staggered release 误译为「曲的发布/曲版模型」；record console launch
     误译为「唱片控制台」；句尾重复拼接文章标题。
  4) 'A World Model to Predict What You'll Look at Next'
     frustrating 误译为「丧」；eyeline 误译为「眼光线」。
  5) 'SAP Could Cut at Least 10,000 Jobs in Reported AI Overhaul'
     Bloomberg 漏译为「博社」；job positions 译为「工作位」不顺。
  6) 'Jensen Huang returns, but controversies keep growing around Nvidia'
     Nvidia 译为「诺维迪亚」；lame-duck President 误译为「瓜总统」。

人工定稿后写回 data 与覆盖表，随后运行 scripts/regen_overrides.py 同步到
代码层覆盖表，保证后续轮次不再被模型译文覆盖。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

FIXES = [
    (
        "AI Literacy Is the Missing Layer of Deepfake Defense",
        "AI 素养是深度伪造防御中缺失的一环",
        "检测工具越来越智能，但大多数深度伪造骗局依然得逞——因为电话另一端的人不知道该核查什么。"
        "这道缺口只有靠防范意识才能补上。2024 年 1 月，奥雅纳（Arup）香港办公室的一名财务员工"
        "收到一封邮件，发件人是公司位于英国的首席财务官，要求一笔机密转账。他起了疑心。"
        "随后，他被邀请与这位首席财务官及几位他认识的同事进行视频通话。",
    ),
    (
        "Next Wave of Payer AI: Managing Regulations, Costs, and Fragmented Systems all at once",
        "下一波支付方 AI：同时应对监管、成本与割裂的系统",
        "支付方（医保付款机构）的技术负责人正面临 AI 应用泛滥的局面：嵌入系统的 AI 工具与第三方"
        "智能体平台都承诺更快审计、更快决策、更少人工干预。演示效果令人印象深刻，但由于工作流"
        "集成与用户采用方面的挑战，核心运营人员仍在手工收集背景信息、解读政策、跨多个系统协调"
        "工作，并通过同样的队列推动案件流转。",
    ),
    (
        "Rockstar's AI dilemma: Can GTA 6's staggered release model survive coding agents?",
        "Rockstar 的 AI 困境：GTA 6 的分阶段发行模式能否扛住编码智能体？",
        "在《GTA 6》以 37.9 亿美元创纪录销量发售主机版仅几天后，就有 40 多个项目试图通过逆向工程"
        "将泄露的 Xbox 版本移植到 PC 上。Claude Code 等 AI 编码智能体大幅加快了这一进程，以至于"
        "一个早期的非官方多人模式已经跑了起来。Rockstar 推迟 PC 版发行的商业模式正面临压力。",
    ),
    (
        "A World Model to Predict What You’ll Look at Next",
        "一个能预测你接下来看哪里的世界模型",
        "使用老旧的基于自动编码器的 FaceSwap 程序（或更流行的 DeepFaceLab，它也有完全相同的问题）"
        "时，最令人头疼的一点，就是想让一个人要么看向镜头、要么不看向镜头：如果训练数据里没有足够的"
        "「眼神接触」——也就是面对镜头的样本，那么用它训练出的模型就根本没有数据来生成那条视线，"
        "因为模型把仅有的几个面对镜头的样本当成了训练数据中的异常值而剔除。",
    ),
    (
        "SAP Could Cut at Least 10,000 Jobs in Reported AI Overhaul",
        "据报道 SAP 或在 AI 重组中裁员至少 1 万人",
        "彭博社 2026 年 11 月 26 日援引知情人士报道，SAP 正准备一项计划，在其为适应 AI 而重塑软件"
        "业务的过程中裁减至少 1 万个岗位；该报道由 CNBC 于 2026 年 11 月 27 日转载。SAP 告诉 CNBC，"
        "AI 正在迅速改变其商业环境，促使公司不断审视组织与员工队伍需要如何演进，岗位与职能将在此次"
        "转型中发生变化。",
    ),
    (
        "Jensen Huang returns, but controversies keep growing around Nvidia",
        "黄仁勋回归，但围绕英伟达的争议持续升温",
        "黄仁勋回来了，但并非所有人都乐见其成。英伟达董事会周一撤销了这位前任兼现任 CEO 的辞职，"
        "显然是在知名商业天才、即将卸任总统的唐纳德·特朗普施压之下——他担心没有黄仁勋掌舵，股市"
        "与 AI 交易将受到冲击。",
    ),
]


def main():
    for en, zh_title, zh_summary in FIXES:
        for path, val in ((T_JSON, zh_title), (S_JSON, zh_summary)):
            with open(path, "r", encoding="utf-8") as f:
                d = json.load(f)
            if d.get(en) != val:
                d[en] = val
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(d, f, ensure_ascii=False, indent=2)
                print("[fix_0000] 已更新覆盖表:", os.path.basename(path), "|", en[:50])

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    hit = 0
    for it in data.get("items", []):
        for en, zh_title, zh_summary in FIXES:
            if it.get("title") == en:
                it["title_zh"] = zh_title
                it["summary_zh"] = zh_summary
                it["translated"] = True
                hit += 1
                print("[fix_0000] 已回写:", en[:60])
    if hit:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("[fix_0000] 已回写 news.json，命中条目:", hit)
    else:
        print("[fix_0000] 未命中条目，未改动数据")


if __name__ == "__main__":
    main()
