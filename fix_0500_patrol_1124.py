# -*- coding: utf-8 -*-
"""2026-11-24 05:00 例行巡检：定稿本轮新增 5 条 NLLB 机翻硬伤。

05:00 整点调度抓取到 5 条新条目（净增 4 条，滚出 1 条 10-24 过期数据），
均为纯 nllb 机翻，主要问题：
1) The Verge「Jensen Huang / Nvidia」未统一译名（应为黄仁勋/英伟达），
   「不忠妻子」语法崩坏、「涉嫌的事件」生硬；
2) The Verge Claude Ship：ship code 误作「运输代码」、Claude Ship 误作
   「Claude 船」、PR Steward 误作「PR 管理员」、标题「发送修复问题」不通顺；
3) InfoQ QCon：「确保生产中的 AI 智能体」缺宾语、代词 they 误译为「他们」；
4) TechCrunch：标题「迎接黄仁勋作为一个英雄」严重欧化句式；
5) The Decoder：摘要首句（GPT-6.2 Sol 设为新默认模型、全球推出）整句漏译，
   「指示」应为「指令」。

覆盖三层：news.json 回填 + JSON 覆盖表 + （随后 regen）代码层 manual_overrides.py。
以英文原标题为 key 匹配，避免 id 手工录入偏差。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

FIX = {
    "How Jensen Huang ended up as Nvidia CEO again": (
        "黄仁勋如何再度出任英伟达 CEO",
        "本月，英伟达的黄仁勋时代几乎画上句号。三十年前，黄仁勋联合创立了如今被视为 AI 领域最重要的公司之一，但因涉嫌相关事件面临日益加剧的审视，他于 11 月 12 日辞去 CEO 职务。黄仁勋承认自己对妻子「不忠」，并「给董事会制造了麻烦」。此前数周，他个人与职业上的问题不断升级：先是《纽约时报》报道称，他与一名向中国传递情报的女性关系密切。",
    ),
    "Claude AI can review pull requests and ship fixes on its own now": (
        "Claude AI 现可自行审查拉取请求并推送修复",
        "Anthropic 推出多项新的 Claude AI 功能，帮助软件工程师交付代码。在今日发布的新产品 Claude Ship 中，Claude 现可审查、修复并批准拉取请求（PR）。工程师此前已能借助代码审查功能利用 Claude 的审查能力——该功能于今年 3 月推出、10 月全面开放。此次随 Claude Ship 一同推出的还有 PR Steward 与 Claude Approvals 两个智能体，今日启动测试。",
    ),
    "QCon San Francisco 2026: Securing AI Agents in Production": (
        "旧金山 QCon 2026：保障生产环境中的 AI 智能体安全",
        "在旧金山 QCon 大会上，Google 的阿曼达·沃克（Amanda Walker）将 AI 智能体界定为以机器速度运行的内部风险问题，并介绍了身份、凭证与隔离等模式，以确保其在生产环境中安全运行。",
    ),
    "Nvidia employees greet Jensen Huang like a hero as he returns to company’s HQ": (
        "黄仁勋重返英伟达总部，员工如迎英雄",
        "黄仁勋对员工表示：「第二次当 CEO，我会做得更好。」",
    ),
    "OpenAI updates ChatGPT to handle complex everyday questions, web searches, and images more reliably": (
        "OpenAI 更新 ChatGPT，更可靠地处理复杂日常问题、网络搜索与图像",
        "OpenAI 将 GPT-6.2 Sol 设为 ChatGPT 聊天标签页的新默认模型，并在全球范围推出。内部测试显示，图像理解能力从 47.4% 跃升至 71.7%，该模型现在能正确处理 78.1% 的复杂指令，也更稳定地遵守安全政策。",
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

    print("[fix_0500_1124] news.json 回填 %d 条；标题定稿 %d / 摘要定稿 %d" %
          (changed, added_t, added_s))
    print("[fix_0500_1124] 覆盖表 %d / %d 条" % (len(titles), len(summaries)))
    return 0 if changed == len(FIX) else 1


if __name__ == "__main__":
    raise SystemExit(main())
