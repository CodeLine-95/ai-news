# -*- coding: utf-8 -*-
"""06:00 例行巡检：人工定稿新增的 1 条低质量译文。

问题条目：
  'OpenAI might rebrand its data centers as ‘AI compute campuses’'（TechCrunch, 05:55）
    模型把专有名词 OpenAI 误译成「开通 AI」，把 compute campuses 直译成
    「计算机校园」，标题语义完全跑偏；摘要也是逐字硬译，读不成句。
处理：写入人工定稿标题 + 摘要覆盖，并回写数据与报告。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

EN_TITLE = "OpenAI might rebrand its data centers as ‘AI compute campuses’"
ZH_TITLE = "OpenAI 或将数据中心改名为「AI 算力园区」"
ZH_SUMMARY = (
    "数据中心在各地一直备受争议、招人嫌。但如果换个名字称呼它呢？"
    "OpenAI 可能考虑把自家数据中心统称为「AI 算力园区」（AI compute campuses），"
    "一方面弱化「数据中心」带来的电力与水资源消耗等负面联想，"
    "另一方面也把叙事重心从「机房与能耗」转向「智能算力供给」，"
    "让这类基础设施更容易获得地方政府的土地与能源审批支持。"
)


def main():
    for path, key, val in (
        (T_JSON, EN_TITLE, ZH_TITLE),
        (S_JSON, EN_TITLE, ZH_SUMMARY),
    ):
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
        if d.get(key) != val:
            d[key] = val
            with open(path, "w", encoding="utf-8") as f:
                json.dump(d, f, ensure_ascii=False, indent=2)
            print("[fix_0600] 已更新覆盖表:", os.path.basename(path))

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    hit = 0
    for it in data.get("items", []):
        if it.get("title") == EN_TITLE:
            it["title_zh"] = ZH_TITLE
            it["summary_zh"] = ZH_SUMMARY
            it["translated"] = True
            hit += 1
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("[fix_0600] 已回写数据 %d 条" % hit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
