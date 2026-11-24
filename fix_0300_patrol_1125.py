# -*- coding: utf-8 -*-
"""2026-11-25 03:00 巡检：定稿整点新增的 5 条 NLLB 机翻。

本轮新增覆盖 iFood 编码智能体规模化、David Fincher 新片 AI 争议、
Anthropic 服务器侧技能与后台任务、亚马逊无人机坠机 FAA 调查、
Anthropic 股价破发等主题。机翻在专有名词（Anthropic→「人类」、
FAA「调查」→「探测器」）与语义关系上偏差明显，统一人工定稿，
并回填数据文件与三层覆盖表。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

FIXES = [
    {
        "title": "How iFood scales coding agents across 15,000 repositories",
        "title_zh": "iFood 如何把编码智能体扩展到 15,000 个代码仓库",
        "summary_zh": "",
    },
    {
        "title": "David Fincher is being dragged for suspected use of AI in his latest film",
        "title_zh": "大卫·芬奇因新片涉嫌使用 AI 遭质疑",
        "summary_zh": (
            "虽然大卫·芬奇的影迷一直期待《克里夫·布斯的进一步错误冒险》——"
            "布拉德·皮特主演的《好莱坞往事》续集——但早期点映引发了对影片是否使用生成式 AI 的质疑。"
            "有人声称这部电影充斥着诡异且前后不一致的画面，感觉更像粗制滥造的内容，"
            "而不是这位曾执导《搏击俱乐部》《社交网络》等精致作品的导演应有的水准。"
        ),
    },
    {
        "title": "Anthropic Brings Server-Supplied Skills and Background Tasks to Claude",
        "title_zh": "Anthropic 为 Claude 引入服务器提供的技能与后台任务",
        "summary_zh": (
            "Anthropic 于 2026 年 11 月 24 日宣布，Skills over MCP 已在 Claude 与 Claude Code 中"
            "进入公开测试阶段，Tasks 与 Elicitation 正式可用，文件上传功能也即将推出。"
            "这些功能让连接的服务器能够提供工作流指导、运行耗时任务、请求用户输入，"
            "并在文件上传上线后与 Claude 交换文件。"
        ),
    },
    {
        "title": "FAA opens probe after Amazon delivery drone clips cable, crashes into garage",
        "title_zh": "亚马逊送货无人机刮断光缆、撞上车库后，FAA 启动调查",
        "summary_zh": (
            "一架亚马逊送货无人机在刮到光纤线缆后坠落在车库屋顶上，"
            "目前已成为美国联邦航空管理局（FAA）的调查对象。"
            "随着亚马逊等公司在美国各地加快空中送货运营，又一起送货无人机事故被视频记录下来。"
            "据 WXYZ 7 News Detroit 报道，11 月 20 日的事件始于密歇根州亨廷顿森林市的 "
            "Jim Brennan 夫妇下单购买洗发水，并惊讶地收到包裹将在七分钟内由无人机送达的通知。"
            "无人机把包裹投到 Brennan 家后院后，螺旋桨被光纤线缆缠住而失灵，机身横向翻滚，"
            "最终卡在邻居车库屋顶与一些电线之间。"
        ),
    },
    {
        "title": "Anthropic shares fall below IPO price, a worrying sign for AI startups",
        "title_zh": "Anthropic 股价跌破 IPO 发行价，为 AI 初创公司敲响警钟",
        "summary_zh": "Anthropic 上市后的股价低迷可能给 AI 初创公司的估值带来压力。",
    },
]


def main():
    db = json.load(open(DATA, encoding="utf-8"))
    items = db["items"] if isinstance(db, dict) else db
    titles = json.load(open(T_JSON, encoding="utf-8"))
    summaries = json.load(open(S_JSON, encoding="utf-8"))

    by_title = {fx["title"].strip(): fx for fx in FIXES}
    changed = 0
    for it in items:
        fx = by_title.get((it.get("title") or "").strip())
        if fx:
            it["title_zh"] = fx["title_zh"]
            it["summary_zh"] = fx["summary_zh"]
            it["translated"] = True
            it["method"] = "nllb+manual"
            changed += 1
            print("fixed:", it.get("date"), it.get("time"), it.get("title", "")[:60])

    for fx in FIXES:
        titles[fx["title"]] = fx["title_zh"]
        summaries[fx["title"]] = fx["summary_zh"]

    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    with open(T_JSON, "w", encoding="utf-8") as f:
        json.dump(titles, f, ensure_ascii=False, indent=2)
    with open(S_JSON, "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)

    print("回填条目:", changed)
    assert changed == len(FIXES), "定稿条目数不符：%d != %d" % (changed, len(FIXES))


if __name__ == "__main__":
    main()
