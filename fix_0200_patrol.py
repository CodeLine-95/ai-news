# -*- coding: utf-8 -*-
"""02:00 例行巡检：调度新抓取条目抽查发现 10 条 NLLB 机翻硬伤，人工定稿。

硬伤清单（品牌名音译/术语崩坏）：
1) Citi 被译成「城市」；2) post-Jensen all-hands 译成「第一张 Jensen 全手」；
3) animatronics 译成「动画」；4) AI pilot sprawl 译成「人工智能飞行员流程」；
5) Qodo→科多、session review→会议评论；6) OneTrust→「一 Trust」；
7) Trina Storage 标题整句结构崩坏；8) China-Nexus→「中国-尼克苏间」；
9) Neurons Context→「神经元的机会」；10) ForShor 标题结构崩坏。

覆盖三层（与历史巡检一致）：
1) data/news.json 内条目直接回填（立即生效）
2) data/titles_override.json / data/summaries_override.json（持久卷 JSON 层）
3) 再运行 scripts/regen_overrides.py 同步到 manual_overrides.py（代码层）
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

# 用简短片段定位条目，key 取数据内真实英文标题，避免弯引号匹配问题
FIXES = [
    {
        "match": "More banks says customers using AI agents are on their own",
        "title_zh": "更多银行称，使用 AI 智能体的客户需自担风险——即便遭遇黑客攻击",
        "summary_zh": "花旗（Citi）成为最新一家对个人理财 AI 智能体踩下刹车的主要金融机构。",
    },
    {
        "match": "Inside Nvidia",
        "title_zh": "直击英伟达「后黄仁勋时代」首场全员大会：加薪与更多股权",
        "summary_zh": "临时首席执行官科莱特·克雷斯（Collette Kress）试图缓解员工对黄仁勋（Jensen Huang）离职的担忧，部分举措是承诺全面加薪。",
    },
    {
        "match": "new Star Wars animatronics",
        "title_zh": "迪士尼新款《星球大战》电子动画人偶借助 AI 与游客互动",
        "summary_zh": "迪士尼乐园的电子动画人偶虽已高度拟真，但通常只能按预设动作和流程演出，或由视线之外的木偶师操控，使其行为显得更自然。这一情况或将改变：华特迪士尼幻想工程研发部门公布了三个全新的电子与动画人偶（Audio-Animatronic）原型，它们依托亚马逊 AWS 云与 AI 能力，能针对游客互动实时做出独特回应。",
    },
    {
        "match": "Andus Labs Index",
        "title_zh": "Andus Labs 指数：AI 试点泛滥与工作流断层位居企业风险榜首",
        "summary_zh": "Andus Labs 将 AI 试点泛滥与浅层助理采用列为主要企业障碍，凸显工具使用与运营变革之间的落差。",
    },
    {
        "match": "Qodo Adds Policy-Driven Approvals",
        "title_zh": "Qodo 为 AI 生成代码新增策略驱动的审批与会话审查功能",
        "summary_zh": "Qodo 推出测试版审批工作流与会话审查预览，帮助团队在拉取请求和代码库中治理 AI 生成的代码。",
    },
    {
        "match": "OneTrust Expands AI Governance",
        "title_zh": "OneTrust 通过模型智能与持续监督扩展 AI 治理能力",
        "summary_zh": "OneTrust 2026 秋季版（Fall '26 Release）新增模型智能、AI 血缘视图与运营仪表板，同时扩展了隐私与第三方风险工具。",
    },
    {
        "match": "Trina Storage Debuts",
        "title_zh": "天合储能推出燃气-电池混合系统，为 AI 数据中心供电",
        "summary_zh": "天合储能（Trina Storage）于 2026 年 11 月 18 日在拉斯维加斯 RE+ 2026 展会上正式推出 Elementa 混合发电机组，为 AI 数据中心开发商提供一种模块化方案——在市政电网接入延迟、受限或不可用时实现现场发电。其控制架构面向 5 MW 至 1 GW 的应用规模。AI 算力需求可能骤然变化，对持续供能与即时响应提出了不同要求。",
    },
    {
        "match": "Team Cymru Report",
        "title_zh": "Team Cymru 报告审视关联中国的间谍活动对金融服务业的威胁",
        "summary_zh": "Team Cymru 的新研究审视了关联中国的间谍活动如何借由恶意软件与隐蔽中继网络背后的基础设施瞄准金融服务业。该分析于 11 月 17 日发布，将全行业威胁评估与公司对互联网基础设施的独立追踪相结合。2026 年 1 月 1 日至 6 月 1 日期间，Team Cymru 识别出 64 台符合已知 ShadowPad 命令与控制模式的服务器，以及 115 台符合 Vshell 模式的服务器。",
    },
    {
        "match": "Ivanti Gives AI Clients",
        "title_zh": "Ivanti 让 AI 客户端受控访问 Neurons 上下文数据",
        "summary_zh": "Ivanti 于 2026 年 11 月 18 日宣布推出模型上下文协议（MCP）连接，使受支持的 AI 客户端能够受控访问 Ivanti Neurons 中的运营数据——Neurons 是其记录终端、服务与暴露信息的系统记录平台。该连接旨在让 AI 的建议、调查与行动扎根于设备、数字体验、补丁、暴露面与软件情报信息。",
    },
    {
        "match": "Zapata and UMD Launch ForShor",
        "title_zh": "Zapata 与马里兰大学推出 ForShor，用于经验证的 AI 辅助量子研究",
        "summary_zh": "Zapata Quantum 与马里兰大学（UMD）推出 ForShor.ai——一项围绕 Shor 算法形式化验证实现打造的 AI 辅助量子研究开放挑战。参与者可借助 AI 提出改进方案，将答案提交至排行榜，并探索将数学与机器校验证明相联系的文档。",
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
