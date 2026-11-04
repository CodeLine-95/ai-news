# -*- coding: utf-8 -*-
"""2026-11-03 14:00 巡检（第二批）：修复 14:02 新增条目的译文缺陷。

条目：Unite.AI《OpenAI Plans New Security Sprint and Raises Bug Bounty
Rewards》（14:02）

缺陷 a：「大教堂的研究人员」——原文 "Cathedral researchers"，
       指安全公司 Cathedral Systems，模型把公司名意译成「大教堂」，
       中文读者会当成一个虚构的教堂机构。
       根因修复：translate.py 既有规则只覆盖「大教堂系统」，
                 原文只写 "Cathedral" 时匹配不到。
       修复：新增「Cathedral」品牌还原规则。
缺陷 b：「提高了奖励和引入了奖励」——同义重复，机器味极重。
       根因修复：新增 TERM_FIXES 规则。
缺陷 c：「特殊的关键付款」——critical payouts（严重漏洞赏金支付）
       被译成金融术语「关键付款」。
       根因修复：新增 TERM_FIXES 规则。

处理：重译 + 人工定稿标题与摘要，写入覆盖表。
"""
import json
import os

import translate

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

TITLE = "OpenAI Plans New Security Sprint and Raises Bug Bounty Rewards"

TITLE_FIX = {
    TITLE:
        "OpenAI 筹备新一轮安全冲刺，并提高漏洞赏金奖励",
}

SUMMARY_FIX = {
    TITLE:
        "2026 年 11 月 2 日，OpenAI 宣布正与 Cathedral Systems 及其他外部"
        "研究人员筹备又一轮内部安全冲刺；同日发布的一次漏洞赏金更新提高了"
        "奖励额度并新增专项奖金，特别严重的漏洞赏金最高可提升至 17.2 万"
        "美元。Cathedral 的研究人员将与 OpenAI 内部团队一道使用 OpenAI 的"
        "模型挑战其防御体系、寻找弱点。该公告涉及的是计划中的冲刺，"
        "而非已完成的一轮测试。",
}


def main():
    with open(DATA, "r", encoding="utf-8") as f:
        data = json.load(f)
    items = data.get("items", [])

    targets = [it for it in items if it.get("title") == TITLE]
    if not targets:
        print("[fix_1400b_1103] 未找到目标条目")
        return 1

    zh_titles, _ = translate.translate_list([it["title"] for it in targets],
                                            beams=2)
    zh_sums, _ = translate.translate_list_chunked(
        [it.get("summary") or "" for it in targets], beams=3)
    for it, zt, zs in zip(targets, zh_titles, zh_sums):
        it["title_zh"] = zt
        it["summary_zh"] = zs
        it["translated"] = True
        it["method"] = "nllb"
        print("[重译] -> %s" % zt)
        print("       %s" % zs[:250])

    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    with open(T_JSON, "r", encoding="utf-8") as f:
        to = json.load(f)
    with open(S_JSON, "r", encoding="utf-8") as f:
        so = json.load(f)
    to.update(TITLE_FIX)
    so.update(SUMMARY_FIX)
    with open(T_JSON, "w", encoding="utf-8") as f:
        json.dump(to, f, ensure_ascii=False, indent=2)
    with open(S_JSON, "w", encoding="utf-8") as f:
        json.dump(so, f, ensure_ascii=False, indent=2)

    print("[fix_1400b_1103] 覆盖表 标题 %d 条 / 摘要 %d 条" % (len(to), len(so)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
