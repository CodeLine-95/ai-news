# -*- coding: utf-8 -*-
"""02:00 例行巡检：定稿 01:28 The Decoder 那条 NLLB 机翻崩坏条目。

- 原标题 “GPT-6.2 Astra users now hit limits 40% faster after OpenAI
  patched a pricing error” 被机翻为「现在达到 40%的速度更快」，语义不通。
- 摘要把 Astra / Sol 两个产品名译成「阿斯特拉和索尔」，「hit limits 40
  and 25 percent faster」译成「比上周快速达到了 40 和 25%的限制」，
  并把账单错误（billing bug）误译为「发票错误」；末尾抓取残留 “The
  article GPT-6.” 应剔除。按原文重述，保留产品名与百分比对应关系。

回填 news.json + JSON 覆盖表，再由 scripts/regen_overrides.py 同步到
代码层 manual_overrides.py，确保部署端持久卷的旧覆盖表不会回退译文。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

FIX = {
    "GPT-6.2 Astra users now hit limits 40% faster after OpenAI patched a pricing error": (
        "OpenAI 修复计费错误后，GPT-6.2 Astra 用户触及用量上限快了 40%",
        "OpenAI 表示，一项计费漏洞让 GPT-6.2 用户获得了错误的折扣。修复后，Astra 与 Sol 用户"
        "触及用量上限的速度较上周分别快了 40% 和 25%。作为致歉，订阅用户可获得一次额外的"
        "额度重置，企业用户可在年底前免费使用快速模式。OpenAI 还在测试将聊天模式与工作模式合并。",
    ),
}


def main():
    db = json.load(open(os.path.join(DATA, "news.json"), encoding="utf-8"))
    items = db["items"] if isinstance(db, dict) else db

    tpath = os.path.join(DATA, "titles_override.json")
    spath = os.path.join(DATA, "summaries_override.json")
    tov = json.load(open(tpath, encoding="utf-8")) if os.path.exists(tpath) else {}
    sov = json.load(open(spath, encoding="utf-8")) if os.path.exists(spath) else {}

    changed = 0
    matched = set()
    for it in items:
        en = it.get("title") or ""
        if en in FIX:
            matched.add(en)
            title_zh, summary_zh = FIX[en]
            for key, value in (("title_zh", title_zh), ("summary_zh", summary_zh)):
                if it.get(key) != value:
                    it[key] = value
                    it["translated"] = True
                    it["method"] = "nllb+manual"
                    changed += 1
                    print("[fix] %s: %s" % (key, en[:58]))
            tov[en] = title_zh
            sov[en] = summary_zh

    missing = set(FIX) - matched
    if missing:
        print("[warn] 未匹配到条目:", missing)

    json.dump(tov, open(tpath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(sov, open(spath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(db, open(os.path.join(DATA, "news.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("[fix] 变更 %d 处 | 覆盖表 标题 %d 条 / 摘要 %d 条"
          % (changed, len(tov), len(sov)))


if __name__ == "__main__":
    main()
