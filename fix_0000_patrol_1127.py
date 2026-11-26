# -*- coding: utf-8 -*-
"""00点例行巡检：定稿 23:09 与 23:45 两条 NLLB 机翻崩坏条目。

- Simon Willison / Quoting Jack Despain Zhou：标题机翻为「引用……的话。」，
  摘要把 de-individualization 译成「非个性化」，长句语序崩坏；按原文重述。
- The Decoder / After OpenAI and Anthropic shut the door on their data...：
  「关闭了他们的数据的门」为机翻腔，且「一个中国的人工智能开发人员」与
  摘要中 Z.AI、Moonshot AI 两家主体矛盾；training data 误译为「培训数据」。

回填 news.json + JSON 覆盖表，再由 scripts/regen_overrides.py 同步到
代码层 manual_overrides.py，确保部署端持久卷的旧覆盖表不会回退译文。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

FIX = {
    "Quoting Jack Despain Zhou": (
        "引用杰克·德斯潘·周的观点",
        "AI 已经带来的诸多影响中，有一项是明显的「去个性化」。我打开一段 YouTube 视频，听到的是 Claude；"
        "参加一场会议演讲，听到的还是 Claude；打开邮箱，看到一些看似严肃的人——带着看似严肃的资历、"
        "供职于看似严肃的机构，想发表一些挂着我与他们名头的文章——我看到的依然是 Claude。",
    ),
    "After OpenAI and Anthropic shut the door on their data, a Chinese AI developer is turning to Google and Meta instead": (
        "OpenAI 与 Anthropic 收紧数据访问后，中国 AI 开发商转向 Google 与 Meta",
        "中国的 AI 公司 Z.AI 与 Moonshot AI 不得不推迟下一代旗舰模型的发布，并正在寻找新的训练数据来源。",
    ),
}


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
