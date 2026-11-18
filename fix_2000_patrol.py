# -*- coding: utf-8 -*-
"""2026-11-18 20:00 例行巡检：修复本轮新增 7 条的 NLLB 机翻缺陷。

本轮 20:00 调度新增 7 条（19:16~20:00），多条存在品牌误译 / 术语错译 / 摘要语病：
  #1 Suno「苏诺」→ 保留品牌「Suno」；摘要「交互/缩影图像/艺术品」理顺
  #2 Propel「推进」、Plaid「投资」、underwriting「承载」→ 保留品牌 Propel/Plaid，承销
  #3 Humyn Labs 标题「以为…提供」→「为…提供所需训练数据」
  #4 vibe-coded「振动编码」→「氛围编程（vibe coding）」
  #5 Subtle Medical「微妙医疗」、「保证日本许可证」→「获日本上市批准」
  #6 methane leaks「甲泄漏」→「甲烷泄漏」；store outlets「商店」→「门店插座」
  #7 "AI Coding Eat Game Engines"「吃掉」→「颠覆」；摘要人名/术语/断句理顺

按既有巡检策略：同引擎全量重译会重复同样错误并覆盖 500+ 条既有人工定稿，
故这里只人工定稿本轮 7 条，并写入覆盖表（data JSON + 代码层 manual_overrides），
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
    "Suno now lets you make AI videos for your AI music": (
        "Suno 现可为 AI 音乐生成 AI 视频",
        "AI 音乐平台 Suno 推出名为「Visuals（视觉）」的图像与视频生成新功能，"
        "可将 Suno 歌曲转化为自动与歌词对口型的 AI 视频片段，"
        "也可通过提示词生成用作缩略图和专辑封面的图像。该功能已在网页、iOS 和 Android 上线，"
        "位于「创建」模式下的新 Visuals 标签页；网页用户还可通过曲库中歌曲的三点菜单进入。",
    ),
    "Propel Adds Plaid Cash-Flow Data to AI Credit Underwriting": (
        "Propel 引入 Plaid 现金流数据升级 AI 信贷承销",
        "2026 年 11 月 18 日，Propel Holdings 宣布升级其 AI 现金流承销模型，"
        "并与 Plaid 达成合作引入经消费者授权的财务数据，估计可将信贷覆盖面扩大最多 15%。"
        "该模型旨在评估传统征信机构数据可能无法充分覆盖的消费者，"
        "其内部系统已于 2026 年第三季度末投入运营。",
    ),
    "India’s Humyn Labs raises $47M to feed U.S. robotics companies the data they need": (
        "印度 Humyn Labs 融资 4700 万美元，为美国机器人公司提供所需训练数据",
        "Humyn Labs 成立于今年 2 月，与 Mecka AI、XDOF 等初创公司竞争，"
        "约 90% 营收来自美国。",
    ),
    "The App Economy Is Changing: What Happens When Anyone Can Build Their Own Software?": (
        "应用经济正在改变：当人人都能开发自己的软件时会怎样？",
        "从「选应用」到「描述应用」：2026 年 10 月 13 日，Google 宣布 Android 用户"
        "现可通过 Google AI Studio 自行构建应用，并通过 Google Play 在自己手机上私密运行，"
        "无需公开上架。这些应用采用「氛围编程（vibe coding）」方式："
        "你用日常语言描述需求，AI 负责编写代码。",
    ),
    "Subtle Medical Secures Japan Clearance for SubtleHD AI Software": (
        "Subtle Medical 的 SubtleHD AI 软件获日本上市批准",
        "2026 年 11 月 18 日，Subtle Medical 宣布其 AI 软件 SubtleHD 获得日本市场准入认证。"
        "该软件可将 MRI 扫描序列加速最多 80%，并在现有扫描仪上提升图像质量。"
        "获得认证后，日本各地的医院与影像中心均可使用该软件。"
        "该认证由日本医疗设备进步协会依据《药品与医疗器械法》"
        "（日本医疗产品监管框架）颁发。",
    ),
    "From store outlets to methane leaks, every scrap of power is now fair game for AI compute": (
        "从门店插座到甲烷泄漏，每一份电力都成为 AI 算力的争夺对象",
        "随着模型规模不断扩大、分布式推理从概念走向部署，AI 工厂正在突破传统数据中心的边界。"
        "支撑这些模型的基础设施如今必须横跨机架、站点，甚至分散各处的小型电力资源。"
        "戴尔科技公司（Dell Technologies）表示，AI 工厂最难的部分不再是采购硬件，"
        "而是让机架、交换机、GPU 与冷却系统在通电后持续稳定运行。",
    ),
    "Will AI Coding Eat Video Game Engines?": (
        "AI 编程会颠覆游戏引擎吗？",
        "2026 年 9 月，Travis McGeathy 的工作室 Seeker Entertainment 资金耗尽，"
        "其游戏 KinForge 也随之停摆。KinForge 是一款基于 Unreal Engine 5.7 打造的在线游戏，"
        "原本运行在亚马逊云科技（AWS）的服务器上。无人续付服务器账单后，"
        "即便持有代码的少数开发者（包括联合创始人 McGeathy）也无法再游玩。"
        "后来 McGeathy 一时兴起，让 Anthropic 的 Claude Code 处理该项目，"
        "要求它在不依赖 AWS 的情况下让 KinForge 可运行。经过约四小时、"
        "基本无需人工干预的工作，他得到一个可让玩家自行托管游戏的构建版本。"
        "Claude 加入了对互联网和局域网点对点联机的支持；令 McGeathy 意外的是，"
        "它还加入了持久化存档功能，让玩家断线后可以恢复游戏。",
    ),
}


def put_override(path, key, value):
    if not os.path.exists(path):
        return
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
    for en in mapping:
        pat = re.compile(r"^\s*'" + re.escape(en) + r"'.*$", re.M)
        body = pat.sub("", body)
    additions = ""
    for en, zh in mapping.items():
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

    if os.path.exists(PY_FILE):
        with open(PY_FILE, "r", encoding="utf-8") as f:
            src = f.read()
        src = upsert_py_dict(src, "TITLE_OVERRIDES",
                             {en: zh_t for en, (zh_t, _) in FIXES.items()})
        src = upsert_py_dict(src, "SUMMARY_OVERRIDES",
                             {en: zh_s for en, (_, zh_s) in FIXES.items()})
        with open(PY_FILE, "w", encoding="utf-8") as f:
            f.write(src)

    # 重新生成摘要报告，保持与网站数据一致
    import report
    report.main()

    print("[fix_2000_patrol] 已定稿 %d 条（data + 覆盖表 + 代码层 + 报告）" % n)
    return 0 if n == len(FIXES) else 1


if __name__ == "__main__":
    raise SystemExit(main())
