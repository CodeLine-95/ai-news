# -*- coding: utf-8 -*-
"""2026-11-03 01:00 例行巡检修复（本轮新增 5 条，全部人工定稿）。

NLLB 直译缺陷集中在以下几类：
1. Putin Orders → 「普京订单」：Orders 是动词「下令」，不是名词「订单」；
   covered non-government data-center owners → 「覆盖的非政府组织数据中心所有者」，
   把定语误挂到「组织」上，译法错误；
   reserve（预留配额）→「预订」，语义完全跑偏。
2. Perplexity → 「困惑性」：品牌名被当普通名词直译，
   且 Perplexity Computer → 「Perplexity 计算机」、Brain → 「脑」均为机翻口吻；
   "tests for whether stored context improves an agent's later work"
   → 「测试是否存储的环境可以改善」：context（上下文）被译成「环境」。
3. 42AI comes out of stealth → 「从隐形中出现了」：stealth mode 固定译法为「隐身」，
   comes out of stealth 是「走出隐身模式/正式亮相」；
   $62.5M → 「6250 万美元」应写「6,250 万美元」。
4. throttles → 「推迟」：throttle 在此意为「收紧/限制额度」，
   与「推迟」是完全不同的动作。
5. AI Audit Employees → 「AI 审计员工」：这里 employees 是产品名（AI 员工），
   不应拆成「AI 审计员工」；Touring Capital → 保留原名，
   Marathon Management Partners → 直译「马拉松管理合作伙伴」属品牌误译。
6. Ali Hayat → 「阿里哈伊特」：人名保留原拼写更自然，
   且原译「艾克西普罗」把 Axipro 拆成两截。

同时补齐摘要过短条目（42AI / Grok Bot）的事实信息。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

TITLE_FIX = {
    "Putin Orders 10% Data Center Reserve for Russian Information Resources":
        "普京下令：数据中心须为俄语信息资源预留 10% 容量",
    "Ali Hayat, CEO and Founder of Axipro – Interview Series":
        "Axipro 创始人兼 CEO Ali Hayat 专访",
    "42AI comes out of stealth with $62.5M and a world model that can ‘predict human behavior’":
        "42AI 走出隐身模式，获 6,250 万美元融资，发布可「预测人类行为」的世界模型",
    "Elon Musk throttles Grok Bot limits due to ‘unsustainably high’ costs":
        "马斯克因成本「高得难以持续」收紧 Grok Bot 使用额度",
    "Clark Raises $11M Seed to Bring AI Audit Employees to More CPA Firms":
        "Clark 获 1,100 万美元种子轮融资，把 AI 审计员工带进更多会计师事务所",
    "Perplexity Details Brain Memory Architecture and Agent API Testing":
        "Perplexity 详解 Brain 记忆架构与 Agent API 测试",
}

SUMMARY_FIX = {
    "Putin Orders 10% Data Center Reserve for Russian Information Resources":
        "据克里姆林宫公告，俄罗斯总统普京于 2026 年 11 月 2 日签署法令，"
        "要求俄罗斯境内受管辖的非政府数据中心所有者，将现有楼层空间和算力容量的 "
        "10% 预留给俄语信息资源。这些所有者在法令生效后最多有 10 天完成预留。",
    "Ali Hayat, CEO and Founder of Axipro – Interview Series":
        "Ali Hayat 是 Axipro 的创始人兼 CEO，其背景兼具工业风险管理与 ISO 审计经验，"
        "以及网络安全与合规咨询经历。他早期在高风险的工业环境中工作，"
        "安全、监管要求与运营风险是核心关切；后来在没有外部投资的情况下创办 Axipro，"
        "专注于帮助成长型企业采用可落地的安全控制措施、准备审计并管理新出现的 AI 风险。",
    "42AI comes out of stealth with $62.5M and a world model that can ‘predict human behavior’":
        "42AI 走出隐身模式，宣布获得 6,250 万美元融资，并发布一款世界模型——"
        "据称能够「预测人类行为」。这项技术的设想直接来自科幻："
        "如果 AI 能在你做出决定之前就预测出你要做什么，"
        "即便面对的是一种全新的处境，它是否仍然成立。",
    "Elon Musk throttles Grok Bot limits due to ‘unsustainably high’ costs":
        "马斯克表示，Grok Bot 是「我这辈子见过增长最快的产品」，"
        "但由于成本「高得难以持续」，他收紧了该产品的使用额度限制。",
    "Clark Raises $11M Seed to Bring AI Audit Employees to More CPA Firms":
        "Clark 推出了 Clerks——一家主打会计师事务所审计业务的「AI 员工」公司，"
        "并于 2026 年 11 月 2 日宣布完成 1,100 万美元种子轮融资。"
        "本轮由 Touring Capital 领投，回投方包括 Marathon Management Partners、"
        "Rerail 与 Sofeon Ventures。Clark 在通过 PR Newswire 发布的声明中表示，"
        "加上 2025 年 9 月由 Marathon Management Partners 领投的 500 万美元融资，"
        "其累计融资额已达 1,600 万美元。",
    "Perplexity Details Brain Memory Architecture and Agent API Testing":
        "Perplexity 于 2026 年 11 月 2 日发布了一份关于持久化 AI 智能体记忆的技术指南，"
        "详解了 Perplexity Computer 中的 Brain 系统、Agent API 的记忆构建组件，"
        "并给出测试方案，用以验证存储的上下文是否能改善智能体后续的工作表现。"
        "Perplexity 称 Brain 是为 Computer 打造的自我改进型记忆系统，"
        "可将过往工作与修正整理成一份持续演进的知识维基。",
}


def main():
    with open(os.path.join(DATA, "news.json"), encoding="utf-8") as f:
        db = json.load(f)
    items = db["items"] if isinstance(db, dict) else db

    hit = 0
    for it in items:
        t = it.get("title", "")
        if t in TITLE_FIX:
            it["title_zh"] = TITLE_FIX[t]
            it["translated"] = True
            it["method"] = "nllb+manual"
            hit += 1
            print("fixed:", it["date"], it["time"], it["source"], "|", t[:50])
        if t in SUMMARY_FIX:
            it["summary_zh"] = SUMMARY_FIX[t]
            it["translated"] = True
            it["method"] = "nllb+manual"

    with open(os.path.join(DATA, "news.json"), "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    for name, fix in (("titles_override.json", TITLE_FIX),
                      ("summaries_override.json", SUMMARY_FIX)):
        path = os.path.join(DATA, name)
        cur = {}
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                cur = json.load(f)
        cur.update(fix)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cur, f, ensure_ascii=False, indent=2)

    print("fixed items:", hit, "/ expected", len(TITLE_FIX))


if __name__ == "__main__":
    main()
