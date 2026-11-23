# -*- coding: utf-8 -*-
"""2026-11-24 07:00 例行巡检：定稿本轮新增 7 条 NLLB 机翻硬伤。

07:00 整点调度（进程 07:00:39 启动后首轮）新增 7 条，均含明显硬伤：
1) The Verge「throw another wrench into」误作「将另一个关键带入」；
2) OpenAI「introduce Shirudo」误作「介绍了」，runtime 误作「运行时间」；
3) TechCrunch「Supertake」误音译为「超级投资」（公司名应保留）；
4) TechCrunch「Claude Ship」摘要「bottleneck」截断为「瓶」；
5) The Verge「elite impunity」误作「精英无处罚」、「Jensen Huang」未译、
   「strong-arming」误作「强烈武装」、「tech overlords」误作「科技主管」；
6) SiliconANGLE「Matters.AI」摘要误作「由于它…」句式崩坏；
7) The Verge「risky comeback」误作「风险性的回归」，摘要「中国间的外遇」
   不慎改为「中国间谍的外遇」需回归原文含义，「end up on his feet」误作「站起来」。

覆盖三层：news.json 回填 + JSON 覆盖表 + 代码层 manual_overrides.py（regen）。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

FIX = {
    "AI data centers throw another wrench into chaotic UN climate talks": (
        "AI 数据中心给混乱的联合国气候谈判再添变数",
        "11 月 20 日，在土耳其安塔利亚举行的联合国气候变化大会 COP31 最后一天，人们在全体会议场外抗议。摄影：Getty Images。清洁能源革命有赖于让整个全球经济实现电气化，而耗电巨大的数据中心却在迅猛扩张。这正是来自世界各地的代表在 COP31 气候大会上必须应对的难题——这场大会于周日在安塔利亚混乱且不尽如人意地落幕。每年，与会者都试图兑现 2015 年《巴黎气候协定》中遏制气候变化的承诺。要防止极端天气愈演愈烈、沿海社区遭洪水侵袭、干旱破坏粮食与供水系统，就必须大幅削减温室气体排放。",
    ),
    "OpenAI and Cisco introduce Shirudo": (
        "OpenAI 与思科推出 Shirudo",
        "OpenAI 与思科推出 Shirudo——一款面向 Linux 的开源运行时。它帮助团队在滚动部署补丁的过程中保护正在运行的系统。",
    ),
    "Supertake raises $20M to let AI agents turn your market predictions into stock portfolios": (
        "Supertake 融资 2000 万美元，让 AI 智能体把市场预测变成股票投资组合",
        "觉得自己知道市场走向？初创公司 Supertake 让你为自己的想法下注，而不必自己挑选股票。",
    ),
    "Anthropic launches Claude Ship, letting AI agents review, fix, and approve code changes": (
        "Anthropic 推出 Claude Ship，让 AI 智能体审查、修复并批准代码变更",
        "随着 AI 生成的代码不断堆积，Anthropic 的新开发工具旨在让智能体处理常规审批，从而消除另一个瓶颈。",
    ),
    "Welcome to elite impunity, Jensen Huang": (
        "欢迎来到精英免责的世界，黄仁勋",
        "「大而不能倒」续集。图片：The Verge；Getty Images。我想我得向黄仁勋致以热烈祝贺。黄仁勋再次出任英伟达 CEO，这让除唐纳德·特朗普总统和 J.D.万斯副总统（正是他们促成了此事）之外的所有人几乎都感到意外。现在，我们这些对「自由市场」有些基本认知的人，或许会觉得美国总统对一家美国大公司施压令人反感。但我们的亿万富翁科技大佬们对「自由市场」的在意程度，与他们对「言论自由」的在意程度一样——也就是说，根本不在乎。",
    ),
    "Matters.AI raises $12M as it expands its data security business in North America": (
        "Matters.AI 融资 1200 万美元，在北美扩展数据安全业务",
        "企业数据安全初创公司 Matters.AI 今日宣布，随着在北美拓展业务，公司获得 1200 万美元新融资。Matters.AI 提供一个名为「AI Security Engineer for Data」的平台，旨在保护全企业范围内员工、AI 系统与 AI 智能体使用的敏感数据。",
    ),
    "Trump engineered a risky comeback for Jensen Huang": (
        "特朗普为黄仁勋策划了一场高风险的回归",
        "在英伟达董事会接受黄仁勋辞去 CEO 一职后——此前有报道称黄仁勋与一名疑似中国间谍有染——唐纳德·特朗普总统似乎也接受了这一新现实。消息传出后不久，特朗普现身斯蒂芬·A·史密斯的广播节目，称黄仁勋「最终会重新站起来」。特朗普说：「你知道那句话，谁都可以被取代。」他还抛出苹果前 CEO 蒂姆·库克作为潜在 CEO 人选。特朗普没过多久便开始软化立场，明确表示即便英伟达董事会尚未准备好，他也乐见黄仁勋重返 CEO 岗位。",
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

    print("[fix_0700_1124] news.json 回填 %d 条；标题定稿 %d / 摘要定稿 %d" %
          (changed, added_t, added_s))
    print("[fix_0700_1124] 覆盖表 %d / %d 条" % (len(titles), len(summaries)))
    return 0 if changed == len(FIX) else 1


if __name__ == "__main__":
    raise SystemExit(main())
