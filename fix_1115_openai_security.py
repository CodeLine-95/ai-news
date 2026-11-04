# -*- coding: utf-8 -*-
"""2026-11-03 11:15 巡检：定向人工定稿 OpenAI 两条安全公告。

11:00 后服务重启触发的补抓新增 2 条（344 → 346），均为 OpenAI 官方博客
的安全公告。自动译文存在整句直译问题：

条目 1 —— "Rewarding defenders with bigger bug bounties"（02:00）
  标题：「奖励更大的 bug 奖励的捍卫者」
  问题："bigger bug bounties"（更高额的漏洞赏金）被逐词直译成
        「更大的 bug 奖励」，"rewarding defenders" 又译成「奖励…的捍卫者」，
        叠加后变成「奖励更大的 bug 奖励的捍卫者」——"bug 奖励"这种
        自指表述在中文里根本不成词。业界标准译法是「漏洞赏金」。
  摘要问题：
    a) "Security Bug Bounty"（安全漏洞赏金）被拆成「安全 Bug Bounty」，
       中英混排且丢掉了"漏洞"这层含义；
    b) "campaign bonuses"（专项活动奖金）→「优先活动奖励」，
       "priority"（优先）与 "campaign"（专项活动）被拆错位；
    c) "报告质量，忠诚度和优先活动奖励"三个并列项用半角逗号分隔，
       与站内全角标点风格不一致。

条目 2 —— "Preparing our next security sprint to harden OpenAI"（02:00）
  标题：「准备我们的下一次安全冲刺，以加强 OpenAI」
  问题：中文主语冗余（"我们的"），且"以加强 OpenAI"没说清加强什么——
        harden 在安全语境下是「加固」，加强的对象是 OpenAI 的防御体系。
  摘要问题：
    a) "Cathedral Systems" 是合作安全公司名，被译成「大教堂系统」，
       中文读者完全无法识别是哪家公司，必须保留英文原名；
    b) "its defenses"（其防御体系）被译成「其防御」，漏掉了"体系"这层含义。

处理顺序与 server.py 的调度周期完全一致：
    人工定稿 → 术语确定性重清洗 → 应用人工标题覆盖 → 应用人工摘要覆盖
    → 重新生成报告

用法：
    python3.11 fix_1115_openai_security.py
"""
import json
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
sys.path.insert(0, BASE)

import server  # noqa: E402  复用 server 的清洗/覆盖函数，保证顺序一致

TITLE_FIX = {
    # "bigger bug bounties" → 更高额的漏洞赏金；
    # "defenders" 指提交漏洞的防御者（安全研究员），译「贡献者」更准确。
    "Rewarding defenders with bigger bug bounties":
        "以更高额的漏洞赏金奖励安全贡献者",
    # harden OpenAI = 加固 OpenAI 的防御体系，去掉冗余的"我们的"。
    "Preparing our next security sprint to harden OpenAI":
        "筹备下一轮安全冲刺，加固 OpenAI 防御体系",
}

SUMMARY_FIX = {
    "Rewarding defenders with bigger bug bounties":
        (
            "OpenAI 正在提高安全漏洞赏金（bug bounty）的奖励额度，并为独立安全研究人员"
            "推出报告质量、忠诚度与优先响应三项专项活动奖金。"
        ),
    "Preparing our next security sprint to harden OpenAI":
        (
            "OpenAI 正与 Cathedral Systems 筹备下一轮内部安全冲刺，将借助 AI 对其防御"
            "体系进行测试与加固。"
        ),
}


def main():
    with open(os.path.join(DATA, "news.json"), encoding="utf-8") as f:
        db = json.load(f)
    items = db["items"] if isinstance(db, dict) else db

    hit_t = hit_s = 0
    for it in items:
        t = it.get("title", "")
        if t in TITLE_FIX:
            it["title_zh"] = TITLE_FIX[t]
            it["translated"] = True
            it["method"] = "nllb+manual"
            hit_t += 1
            print("fix title:", it["date"], it["time"], it["source"], "|", t[:45])
        if t in SUMMARY_FIX:
            it["summary_zh"] = SUMMARY_FIX[t]
            it["translated"] = True
            it["method"] = "nllb+manual"
            hit_s += 1
            print("fix summary:", it["date"], it["time"], it["source"], "|", t[:45])

    # 与 server.py 调度周期一致的顺序
    server.apply_term_cleanup(items)
    server.apply_title_overrides(items)
    server.apply_summary_overrides(items)

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

    print("fixed titles:", hit_t, "/", len(TITLE_FIX))
    print("fixed summaries:", hit_s, "/", len(SUMMARY_FIX))
    if hit_t != len(TITLE_FIX) or hit_s != len(SUMMARY_FIX):
        raise SystemExit("覆盖未全部命中，请检查英文原标题是否一致")

    import report
    report.main()


if __name__ == "__main__":
    main()
