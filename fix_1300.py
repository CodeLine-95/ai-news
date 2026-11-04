# -*- coding: utf-8 -*-
"""2026-11-03 13:00 巡检：修复本轮新增 2 条的译文缺陷。

本轮新增
--------
1) MIT Tech Review《Here's who is falling in line for Trump's "Super
   Intelligence" loyalty test》（12:18）
   缺陷：摘要首句是站点的订阅引导语
        "To get stories like this in your inbox first, sign up here ."
   译文变成「要先在收件箱里收到这样的故事，请在这里注册。」——这不是
   文章内容，读者点进原文才发现是求订阅。
   根因修复：fetcher 新增 _HEAD_CTA_PATTERNS，在抓取层剥离摘要头部的
             订阅引导语（对后续所有条目生效）。

2) Unite.AI《Anthropic Releases FlashProve for Cryptographic AI
   Inference Proofs》（12:44）
   缺陷 a：Anthropic 被意译成「人类」，标题变成「人类发布了 FlashProve…」
   缺陷 b：修饰语整段留成英文未译，「FlashProve for Cryptographic AI
           推理证据」中英拼接。
   根因修复：translate._ANTHROPIC_SUBJECT_RE 扩充动词集合（发布/推出/
             宣布/带来/开源/提出/展示/揭晓/上线）；
             translate.GLOSSARY 补 Cryptographic AI 系列短语。

本脚本做三件事：
  A. 把 MIT 那条的**英文原文**也剥掉订阅引导语（用户点「看翻译原文」
     时看到的应是文章内容，而不是站点推销语）；
  B. 重译这两条（标题 + 摘要），写入 data/titles_override.json 与
     data/summaries_override.json；
  C. 人工定稿标题中残留的中英拼接形态。

最后由 scripts/regen_overrides.py 固化为 manual_overrides.py（随发布走）。
"""
import json
import os

import fetcher

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

MIT_TITLE = (
    "Here’s who is falling in line for Trump’s “Super Intelligence” loyalty test"
)
FLASH_TITLE = (
    "Anthropic Releases FlashProve for Cryptographic AI Inference Proofs"
)

# 人工定稿：标题里的中英拼接（"FlashProve for Cryptographic AI 推理证据"）
# 机器译文保留了英文修饰语，读起来断裂，定稿为通顺中文。
TITLE_FIX = {
    FLASH_TITLE: "Anthropic 发布 FlashProve：面向密码学 AI 推理的加密证明方案",
}

# 人工定稿摘要（英文原文已剥离订阅引导语）
SUMMARY_FIX = {
    MIT_TITLE:
        "9 月底，特朗普总统签署了一项行政命令，其中只有一条指令：要求政府"
        "机构把此前所称的人工智能统一改名为「超级智能」。该名称胜过了其他"
        "候选，包括总统几周前在 X 上发起的一项投票中提出的「极端智能」与"
        "「至高智能」。改名如今已成白宫的传统：特朗普曾为宣示美国对特定"
        "水域（美国湾与美国湖）的主导权而改名，也为标示新的机构优先级"
        "（战争部）而改名，或只是为了在历史性地标上留名（见围绕肯尼迪"
        "中心改名而持续进行的争论）。",
    FLASH_TITLE:
        "2026 年 11 月 2 日，Anthropic 发布了 FlashProve：一种开源研究原型，"
        "用加密证明来展示语言模型的输出来自已承诺（committed）的权重，而"
        "无需公开权重本身。该公司报告称，针对 Meta 的 Llama 4 Maverick，"
        "其证明生成速度达到每秒 110 个 token。该工作针对的是托管式 AI 中"
        "长期存在的验证缺口。",
}


def main():
    with open(DATA, "r", encoding="utf-8") as f:
        data = json.load(f)
    items = data.get("items", [])

    # A. 英文原文剥离订阅引导语
    cleaned_en = 0
    for it in items:
        en = it.get("summary") or ""
        if "To get stories like this in your inbox" in en:
            new = fetcher._strip_head_sponsor(en)
            if new and new != en:
                it["summary"] = new
                cleaned_en += 1

    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # B. 覆盖表
    with open(T_JSON, "r", encoding="utf-8") as f:
        titles = json.load(f)
    with open(S_JSON, "r", encoding="utf-8") as f:
        summaries = json.load(f)

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

    print("[fix_1300] 英文原文剥离订阅引导语 %d 条" % cleaned_en)
    print("[fix_1300] 标题定稿 %d 条 / 摘要定稿 %d 条" % (added_t, added_s))
    print("[fix_1300] 覆盖表 %d 条 / %d 条" % (len(titles), len(summaries)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
