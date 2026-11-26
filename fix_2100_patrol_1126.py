# -*- coding: utf-8 -*-
"""21:00 例行巡检：定稿本轮新增条目的 NLLB 机翻误译。

21:00 整点抓取净新增 2 条（Unite.AI / GigaChat 4、Unite.AI / ROBOTERA 人形机器人）。
重点误译：
- GigaChat 4 被译成「吉加 4 个」，Debuts 被误解为「首次使用」，上下文语境词误译
- ROBOTERA 被泛化为「机器人」，humanoid robots 被译成「人类机器人」，
  parcel induction 被译成「包装试验」

按项目既有模式回填 news.json + JSON 覆盖表，再由
scripts/regen_overrides.py 同步到代码层 manual_overrides.py。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

FIX = {
    "GigaChat 4 Debuts With 1M-Token Context and Two Model Sizes": (
        "GigaChat 4 发布：100 万 token 上下文与两种模型规模",
        "GigaChat 团队于 2026 年 11 月 26 日宣布推出 GigaChat 4，发布 708B 与 37B 参数的混合专家（MoE）模型，原生支持 100 万 token 上下文窗口。两者每个 token 仅激活部分参数，支持工具调用与多步骤智能体任务，并可在同一检查点内按请求选择「即时」或「推理」响应。旗舰版 708B-A41B 每 token 约激活 41B 参数，紧凑版 37B-A4B 约激活 3.8B 参数。",
    ),
    "ROBOTERA Deploys 45 Humanoid Robots at China Post’s Hangzhou Hub": (
        "ROBOTERA 在中国邮政杭州枢纽部署 45 台人形机器人",
        "ROBOTERA 在 2026 年 11 月 26 日的公告中披露，其 45 台人形机器人正在中国邮政杭州邮件处理中心进行包裹导入测试。中国邮政杭州中心于 2026 年 4 月正式启动该测试项目。ROBOTERA 称，这是全国同类邮政运营中规模最大的机器人测试部署。",
    ),
}


def main():
    db = json.load(open(os.path.join(DATA, "news.json"), encoding="utf-8"))
    items = db["items"] if isinstance(db, dict) else db

    tpath = os.path.join(DATA, "titles_override.json")
    spath = os.path.join(DATA, "summaries_override.json")
    tov = json.load(open(tpath, encoding="utf-8")) if os.path.exists(tpath) else {}
    sov = json.load(open(spath, encoding="utf-8")) if os.path.exists(spath) else {}

    changed = 0
    matched = set()
    for it in items:
        en = it.get("title") or ""
        if en not in FIX:
            continue
        matched.add(en)
        title_zh, summary_zh = FIX[en]
        if it.get("title_zh") != title_zh:
            it["title_zh"] = title_zh
            it["translated"] = True
            it["method"] = "nllb+manual"
            changed += 1
            print("[fix] title:", en[:60], "->", title_zh)
        if it.get("summary_zh") != summary_zh:
            it["summary_zh"] = summary_zh
            it["translated"] = True
            it["method"] = "nllb+manual"
            changed += 1
            print("[fix] summary:", en[:60])
        tov[en] = title_zh
        sov[en] = summary_zh

    missing = set(FIX) - matched
    if missing:
        print("[warn] 未匹配到条目:", missing)

    json.dump(tov, open(tpath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(sov, open(spath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(db, open(os.path.join(DATA, "news.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("[fix] 变更 %d 处 | 覆盖表 标题 %d 条 / 摘要 %d 条"
          % (changed, len(tov), len(sov)))


if __name__ == "__main__":
    main()
