# -*- coding: utf-8 -*-
"""04:00 例行巡检：定稿 03:31 The Decoder 那条 NLLB 机翻崩坏条目。

- 原标题 “Former OpenAI researcher says the Riemann proof matters less than
  the fact that an AI system can produce it” 被机翻为「前的 OpenAI 研究人员
  说，里曼证据并不像人工智能系统能够产生它那样重要」：“前的”缺字、
  “Riemann proof”误作「里曼证据」（应为「黎曼猜想证明」）。
- 摘要出现「范围内的范围」「坐着一个或多个炸弹」等机翻腔，按原文重述。

回填 news.json + JSON 覆盖表，再由 scripts/regen_overrides.py 固化到代码层。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

FIX = {
    "Former OpenAI researcher says the Riemann proof matters less than the fact that an AI system can produce it": (
        "前 OpenAI 研究员称，黎曼猜想证明的意义不及 AI 系统能够给出证明这件事重要",
        "复杂性理论家、前 OpenAI 研究员 Scott Aaronson 认为，AI 近期的数学突破意义远超学术界本身。"
        "他写道，其潜在影响从重塑全球经济到威胁地球上的全部生命。"
        "他还表示「几乎可以肯定」，AI 实验室在密码学领域握有「一颗或多颗重磅炸弹」。",
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
