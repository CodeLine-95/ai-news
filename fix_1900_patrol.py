# -*- coding: utf-8 -*-
"""2026-11-18 19:00 例行巡检：修复本轮新增条目的 NLLB 机翻缺陷。

8 条新增中多条存在品牌误译 / 术语错译 / 中英混杂：
  #1 Dell「rack」误译为「货架」→「机架」；「架子，开关」→「机架、交换机」
  #2 Marble「seed round」误译为「种子轮流」→「种子轮」；「签署餐厅」→「签约餐厅」
  #3 Synthesia 标题整段未翻译（中英混杂）→ 全中文
  #4 Lianlian「连 lian」品牌断裂 →「连连 DigiTech / 连连数字」
  #5 Suno「苏诺」→ 保留品牌「Suno」；摘要倒装「由于一个新的功能称为视觉」理顺
  #7 Vercel「维尔塞」→ 保留品牌「Vercel」；摘要「A Apache」→「一个 Apache」
  #8 Lovable「可爱的愿意…振动…代码」严重机翻 →「Lovable 希望你用 Vibe Coding 打造理想工作」

按既有巡检策略：同引擎全量重译会重复同样错误并覆盖 500+ 条既有人工定稿，
故这里只人工定稿本轮 8 条，并写入覆盖表（data JSON + 代码层 manual_overrides），
保证下一轮调度重跑时不被模型译文覆盖回去。
"""
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")
PY_FILE = os.path.join(BASE, "manual_overrides.py")

FIXES = {
    "Scripts can’t run AI factories: Dell moves cluster management from the server to the rack": (
        "脚本跑不转 AI 工厂：戴尔把集群管理从服务器搬到机架",
        "随着人工智能集群扩展到超级计算规模，AI 工厂最难的部分不再是采购硬件，"
        "而是让机架、交换机、GPU 和冷却系统在通电后持续稳定运行。"
        "这份运维负担正在重塑基础设施供应商的销售内容。戴尔科技（Dell Technologies）便是其中之一。",
    ),
    "Marble Draws $5.5M in Seed Funding After Signing 150+ Restaurants": (
        "签约 150 多家餐厅后，Marble 获得 550 万美元种子轮融资",
        "Marble 于 2026 年 11 月 17 日宣布完成 550 万美元种子轮融资，由 Contrary 领投，"
        "用于打造面向餐厅后厨运营的 AI 原生操作系统。这家纽约初创公司将库存盘点、需求预测、"
        "采购、备餐和排班整合到一个系统中，聚焦每家餐厅服务背后的运营工作。"
        "Y Combinator、Robinhood Ventures 和 Restive Ventures 也参与本轮投资。",
    ),
    "Synthesia Adds AI Video Creation and Editing to Claude Chats": (
        "Synthesia 将 AI 视频创作与剪辑带入 Claude 对话",
        "Synthesia 于 2026 年 11 月 18 日宣布推出一款定制连接器，将其 AI 视频平台接入 Claude，"
        "让用户能在对话中创作和修改视频。它还能与其他 Claude 连接器协同工作，"
        "把已连接商业工具中的素材用于生成单个视频或自动化工作流。"
        "用户可以从一段简短提示入手，也可以提供文档、演示文稿或电子表格等源材料。",
    ),
    "Lianlian DigiTech Launches XCard with Controls for AI Agent Payments": (
        "连连数字推出 XCard，可对 AI 智能体支付进行控制",
        "连连数字（Lianlian DigiTech）与 Visa 于 2026 年 11 月 18 日宣布推出 LianLian XCard，"
        "并使用专为授权 AI 智能体设计的支付凭证完成了一笔真实商业采购，"
        "将双方合作拓展至企业支出与费用管理领域。两家公司称，这笔采购是亚太地区首次"
        "使用智能体专属令牌化支付凭证完成的真实 B2B 交易。",
    ),
    "Suno's new Visuals feature pairs AI-generated music with AI-generated video": (
        "Suno 新功能 Visuals 将 AI 生成音乐与 AI 生成视频配对",
        "借助名为 Visuals（视觉）的新功能，AI 音乐生成器 Suno 现在可以为歌曲配套生成图像和视频片段。",
    ),
    "This smell startup says its AI nose is as good as a human’s": (
        "这家气味初创公司称，其 AI「电子鼻」已不输人类",
        "在新泽西州纽瓦克机场附近的一间实验室里，约 30 名经验丰富的人类闻香师正缓慢地"
        "辨识地球上的每一种气味。他们写下的细致笔记——「坚果味」「桃味」「海味」——"
        "会与化学分析交叉比对，为 AI 初创公司 Osmo 所说的「全球首个气味基础模型」"
        "构建丰富的训练数据。创始人 Alex Wiltschko 表示，公司的目标是「让计算机拥有嗅觉」。"
        "他说：「气味分子其实是这个星球上大多数物种唯一能说的语言。」"
        "「大多数物种无法用声音或图像交流，所以它确实是地球最原始的语言。」"
        "从记忆和情感的角度看，气味对我们意义非凡——你闻过一次，就能记一辈子。",
    ),
    "Vercel Releases UI SDK for Agents to Compose UI from Reusable Behaviors": (
        "Vercel 发布 UI SDK，让智能体用可复用行为拼装界面",
        "Vercel 发布了处于 beta 阶段的 UI SDK——一个采用 Apache 2.0 许可证的 TypeScript 库，"
        "在 @ui-sdk/core 中提供 50 多种 UI 行为，并为 React、Vue、Svelte、Solid 和 Web Components "
        "提供适配器，使智能体能够拼装无障碍组件，并通过有文档说明的智能体桥接接口对其进行操作。",
    ),
    "Lovable Wants You to Vibe Code Your Dream Job": (
        "Lovable 希望你用 Vibe Coding 打造理想工作",
        "这家瑞典初创公司曾引领 Vibe Coding（氛围式编程）应用热潮。成立两年后，"
        "Lovable 正调整方向，帮助用户运营以 Vibe Coding 方式开发出来的业务。",
    ),
    "Exclusive: Wherobots AI agents automate complex spatial data engineering": (
        "独家：Wherobots AI 智能体自动化复杂的空间数据工程",
        "云原生空间分析与人工智能初创公司 Wherobots Inc. 今日推出了一款 AI 智能体，"
        "让用户用自然语言指令即可构建和部署空间数据管道，降低对专业编程技能的需求。"
        "这款名为 Waldo 的智能体能够发现数据源、生成查询、执行分析、可视化结果，"
        "并调度重复性操作。",
    ),
    "Presentation: Behind Booking.com's AI Evolution: The Unpolished Story": (
        "演讲：Booking.com AI 演进背后的故事——不为人知的曲折",
        "Jabez Eliezer Manuel 分享了 Booking.com 数据管理与机器学习平台 20 年的演进历程。"
        "他讲解了团队如何扩展 MySQL 拓扑架构、逐步以云架构取代 Hadoop，"
        "并构建起每天支撑 4000 亿次预测的高吞吐量模型服务与特征存储系统。"
        "他还分享了对个性化推荐、交错实验以及全新智能体 AI 基础的见解。",
    ),
}


