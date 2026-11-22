# -*- coding: utf-8 -*-
"""2026-11-22 21:00 巡检：本轮新增 1 条（The Decoder 20:07:56），NLLB 硬伤人工定稿。

  The Decoder《Security researchers show how cheap AI inference providers
  steal keys and snoop on users》——
    * "snoop on users" 被译成「窃取用户」（应为「窥探用户」）；
    * 安全公司 Dragos 被音译成「德拉戈斯」；
    * "marketplace resellers ... reading customer requests" 译成「市场零售商只是阅读客户请求」，
      语义生硬；
    * "endpoints" 译成「终端点」（应为「端点」）。

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
        "95f39de51bcabaefc5517ef2480c325f",
        "安全研究人员揭示廉价 AI 推理服务商如何窃取密钥并窥探用户",
        "Dragos 安全研究人员利用 200 万个虚假 AI 请求，揭露了 AI 供应链中的严重漏洞："
        "至少发现三家服务商遭到入侵、数百个 AWS 密钥被盗，以及直接读取客户请求的应用商店转售商。"
        "OpenRouter 随后移除了三家服务商和 125 个端点作为回应。",
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
