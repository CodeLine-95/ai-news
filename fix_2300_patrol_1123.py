# -*- coding: utf-8 -*-
"""2026-11-23 23:00 例行巡检：定稿本轮新增 12 条 NLLB 机翻硬伤。

主要问题：
1) The Verge / Ars Technica：黄仁勋复职新闻摘要引号错乱、人名「华安」误译、
   语序破碎（「先生。「这种保证不构成国家安全的风险「。」）。
2) Unite.AI Amazon/Decart：「优化堆」应为「优化栈」（Optimization Stack）。
3) The Decoder：「试过生活」不通顺（应为「试过没有…的日子」）。
4) Wired：direct report 误作「直接报告」（应为「直属下属」）、「恢复了黄职位」残缺。
5) Unite.AI Reasoning：idioms 误作「语句」（应为「习语」）、present subjunctive
   误作「当前子词」（应为「现在虚拟式」）、「丹麦的语说」残缺。
6) InfoQ AI：Data Mapper 误作「数据地图图器」、typed builders 误作「打字构建器」；
   原标题自身重复截断，按正文语义修正。
7) Unite.AI Trump：9:07 a.m. ET 误作「以天为时 9 点 07 分」、Truth Social 误作
   「真相社会」。
8) Unite.AI Workday：品牌名 Workday 被误译为「工作日」（标题+摘要多处）。
9) Unite.AI Five-Person Studio：typed every line 误作「打字每一行」、ship 误作「运输」。

覆盖三层：news.json 回填 + JSON 覆盖表（regen 时复用）。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

# 用稳定的 id 定位回填，覆盖表 key 使用数据中的真实英文标题
FIX = {
    "9d21fd7b5be3f1eea24e59965a6139a1": (
        "黄仁勋回归，再度出任英伟达 CEO",
        "英伟达已重新任命黄仁勋为公司 CEO。公司周一上午宣布，董事会「在与黄先生进行了一系列讨论和会面后，一致投票决定让其复职，此后董事会对黄先生的坦诚及其领导英伟达的能力表示认可」。董事会在声明中称，其听取了「来自美国政府高层的意见」，并判定「黄仁勋的复职不构成国家安全风险」。",
    ),
    "5514faa02204cf0137dd67a394f268f7": (
        "黄仁勋复职英伟达 CEO 兼董事会主席",
        "英伟达董事会已投票决定重新任命黄仁勋为 CEO 兼董事会主席，距其在一系列丑闻后辞职仅 11 天。周一上午宣布的复职「立即生效」，其依据部分来自「美国政府高层的意见」——该意见向董事们保证「黄先生的复职不构成国家安全风险」。尽管黄仁勋已承认与一名被美国情报部门认为是中国间谍的女子有染，且英伟达被指控规避旨在阻止其芯片流入中国的出口管制，这一保证仍得以作出。此外，多个政府部门仍在对上述及其他涉嫌国家安全、会计与公司治理失当的问题展开调查。",
    ),
    "251eb8352b7fae175006a9f0f2dbb0b8": (
        "旧闻若成假新闻，危害更大",
        "虽然互联网档案馆的庞大规模使这一理论难以证实，但我认为，archive.org 以及其他允许用户随意上传「档案」PDF、监管极少或时有时无的网站，将在未来几年日益成为制造「高权威」假新闻的攻击载体。原因就在于，archive...（原文至此截断）",
    ),
    "db862b8d44025dfafa313af63b0f9b45": (
        "亚马逊签约收购 Decart 的 AI 优化技术并引进其团队",
        "亚马逊于 2026 年 11 月 23 日宣布，已签署协议，拟收购 Decart Optimization Stack 背后的专有技术，并将这家 AI 初创公司的三位联合创始人及其 AI 研究员与工程师团队纳入麾下。该协议涵盖 DOS（Decart Optimization Stack）技术，以及计划招揽联合创始人 Dean Leitersdorf、Moshe Shalev 和 Orian Leitersdorf 及其团队。",
    ),
    "1d1e4778672a6f3a35c1a8b02ba86282": (
        "英伟达试过没有黄仁勋的日子，只撑了约两周",
        "英伟达董事会已投票决定重新任命黄仁勋为总裁、CEO 兼董事，立即生效。",
    ),
    "87d5fd7edaca0a3ff6325cd8e25fd5ee": (
        "黄仁勋回归，再任英伟达 CEO",
        "在该 CEO 因涉嫌多段婚外情（包括与一名直属下属的关系）辞职一周多后，公司董事会已让其复职。",
    ),
    "ecad73e7ee9448ee1445aa1e3b8672f6": (
        "推理无法弥补模型从未读过的知识",
        "我测试过的最佳模型，在 30 种语言的语法与日历运算上拿到 90 分，但在习语上只有 48 分。思考时长解释了前一个数字，却无法改变后一个。让顶级 AI 模型把一个古意大利语动词变成现在虚拟式、且两个宾语都用代词，它大概率能做对；但问它一句「慢工出细活、装备简陋者终达目的」的丹麦谚语，我测试的 17 个模型里有 16 个会答不出来。",
    ),
    "157ef0121d5a8949c6c7da21ec61e8bf": (
        "Agoda 借助模块化架构将 API 代码评审时间缩短 64%",
        "Agoda 在其预订后 API 中引入模块化单体框架，在不做彻底重写的前提下降低耦合。该平台采用领域组件、Data Mapper（数据映射器）模式、类型化构建器，并用 ArchUnit 测试来强化边界。与旧有改动相比，采用该框架的改动中位评审时长缩短 64%，首次反馈速度提升 34%。",
    ),
    "49519376c52bf2f5995f36d159dee251": (
        "特朗普支持英伟达重新任命黄仁勋为 CEO",
        "唐纳德·特朗普总统于 2026 年 11 月 23 日美国东部时间上午 9:07 在 Truth Social 上表示，英伟达恢复黄仁勋 CEO 职位是「正确且恰当的决定」，并称美国司法部长已确认政府没有掌握黄仁勋违法行为的证据。特朗普说，美国政府没有理由认为黄仁勋回归会带来国家安全风险。",
    ),
    "5c6d30e3f95ad64045aa8014ca4ccd2f": (
        "五人工作室在智能体开始写代码后学到的经验",
        "我在瑞士卢加诺经营一家五人 AI 工作室。我们为中小企业开发软件，同时维护多款自有产品。若仍要亲手敲下每一行代码，我们根本无法承受这样的工作量。如今，编码智能体已写下了我们交付产品的绝大部分初版代码。本文讲述这一变化在实践中的体现：我们白天做什么、哪里会出错，以及我为何不再以「小时」作为工作计量单位。",
    ),
    "15da0cbca7e4582eeaebd7005195bcfa": (
        "客户需求激增，Sierra 半年内估值翻倍至 300 亿美元",
        "由前 Salesforce 联席 CEO Bret Taylor 联合创立的企业客户体验公司 Sierra 周一表示，已完成 17.5 亿美元 F 轮融资。",
    ),
    "ef0a58e4e71d95031f9ca42013cf6ede": (
        "Workday 完成收购 C1.ai，统一管理员工与 AI 智能体的访问权限",
        "Workday 于 2026 年 11 月 23 日宣布完成对 C1.ai 的收购，将面向员工与 AI 智能体的身份治理软件纳入其 HR、财务及 IT 平台。该交易旨在把 Workday 的员工记录扩展为一层安全能力，管控人员与智能体在业务应用和云基础设施中可访问的资源。Workday 计划将其员工数据与 C1.ai 的身份控制能力结合，简化访问管理并减少人工流程。这套系统可管理权限、监控活动，并为人类员工与自主智能体实施策略驱动的安全控制。",
    ),
}


def main():
    db = json.load(open(DATA, encoding="utf-8"))
    items = db["items"] if isinstance(db, dict) else db
    titles = json.load(open(T_JSON, encoding="utf-8"))
    summaries = json.load(open(S_JSON, encoding="utf-8"))

    changed = added_t = added_s = 0
    for it in items:
        iid = it.get("id")
        if iid not in FIX:
            continue
        title_zh, summary_zh = FIX[iid]
        en = (it.get("title") or "").strip()
        it["title_zh"] = title_zh
        it["summary_zh"] = summary_zh
        it["translated"] = True
        it["method"] = "nllb+manual"
        changed += 1
        print("fixed:", it.get("date"), it.get("time"), en[:60])
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

    print("[fix_2300_1123] news.json 回填 %d 条；标题定稿 %d / 摘要定稿 %d" %
          (changed, added_t, added_s))
    print("[fix_2300_1123] 覆盖表 %d / %d 条" % (len(titles), len(summaries)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
