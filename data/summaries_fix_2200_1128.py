# -*- coding: utf-8 -*-
"""2026-11-28 22:00 例行巡检 · 人工核对译文覆盖表。

本轮 2 条缺陷（NLLB 专有名词 / 体裁误译）：
  1. IEEE Spectrum 诗歌题材：Prompt Engineering 被译成「快速工程」，
     Odysseus / Cyclops / Sirens 被音译成「奥迪西斯 / 百科动物 / 声」；
  2. The Decoder：Anthropic 被误译成「人类」，unredacted 被译成「未经编辑」。

键为英文原标题。先运行本脚本合并进 JSON 覆盖表，再运行
scripts/regen_overrides.py 同步到随发布生效的代码层覆盖表。
"""
import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

TITLE_OVERRIDES = {
    "Poetry for Engineers: Prompt Engineering for Odysseus":
        "写给工程师的诗：为奥德修斯做提示工程",
    "UK Parliament demands unredacted METR safety report after Anthropic redacts most of the evidence":
        "Anthropic 删减大部分证据后，英国议会要求公开未经删节的 METR 安全报告",
}

SUMMARY_OVERRIDES = {
    "Poetry for Engineers: Prompt Engineering for Odysseus":
        "I. 奥德修斯问神谕：去伊塔卡的最短路线？避开独眼巨人，避开塞壬，优先选有 Wi-Fi 的渡轮。"
        "神谕思考三秒：正在重新计算……思考中……要不要换一条风景更好的路线？"
        "II. 奥德修斯再问：告诉我已知世界之外有什么。神谕给出十二个来源、三张地图、两条警告，"
        "还有一座从未存在过、却被说得煞有介事的岛屿。奥德修斯低声自语：哦，缪斯，神谕又产生幻觉了……"
        "神谕继续说：看，我知道凯法利尼亚有个特别的地方，还有几招能带你回家。要我继续吗？"
        "III. 于是奥德修斯问出最后一个问题：如果我能知道一切，为什么还要亲自前往？"
        "从未横渡咸海的知识，价值何在？神谕沉默，光标闪烁，没有答案。"
        "奥德修斯依旧足智多谋，启航出海并喊道：那么，究竟是谁在为谁导航？",

    "UK Parliament demands unredacted METR safety report after Anthropic redacts most of the evidence":
        "英国议会正向 Anthropic 施压。委员会主席 Liam Byrne 要求在 12 月 4 日前拿到 METR "
        "关于 AI 加速发展的安全报告完整版（未经删节）。METR 批评 Anthropic 在发布前删去了"
        "「信息量最大」的证据。此事引发更广泛的质疑：自愿性 AI 安全评估究竟有多透明，"
        "也再次凸显欧洲对美国 AI 实验室的依赖。",
}


def main():
    for path, overrides in ((T_JSON, TITLE_OVERRIDES), (S_JSON, SUMMARY_OVERRIDES)):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        changed = 0
        for k, v in overrides.items():
            if data.get(k) != v:
                data[k] = v
                changed += 1
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("[fix] %s 更新 %d 条（共 %d 条）" % (os.path.basename(path), changed, len(data)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
