# -*- coding: utf-8 -*-
"""22:00 第二轮：重启后新增 4 条中的 3 条品牌/标题缺陷定稿。"""
import json
import os
BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

FIXES = {
    "Reson8 releases Rumble-2-Flash speech model as a free open-weights download": {
        "title_zh": "Reson8 发布 Rumble-2-Flash 语音模型，开放权重免费下载",
        "summary_zh": "总部位于阿姆斯特丹的语音识别初创公司 Resonate Labs B.V. 今日发布其 Rumble-2-Flash 转写模型，以开放权重形式免费提供下载。这款 5 亿参数模型专为预录音频的快速转写而设计，支持 40 多种语言。Reson8 将本次发布面向需要非英语语音识别能力的开发者与研究人员。",
    },
    "Tesorai raises $5.3M to feed starving AI models with biological data and accelerate drug discovery": {
        "title_zh": "Tesorai 融资 530 万美元，用生物数据「喂养」饥饿的 AI 模型并加速药物发现",
        "summary_zh": "药物研究人员与医学实验室每天都会产生海量生物数据，然而用于加速药物发现的人工智能模型却仍然缺乏有用信息——这是一个奇怪的悖论。一家名为 Tesorai Inc. 的初创公司认为，在今日完成 530 万美元种子轮融资后，自己已找到解决之道。",
    },
    "OneTrust’s Fall ’26 Release expands AI visibility, privacy and third-party risk tools": {
        "title_zh": "OneTrust 2026 秋季版发布，扩展 AI 可见性、隐私与第三方风险工具",
        "summary_zh": "治理平台提供商 OneTrust LLC 今日宣布推出其 2026 秋季版（Fall '26 Release），这是一组平台更新，据称可将治理能力嵌入业务决策所在的工作流程之中。",
    },
    "Will Wright’s next game uses AI to map your memories": {
        "title_zh": "威尔·赖特的新作利用 AI 描绘你的记忆",
        "summary_zh": "《模拟城市》与《模拟人生》等传奇系列的创作者威尔·赖特（Will Wright）正在开发一款新游戏，且围绕 AI 打造。这款聚焦玩家记忆的新作名为《MyMems》。与赖特的其他作品一样，它听起来极具雄心，为玩家提供一种探索自己创造世界的新方式。他告诉 The Verge：「我们想把你的自传变成一个玩具世界。」MyMems 官网将这款手游描述为一款「社交模拟」游戏，其中的世界「由你的记忆以及塑造了你的人构建而成」。",
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
            it["title_zh"] = FIXES[en]["title_zh"]
            it["summary_zh"] = FIXES[en]["summary_zh"]
            it["translated"] = True
            it["method"] = "nllb+manual"
            changed += 1
    tpath = os.path.join(DATA, "titles_override.json")
    spath = os.path.join(DATA, "summaries_override.json")
    tov = json.load(open(tpath, encoding="utf-8"))
    sov = json.load(open(spath, encoding="utf-8"))
    for en, fx in FIXES.items():
        tov[en] = fx["title_zh"]
        sov[en] = fx["summary_zh"]
    for p, obj in ((tpath, tov), (spath, sov)):
        with open(p, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)
    with open(os.path.join(DATA, "news.json"), "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    with open(os.path.join(BASE, "manual_overrides_2200b.snippet"), "w", encoding="utf-8") as f:
        f.write("# TITLE\n")
        for en, fx in FIXES.items():
            f.write("    %r: %r,\n" % (en, fx["title_zh"]))
        f.write("# SUMMARY\n")
        for en, fx in FIXES.items():
            f.write("    %r: %r,\n" % (en, fx["summary_zh"]))
    print("changed:", changed)

if __name__ == "__main__":
    main()
