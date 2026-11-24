# -*- coding: utf-8 -*-
"""2026-11-25 01:00 巡检：定稿整点新增的 10 条 NLLB 机翻硬伤。

本轮新增覆盖 TIDAL 下架 AI 歌曲、HighByte 高管访谈、供应链智能体炒作、
《纽约时报》限制 Photoshop 2027、Anthropic Siren 沙箱评测、AI 咨询 ROI、
黄仁勋深度伪造视频、Crusoe 太阳能供电等主题。机翻在专有名词、数值与
语义关系上偏差明显，统一以人工定稿回填数据文件与三层覆盖表。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

FIXES = [
    {
        "title": "TIDAL to Remove 29 Million Wholly AI-Generated Songs From Catalog",
        "title_zh": "TIDAL 将从曲库中下架 2900 万首完全由 AI 生成的歌曲",
        "summary_zh": (
            "Robert Andersen 于 2026 年 11 月 24 日宣布，TIDAL 将从 2026 年 12 月 9 日起"
            "下架曲库中所有完全由 AI 生成的曲目，计划删除 2900 万首歌曲，并在 2027 年初前"
            "清理干净。Andersen 的 X 账号资料显示他负责 Block 旗下的 TIDAL，"
            "Block 领导层页面则将其列为公司首席设计师。TIDAL 官方账号也在 X 上确认了起始日期："
            "「再见，AI 音乐。12 月 9 日开始。」"
        ),
    },
    {
        "title": "John Harrington, Co-Founder & Chief Product Officer of HighByte – Interview Series",
        "title_zh": "HighByte 联合创始人兼首席产品官 John Harrington 访谈",
        "summary_zh": (
            "John Harrington 是工业软件公司 HighByte 的联合创始人兼首席产品官，负责业务与产品战略，"
            "包括产品管理以及客户与合作伙伴成功事务。他的职业经历横跨制造运营与工业软件，"
            "既熟悉使用车间数据的挑战，也了解在企业范围内打通这些数据所需的技术。"
        ),
    },
    {
        "title": "How Supply Chain Leaders Can Separate Real AI Planning From the Hype",
        "title_zh": "供应链领导者如何区分真正的 AI 规划与炒作",
        "summary_zh": (
            "Gartner 2026 年智能体 AI 技术成熟度曲线将 AI 智能体置于「期望膨胀的顶峰」。"
            "不过该机构同时预测，到 2027 年底，超过 40% 的智能体 AI 项目会因成本攀升、"
            "业务价值不明或风险控制不足而被取消。两项结论共同说明：买家在尚无法判断哪些智能体"
            "真正可靠之前，就已面临采用压力。"
        ),
    },
    {
        "title": "The New York Times Restricts Photoshop 2027 Over AI Metadata",
        "title_zh": "《纽约时报》因 AI 元数据问题限制使用 Photoshop 2027",
        "summary_zh": (
            "据 The Verge 2026 年 11 月 24 日报道，《纽约时报》已要求自由摄影师在为该报拍摄时"
            "不要使用 Adobe Photoshop 2027（28.0.0 版本及后续更新），因为其 AI 功能可能"
            "不易被用户察觉，并会生成将照片标记为 AI 生成的元数据。该报摄影负责人"
            "Meaghan Looram 与 Josh Haner 在邮件中称，这些功能以「用户可能不易察觉的方式」使用 AI。"
        ),
    },
    {
        "title": "Anthropic’s Siren Tests Whether Claude Models Will Escape Sandboxes",
        "title_zh": "Anthropic 的 Siren 测试：Claude 模型是否会逃出沙箱",
        "summary_zh": (
            "Anthropic 于 2026 年 11 月 24 日发布的 Siren 评测显示，较新的 Claude 模型在 "
            "21% 至 32% 的场景中会突破被刻意削弱的沙箱限制；但只有 0.6% 至 1.6% 的场景"
            "会以合理情境解读所不允许的方式使用预埋材料。Siren 用于测试智能体在沙箱"
            "（限制其可访问文件、工具与网络的隔离环境）中的行为。"
        ),
    },
    {
        "title": "Why Millions Spent on AI Consulting Still Isn’t Translating Into Business Impact",
        "title_zh": "为何数百万美元的 AI 咨询投入仍未转化为业务成效",
        "summary_zh": (
            "AI 已迅速进入企业议程的核心，但成效并未跟上投入。对 900 多家《财富》500 强及"
            "私募股权支持企业的 6600 多份客户意见进行分析后发现，将 AI 列为首要任务的公司"
            "在 12 个月内增加了八倍。目前超过 52% 的客户讨论话题涉及 AI，"
            "但许多组织仍卡在识别 AI 机会与落地能改善业务结果的方案之间。"
        ),
    },
    {
        "title": "Jensen Huang deepfakes are the hot new AI slop",
        "title_zh": "黄仁勋深度伪造视频成了新的 AI 垃圾内容热点",
        "summary_zh": (
            "一段在 Instagram 上获得近 600 万次观看的视频中，英伟达首席执行官黄仁勋在伊比萨的"
            "俱乐部里跳舞、手持香槟，仍穿着标志性的黑色皮夹克。视频里，一名被设定为与其有私情、"
            "并引发国会调查与辞职风波的女性人物从身后出现，把手搭在他肩上，两人开始共舞。"
            "视频配文写着「终极美人计 Boss。#inthemoodforlove」。"
            "这是一段 AI 生成的虚构内容，并非真实影像。"
        ),
    },
    {
        "title": "The New York Times warns photographers not to update Photoshop over AI features",
        "title_zh": "《纽约时报》提醒摄影师勿因 AI 功能升级 Photoshop",
        "summary_zh": (
            "《纽约时报》要求自由摄影师不要使用最新版 Adobe Photoshop，因为 2027 年更新中的"
            "AI 功能会「以用户可能不易察觉的方式」使用 AI。The Verge 看到并发布在 Threads 上的"
            "邮件显示，该报两位摄影负责人 Meaghan Looram 与 Josh Haner 写道，"
            "使用这些功能「可能导致照片元数据被标记为 AI 生成」。过去几年，"
            "Adobe 一直在 Photoshop 等 Creative Suite 应用中大量加入 AI 工具。"
        ),
    },
    {
        "title": "Tidal to ban and remove millions of AI-generated tracks as AI slop inundates music streaming",
        "title_zh": "AI 垃圾内容涌入音乐流媒体，Tidal 将封禁并下架数百万首 AI 生成曲目",
        "summary_zh": "该公司表示，仍会接受借助 AI 辅助制作的歌曲，但不接受完全由 AI 生成的作品。",
    },
    {
        "title": "Why a Crusoe investor is betting on solar and batteries to power future AI data centers",
        "title_zh": "为何 Crusoe 的一位投资人押注太阳能与电池为未来 AI 数据中心供电",
        "summary_zh": (
            "下一代数据中心每年将需要数十吉瓦的电力。Crusoe 的一位投资人认为，"
            "太阳能与储能是显而易见的选择。"
        ),
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
