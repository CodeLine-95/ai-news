# -*- coding: utf-8 -*-
"""04:00 例行巡检：人工定稿 10 条 NLLB 机翻硬伤。

问题类型：品牌名被音译/意译错（Databricks→数据片、Weebit Nano→微信纳米、
SoundCloud→CloudCloud、Reddit→推特、Ramp→拉普、StitchStudio→斯蒂奇斯图迪奥、
Instagram's Edits→易斯加、neolabs→新浪）、金额错（8M→8800万）、
术语错（sandboxing→智能体砂、dot-com boom→点通勃、workload→工作负担）。

按历史惯例固化覆盖三层，防止下一轮被模型译文覆盖：
1) data/news.json 内条目直接回填（立即生效）
2) data/titles_override.json / data/summaries_override.json（持久卷 JSON 层）
3) 再运行 scripts/regen_overrides.py 同步到 manual_overrides.py（代码层）
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

FIXES = [
    {
        "match": "Databricks Launches Native Genie Plugins for Four AI Agents",
        "title_zh": "Databricks 为四款 AI 智能体推出原生 Genie 插件",
        "summary_zh": (
            "2026 年 11 月 11 日，Databricks 为 ChatGPT、Claude、Microsoft Copilot Cowork 和 "
            "Grok Bot 推出原生 Genie 插件。这些集成让四款智能体都能受控访问 Databricks 中保存的"
            "业务上下文，其他兼容智能体仍可通过 Genie One MCP 服务器连接。在此次发布前，"
            "Databricks 就已将 Genie 接入外部助手。"
        ),
    },
    {
        "match": "Weebit Nano Launches Matrix ReRAM Research Program",
        "title_zh": "Weebit Nano 推出面向存内 AI 计算的 Matrix ReRAM 研究计划",
        "summary_zh": (
            "Weebit Nano 启动了 Weebit Matrix 存内计算研究计划，向学术界和产业界研究人员开放 "
            "ReRAM 硬件，以测试一种运行 AI 计算的不同路径：在数据存储的位置直接完成计算。"
            "该计划提供基于 32×32 交叉开关阵列构建的研究套件，支持向量矩阵乘法、卷积以及"
            "脉冲神经网络等运算。"
        ),
    },
    {
        "match": "SoundCloud Adds Direct Publishing for ElevenMusic Creators",
        "title_zh": "SoundCloud 为 ElevenMusic 创作者新增直接发布功能",
        "summary_zh": (
            "SoundCloud 于 2026 年 11 月 5 日宣布，创作者可以直接将音乐从 ElevenMusic 发布到 "
            "SoundCloud；新旧 SoundCloud Artist Pro 订阅用户可免费获得三个月 ElevenMusic Pro。"
            "直接发布功能省去了制作曲目与分发之间单独的导出、上传步骤。"
        ),
    },
    {
        "match": "Reddit Tests AI Product Reviews Built From Community Comments",
        "title_zh": "Reddit 测试基于社区评论生成的 AI 产品评测",
        "summary_zh": (
            "Reddit 于 2026 年 11 月 10 日宣布，正在测试 Reddit Reviews——一项由 AI 整理的购物"
            "功能，将符合条件的社区讨论整合为产品页面，包含情绪总结、反复出现的主题以及原始"
            "评论链接。初始测试覆盖约 1 万款被频繁讨论的商品。该功能将在未来数周面向美国 iOS、"
            "Android 和网页端用户推出，首批涵盖电子、健康与美容、家居与园艺、时尚与服饰等品类。"
        ),
    },
    {
        "match": "Ramp data shows AI spending stalling just as Anthropic nears its IPO",
        "title_zh": "Ramp 数据显示：Anthropic 临近 IPO 之际，AI 支出却陷入停滞",
        "summary_zh": (
            "AI 使用量持续攀升，但支出已经停滞。最大支出方纷纷降价并采取更精细的成本控制，"
            "这可能挑战投资者对 AI 高速增长的预期。"
        ),
    },
    {
        "match": "Lets AI Agents Build Rough Cuts",
        "title_zh": "Instagram 的 Edits Mac 版让 AI 智能体制作粗剪",
        "summary_zh": (
            "The Verge 于 2026 年 11 月 5 日报道，Instagram 的独立视频编辑器 Edits 现已推出免费的 "
            "macOS 应用，新增 4K 导出，并支持 AI 智能体通过模型上下文协议（MCP）使用其桌面工具。"
            "Instagram 的 Edits 产品管理负责人 Matthew Simari 表示，桌面版为应用内所有工具提供了 "
            "MCP 接口，创作者对桌面版和 AI 计划的需求共同促成了这次扩展。"
        ),
    },
    {
        "match": "Frontier Radar #5: If AGI is so close",
        "title_zh": "前沿雷达 #5：AGI 近在眼前，为何众人纷纷离开？新兴实验室及其押注",
        "summary_zh": (
            "OpenAI 声称已进入 AGI 时代，NVIDIA 首席执行官黄仁勋也称 AGI 已经到来。与此同时，"
            "当今模型的共同缔造者正离开 OpenAI、Google DeepMind 和 Meta 去创办自己的实验室，"
            "在没有产品的情况下募集数十亿美元。原因何在？他们押注仅靠现有路线远远不够。"
            "我们按研究押注梳理了 45 家新兴实验室，描绘它们试图克服的当前 AI 局限，"
            "审视其成果中已初现端倪的部分，并解释为何 NVIDIA 总能笑到最后。"
        ),
    },
    {
        "match": "StitchStudio Raises $8M to Expand Insurance AI",
        "title_zh": "StitchStudio 融资 800 万美元，扩展保险 AI 产品与客户支持",
        "summary_zh": (
            "StitchStudio 于 2026 年 11 月 11 日宣布完成 800 万美元融资，由 Voyager Capital 领投，"
            "用于扩展其保险 AI 产品、客户成功团队，以及面向运营商和经纪商的自助服务工具。"
            "Lookout Ventures 和 Grit Capital Partners 参投，ManchesterStory 与 BrokerTech Fund "
            "继续追加投资，另有多位保险业资深人士提供支持。"
        ),
    },
    {
        "match": "Agents may soon be the main workload",
        "title_zh": "智能体或很快成为主要工作负载，而大多数时候它们什么也没做",
        "summary_zh": (
            "随着 AI 智能体承担越来越多的企业工作，智能体沙箱已从可选的补充措施变成基本要求。"
            "每一个编写代码、运行工具或驱动浏览器的智能体都需要坚固的隔离边界；"
            "而这些边界又不能带来失控的算力账单。"
        ),
    },
    {
        "match": "What Will Remain After AI? Where Value Survives",
        "title_zh": "AI 之后还剩什么？价值何处存续",
        "summary_zh": (
            "今年 10 月，多位重量级投资者指出，AI 市场越来越像 1990 年代末的互联网泡沫。"
            "亿万富翁、桥水基金（Bridgewater Associates）创始人瑞·达利欧（Ray Dalio）将这一"
            "局面形容为「典型泡沫」——企业在利率上升之际通过举债为 AI 基础设施融资。"
            "紧随其后，城堡投资（Citadel LLC）创始人兼首席执行官肯·格里芬（Ken Griffin）"
            "也对 AI 领域的巨额投资能否获得回报表示怀疑。"
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
