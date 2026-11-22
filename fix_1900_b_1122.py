# -*- coding: utf-8 -*-
"""2026-11-22 19:00 巡检第二批：又落地 2 条，NLLB 硬伤人工定稿。

  1) Wired《Banks Have Had It Up to Here With Your AI Agent》——
     标题「银行与你的 AI 智能体一起做了什么」曲解了 have it up to here
     （受够了/忍无可忍）的语义，应为「银行已经受够了你的 AI 智能体」。
  2) InfoQ AI《Claude Code Has Been Leaking Secrets ...》——
     标题「Claude 代码」应为产品名 Claude Code；「不要再问」应保留英文
     功能名 Don't Ask Again 并说明；摘要「在 git 历史中，在共享的...」断句错乱。

三层覆盖：news.json 回填 + JSON 覆盖表 + (regen) manual_overrides.py。
"""
import json
import os
import report

BASE = os.path.dirname(os.path.abspath(__file__))
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")
N_JSON = os.path.join(BASE, "data", "news.json")

FIXES = [
    (
        "9315ed20f1b1d3f4b2158c73e246d060",
        "银行已经受够了你的 AI 智能体",
        "美国主要金融机构正在禁止第三方智能体机器人登录用户账户，并警告说：机器人犯下的任何代价高昂的错误，责任都由用户自己承担。随着 AI 智能体开始代替用户执行转账、支付等操作，银行正收紧对自动化程序访问账户的控制，试图在便利性与安全风险之间重新划出界限。",
    ),
    (
        "3b9c5fc789e0b9ed6df7b8347fa6ff5b",
        "Claude Code 通过「Don't Ask Again」功能泄露机密信息",
        "智能体安全公司 Apiiro 发现，Claude Code 一直在公共存储库中泄露机密信息——原因是它把机密存储在开发者机器上的本地文件中，以实现「Don't Ask Again」（不要再问）功能。该公司在 claude/settings.local.json 文件中识别出 1122 个机密；此外，在 git 历史、共享的 settings.json 文件以及存储的智能体对话转录中，还发现了另外 1160 个机密。",
    ),
]


def main():
    titles = json.load(open(T_JSON, encoding="utf-8"))
    summaries = json.load(open(S_JSON, encoding="utf-8"))
    news = json.load(open(N_JSON, encoding="utf-8"))
    by_id = {it["id"]: it for it in news["items"]}

    ok = 0
    for iid, zh_t, zh_s in FIXES:
        it = by_id.get(iid)
        if not it:
            print("[WARN] id 未找到:", iid)
            continue
        en = (it.get("title") or "").strip()
        titles[en] = zh_t
        summaries[en] = zh_s
        it["title_zh"] = zh_t
        it["summary_zh"] = zh_s
        it["method"] = "manual"
        it["translated"] = True
        ok += 1
        print("[FIX]", iid[:8], "->", zh_t)

    json.dump(titles, open(T_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(summaries, open(S_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(news, open(N_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("[OK] 定稿 %d 条；覆盖表 标题=%d 摘要=%d；news.json=%d 条"
          % (ok, len(titles), len(summaries), len(news["items"])))

    report.main()
    print("[OK] 报告已重生成")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
