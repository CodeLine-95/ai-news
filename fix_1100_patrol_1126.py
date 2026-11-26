# -*- coding: utf-8 -*-
"""11:00 例行巡检：定稿 10:52 新增条目的 NLLB 机翻腔。

- 标题 "fully authorized and still do damage" 直译为「可以得到充分授权，但仍然会造成损害」，
  语气平淡，定稿为「即便权限完整授予，仍可能造成损害」。
- 摘要 "Identity, zero trust and least privilege all exist to answer that question"
  被直译为「身份，零信任和最小特权都存在来回答这个问题」，定稿为通顺中文。

按项目既有模式回填 news.json + JSON 覆盖表，再由
scripts/regen_overrides.py 同步到代码层 manual_overrides.py。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

FIX = {
    "Your AI agents can be fully authorized and still do damage": (
        "即便权限完整授予，AI 智能体仍可能造成损害",
        "企业安全一直围绕一个核心问题展开：谁有权做什么？身份管理、零信任与最小权限原则都是为回答这个问题而生。互联网与移动设备把更多人和终端接入网络，改变了安全格局，但这一根本问题始终未变。",
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
    for it in items:
        en = it.get("title") or ""
        if en not in FIX:
            continue
        title_zh, summary_zh = FIX[en]
        if it.get("title_zh") != title_zh:
            it["title_zh"] = title_zh
            it["translated"] = True
            it["method"] = "nllb+manual"
            changed += 1
            print("[fix] title:", en[:60], "->", title_zh)
        if it.get("summary_zh") != summary_zh:
            it["summary_zh"] = summary_zh
            changed += 1
            print("[fix]  summary:", en[:60])
        tov[en] = title_zh
        sov[en] = summary_zh

    json.dump(tov, open(tpath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(sov, open(spath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(db, open(os.path.join(DATA, "news.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("[fix] 变更 %d 处 | 覆盖表 标题 %d 条 / 摘要 %d 条"
          % (changed, len(tov), len(sov)))


if __name__ == "__main__":
    main()
