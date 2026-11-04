# -*- coding: utf-8 -*-
"""15:00 巡检：定稿 Pando 条目的译文并写回覆盖表。

问题条目：
  'OpenAI Introduces Pando: A Git Backend That Cuts Median Push Latency ~80%'
  （Marktechpost, 2026-11-03 13:51）

离线模型（NLLB-200）产出的译文有 8 类缺陷：
    1) 「一百字节」——petabyte（10^15 字节）被逐字直译，量级差 10^13 倍；
    2) 「中位 push 延迟」——Git 的 push 是「推送」不是「推迟」；
    3) 「非干部历史」——Git trunk 被译成党政语「干部」；
    4) 「商品硬件」——commodity hardware 应为「通用商用硬件」；
    5) 「同时推进的推进器」——concurrent pushers 被译成推进器；
    6) 「时化 10Gbps 链接」——saturate 被吞成残句；
    7) 「每次 OpenAI 自己的测试」——per … own testing 误读为「每次」；
    8) 标签形态不统一（最糟糕的是／运行／TL;DR Scale）与半角句号粘连。

根因修复已在 translate.py 完成（TERM_FIXES / _normalize_sentence_end /
_fix_cjk_latin_spacing / _STRUCT_LABELS / _fix_zh_label_variants），
本脚本只负责把人工定稿结果写回数据与覆盖表，使后续轮次不被模型译文覆盖。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

EN = ("OpenAI Introduces Pando: A Git Backend That Cuts Median Push "
      "Latency ~80%")
ZH_TITLE = "OpenAI 介绍了 Pando：一个 Git 后端，可减少推送延迟中位数~80%"
ZH_SUMMARY = (
    "OpenAI 推出了 Pando，一个新的 Git 后端，现在它在 monorepo 中服务于所有开发。"
    "OpenAI Pando Git 后端保留了标准的 Git 客户端和协议。"
    "工程师和 Codex 智能体仍然像以前一样运行 Git push 和 Git fetch。只有服务器发生了变化。"
    "OpenAI 团队报告的推送延迟中位数下降了近 80%。"
    "Pando 现在每天提供了几乎 1 PB 的 Git 数据。"
    "TL;DR 规模：每天近 1 PB 的 Git 数据；在 1 小时内达到 57 TB 以上的峰值。"
    "运行方式：通用商用硬件；标准云 VM 在克隆和获取时可跑满 10 Gbps 链路。"
    "性能：据 OpenAI 自身测试，数千个并发推送方都没有降级。"
    "最佳：推送延迟中位数下降了近 80%（约 5 倍）。"
    "最差：不开源；通过重复分支推送非主干历史（p99 包 3 MiB 以下）。"
    "OpenAI Pando 是什么？"
)


def main():
    for path, val in ((T_JSON, ZH_TITLE), (S_JSON, ZH_SUMMARY)):
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
        if d.get(EN) != val:
            d[EN] = val
            with open(path, "w", encoding="utf-8") as f:
                json.dump(d, f, ensure_ascii=False, indent=2)
            print("[fix_1500_pando] 已更新覆盖表:", os.path.basename(path))

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    hit = 0
    for it in data.get("items", []):
        if it.get("title") == EN:
            it["title_zh"] = ZH_TITLE
            it["summary_zh"] = ZH_SUMMARY
            it["translated"] = True
            hit += 1
    if hit:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("[fix_1500_pando] 已回写 news.json，命中条目:", hit)
    else:
        print("[fix_1500_pando] 未命中条目，未改动数据")


if __name__ == "__main__":
    main()
