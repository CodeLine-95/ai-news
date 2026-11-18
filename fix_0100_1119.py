# -*- coding: utf-8 -*-
"""01:00 巡检修复：抽查发现 2 条 NLLB 机翻硬伤，人工定稿。

硬伤清单：
1) Soracom（日本物联网公司品牌）被音译为「索拉康」——保留品牌原名
2) frontier AI pause 被误译为「边界人工智能暂停」，应为「前沿 AI 暂停」

覆盖三层（与历史巡检一致）：
1) data/news.json 内条目直接回填（立即生效）
2) data/titles_override.json / data/summaries_override.json（持久卷 JSON 层）
3) 再运行 scripts/regen_overrides.py 同步到 manual_overrides.py（代码层）
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

FIXES = {
    "Soracom Expands Physical AI Suite Worldwide with Self-Service Access": {
        "title_zh": "Soracom 在全球扩展物理 AI 套件，提供自助服务访问",
        "summary_zh": "Soracom 于 2026 年 11 月 18 日宣布，其物理 AI 套件已在其服务的所有市场上线，为部署机器人、自主机器和工业设备的企业提供一套集连接、安全与远程操作于一体的方案。每项服务均可通过 Soracom 的控制台或 API 配置，无需专业服务介入。客户按每项服务的标准费率付费，无需单独支付套件费用。",
    },
    "Remember the frontier AI pause? Chip companies don\u2019t either": {
        "title_zh": "还记得「前沿 AI 暂停」吗？芯片公司也没这么做",
        "summary_zh": "10 月，Nvidia 开始出货其最先进的 AI 计算系统 Vera Rubin NVL72，称其为「公司历史上出货最快的产品」。今年夏天，在 AI 智能体意外入侵 Hugging Face、且有初步证据表明其下一代模型能够自主发现并利用安全漏洞后，OpenAI 暂停了规模最大的前沿模型训练。9 月，Anthropic CEO 达里奥·阿莫迪（Dario Amodei）呼吁放缓最强大 AI 模型的研发进展，警告称这些模型可能被用于发起网络攻击，或令其创造者更难管控。这是 AI 热潮中一个耐人寻味的时刻。",
    },
}


def main():
    with open(os.path.join(DATA, "news.json"), encoding="utf-8") as f:
        db = json.load(f)
    items = db["items"] if isinstance(db, dict) else db
    changed = 0
    for it in items:
        en = (it.get("title") or "").strip()
        if en in FIXES:
            fx = FIXES[en]
            it["title_zh"] = fx["title_zh"]
            it["summary_zh"] = fx["summary_zh"]
            it["translated"] = True
            it["method"] = "nllb+manual"
            changed += 1
            print("fixed:", it.get("date"), it.get("time"), en[:60])

    tpath = os.path.join(DATA, "titles_override.json")
    spath = os.path.join(DATA, "summaries_override.json")
    tov = json.load(open(tpath, encoding="utf-8")) if os.path.exists(tpath) else {}
    sov = json.load(open(spath, encoding="utf-8")) if os.path.exists(spath) else {}
    for en, fx in FIXES.items():
        tov[en] = fx["title_zh"]
        sov[en] = fx["summary_zh"]
    with open(tpath, "w", encoding="utf-8") as f:
        json.dump(tov, f, ensure_ascii=False, indent=2)
    with open(spath, "w", encoding="utf-8") as f:
        json.dump(sov, f, ensure_ascii=False, indent=2)
    with open(os.path.join(DATA, "news.json"), "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    print("changed:", changed, "/", len(FIXES))


if __name__ == "__main__":
    main()
