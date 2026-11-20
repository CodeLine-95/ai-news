# -*- coding: utf-8 -*-
"""2026-11-21 03:00 巡检：人工定稿 2 条 NLLB 机翻硬伤。

1) MIT Tech Review《The most misunderstood graph in AI just got a major update》
   本轮 02:03 调度新入库。标题机翻「人工智能最被误解的图表刚刚得到了重大更新。」
   尚可，但摘要出现「指数 Trajectory」中英混杂、「该报告是更新了组织的时间表图」
   语义崩坏、末句「根据他们能够完成的任务的长度」指代不清。
2) 历史遗留《Kakao Mobility Signs NVIDIA MOU for Level 4 Autonomous Driving》
   标题被机翻成「可可可」，Kakao 专名音译崩坏。

同引擎重译会重复相同错误，故人工定稿；覆盖 news.json + JSON 覆盖表 +
代码层 manual_overrides.py（regen）。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

T1 = "The most misunderstood graph in AI just got a major update"
T2 = "Kakao Mobility Signs NVIDIA MOU for Level 4 Autonomous Driving"

TITLE_FIX = {
    T1: "AI 领域最被误解的图表刚刚迎来重大更新",
    T2: "Kakao Mobility 与 NVIDIA 签署 L4 级自动驾驶谅解备忘录",
}

SUMMARY_FIX = {
    T1: (
        "AI 评估非营利组织 METR 发布的新报告发现，部分 AI 能力仍在沿指数级轨迹持续提升——"
        "但报告也指出，模型在需要判断力的任务上，表现并不像在编程任务上那么出色。"
        "这份报告是对该机构「时间跨度图」（time horizon plot）的更新版本；"
        "由于所采用衡量指标十分复杂，该图此前被广泛传播，也被广泛误解。"
        "METR 通过让模型尝试大量任务来开展评估，其中每项任务也都由人类完成过。"
        "每项任务的难度以人类测试者完成任务所需的时间来评分，"
        "随后按模型能够完成的任务时长对模型进行评级。"
        "该图显示，AI 系统正在快速进步：前沿模型能够成功完成的任务时长，每四个月翻一番。"
    ),
    T2: (
        "Kakao Mobility 于 2026 年 11 月 9 日宣布，已与 NVIDIA 签署谅解备忘录，"
        "双方将共同开发 L4 级自动驾驶技术，初期在起亚（Kia）专用车辆（PBV）上整合各自系统。"
        "该合作把 Kakao Mobility 的自动驾驶 AI 与出行平台，"
        "同 NVIDIA 的计算、传感与安全技术相结合。"
    ),
}


def main():
    db = json.load(open(DATA, encoding="utf-8"))
    items = db["items"] if isinstance(db, dict) else db
    changed = 0
    for it in items:
        en = (it.get("title") or "").strip()
        touched = False
        if en in TITLE_FIX:
            it["title_zh"] = TITLE_FIX[en]
            touched = True
        if en in SUMMARY_FIX:
            it["summary_zh"] = SUMMARY_FIX[en]
            touched = True
        if touched:
            it["translated"] = True
            it["method"] = "nllb+manual"
            changed += 1
            print("fixed:", it.get("date"), it.get("time"), en[:60])
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    titles = json.load(open(T_JSON, encoding="utf-8"))
    summaries = json.load(open(S_JSON, encoding="utf-8"))
    added_t = added_s = 0
    for k, v in TITLE_FIX.items():
        if titles.get(k) != v:
            titles[k] = v
            added_t += 1
    for k, v in SUMMARY_FIX.items():
        if summaries.get(k) != v:
            summaries[k] = v
            added_s += 1
    with open(T_JSON, "w", encoding="utf-8") as f:
        json.dump(titles, f, ensure_ascii=False, indent=2)
    with open(S_JSON, "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)

    print("[fix_1121_0300] news.json 回填 %d 条；标题定稿 %d / 摘要定稿 %d" %
          (changed, added_t, added_s))
    print("[fix_1121_0300] 覆盖表 %d 条 / %d 条" % (len(titles), len(summaries)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
