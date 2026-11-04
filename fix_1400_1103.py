# -*- coding: utf-8 -*-
"""2026-11-03 14:00 巡检：修复本轮新增 2 条的译文缺陷 + 根因修复。

本轮新增
--------
1) Unite.AI《Anthropic's Planned IPO Would Give CommSec Australian
   Retail Lead Role》（13:32）
   缺陷 a：「进入 Claude Reuters 开发商的公开发行」——原文是
         "the Claude developer's public offering"，模型把上一句的主语
         Reuters 与 Claude 开发者拼在一起，读者会误以为存在一家
         「Claude Reuters」公司。
   缺陷 b：「将该报价纳入……招商说明书」——offer 是"发行"不是"报价"，
         prospectus 是"招股说明书"不是"招商说明书"。
   缺陷 c：标题「将给 CommSec 澳大利亚零售业领先作用」语义不通。

2) Unite.AI《PATEO Deploys Doubao and Nemotron in Thor-Based Vehicle
   AI Box》（13:17）
   缺陷 a：「35 亿参数」——原文 35-billion-parameter，实为 350 亿参数，
         数量级差 10 倍。这是严重事实错误。
         根因：translate._EN_SCALED_RE 只认 "35 billion"，
               不认连字符写法 "35-billion-parameter"，导致数量级
               校正（_align_scale_magnitude）拿不到英文侧锚点。
         修复：正则允许 "35-billion" 这种连字符形式。
   缺陷 b：「本地 AI 推断」——AI 语境 inference 一律是「推理」。
         根因：TERM_FIXES 只覆盖「本地推断」，中间夹 "AI" 时匹配不上。
   缺陷 c：PATEO 被音译成「帕蒂奥」，中文读者无法定位公司。
         根因：BRAND_TERMS 未登记 PATEO。
   缺陷 d：标题「在 Thor-Based Vehicle AI Box 中」中英拼接；
         摘要「车辆驾驶的智能体平台」实为 "agent platform for vehicle
         cockpits"（座舱智能体平台）。

本脚本做三件事：
  A. 用修好的 translate.py 重译这两条（标题 + 摘要），写回 data/news.json；
  B. 对机器译文仍不达标的字段做人工定稿，写入 JSON 覆盖表；
  C. 由 scripts/regen_overrides.py 固化到 manual_overrides.py（随发布走）。
"""
import json
import os

import translate

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

IPO_TITLE = ("Anthropic’s Planned IPO Would Give CommSec Australian "
             "Retail Lead Role")
PATEO_TITLE = ("PATEO Deploys Doubao and Nemotron in Thor-Based Vehicle "
               "AI Box")

# 人工定稿标题（机器译文仍中英拼接或语义不通）
TITLE_FIX = {
    IPO_TITLE:
        "Anthropic 拟议 IPO 将让 CommSec 担任澳洲零售牵头券商",
    PATEO_TITLE:
        "PATEO 在 Thor 车载 AI Box 中部署 Doubao 与 Nemotron",
}

# 人工定稿摘要
SUMMARY_FIX = {
    IPO_TITLE:
        "2026 年 11 月 3 日，路透社报道，若 IPO 顺利推进，澳大利亚联邦银行"
        "（CBA）旗下券商部门 CommSec 将担任 Anthropic 拟议澳洲零售股发行的"
        "牵头零售经纪商，为本地投资者提供参与这家 Claude 开发商公开发行的"
        "潜在通道。CommSec 表示，Anthropic 预计会把本次发行纳入提交给该国"
        "企业监管机构的招股说明书中。",
    PATEO_TITLE:
        "2026 年 11 月 2 日，PATEO 宣布将在基于 NVIDIA DRIVE AGX Thor "
        "打造的 AI Box 中部署 NVIDIA Nemotron 与字节跳动的 350 亿参数 "
        "Doubao 语言模型，把本地 AI 推理与面向车辆座舱的智能体平台结合在"
        "一起。PATEO 还获得了一家未具名的新能源汽车头部厂商的新一代车型"
        "项目提名。",
}


def main():
    with open(DATA, "r", encoding="utf-8") as f:
        data = json.load(f)
    items = data.get("items", [])

    targets = [it for it in items
               if it.get("title") in (IPO_TITLE, PATEO_TITLE)]
    if not targets:
        print("[fix_1400_1103] 未找到目标条目，跳过重译")
        return 1

    # A. 用修好的引擎重译
    titles = [it["title"] for it in targets]
    summaries = [it.get("summary") or "" for it in targets]
    zh_titles, _ = translate.translate_list(titles, beams=2)
    zh_sums, _ = translate.translate_list_chunked(summaries, beams=3)
    for it, zt, zs in zip(targets, zh_titles, zh_sums):
        it["title_zh"] = zt
        it["summary_zh"] = zs
        it["translated"] = True
        it["method"] = "nllb"

    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    for it in targets:
        print("[重译] %s\n    -> %s" % (it["title"], it["title_zh"]))
        print("       %s" % it["summary_zh"][:200])

    # B. 人工定稿写入覆盖表
    with open(T_JSON, "r", encoding="utf-8") as f:
        to = json.load(f)
    with open(S_JSON, "r", encoding="utf-8") as f:
        so = json.load(f)
    for k, v in TITLE_FIX.items():
        to[k] = v
    for k, v in SUMMARY_FIX.items():
        so[k] = v
    with open(T_JSON, "w", encoding="utf-8") as f:
        json.dump(to, f, ensure_ascii=False, indent=2)
    with open(S_JSON, "w", encoding="utf-8") as f:
        json.dump(so, f, ensure_ascii=False, indent=2)

    print("[fix_1400_1103] 覆盖表 标题 %d 条 / 摘要 %d 条" % (len(to), len(so)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
