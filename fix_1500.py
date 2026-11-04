# -*- coding: utf-8 -*-
"""15:00 例行巡检：人工定稿本轮新增条目的译文。

问题条目：
  'OpenAI Sets Shared ChatGPT and Codex Usage Allowance for December'
  （Unite.AI, 14:21）

  离线模型（NLLB-200）产出的译文有三处缺陷：
    1) 标题「共享聊天 GPT」——ChatGPT 被意译成「聊天 GPT」，
       品牌名丢失，且中英混排空格破坏可读性；
    2) 摘要「OpenAI 将将 Plus」——「将」重复（NLLB 常见重复虚词）；
    3) 「usage allowance」译成「单个使用权」语义不通，
       且 Plus / Pro / Business 用逗号并列不符合中文顿号排版惯例。

根因修复（translate.py）：
    - BRAND_TERMS 补入「聊天 GPT」变体，TERM_FIXES 补入
      「聊天 GPT」→「ChatGPT」规则，使后续轮次自动还原；
    - _clean_zh 新增「重复虚词折叠」（仅限虚词白名单，
      避免误伤「源源不断」「软乎乎」等正常叠词）。

处理：写入人工定稿标题 + 摘要覆盖，并回写数据。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

EN = "OpenAI Sets Shared ChatGPT and Codex Usage Allowance for December"
ZH_TITLE = "OpenAI 为 12 月设定 ChatGPT 与 Codex 共享使用额度"
ZH_SUMMARY = (
    "根据 OpenAI 帮助中心发布的通知，自 2026 年 12 月起，"
    "Plus、Pro 与 Business 订阅用户将转入 ChatGPT 与 Codex 共用的同一份使用额度，"
    "其中即时对话不占用共享额度。新的计费结构下，"
    "ChatGPT 与 Codex 的使用量以 token 为单位衡量，"
    "即模型处理与生成的信息的基本单位。"
)


def main():
    for path, val in ((T_JSON, ZH_TITLE), (S_JSON, ZH_SUMMARY)):
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
        if d.get(EN) != val:
            d[EN] = val
            with open(path, "w", encoding="utf-8") as f:
                json.dump(d, f, ensure_ascii=False, indent=2)
            print("[fix_1500] 已更新覆盖表:", os.path.basename(path))

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    hit = 0
    for it in data.get("items", []):
        if it.get("title") == EN:
            it["title_zh"] = ZH_TITLE
            it["summary_zh"] = ZH_SUMMARY
            it["translated"] = True
            hit += 1
            print("[fix_1500] 已回写:", EN[:60])
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("[fix_1500] 已回写数据 %d 条" % hit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
