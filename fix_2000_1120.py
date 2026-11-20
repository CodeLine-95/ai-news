# -*- coding: utf-8 -*-
"""2026-11-20 20:00 例行巡检：修复本轮新增条目的 NLLB 机翻缺陷。

本轮 20:00 调度新增 4 条（19:22~20:00）。其中 2 条存在硬伤：
  #1 ARCS∙ai（19:27）：西里尔文「Ереван」未译（应为「埃里温」）；摘要语法崩坏
     「每年毕业的 50 名专业工程师」→「每年培养 50 名专业工程师」。
  #2 Signal（19:22）：品牌名误译为「信号」（Signal 是加密通讯应用名，须保留）；
     标题「信号添加了屏幕截图限制移动 AI 数据捕获」生硬；摘要断句与指代理顺。

同引擎全量重译会重复同样错误并覆盖 500+ 条既有人工定稿，故只人工定稿这 2 条，
写入覆盖表（data JSON + 代码层 manual_overrides），保证下轮调度不覆盖回去。
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
    "ARCS∙ai Opens Shared ARPI Center for Physical AI Training": (
        "ARCS∙ai 开设面向物理 AI 训练的共享 ARPI 中心",
        "计算科学与人工智能先进研究中心（ARCS∙ai）宣布，于 2026 年 11 月 20 日在埃里温"
        "启动 ARPI 中心。这座共享的机器人与物理 AI 中心的目标是：整合三所亚美尼亚大学的"
        "师资、学生与设备，每年培养 50 名专业工程师。ARPI 代表「亚美尼亚机器人技术与物理智能」"
        "（Armenian Robotics & Physical Intelligence）。",
    ),
    "Muse Is Unleashing a World of Pettiness on Instagram": (
        "Muse 在 Instagram 上掀起一场「小心眼」风潮",
        "Meta 的 AI 助手可以追踪并取消关注那些没有回关你的 Instagram 用户，"
        "而有些人正在充分利用这一功能。",
    ),
    "Signal Adds Screenshot Restrictions to Limit Mobile AI Data Capture": (
        "Signal 新增截图限制，防止移动端 AI 抓取数据",
        "Meredith Whittaker 于 2026 年 11 月 20 日宣布，这款加密通讯应用将在 iOS 27 与"
        " Android 上限制屏幕截图——当检测到 AI 助手试图读取屏幕时即加以阻止，以免操作系统"
        "智能体捕获私人聊天内容。这些保护措施尚不完整，Signal 无法可靠阻止 macOS 上的截图。"
        "在 iOS 27 上，相关公告会显示已启用的「阻止 Siri AI」设置。",
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

    import report
    report.main()

    print("[fix_2000_1120] 已定稿 %d 条（data + 覆盖表 + 代码层 + 报告）" % n)
    return 0 if n == len(FIXES) else 1


if __name__ == "__main__":
    raise SystemExit(main())
