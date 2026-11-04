# -*- coding: utf-8 -*-
"""16:00 例行巡检（第三批）：人工定稿本轮新增条目的译文。

问题条目：
  'TIER IV Leads Autoware 2.0 Ecosystem for AI-Defined Vehicles'
  （Unite.AI, 16:19）

  离线模型（NLLB-200）产出的译文有四处缺陷：
    1) 标题「自动化工 2.0 生态系统」——Autoware 是自动驾驶开源项目名，
       模型把它意译成「自动化工」，项目名彻底丢失；
    2) 标题「带领了 AI 定义车辆的……」语序颠倒
       （英文是 Leads Autoware ... Ecosystem for AI-Defined Vehicles）；
    3) 摘要「TIER IVER」——罗马数字 IV 被模型误当英文缩写写成 IVER，
       公司名被改坏；
    4) 摘要「混合驾驶堆」「建立的基于规则的模块」等为直译，
       且末句「描述了 Autoware 2。」以数字结尾，句子被截断。

根因修复（translate.py）：
    - TERM_FIXES 补入「自动化工」→「Autoware」（触发词 autoware）、
      「TIER IVER」→「TIER IV」（触发词 tier iv）。

处理：写入人工定稿标题 + 摘要覆盖，并回写数据。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

EN = "TIER IV Leads Autoware 2.0 Ecosystem for AI-Defined Vehicles"
ZH_TITLE = "TIER IV 领衔 Autoware 2.0 生态，面向 AI 定义汽车"
ZH_SUMMARY = (
    "TIER IV 于 2026 年 11 月 2 日宣布，正与 Autoware 基金会及全球开源社区"
    "协作推动 Autoware 2.0 计划；同日，该基金会发布了 2.0 版本的开源自动驾驶软件，"
    "新增对端到端 AI 与混合驾驶栈的支持，同时保留既有的基于规则的模块。"
    "TIER IV 表示，Autoware 2.0 是迈向由 AI 定义汽车的关键一步。"
)


def main():
    for path, val in ((T_JSON, ZH_TITLE), (S_JSON, ZH_SUMMARY)):
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
        if d.get(EN) != val:
            d[EN] = val
            with open(path, "w", encoding="utf-8") as f:
                json.dump(d, f, ensure_ascii=False, indent=2)
            print("[fix_1600c] 已更新覆盖表:", os.path.basename(path))

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    hit = 0
    for it in data.get("items", []):
        if it.get("title") == EN:
            it["title_zh"] = ZH_TITLE
            it["summary_zh"] = ZH_SUMMARY
            it["translated"] = True
            hit += 1
            print("[fix_1600c] 已回写:", EN[:60])
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("[fix_1600c] 已回写数据 %d 条" % hit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
