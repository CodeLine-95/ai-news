# -*- coding: utf-8 -*-
"""22 点巡检：定稿 2 条 NLLB 机翻硬伤并写回覆盖表。

问题条目（22 点整点抓取新增）：

  1) 'TrueLayer Tests AI Agent Payments at Papa John’s in the UK'
     缺陷：标题「真实层测试」把公司名 TrueLayer 直译；摘要把 Pay by Bank
     拆成「Pay 银行 by 银行支付」，FCA 名称也译成「Financial Conduct Authoritys」。
  2) 'This ER Doctor Became a Hospital’s First Clinical AI Engineer'
     缺陷：标题「急症医生」不够准确（应为急诊医生），句末多余句号；摘要把
     prompt engineering 误译为「快速工程」，coax 译为「获得」丢失语义，
     还把履历信息与正文粘连。

本脚本把人工定稿结果写回数据与覆盖表，随后运行
    python3.11 scripts/regen_overrides.py
同步到代码层覆盖表，使后续轮次不再被模型译文覆盖。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

FIXES = [
    (
        "TrueLayer Tests AI Agent Payments at Papa John’s in the UK",
        "TrueLayer 在英国测试 AI 智能体支付，落地 Papa John's",
        "TrueLayer 于 2026 年 11 月 27 日宣布，Papa John's 的一个 AI 智能体"
        "完成了其所称的首笔面向英国具名零售商的智能体「银行直付」（Pay by Bank）"
        "支付。这项试点涉及 Lloyds、NatWest 等英国零售银行，并通过英国金融行为"
        "监管局（FCA）的「Supercharged Sandbox」监管沙盒运行。该智能体协助客户"
        "完成下单，随后直接从与客户 Papa John's 账户关联的银行账户中扣款。",
    ),
    (
        "This ER Doctor Became a Hospital’s First Clinical AI Engineer",
        "这位急诊医生成了医院的首位临床 AI 工程师",
        "2023 年，波士顿儿童医院发布了一则招聘提示工程师的职位公告，Dinesh Rai "
        "决定申请——他本没指望能得到这份工作。当时，提示工程正被吹捧为生成式 AI "
        "创造的热门新岗位之一：企业希望找到懂得如何通过精心措辞的指令、提供示例、"
        "赋予系统人设或其他上下文，从大语言模型（LLM）中诱导最佳回答的人才。"
        "Dinesh Rai 任职于波士顿儿童医院，职位是临床 AI 工程师；他拥有罗格斯商学院"
        "供应链管理与营销科学学士学位，以及阿尔伯特·爱因斯坦医学院医学博士学位。"
        "对医院而言这是个不同寻常的岗位，而 Rai 的履历同样不寻常：他虽受训为急诊"
        "医生，但在进入医学院前就已自学编程。",
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
                print("[fix_2200] 已更新覆盖表:", os.path.basename(path), "|", en[:50])

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
                print("[fix_2200] 已回写:", en[:60])
    if hit:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("[fix_2200] 已回写 news.json，命中条目:", hit)
    else:
        print("[fix_2200] 未命中条目，未改动数据")


if __name__ == "__main__":
    main()
