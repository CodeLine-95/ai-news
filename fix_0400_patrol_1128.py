# -*- coding: utf-8 -*-
"""04 点巡检：定稿 3 条 NLLB「Apple → 果」截断硬伤并写回覆盖表。

2026-11-28 04:00 例行巡检复核发现 3 条机翻硬伤：
  1) 'OpenAI Countersues Apple Over Alleged Hardware Trade-Secret Theft'
     标题被译成「果对…进行了 OpenAI 反驳」，主语/宾语颠倒且 Apple 截断为「果」；
     摘要中 Apple/Apple 多处截断。
  2) 'OpenAI countersues Apple over trade secret theft and alleged coercion
     of shared suppliers' 标题与摘要中 Apple 均截断为「果」。
  3) 'Apple’s $50 Intelligence Usage Packs extend access to some AI features'
     标题开头 Apple's 截断为「果」，摘要中「正如果所称」同病。

人工定稿后写回 data 与 JSON 覆盖表，再运行 scripts/regen_overrides.py
同步到代码层 manual_overrides.py（随发布生效）。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

FIXES = [
    (
        "OpenAI Countersues Apple Over Alleged Hardware Trade-Secret Theft",
        "OpenAI 反诉苹果涉嫌窃取硬件商业秘密",
        "2026 年 11 月 27 日，OpenAI 集团 PBC、io Products、Chang Liu 与 Tang Yew Tan "
        "在加州联邦法院对苹果提起反诉，指控苹果盗用了保密的硬件设计与制造记录。"
        "随之提交的答辩否认了苹果关于商业秘密与合同的诉求，反诉包含 12 项诉讼请求。"
        "苹果此前已在美国提起相关诉讼。",
    ),
    (
        "OpenAI countersues Apple over trade secret theft and alleged coercion of shared suppliers",
        "OpenAI 反诉苹果窃取商业秘密并涉嫌胁迫共同供应商",
        "OpenAI 在加州法院起诉苹果，指控其窃取商业秘密并胁迫双方共用的供应商。"
        "此次反诉源于苹果今年夏天提起的诉讼。就在两年前，两家公司还合作将 ChatGPT "
        "引入 iPhone。如今 OpenAI 正自主研发设备，与苹果直接竞争。",
    ),
    (
        "Apple’s $50 Intelligence Usage Packs extend access to some AI features",
        "苹果推出 50 美元智能使用包，扩展部分 AI 功能的访问权限",
        "继 9 月初发布支持文章说明部分 Apple Intelligence 功能的使用限制后，该公司更新了 "
        "Logic Pro，新增「购买更多使用量」选项，一次性购买价格为 49.99 美元（据 9to5Mac 发现）。"
        "Logic Pro 内置 AI 助手，可完成「开启新歌、通过单一提示设置人声轨道或完善当前项目」等任务。"
        "苹果称这类智能使用包将让用户继续使用部分受限的 Apple Intelligence 功能——"
        "这些功能依赖 OpenAI 或 Google Gemini 的云端 AI 模型。",
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
                print("[fix_0400] 覆盖表已更新:", os.path.basename(path), "|", en[:55])

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    hit = 0
    for it in data.get("items", []):
        for en, zh_title, zh_summary in FIXES:
            if it.get("title") == en:
                it["title_zh"] = zh_title
                it["summary_zh"] = zh_summary
                it["translated"] = True
                it["method"] = "manual"
                hit += 1
                print("[fix_0400] 已回写:", en[:60])
    if hit:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("[fix_0400] 已回写 news.json，命中条目:", hit)
    else:
        print("[fix_0400] 未命中条目，仅更新覆盖表")


if __name__ == "__main__":
    main()
