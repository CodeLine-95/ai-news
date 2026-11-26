# -*- coding: utf-8 -*-
"""05:00 巡检：定稿 5 条 NLLB 机翻硬伤（2026-11-27 00:xx 条目）。

把这些人工定稿合并进 data/ 的 JSON 覆盖表，随后运行
python3.11 scripts/regen_overrides.py 同步到代码层 manual_overrides.py，
再由 server 的启动回填逻辑写回 news.json 并重建报告。
"""
import json
import os
import shutil

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

TITLES = {
    "AI Could Soon Edit Live Videos in Real Time":
        "AI 很快就能实时编辑直播视频",
    "Nvidia GPU Sellers Reject Any Chinese Rental Capacity, CNBC Reports":
        "CNBC 报道：英伟达 GPU 卖家拒绝向中国出租算力",
    "Moonshot AI Begins Distilling From Google and Meta Models Amid Delays":
        "模型延期之际，月之暗面开始从 Google 和 Meta 模型中蒸馏",
    "As Anthropic IPOs, Grand Theft Auto VI proves why efficiency isn’t a virtue":
        "Anthropic 上市之际，《侠盗猎车手 VI》证明效率为何不是美德",
    "Slack vs. ClickUp: Which Is Better for Teamwork and Project Delivery?":
        "Slack 与 ClickUp 对比：哪个更适合团队协作与项目交付？",
}

SUMMARIES = {
    "AI Could Soon Edit Live Videos in Real Time":
        "现场视频让观众与事件进程保持直接连接，既能跟上事态发展，也能在语境中听到发言人的声音。"
        "AI 驱动的编辑可以在语音播出前重新塑造这种连接。例如，微软近期公布的专利申请提出"
        "替换口述词语并调整唇部动作，以接近实时地匹配改动后的语音。",
    "Nvidia GPU Sellers Reject Any Chinese Rental Capacity, CNBC Reports":
        "CNBC 于 2026 年 11 月 26 日报道，英伟达芯片供应商已告知 Neocloud 运营商："
        "若其计算容量将被租给中国公司，就不再提供 GPU。两名熟悉私人沟通内容的人士透露了此事。",
    "Moonshot AI Begins Distilling From Google and Meta Models Amid Delays":
        "路透社 2026 年 11 月 26 日报道称，Z.ai 在 GLM-5.5 上进度落后，其下一款旗舰模型约有"
        " 3 万亿参数。与此同时，月之暗面（Moonshot AI）已开始从 Google 和 Meta 的模型中蒸馏，"
        "因为 OpenAI 等模型的训练数据变得难以获取。蒸馏是指用能力更强的模型生成的答案来"
        "训练另一个系统。",
    "As Anthropic IPOs, Grand Theft Auto VI proves why efficiency isn’t a virtue":
        "在 Anthropic 上市当天，一款精心打磨的游戏成为史上最成功的娱乐产品之一。",
    "Slack vs. ClickUp: Which Is Better for Teamwork and Project Delivery?":
        "热闹的团队频道并不意味着项目能按时交付：对话在发生，但负责人、逾期任务与依赖关系"
        "无人可靠掌握。Slack 与 ClickUp 解决的是问题的不同侧面——Slack 把人和已接入的工具"
        "带入对话，ClickUp 则包含聊天与协作文档。当核心需求是跨部门沟通且已在使用相关工具时，"
        "Slack 更合适；若需要组织、监控工作记录，ClickUp 更合适。",
}


def merge(path, updates):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    shutil.copyfile(path, path + ".bak.0500patrol1127")
    before = len(data)
    data.update(updates)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print("[fix] %s: %d -> %d" % (os.path.basename(path), before, len(data)))


if __name__ == "__main__":
    merge(T_JSON, TITLES)
    merge(S_JSON, SUMMARIES)
