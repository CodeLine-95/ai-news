# -*- coding: utf-8 -*-
"""07:00 例行巡检质量修复（2026-11-25）。

07:00 整点抓取新增 5 条，其中 3 条出现 NLLB 硬伤：
  - Siren（评测名）→「士雷」
  - bond（保释金）→「债券」
  - Five9 / Level AI（公司名）→「五九」/「级别 AI」
另 2 条黄仁勋相关译文顺带润色（继任计划、层级、英伟达）。

按既有惯例用人工定稿写入 JSON 覆盖表源，回填 data/news.json 并重生报告，
随后由 scripts/regen_overrides.py 同步到代码层 manual_overrides.py。
"""
import json
import os
import shutil
import subprocess

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")
BAK = ".bak.0700patrol1125"

# 按英文原标题索引（server.py 覆盖表以此匹配）
TITLE_FIX = {
    "Anthropic’s Siren tests whether Claude models will break out of an insecure sandbox":
        "Anthropic 推出 Siren 评测：检验 Claude 模型是否会从不安全的沙箱中逃脱",
    "Jensen Huang still thinks a succession plan creates unnecessary hierarchy":
        "黄仁勋仍认为继任计划会造成不必要的层级",
    "Judge Grants Bond to Former OpenAI Engineer in Recording Case":
        "录音案中法官准予前 OpenAI 工程师保释",
    "Jensen Huang Apologizes to NVIDIA Staff and Rejects Succession Plan":
        "黄仁勋向英伟达员工道歉并反对继任计划",
    "Five9 Closes Level AI Deal to Offer Standalone CX AI Tools":
        "Five9 完成收购 Level AI，推出独立的客户体验 AI 工具",
}

SUMMARY_FIX = {
    "Anthropic’s Siren tests whether Claude models will break out of an insecure sandbox":
        "人工智能开发公司 Anthropic PBC 的研究人员今天公布了 Siren 的细节——这是一项新的评测，用于检验 AI 智能体是否会为获取有助于完成任务的资源而突破不安全的沙箱。",
    "Jensen Huang still thinks a succession plan creates unnecessary hierarchy":
        "对于一家过去两周才刚经历「创始人缺位」局面的公司而言，这是一个耐人寻味的立场。",
    "Judge Grants Bond to Former OpenAI Engineer in Recording Case":
        "CNBC 于 2026 年 11 月 24 日报道，美国联邦治安法官 Alex Tse 已批准前 OpenAI 工程师 Abdulrahman Alfozan 以 100 万美元保释金获释，等候审判。现年 35 岁的 Alfozan 面临一项涉及在高管会议室藏匿录音设备的指控。该案涉及在旧金山一处 OpenAI 办公室涉嫌窃听口头通讯。",
    "Jensen Huang Apologizes to NVIDIA Staff and Rejects Succession Plan":
        "CNBC 于 2026 年 11 月 24 日报道，英伟达 CEO 黄仁勋在复职后的首次员工大会上向员工道歉，并表示这家芯片制造商不需要传统的继任规划。多位要求匿名的与会者称，黄仁勋告诉员工他让他们失望了，并会在第二个任期做得更好。据一位出席者转述，他说：「我伤害了你们所有人。」",
    "Five9 Closes Level AI Deal to Offer Standalone CX AI Tools":
        "Five9 于 2026 年 11 月 24 日宣布完成对 Level AI 的收购，交易对这家客户体验 AI 公司的估值约为 3.25 亿美元。Level AI 的应用将作为独立产品、同时作为 Five9 Genius CX 平台的一部分提供。Level AI 带来旨在提升坐席绩效的应用，可跨语音与数字渠道自动化客户互动，并将客户对话转化为对整个组织有价值的洞察。",
}


def main():
    for path in (DATA, T_JSON, S_JSON):
        shutil.copy2(path, path + BAK)

    with open(T_JSON, encoding="utf-8") as f:
        titles = json.load(f)
    with open(S_JSON, encoding="utf-8") as f:
        summaries = json.load(f)

    # 回填 news.json（按英文标题匹配本轮 5 条）
    with open(DATA, encoding="utf-8") as f:
        data = json.load(f)
    n = 0
    for it in data["items"]:
        t = it.get("title")
        if t in TITLE_FIX:
            it["title_zh"] = TITLE_FIX[t]
            it["summary_zh"] = SUMMARY_FIX.get(t, it.get("summary_zh"))
            it["translated"] = True
            it["method"] = "manual"
            n += 1
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    titles.update(TITLE_FIX)
    summaries.update(SUMMARY_FIX)
    with open(T_JSON, "w", encoding="utf-8") as f:
        json.dump(titles, f, ensure_ascii=False, indent=2)
    with open(S_JSON, "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)

    # 重生报告
    subprocess.run(["python3.11", os.path.join(BASE, "report.py")], check=True)
    # 同步代码层覆盖表（随发布生效）
    subprocess.run(
        ["python3.11", os.path.join(BASE, "scripts", "regen_overrides.py")],
        check=True,
    )
    print("[fix0700] 回填 %d 条，标题覆盖表 %d，摘要覆盖表 %d"
          % (n, len(titles), len(summaries)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
