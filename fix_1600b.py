# -*- coding: utf-8 -*-
"""16:00 例行巡检（第二批）：人工定稿本轮新增条目的译文。

问题条目：
  'Envision Deploys SST-Based 800V DC Power at Ulanqab AI Data Center'
  （Unite.AI, 16:02）

  离线模型（NLLB-200）产出的译文有四处缺陷：
    1) 标题「展望部署了……」——Envision（远景能源）被意译成「展望」，
       公司名彻底丢失，读者无法识别主体；
    2) 标题「电源在 Ulanqab AI 数据中心」——地名直接留英文，
       且「电源在……数据中心」语序颠（英文是 Deploys ... at ...）；
    3) 摘要「数据中心校园」——campus 在数据中心语境应译「园区」
       （站内另一条同类报道已用「AI 算力园区」）；
    4) 摘要「乌兰卡布」——Ulanqab 的中文地名是「乌兰察布」，
       模型音译失真。

根因修复（translate.py）：
    - BRAND_TERMS 补入「展望」→ Envision 的还原；
    - TERM_FIXES 补入「乌兰卡布 / Ulanqab」→「乌兰察布」、
      「数据中心校园」→「数据中心园区」（触发词 campus）；
    - _fix_cjk_latin_spacing 补上「中文与中文之间不留空格」，
      收口术语还原后残留的空格粘连。

处理：写入人工定稿标题 + 摘要覆盖，并回写数据。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

EN = "Envision Deploys SST-Based 800V DC Power at Ulanqab AI Data Center"
ZH_TITLE = "Envision 在乌兰察布 AI 数据中心部署基于 SST 的 800V 直流供电系统"
ZH_SUMMARY = (
    "Envision 于 2026 年 11 月 2 日宣布，一套集成式 800 伏直流（800V DC）"
    "供电系统已在其位于中国乌兰察布的 Galaxy AI 数据中心园区为实时计算负载供电。"
    "公司在公告中表示，这是该类系统首次在大型人工智能数据中心投入商业化应用。"
)


def main():
    for path, val in ((T_JSON, ZH_TITLE), (S_JSON, ZH_SUMMARY)):
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
        if d.get(EN) != val:
            d[EN] = val
            with open(path, "w", encoding="utf-8") as f:
                json.dump(d, f, ensure_ascii=False, indent=2)
            print("[fix_1600b] 已更新覆盖表:", os.path.basename(path))

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    hit = 0
    for it in data.get("items", []):
        if it.get("title") == EN:
            it["title_zh"] = ZH_TITLE
            it["summary_zh"] = ZH_SUMMARY
            it["translated"] = True
            hit += 1
            print("[fix_1600b] 已回写:", EN[:60])
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("[fix_1600b] 已回写数据 %d 条" % hit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
