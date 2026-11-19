# -*- coding: utf-8 -*-
"""05 点例行巡检：对本轮 13 条 NLLB 机翻硬伤人工定稿。

问题：产品名/公司名误译（Muse Charm→「Muse 迷人」、Chenghengwei→「切威」、
Blast Radius→「爆炸射线」、Strands→「字符串」）、术语错译（Foundry→「工厂」、
gated→「关闭版本」、consenting speaker→「同意扬声器」）、英文标题残留、
以及 3 条语义截断。写入三层覆盖表：JSON 标题表 / JSON 摘要表 / news.json。
随后运行 scripts/regen_overrides.py 同步到代码层 manual_overrides.py。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")
NEWS = os.path.join(BASE, "data", "news.json")

# 英文原标题 -> (定稿中文标题, 定稿中文摘要)
FINAL = {
    "Meta’s Muse Charm Price and Free Verizon 5G Plan Detailed in Report": (
        "报告披露 Meta Muse Charm 定价及免费 Verizon 5G 套餐",
        "据 The Information 于 2026 年 11 月 19 日报道、经 The Verge 转载，Meta 计划将其 Muse Charm AI 设备定价为 300 美元，并附赠为期 12 个月的免费 Verizon 5G 数据套餐。Meta 尚未正式公布价格。报道还称，Meta 另款智能手表的发布已推迟至 2027 年，因公司正全力将 Charm 推向市场。",
    ),
    "PostgreSQL 19 Released": (
        "PostgreSQL 19 发布",
        "以往 PostgreSQL 多在 9 月发布新版本，但今年晚了两个月，主要原因是 PostgreSQL 团队需要应对由 AI 报告的漏洞潮引发的一系列问题。这个版本绝对值得等待。作者最喜欢的新特性是：对于将读请求发往备库的应用程序，PostgreSQL 19 通过新的 WAIT FOR LSN 命令实现了读己之写一致性。备库上的会话可使用 WAIT FOR LSN，等待备库将预写日志（WAL）重放到指定的日志序列号（LSN）后再执行查询，这样应用就能读到它刚刚写在主库上的数据。实际用法如下：UPDATE movie SET genre = 'Dramatic' WHERE genre = 'Drama'; SELECT pg_current_wal_insert_lsn(); 后者会返回类似 0/0306EE20 的值。",
    ),
    "NVIDIA Expands Microsoft AI Collaboration with Vera Rubin and Nemotron": (
        "NVIDIA 借 Vera Rubin 与 Nemotron 扩大与微软的 AI 合作",
        "2026 年 11 月 19 日，NVIDIA 在 Microsoft Ignite 大会上宣布扩大与微软的 AI 合作，涵盖在 Azure 数据中心运行的 Vera Rubin NVL72 系统、在 Microsoft Foundry 中对 Nemotron 开放模型更广泛的支持，以及面向本地系统、工业边缘设备和 Windows 云 PC 的部署选项。两家公司正通过 Azure 的 Vera Rubin 预览计划，扩大由 Vera Rubin NVL72 驱动的 Azure 虚拟机的使用范围。",
    ),
    "Chenghengwei Raises Nearly RMB 200M Series A to Scale Edge AI SoC Output": (
        "边缘 AI 芯片厂商 Chenghengwei 完成近 2 亿元 A 轮融资以扩大 SoC 产能",
        "Chenghengwei 于 2026 年 11 月 19 日宣布，公司近期完成近 2 亿元人民币的 A 轮融资。中金资本（CICC Capital）、中车资本（CRRC Capital）、Addor Capital、西创兴务（Xichuang Xingwu）与启安投资（Qi'an Investment）参与了这家边缘 AI 芯片开发商的融资。资金主要用于日常运营与业务扩张，具体用于支持其边缘 AI 系统级芯片（SoC）产品的规模化量产与市场交付。",
    ),
    "The Jensen Huang Blast Radius Has Hit His Favorite Restaurants": (
        "黄仁勋的影响力波及他最爱的餐厅",
        "在中国台湾，一些餐饮摊主正与英伟达首席执行官黄仁勋划清界限，另一些则坚定支持他。一位店家说：“他又没杀人，也没纵火。”",
    ),
    "Google Adds a Sidebar for Recent AI Searches to Its Desktop Homepage": (
        "Google 在桌面首页新增近期 AI 搜索侧边栏",
        "Google 搜索产品副总裁 Robby Stein 于 2026 年 11 月 19 日宣布，Google 正在全球范围推出桌面首页的可折叠侧边栏，用于查找和恢复近期进行的 AI 搜索。这项改动针对的是需要经过多轮交互、而非一次回答即告结束的搜索。Stein 表示，此类查询正越来越多；在测试中，该侧边栏帮助用户取得进展并继续浏览网页。",
    ),
    "Meta’s Muse Charm might cost $300": (
        "Meta Muse Charm 售价或为 300 美元",
        "据 The Information 报道，Meta 计划将 Muse Charm 定价为 300 美元。这是一款带屏幕的小设备，用户可借此与 Muse AI 智能体聊天。CEO 马克·扎克伯格今年早些时候展示了该设备，并称公司预计在 12 月的假日季及时出货 Charm，但当时未透露价格。扎克伯格在发布 Muse Charm 时表示，公司已将完整的 Muse 体验（包括实时语音和虚拟化身技术）装进这款设备。它配有指纹传感器，轻触即可与 Muse AI 智能体对话，无需解锁手机或打开应用。",
    ),
    "AWS Adds Strands Defaults and Lifecycle Hooks to AgentCore Harness": (
        "AWS 为 AgentCore Harness 增加 Strands 默认配置与生命周期钩子",
        "亚马逊云科技（AWS）于 2026 年 11 月 19 日宣布，将升级 Amazon Bedrock AgentCore Harness 以采用开源的 Strands 框架，加入不断演进的托管默认配置、更多内置工具以及确定性的生命周期钩子，且无需新增资源类型或集成。Strands 于 2026 年早些时候以 Apache 2.0 许可证发布，提供了一套组装好的智能体基础能力，涵盖指令、工具与上下文管理。",
    ),
    "Traumatized teens sue school, cops after Doritos bag triggers AI gun alert": (
        "一袋多力多滋触发 AI 枪支警报，受惊学生起诉学校与警方",
        "2025 年 10 月，四名黑人高中生在橄榄球训练后分享 Cool Ranch 口味的多力多滋薯片，放松身心、等待家人来接。就在这种任何参加课后活动的青少年都熟悉的片刻宁静中，学校的 AI 枪支检测系统突然将其中一名手拿薯片袋的学生标记为潜在枪手。两分钟内，巴尔的摩县公立学校的官员查看与该警报关联的监控录像后，认定并无实际威胁。他们认出了那是多力多滋的袋子，随即取消了警报——该警报不仅通知了链条上的其他校方人员，还通知了巴尔的摩县警察局，告知无需响应。这场误报本可就此结束，在发生与警方那场造成心理创伤的校园冲突之前——但事情并没有。",
    ),
    "Amazon Polly Adds Gated Voice Cloning for Custom Brand Voices": (
        "Amazon Polly 推出面向品牌定制声音的门控式语音克隆",
        "亚马逊云科技于 2026 年 11 月 19 日宣布发布 Amazon Polly，以门控发布的形式正式开放语音克隆功能。获批的 AWS 账户可基于一位同意授权者的录音，创建定制的文本转语音声音，上线初期支持七种语言。访问权限按 AWS 账户逐一开通。部分 Polly 客户已获得该能力，其他客户可联系其 AWS 账户团队或提出申请。",
    ),
    "Google is putting AI chats right on the homepage": (
        "Google 将 AI 对话直接搬上首页",
        "Google 正在更新其首页，加入 AI 搜索功能。在 X 上的一篇帖子中，Google 产品副总裁 Robby Stein 展示了如今如何打开一个可折叠侧边栏，查看并继续你的 AI 对话。根据 Stein 分享的动图，点击屏幕左侧出现的灰色条即可打开侧边栏。从那里，Google 会列出你通过 AI 模式进行的搜索，并支持开启新对话、搜索历史对话，或连接 Gemini 笔记本（Gemini Notebook）。",
    ),
    "NVIDIA and Microsoft Expand Accelerated Computing From Azure to Windows PCs": (
        "NVIDIA 与微软将加速计算从 Azure 扩展至 Windows PC",
        "NVIDIA 与微软正在扩展其全栈合作，帮助各类组织构建、定制和部署智能应用——从 Azure 上的下一代基础设施，到工业系统与 Windows PC。在 Microsoft Ignite 大会上，两家公司正扩大由 NVIDIA Vera Rubin NVL72 系统驱动的 Azure 虚拟机的供应，并通过 Microsoft Foundry 增加 NVIDIA 开放模型的客户可用性与定制能力，同时提供在边缘侧运行 AI 的新选项——企业正是在边缘产生并使用其数据。微软还在使用 NVIDIA 技术加速自身模型与服务，包括用于后训练的 NVIDIA Dynamo 推理软件，以及用于 Bing 搜索模型的 NVIDIA RTX PRO 6000 Blackwell GPU。",
    ),
    "More Managers Require AI at Work, but Employees See Its Role Differently": (
        "更多管理者要求工作中使用 AI，但员工对其角色的看法不同",
        "Slingshot 对 500 名美国员工与管理者的调查发现，工作场所对 AI 的强制使用要求正日益增多，而两类人群对技术依赖程度的看法存在差距。",
    ),
    # 历史遗留硬伤：blast radius 被误译为「爆炸射线」
    "AI Security in 2027: Agent Permissions Will Define the Blast Radius": (
        "2027 年 AI 安全：智能体权限将定义影响范围",
        "想象一名员工让 AI 助理整理塞满的收件箱。这项任务听起来无害，直到某条消息说服助理打开客户记录、导出附件或发起付款请求。安全问题已不再只是答案是否可信，而是软件是否有权把误解变成行动。这正是 2027 年智能体安全背后的压力所在：公司希望助理能够真正完成工作。",
    ),
}


def main():
    t = json.load(open(T_JSON, encoding="utf-8"))
    s = json.load(open(S_JSON, encoding="utf-8"))
    news = json.load(open(NEWS, encoding="utf-8"))
    items = news.get("items", [])

    hit = 0
    for en, (zh_t, zh_s) in FINAL.items():
        t[en] = zh_t
        s[en] = zh_s
        found = 0
        for it in items:
            if (it.get("title") or "").strip() == en:
                it["title_zh"] = zh_t
                it["summary_zh"] = zh_s
                it["translated"] = True
                it["method"] = "manual"
                it.pop("needs_retranslate", None)
                it.pop("retranslate_attempts", None)
                found += 1
        if not found:
            print("  [警告] news.json 未匹配:", en)
        hit += found

    json.dump(t, open(T_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(s, open(S_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(news, open(NEWS, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("[fix_patrol_0500] 定稿 %d 条 / 命中 news.json %d 处" % (len(FINAL), hit))
    print("[fix_patrol_0500] 覆盖表: 标题 %d / 摘要 %d" % (len(t), len(s)))
    if hit != len(FINAL):
        print("[fix_patrol_0500] 警告: 命中数与定稿数不一致")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
