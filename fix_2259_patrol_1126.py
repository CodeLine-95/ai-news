# -*- coding: utf-8 -*-
"""22:59 例行巡检：定稿 22:00 之后新增的 2 条 NLLB 机翻，并统一地区表述。

- Unite.AI / AI Regulation in 2027：compliance playbooks 被译成「合规性游戏书」，
  ship the same model 被译成「发送相同的模型」，consequential decision 被译成
  「后果决策」；需按监管语境重写。
- Unite.AI / Improving Human Impersonation：标题被译成「改进人类仿真，因为网络
  关闭了 AI」，摘要长句语序崩坏；需按网页抓取与反爬语境重写。
- 地区表述：LINE Taiwan / 「向台湾两家主要客户」/「平台在台湾的先进包装业务」
  统一为「中国台湾」，与项目既有译文风格一致。

回填 news.json + JSON 覆盖表，再由 scripts/regen_overrides.py 同步到
代码层 manual_overrides.py，确保部署端持久卷的旧覆盖表不会回退译文。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

FIX = {
    "AI Regulation in 2027: One Global Product Will Need Multiple Compliance Playbooks": (
        "2027 年 AI 监管：同一款全球产品将需要多套合规手册",
        "产品团队可能把同一个模型交付给两位客户，却因此面对两种不同的合规问题：一位客户用它起草内部笔记，另一位则把它用于会产生重大影响的决策。技术看似相同，但法律定位、证据要求与受影响人群都已改变。这正是 2027 年 AI 监管成为一项运营挑战的原因。",
    ),
    "Improving Human Impersonation, as the Web Closes Up Against AI": (
        "随着网站加强防范 AI，模拟人类上网的技术持续升级",
        "过去，网页抓取相对随意：人们用机器人流程自动化（RPA）录制浏览操作，反复优化后让程序定时无人值守地运行，从那些只允许真人（或付费客户）访问数据、并采取措施抵御自动化浏览的网站获取信息。如今随着这类防护收紧，模拟人类行为的做法也在不断升级。",
    ),
    "LINE Taiwan Unveils Three-Part AI Agent Strategy for Businesses": (
        "LINE 中国台湾发布面向企业的三部分 AI 智能体战略",
        "在 2026 年 11 月 26 日举行的 LINE BIZ CONVERGE 2026 上，LINE 中国台湾表示将推进涵盖消费者助手、品牌服务与商家运营的三部分 AI 智能体战略，依托超过 360 万个官方账号，让客户互动从回答问题走向完成任务。该战略把消费者触达、品牌履约与商家决策串联起来。",
    ),
}

# 仅摘要中出现的地区表述（标题不变），按英文原标题匹配。
SUMMARY_ONLY_FIX = {
    "Kulicke & Soffa Ships Panel-Level Bonding Systems for AI Packaging":
        None,  # 占位，实际按下方子串匹配，避免英文标点差异导致漏改
}

# 对摘要做确定性替换，覆盖所有条目（含无英文标题精确匹配的场景）。
TEXT_REPLACEMENTS = (
    ("向台湾两家主要客户", "向中国台湾两家主要客户"),
    ("平台在台湾的先进包装业务", "平台在中国台湾的先进包装业务"),
    ("LINE 台湾", "LINE 中国台湾"),
)


def main():
    db = json.load(open(os.path.join(DATA, "news.json"), encoding="utf-8"))
    items = db["items"] if isinstance(db, dict) else db

    tpath = os.path.join(DATA, "titles_override.json")
    spath = os.path.join(DATA, "summaries_override.json")
    tov = json.load(open(tpath, encoding="utf-8")) if os.path.exists(tpath) else {}
    sov = json.load(open(spath, encoding="utf-8")) if os.path.exists(spath) else {}

    changed = 0
    matched = set()
    for it in items:
        en = it.get("title") or ""
        if en in FIX:
            matched.add(en)
            title_zh, summary_zh = FIX[en]
            for key, value in (("title_zh", title_zh), ("summary_zh", summary_zh)):
                if it.get(key) != value:
                    it[key] = value
                    it["translated"] = True
                    it["method"] = "nllb+manual"
                    changed += 1
                    print("[fix] %s: %s" % (key, en[:58]))
            tov[en] = title_zh
            sov[en] = summary_zh
        # 兜底：其余条目的裸「台湾」统一为「中国台湾」
        for key in ("title_zh", "summary_zh"):
            text = it.get(key) or ""
            new = text
            for old, repl in TEXT_REPLACEMENTS:
                new = new.replace(old, repl)
            if new != text:
                it[key] = new
                it["translated"] = True
                it["method"] = "nllb+manual"
                changed += 1
                print("[fix] region in %s: %s" % (key, en[:58]))
            if key == "title_zh" and new and en:
                tov[en] = new
            if key == "summary_zh" and new and en:
                sov[en] = new

    missing = set(FIX) - matched
    if missing:
        print("[warn] 未匹配到条目:", missing)

    json.dump(tov, open(tpath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(sov, open(spath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(db, open(os.path.join(DATA, "news.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("[fix] 变更 %d 处 | 覆盖表 标题 %d 条 / 摘要 %d 条"
          % (changed, len(tov), len(sov)))


if __name__ == "__main__":
    main()
