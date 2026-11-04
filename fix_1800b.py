# -*- coding: utf-8 -*-
"""2026-11-02 18:00 例行巡检（第二批）：人工定稿 Wired 深度伪造报道。

问题条目：
  'Hundreds of Mundane AI Apps Are Hiding Sexually Abusive Deepfake Features'
  （Wired, 2026-11-02 18:00）

  离线模型译文缺陷：
    1) "mundane AI apps" 译成「世界智能应用程序」——mundane 是「平淡无奇的/
       普通的」，模型译成「世界的」（疑似与 "world-wide" 串味）；
    2) "deepfake" 被拆成「深度 fake」——离线模型对不认识的复合词常把
       构词部分意译、词根留英文；中文通用写法是「深度伪造」；
    3) 媒体名 "WIRED" 译成「电线」——品牌还原表漏了该变体；
    4) "Sexually Abusive" 译成「性虐待」——语境是「性暴力滥用」，
       直接译成「性虐待」在中文里读起来过于直白且不准确；
    5) "linked to Chinese-language developers" 译成「与中文开发人员相关」，
       原文指「与中文（语言）开发者有关联的」。

根因修复（translate.py）：
    BRAND_TERMS 的 "Wired" 补入「电线」变体；
    _PROPER_NOUN_FIXES 补入 深度 fake→深度伪造、世界智能→普通智能 等规则。

处理：写入人工定稿标题 + 摘要覆盖，并回写数据。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

EN = ("Hundreds of Mundane AI Apps Are Hiding Sexually Abusive "
      "Deepfake Features")
ZH_TITLE = "数百个平淡无奇的 AI 应用暗藏性暴力深度伪造功能"
ZH_SUMMARY = (
    "Wired 调查发现，约有 400 个与中文开发者有关联的应用程序和网站，"
    "表面上看起来就是普通的 AI 工具，实际上却藏有秘密功能，"
    "允许用户生成暴力的 AI 图像和视频。"
)


def main():
    for path, val in ((T_JSON, ZH_TITLE), (S_JSON, ZH_SUMMARY)):
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
        if d.get(EN) != val:
            d[EN] = val
            with open(path, "w", encoding="utf-8") as f:
                json.dump(d, f, ensure_ascii=False, indent=2)
            print("[fix_1800b] 已更新覆盖表:", os.path.basename(path))

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    hit = 0
    for it in data.get("items", []):
        if it.get("title") == EN:
            it["title_zh"] = ZH_TITLE
            it["summary_zh"] = ZH_SUMMARY
            it["translated"] = True
            hit += 1
            print("[fix_1800b] 已回写:", EN[:60])
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("[fix_1800b] 已回写数据 %d 条" % hit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
