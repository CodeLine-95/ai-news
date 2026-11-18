# -*- coding: utf-8 -*-
"""05:00 例行巡检：人工定稿 10 条 NLLB 机翻硬伤。

本轮新增条目中的问题：品牌名音译错（Wispr Flow→威斯普流、Vitruvian→维特鲁维亚）、
术语错（agent→经纪人、sugar daddy→糖爸爸、land grab→土地抢占、flapping-wing→飞翔翼）、
语义崩坏（"无论什么都没有摇到头脑然利的船"）、人名错（Jensen Huang→詹森·胡安、
unfazed→不满）、JS 脚本混入译文、语序崩坏（MIT 微机器人/Perplexity Brain）。

固化覆盖三层：
1) data/news.json 内条目直接回填
2) data/titles_override.json / data/summaries_override.json（JSON 层）
3) 再运行 scripts/regen_overrides.py 同步到 manual_overrides.py（代码层）
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

FIXES = [
    {
        "match": "Snap Lets Coding Assistants Build and Publish Snapchat Lenses",
        "title_zh": "Snap 开放编码助手构建并发布 Snapchat 镜头（Lens）",
        "summary_zh": (
            "Snap 于 2026 年 11 月 18 日推出 Easy Lens CLI——一款免费命令行工具，"
            "让开发者借助 Claude Code、Codex 和 Cursor 等 AI 编码助手构建、测试并发布 Snapchat "
            "镜头（Lens）。它将 Snap 基于提示词的 Easy Lens 创作系统从网页和移动端扩展到开发者"
            "现有的软件工具链中。开发者只需用自然语言描述想要的镜头即可开始。"
        ),
    },
    {
        "match": "Sam Altman says his life is so weird that he’s unfazed by Andrew Garfield portraying him",
        "title_zh": "Sam Altman 称自己的生活太过离奇，对 Andrew Garfield 在电影中饰演自己毫不在意",
        "summary_zh": (
            "Altman 表示：「这算不上我人生中最离奇的十件事之一。」"
        ),
    },
    {
        "match": "Wispr Flow Brings AI Meeting Notes to iPhone",
        "title_zh": "Wispr Flow 将 AI 会议纪要功能带到 iPhone",
        "summary_zh": (
            "Wispr Flow 将 AI 会议记录能力扩展到 iPhone，把面对面的交谈与桌面端笔记打通，"
            "同时保留了重要的录音与隐私限制。"
        ),
    },
    {
        "match": "Snapchat now lets developers build AR Lenses with AI assistants like Claude Code and Cursor",
        "title_zh": "Snapchat 现支持开发者借助 Claude Code、Cursor 等 AI 助手构建 AR 镜头",
        "summary_zh": (
            "Snapchat 表示，镜头创作者可以用日常语言描述想要的镜头，其 AI 助手会全程处理制作流程。"
        ),
    },
    {
        "match": "Trump’s latest land grab is an AI hub in the Philippines",
        "title_zh": "特朗普最新「圈地」：在菲律宾打造 AI 中心",
        "summary_zh": (
            "据菲律宾本地新闻机构 Rappler 报道，唐纳德·特朗普总统于 2026 年 11 月 17 日抵达"
            "马尼拉维拉莫尔空军基地时受到高规格接待——至少五位选美皇后到场迎接。走下舷梯时，"
            "一名儿童向他递上美国和菲律宾的小国旗。乐队奏起特朗普集会上的保留曲目《YMCA》，"
            "更多身着传统喇叭袖罩衫的女孩和戴宽檐帽的青年随之起舞。机场外，数百名抗议者挤满"
            "街道，举着标语——其中至少有一口道具棺材——高喊「特朗普滚出去」。"
        ),
    },
    {
        "match": "MIT Microrobot Flies Without Motion Capture Using Onboard Sensors",
        "title_zh": "MIT 微型机器人凭借机载传感器实现无动作捕捉飞行",
        "summary_zh": (
            "麻省理工学院研究人员于 2026 年 11 月 18 日宣布推出一款重 1.29 克的扑翼机器人，"
            "它依靠机载传感与计算即可悬停、跟随轨迹并降落，无需依赖外部动作捕捉系统。"
            "发表于《科学·机器人》（Science Robotics）的论文显示，该机器人通过传感器、"
            "状态估计器与底层控制器的组合实现了厘米级定位精度。在一次 30 秒的实验中，"
            "机器人脱离动作捕捉系统自主飞行，成功避开障碍并降落在一朵向日葵上。"
        ),
    },
    {
        "match": "IGEL Tops $1 Billion Valuation With Strategic Investment From Vitruvian Partners",
        "title_zh": "IGEL 获 Vitruvian Partners 战略投资，估值突破 10 亿美元",
        "summary_zh": (
            "IGEL 宣布获得由 Vitruvian Partners 管理或提供咨询的基金的战略投资，估值超过 "
            "10 亿美元，这家终端安全公司由此跻身独角兽行列。随着 IGEL 扩展其软件平台以保障"
            "企业安全访问和业务连续性，Vitruvian 将加入现有投资方 TA Associates。11 月 18 日的"
            "公告未披露投资金额；10 亿美元指的是公司估值，而非募集的资金。"
        ),
    },
    {
        "match": "What’s next for Nvidia? Whatever doesn’t rock the mind-bogglingly profitable boat",
        "title_zh": "英伟达下一步走向何方？只要不颠覆这台利润惊人的「印钞机」就好",
        "summary_zh": (
            "如果有人每秒给你 8,300 美元，你会怎么做？这正是英伟达如今的净利润水平——"
            "读完这段话的工夫，英伟达很可能又赚了 4.5 万美元有余。人们很容易看着这家刚刚因"
            "一连串丑闻失去其富有远见的创始人兼 CEO 的公司，认为它乃至整个 AI 行业都陷入了"
            "大麻烦。也许确实如此？但请理解：英伟达并非那种平平无奇、换个新 CEO 就能修好"
            "问题的半成功公司。"
        ),
    },
    {
        "match": "Perplexity Brain Creates and Updates Agent Skills From Experience",
        "title_zh": "Perplexity Brain 能从经验中创建并更新智能体技能",
        "summary_zh": (
            "Perplexity 于 2026 年 11 月 18 日表示，其计算机智能体的个性化系统 Brain 现已能够"
            "创建并更新可复用的智能体技能。在 2026 年 8 月 1 日至 11 月 14 日期间，Brain 已为"
            "超过 2 万名用户编写了逾 8 万项个人技能。该扩展旨在捕捉通用模型无法预先获知的"
            "特定工作流程偏好与操作程序，从而减少重复的解释与纠正。"
        ),
    },
    {
        "match": "What is Nvidia without AI’s sugar daddy in charge?",
        "title_zh": "如果没有 AI 这位「金主」掌舵，英伟达还算什么？",
        "summary_zh": (
            "打造一家成功的公司，意味着即使没有你它也能顺畅运转。黄仁勋真的打造出了一家"
            "成功的公司吗？如果这场轰轰烈烈的 AI 革命完全系于一人之身，那么 AI 或许并不像"
            "我此前以为的那样是一项强韧的技术。尽管如此，硅谷现在仍有一批人坚称他不可或缺。"
            "例如，如果埃隆·马斯克所言属实，那么黄仁勋（英伟达前首席执行官，该公司市值约 3 "
            "万亿美元）一直与供应商达成「与黄仁勋握个手」式的交易——「而不是书面合同」，"
            "马斯克写道。这些话讲给股东听，确实耐人寻味。"
        ),
    },
]


def main():
    with open(os.path.join(DATA, "news.json"), encoding="utf-8") as f:
        db = json.load(f)
    items = db["items"] if isinstance(db, dict) else db

    tpath = os.path.join(DATA, "titles_override.json")
    spath = os.path.join(DATA, "summaries_override.json")
    tov = json.load(open(tpath, encoding="utf-8")) if os.path.exists(tpath) else {}
    sov = json.load(open(spath, encoding="utf-8")) if os.path.exists(spath) else {}

    changed = 0
    for fx in FIXES:
        hit = None
        for it in items:
            if fx["match"].lower() in (it.get("title") or "").lower():
                hit = it
                break
        if not hit:
            print("MISS:", fx["match"])
            continue
        en = hit["title"]
        hit["title_zh"] = fx["title_zh"]
        hit["summary_zh"] = fx["summary_zh"]
        hit["translated"] = True
        hit["method"] = "nllb+manual"
        tov[en] = fx["title_zh"]
        sov[en] = fx["summary_zh"]
        changed += 1
        print("fixed:", hit.get("date"), hit.get("time"), en[:70])

    with open(tpath, "w", encoding="utf-8") as f:
        json.dump(tov, f, ensure_ascii=False, indent=2)
    with open(spath, "w", encoding="utf-8") as f:
        json.dump(sov, f, ensure_ascii=False, indent=2)
    with open(os.path.join(DATA, "news.json"), "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    print("changed:", changed, "/", len(FIXES))


if __name__ == "__main__":
    main()