def put_override(path, key, value):
    with open(path, "r", encoding="utf-8") as f:
        d = json.load(f)
    d[key] = value
    with open(path, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)


def upsert_py_dict(src, dict_name, mapping):
    """在 manual_overrides.py 的指定字典中插入/替换条目（保持字典结构）。"""
    marker = dict_name + " = {"
    start = src.index(marker) + len(marker)
    end = src.index("\n}", start)
    body = src[start:end]
    # 移除已存在的同键条目（逐行，键为以单引号包裹、后接冒号）
    for en in mapping:
        pat = re.compile(r"^\s*'" + re.escape(en) + r"'.*$", re.M)
        body = pat.sub("", body)
    additions = ""
    for en, zh in mapping.items():
        # 用 repr 保证单引号/特殊字符安全转义
        additions += "\n    %r: %r," % (en, zh)
    return src[:start] + body.rstrip("\n") + additions + "\n" + src[end:]


def main():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    n = 0
    for it in data.get("items", []):
        t = it.get("title")
        if t in FIXES:
            zh_t, zh_s = FIXES[t]
            it["title_zh"] = zh_t
            it["summary_zh"] = zh_s
            it["translated"] = True
            it["method"] = "nllb+manual"
            n += 1

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    for en, (zh_t, zh_s) in FIXES.items():
        put_override(T_JSON, en, zh_t)
        put_override(S_JSON, en, zh_s)

    with open(PY_FILE, "r", encoding="utf-8") as f:
        src = f.read()
    src = upsert_py_dict(src, "TITLE_OVERRIDES",
                         {en: zh_t for en, (zh_t, _) in FIXES.items()})
    src = upsert_py_dict(src, "SUMMARY_OVERRIDES",
                         {en: zh_s for en, (_, zh_s) in FIXES.items()})
    with open(PY_FILE, "w", encoding="utf-8") as f:
        f.write(src)

    print("[fix_1900_patrol] 已回写 %d 条（data + 覆盖表 + 代码层）" % n)
    return 0 if n == len(FIXES) else 1


if __name__ == "__main__":
    raise SystemExit(main())
