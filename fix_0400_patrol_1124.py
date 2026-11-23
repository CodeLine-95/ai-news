# -*- coding: utf-8 -*-
"""2026-11-24 04:00 例行巡检：定稿本轮新增 6 条 NLLB 机翻硬伤。

04:00 整点调度抓取 02:54-03:50 共 6 条，均为 nllb 机翻，主要问题：
1) Unite.AI Embo：$110M 误作「1 亿美元」（应为 1.1 亿）、A16z 未保留缩写、
   Andreessen Horowitz 未括注、「hold up in unfamiliar situations」句式崩坏；
2) The Verge Nothing Ear Note：品牌 Nothing 误译为「什么都没有/没有什么」、
   charging case 误作「充电箱」、Bloomberg 误作「博公司」；
3) TechCrunch Google Search：漏译主语 Google、「tap into」误作「入」、
   Drive/Wallet 误作「驱动器/钱包」、Personal Intelligence 未规范；
4) Unite.AI Nothing Ear Note：品牌 Nothing 同样误译、Bloomberg 误作「博社」、
   充电 case 误作「充电箱」；
5) Unite.AI Ferrum Health：Ferrum 误译为「铁路」、AHN 未展开、
   foundation model 误作「基础模型技术」表述不清；
6) Unite.AI Indiana University：Lilly Endowment 误作「利利基金会」、
   AI literacy 误作「人工智能识别」。

覆盖三层：news.json 回填 + JSON 覆盖表 + （随后 regen）代码层 manual_overrides.py。
覆盖表 key 直接从 item['title'] 读取，避免智能引号/短横线手工录入偏差。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

FIX = {
    "16b03851519ba02df3c7e6c1b1044450": (
        "机器人 AI 初创公司 Embo 获 a16z 领投 1.1 亿美元种子轮融资",
        "Embo 于 2026 年 11 月 23 日宣布，已完成由 Andreessen Horowitz（a16z）领投的 1.1 亿美元种子轮融资，用于构建智能机器人 AI 模型——借助互联网视频与模拟练习，让机器人在陌生场景中也能稳定发挥技能。Khosla Ventures、DST Global、NVIDIA 旗下风投机构 NVentures 及其他战略投资者亦参与本轮。",
    ),
    "ced394d4b6aee05268b067c5c3804855": (
        "Nothing 即将推出的 Ear Note 是一款支持 AI 转录的无线耳机",
        "Nothing 的新 AI 设备 Ear Note 是一副耳机及其配套充电盒，充电盒内置麦克风，可录制并转录对话，并配有应用管理录音、转录文本与 AI 生成的摘要，类似 Apple 新版 Watch 功能以及 Amazon 的 Bee 可穿戴设备等产品。Nothing CEO 卡尔·佩伊（Carl Pei）已向彭博社（Bloomberg）展示该设备，但表示在 12 月 8 日计划发布前尚未确定价格。",
    ),
    "389c89635cfdfbd73445a3e8c9649940": (
        "Google 搜索的 AI 模式现可接入 Drive 与 Wallet，提供更个性化回答",
        "Google 将 AI 模式中的「个人智能」（Personal Intelligence）拓展至 Drive、Wallet 及 Gemini 应用，借此利用其生态系统中已有的海量用户数据，为用户提供更个性化的响应。",
    ),
    "f2218cd7194045881dea537f735ba311": (
        "Nothing 预览 Ear Note 耳机：支持 AI 录音与转录",
        "据 The Verge 转引彭博社 2026 年 11 月 23 日报道，Nothing CEO 卡尔·佩伊（Carl Pei）展示了 Ear Note 耳机及其内置麦克风的充电盒，可用于录音与 AI 转录，计划在 2026 年 12 月 8 日发布。该系统可通过耳机或充电盒采集音频，配套应用负责管理录音、转录文本与 AI 生成的摘要。佩伊表示，公司在发布前尚未敲定价格。",
    ),
    "159abeb4ad6ce6fc7b72993f1a7296cd": (
        "Ferrum Health 将在 AHN 旗下 16 家医院统筹管理影像 AI",
        "Ferrum Health 于 2026 年 11 月 23 日宣布，阿勒格尼健康网络（Allegheny Health Network，AHN）已选定其作为企业级影像 AI 合作伙伴，并将在旗下 16 家医院启动一项计划。该计划将 AI 部署与持续的安全监测及临床、财务影响评估相结合，覆盖现有获得 FDA 批准的应用，以及基于基础模型技术构建的内部模型。",
    ),
    "60481f7495d296f143bdef516a99d3eb": (
        "印第安纳大学获 2500 万美元资助，用于九校区扩展 AI 应用",
        "一笔 2500 万美元的 Lilly Endowment（礼来基金会）资助将支持印第安纳大学到 2030 年开展分学科的 AI 素养教育、重新设计评估方式并改进学生服务。",
    ),
    # 补抓历史条目（2026-11-23 16:00）：connected intelligence 应为「互联智能」，
    # in-house legal 应为「企业法务」，原译「连接的情报用于内部法律」生硬。
    "4201990503e1793f9ebe3e7c2634480d": (
        "面向企业法务的互联智能",
        "观看 OpenAI 的 Stacey Wang 与 Craig Bruney、LECG 的 Mary O'Carroll 以及 Cooley 的 Richard Segal，探讨 AI 如何帮助内部法务团队打通业务背景、构建可复用的工作流程，并更充分地借助外部律师的力量。",
    ),
}


def main():
    db = json.load(open(DATA, encoding="utf-8"))
    items = db["items"] if isinstance(db, dict) else db
    titles = json.load(open(T_JSON, encoding="utf-8"))
    summaries = json.load(open(S_JSON, encoding="utf-8"))

    changed = added_t = added_s = 0
    for it in items:
        iid = it.get("id")
        if iid not in FIX:
            continue
        title_zh, summary_zh = FIX[iid]
        en = (it.get("title") or "").strip()
        it["title_zh"] = title_zh
        it["summary_zh"] = summary_zh
        it["translated"] = True
        it["method"] = "nllb+manual"
        changed += 1
        print("fixed:", it.get("date"), it.get("time"), en[:60])
        if titles.get(en) != title_zh:
            titles[en] = title_zh
            added_t += 1
        if summaries.get(en) != summary_zh:
            summaries[en] = summary_zh
            added_s += 1

    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    with open(T_JSON, "w", encoding="utf-8") as f:
        json.dump(titles, f, ensure_ascii=False, indent=2)
    with open(S_JSON, "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)

    print("[fix_0400_1124] news.json 回填 %d 条；标题定稿 %d / 摘要定稿 %d" %
          (changed, added_t, added_s))
    print("[fix_0400_1124] 覆盖表 %d / %d 条" % (len(titles), len(summaries)))
    return 0 if changed == len(FIX) else 1


if __name__ == "__main__":
    raise SystemExit(main())
