# -*- coding: utf-8 -*-
"""2026-11-03 02:45 巡检：修复 02:32 周期新增 1 条（Apple 家庭机器人）。

NLLB 直译缺陷：
1) 「former Apple CEO Tim Cook」被拆成「果前首席执行官蒂姆·库克」——
   Apple 意译成单字「果」，former 的「前」又跑到品牌名后面，
   产出完全读不通的「果前首席执行官」。
2) 媒体名 The Information 被译成引号包裹的「信息」，
   中文读者无从判断是哪家媒体。
3) 首句结构崩坏：「第一个首次亮相可能是设计的家庭机器人」——
   the first to debut may be a home robot designed to… 被拆成
   「第一个」「首次亮相」「可能是设计的」三个碎片，主谓宾全乱。
4) 「HomeView 静止智能显示器」—— stationary smart display 译成「静止」
   属用词错误，应为「固定式」。
5) 标题「点灯」「尖叫你的猫」是逐词直译，中文口语对应
   「开灯」「冲你的猫大叫」。

同时给 Ebix/Intentyx 补上标题定稿（上一轮只定了摘要）。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

TITLE_FIX = {
    "Apple’s roaming home robot may do FaceTime, switch lights on, and yell at your cat":
        "Apple 的漫游家用机器人可能会 FaceTime 通话、开灯，还会冲你的猫大叫",
    "Ebix and Intentyx Launch SMARE to Track AI Agent Behavior":
        "Ebix 与 Intentyx 推出 SMARE，用于追踪 AI 智能体行为",
}

SUMMARY_FIX = {
    "Apple’s roaming home robot may do FaceTime, switch lights on, and yell at your cat":
        "Apple 新任 CEO 约翰·特纳斯（John Ternus）显然正在推动公司开发家用机器人，"
        "而首个亮相的产品可能是一款可自主漫游的家用机器人：它支持 FaceTime 通话，"
        "并能在有人进入房间时自动开灯。"
        "参与 Apple 机器人项目的知情人士告诉《The Information》，"
        "这款由人工智能驱动的家用机器人代号为 J595，"
        "可能命名为 HomeView Ultra，与 Apple 新推出的 HomeView 固定式智能显示器形成配套。"
        "据报道，公司目标在 2027 年前后推出该机器人产品，售价可能为 1,000 美元或更高，"
        "但研发延期可能将其推迟到 2028 年。"
        "这款家用机器人的最早原型在 2018 年就已亮相，并获时任 Apple CEO 蒂姆·库克批准继续推进。",
}


def main():
    with open(os.path.join(DATA, "news.json"), encoding="utf-8") as f:
        db = json.load(f)
    items = db["items"] if isinstance(db, dict) else db

    hit_t = hit_s = 0
    for it in items:
        t = it.get("title", "")
        if t in TITLE_FIX:
            it["title_zh"] = TITLE_FIX[t]
            it["translated"] = True
            it["method"] = "nllb+manual"
            hit_t += 1
            print("fix title:", it["date"], it["time"], it["source"], "|", t[:50])
        if t in SUMMARY_FIX:
            it["summary_zh"] = SUMMARY_FIX[t]
            it["translated"] = True
            it["method"] = "nllb+manual"
            hit_s += 1

    with open(os.path.join(DATA, "news.json"), "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    for name, fix in (("titles_override.json", TITLE_FIX),
                      ("summaries_override.json", SUMMARY_FIX)):
        path = os.path.join(DATA, name)
        cur = {}
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                cur = json.load(f)
        cur.update(fix)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cur, f, ensure_ascii=False, indent=2)

    print("fixed titles:", hit_t, "/", len(TITLE_FIX))
    print("fixed summaries:", hit_s, "/", len(SUMMARY_FIX))


if __name__ == "__main__":
    main()
