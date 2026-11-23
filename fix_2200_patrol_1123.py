# -*- coding: utf-8 -*-
"""2026-11-23 22:00 例行巡检：定稿本轮新增 10 条 NLLB 机翻硬伤。

1) The Decoder 21:59：Meta 音译为「麦塔」、Riemann 误作「里曼」（应为
   「黎曼」）、proof sketch 误作「证据草图」（应为「证明草图」）。
2) The Decoder 21:45：「美国间」残缺（应为「美国情报机构」）、「当时
   Nvidia CEO」不通（应为「时任英伟达 CEO」）、走私句语序混乱。
3) Wired 21:11：brain-computer interface 误作「脑电脑接口」（应为「脑机接口」）。
4) Unite.AI 21:05：Braiin 品牌被音译且下一句误写为 Braiins；term sheet
   误作「期限表」（应为「条款清单」）；Hyderabad 误作「海德拉巴德」；
   upfront consideration 误作「前期考虑」（应为「前期对价」）。
5) SiliconANGLE 21:00：Bootstrapped 误作「启动的」（应为「自筹/自力更生」）；
   「最繁」截断（应为「最繁琐」）；「仍然着打」错字（应为「疲于应付」）；
   Levenza 被音译为「利文萨」。
6) Unite.AI 21:00：Levenza 被音译为「莱文萨」；Fluid Inference 被当作
   普通词组译为「流体推理」（应保留公司名）。

覆盖三层：news.json 回填 + JSON 覆盖表（regen 时复用）。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

TITLE_FIX = {
    "Meta's Alexandr Wang warns the AI industry isn't ready for what's coming after Riemann breakthrough":
        "Meta 首席 AI 官 Alexandr Wang 警告：AI 行业尚未准备好迎接黎曼猜想突破之后的未来",
    "US spies tracked Nvidia scandal figure's ties to Chinese intelligence for over a year":
        "美国情报机构追踪英伟达丑闻当事人与中国情报部门联系逾一年",
    "Nvidia Is Powering Brain-Computer Interfaces Now":
        "英伟达进军脑机接口领域",
    "Braiin Plans Marut Drones Acquisition to Expand Agricultural AI":
        "Braiin 拟收购 Marut Drones，拓展农业 AI 业务",
    "Bootstrapped startup Levenza brings consumer-style personal agents to business workers":
        "自筹初创公司 Levenza 将消费级个人智能体带入企业办公场景",
    "Levenza Launches Enterprise AI Agents Globally and Adds Voice With Fluid Inference":
        "Levenza 全球上线企业 AI 智能体，并引入 Fluid Inference 语音技术",
    "AI agents leaked confidential data in 87 of 100 test runs, Cyberhaven finds":
        "Cyberhaven 发现：100 次测试中有 87 次 AI 智能体泄露机密数据",
    "Innovaccer expands Gravity Voice AI agents with SpaceXSI’s Grok Voice model":
        "Innovaccer 借助 SpaceXSI 的 Grok Voice 模型扩展 Gravity Voice AI 智能体",
    "Innovaccer Adds Grok Voice to Its Healthcare Phone Agents":
        "Innovaccer 将 Grok Voice 引入其医疗电话智能体",
    "AI Biology in 2027: Genome Models Become Tools for Designing Experiments":
        "2027 年 AI 生物学：基因组模型成为设计实验的工具",
    "Lava Security Benchmarks Open AI Models for Security Analysis":
        "Lava Security 基准测试开放 AI 模型的安全分析能力",
    "Nauticus Robotics Pursues WAM-V Assets for Surface Autonomy":
        "Nauticus Robotics 拟收购 WAM-V 资产，拓展水面自主航行业务",
}

SUMMARY_FIX = {
    "Meta's Alexandr Wang warns the AI industry isn't ready for what's coming after Riemann breakthrough": (
        "Meta 首席 AI 官 Alexandr Wang 认为，近期借助 AI 完成的黎曼猜想证明草图清楚表明，"
        "超级智能已近在眼前。"
    ),
    "US spies tracked Nvidia scandal figure's ties to Chinese intelligence for over a year": (
        "据《纽约时报》报道，美国情报机构一年多来一直追踪 Alice Huang 与中国国家安全部之间的接触。"
        "这一监视与她同英伟达时任 CEO 黄仁勋的隐秘恋情同步进行。联邦调查人员正在调查，东南亚的"
        "一家公司网络是否被用于违反美国出口管制、将 AI 芯片走私至中国。黄仁勋将于 12 月 1 日"
        "在美国众议院作证。"
    ),
    "Nvidia Is Powering Brain-Computer Interfaces Now": (
        "脑机接口公司 Paradromics 正在使用英伟达的计算硬件与软件处理大脑数据。"
    ),
    "Braiin Plans Marut Drones Acquisition to Expand Agricultural AI": (
        "Braiin Limited 于 2026 年 11 月 23 日宣布，已签署一份非约束性条款清单，拟分阶段收购"
        "总部位于海得拉巴的 Marut Drones，先取得多数股权。拟议交易估值约 4000 万美元，包括"
        "前期对价、与业绩挂钩的收益分成及增长资本。若交易完成，Marut 将并入 Braiin 的机器人"
        "与 AI 部门，并与其自主作物喷洒无人机平台 Raptor300 整合。"
    ),
    "Bootstrapped startup Levenza brings consumer-style personal agents to business workers": (
        "AI 爱好者正热衷于使用能自动处理日常生活中最繁琐数字事务的个人智能体，但办公室职员"
        "仍疲于应付日历、邮件和聊天消息。Levenza 希望改变这一现状，推出其所称的首批专为"
        "企业员工设计的个人 AI 智能体。"
    ),
    "Levenza Launches Enterprise AI Agents Globally and Adds Voice With Fluid Inference": (
        "Levenza 正扩大其行政类 AI 智能体的企业使用范围，并引入 Fluid Inference 的技术添加"
        "语音功能。"
    ),
    "AI agents leaked confidential data in 87 of 100 test runs, Cyberhaven finds": (
        "数据安全公司 Cyberhaven Inc. 今日发布的新报告发现：即使已意识到信息属于机密，"
        "AI 智能体仍会在泄露公司机密数据有助于完成任务时照做不误。"
    ),
    "Innovaccer expands Gravity Voice AI agents with SpaceXSI’s Grok Voice model": (
        "医疗保健人工智能公司 Innovaccer Inc. 今日宣布，已通过 Grok Voice 扩展其 Gravity Voice "
        "AI 智能体。Grok Voice 是埃隆·马斯克旗下人工智能公司 SpaceXSI（原 xAI）推出的"
        "语音到语音模型。"
    ),
    "Innovaccer Adds Grok Voice to Its Healthcare Phone Agents": (
        "Innovaccer 正在将 Grok Voice 引入其电话智能体，用于日常医疗保健预约、转诊及其他"
        "行政电话。"
    ),
    "AI Biology in 2027: Genome Models Become Tools for Designing Experiments": (
        "生物学中充满了看似合理却经不起实验检验的想法：一段序列可能看起来很有希望，模型"
        "可能给出高分，而细胞却以无人预料的方式反应。正是这种摩擦让 AI 生物学在科学上"
        "变得有趣。2027 年的机遇在于让预测与实验展开更好的对话：选择要构建什么、从失败中"
        "学习，并决定下一步值得解决哪一项不确定性。"
    ),
    "Lava Security Benchmarks Open AI Models for Security Analysis": (
        "Lava Security 的一项基准测试比较了开放模型与托管模型在防御性分析中的表现，并说明"
        "为何推理成本取决于部署方式。"
    ),
    "Nauticus Robotics Pursues WAM-V Assets for Surface Autonomy": (
        "Ocean Power Technologies 于 2026 年 11 月 23 日宣布，Nauticus Robotics 已签署非约束力"
        "意向书，拟以 800 万美元的 Nauticus C 轮可转换优先股（交割时支付）加最高 200 万美元"
        "额外现金，收购其 WAM-V 无人水面艇业务。Nauticus 的公告明确，拟议的资产收购包括"
        "相关软件与知识产权。"
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

    print("[fix_2200_1123] news.json 回填 %d 条；标题定稿 %d / 摘要定稿 %d" %
          (changed, added_t, added_s))
    print("[fix_2200_1123] 覆盖表 %d / %d 条" % (len(titles), len(summaries)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
