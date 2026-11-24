# -*- coding: utf-8 -*-
"""2026-11-24 11:00 例行巡检：定稿本轮新增 2 条 NLLB 机翻硬伤。

沙箱 resume 后 11:00 整点抓取新增 2 条（Unite.AI），均为 nllb 直译：
1) Bail Fight 被译为「保释斗争」，据称录音被译成「据称录音记录」，
   「数十段录音」被量词错配成「数十张录制的 OpenAI 会议」；
2) Export-control Entity List 被译为「出口控制实体名单」（应为出口管制
   实体清单），「其他六家马来西亚，新加坡和泰国实体」标点与语序生硬。

覆盖三层：news.json 回填 + JSON 覆盖表 + 代码层 manual_overrides.py（regen）。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

FIX = {
    "Prosecutors Detail Alleged Recordings of OpenAI Meetings in Bail Fight": (
        "保释之争中，检方详述据称录有 OpenAI 会议的录音",
        "在 2026 年 11 月 23 日提交的一份法庭文件中，联邦检察官表示，调查人员从前 OpenAI 工程师 Abdulrahman Alfozan 的个人电脑中提取了数百个音频文件，其中包括数十段 OpenAI 会议录音，以及明显由人工智能生成的文字转录。政府方面援引这些材料，反对他再次提出的审前释放请求。",
    ),
    "BIS Adds Megaspeed and Six Other Entities to Entity List": (
        "美国 BIS 将 Megaspeed 及其他六家实体列入实体清单",
        "美国商务部工业与安全局（BIS）于 2026 年 11 月 23 日发布最终规则，以存在将先进计算商品转移至未经授权的最终用途或最终用户的风险为由，将 Megaspeed International Pte. Ltd. 及位于马来西亚、新加坡和泰国的其他六家实体列入其出口管制实体清单。该规则定于 2026 年 11 月 25 日刊登。清单中包括三家马来西亚实体、三家新加坡实体和一家泰国实体。",
    ),
}


def main():
    db = json.load(open(DATA, encoding="utf-8"))
    items = db["items"] if isinstance(db, dict) else db
    titles = json.load(open(T_JSON, encoding="utf-8"))
    summaries = json.load(open(S_JSON, encoding="utf-8"))

    changed = added_t = added_s = 0
    for it in items:
        en = (it.get("title") or "").strip()
        if en not in FIX:
            continue
        title_zh, summary_zh = FIX[en]
        it["title_zh"] = title_zh
        it["summary_zh"] = summary_zh
        it["translated"] = True
        it["method"] = "nllb+manual"
        changed += 1
        print("fixed:", it.get("date"), it.get("time"), en[:60])
        if titles.get(en) != title_zh:
            titles[en] = title_zh
            added_t += 1
        if summaries.get(en) != summary_zh:
            summaries[en] = summary_zh
            added_s += 1

    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    with open(T_JSON, "w", encoding="utf-8") as f:
        json.dump(titles, f, ensure_ascii=False, indent=2)
    with open(S_JSON, "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)

    print("[fix_1100_1124] news.json 回填 %d 条；标题定稿 %d / 摘要定稿 %d" %
          (changed, added_t, added_s))
    print("[fix_1100_1124] 覆盖表 %d / %d 条" % (len(titles), len(summaries)))
    return 0 if changed == len(FIX) else 1


if __name__ == "__main__":
    raise SystemExit(main())
