# -*- coding: utf-8 -*-
"""03 点巡检：定稿 2 条 NLLB 机翻硬伤并写回覆盖表。

本轮（2026-11-28 03:00）整点自动抓取后复核发现 2 条机翻硬伤：
  1) 'Banned Nvidia Blackwell chips turn up in a Shanghai data center
     linked to Alice Huang, Bloomberg reports'
     Bloomberg 误译为「博社」；title 末尾「相关的数据中心」重复冗余；
     摘要里 Bloomberg 误译为「博公司」、Gigabyte 未括注中文。
  2) 'Game Boy Color on My Conference Badge'
     badge 误译为「章」（应为「胸牌」）；Game Boy Color 误译为「Game Boy 颜色」；
     摘要中 Zelda 书名错乱、'touch buttons' 误译为「触摸按」。

人工定稿后写回 data 与 JSON 覆盖表，随后运行 scripts/regen_overrides.py
同步到代码层覆盖表 manual_overrides.py（随发布生效）。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

FIXES = [
    (
        "Banned Nvidia Blackwell chips turn up in a Shanghai data center linked to Alice Huang, Bloomberg reports",
        "彭博社报道：被禁的英伟达 Blackwell 芯片现身与 Alice Huang 关联的上海数据中心",
        "据彭博社调查，两家中国公司在与 Alice Huang 相关联的一处上海数据中心安装了英伟达性能强劲的 "
        "Blackwell 芯片。一个序列号让彭博社追查到台湾制造商技嘉（Gigabyte）。在没有美国许可证的"
        "情况下将这些芯片出口到中国属于违法行为。",
    ),
    (
        "Game Boy Color on My Conference Badge",
        "我会议胸牌上的 Game Boy Color",
        "本周我在 GitHub Universe 大会现场，和去年一样，会议胸牌本身就是一台功能齐全的彩屏计算机。"
        "我再次动手折腾它，遇到了 Steve Francia——他与 Gemini 合作让完整的 NES 模拟器在胸牌上跑了起来，"
        "并且更进一步，部署了 Game Boy 与 Game Boy Color 模拟器。这意味着只要你能拿到 ROM，就能在"
        "胸牌上运行《塞尔达传说：织梦岛》。这个胸牌设计巧妙之处在于，你可以把它倒过来，用嵌入胸牌"
        "机身的触摸按键当作游戏手柄。",
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
                print("[fix_0300] 已更新覆盖表:", os.path.basename(path), "|", en[:50])

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
                print("[fix_0300] 已回写:", en[:60])
    if hit:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("[fix_0300] 已回写 news.json，命中条目:", hit)
    else:
        print("[fix_0300] 未命中条目，未改动数据")


if __name__ == "__main__":
    main()
