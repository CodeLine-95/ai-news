# -*- coding: utf-8 -*-
"""19:00 例行巡检：定稿本轮 3 条新增资讯的 NLLB 生硬译文。

写入 JSON 覆盖表 + 回填 news.json，再运行 scripts/regen_overrides.py
同步代码层 manual_overrides.py（部署端持久卷不会随发布更新 JSON 表）。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")
NEWS = os.path.join(BASE, "data", "news.json")

FIXES = {
    "MIT team discovers that unrealistic training data makes AI climate predictions more reliable": (
        "麻省理工团队发现：用「不真实」的训练数据反而让 AI 气候预测更可靠",
        "麻省理工学院研究人员开发出一种方法，使 AI 气候模型只需一次训练即可完成，"
        "而通常需要六到八次训练。他们用算法刻意生成带有极端二氧化碳或甲烷波动的"
        "非现实场景，让模型更加稳健。研究人员表示，以往这类气候模拟器往往在训练"
        "完成时就已经过时。",
    ),
    "XPENG WorldGPT Uses Shared Learning Across Cars, Robots and Drones": (
        "小鹏 WorldGPT 让汽车、机器人与无人机共享学习成果",
        "小鹏汽车于 2026 年 11 月 24 日发布 WorldGPT——一种能够预测物理场景并规划"
        "机器动作的世界行动模型。该模型在六种「具身形态」（机器类型）上训练："
        "汽车、船只、无人机、单臂机器人、双臂机器人和人形机器人。该系统属于小鹏"
        "图灵世界模型家族。WorldGPT 项目网站介绍，模型以一个或多个摄像头约一秒的"
        "视频片段和一条文字指令为输入。",
    ),
    "AI is straining America’s open records systems": (
        "AI 正在让美国信息公开制度不堪重负",
        "在佛蒙特州潘顿镇（人口 660 人），镇书记员凯尔·罗（Kyle Rowe）包揽所有工作："
        "编制预算、支付供应商款项、处理房产税纠纷，还兼任镇规划主管和选举主持官。"
        "在镇政府（一座 1858 年作为教堂建成的木结构建筑）的上午办公时间里，他还要"
        "处理信息公开申请。最近他忙得不可开交。过去，潘顿镇每年左右会收到 SmartProcure "
        "公司的一次申请，要求提供「全部采购记录」，内容从道路融雪盐、电脑到卫生纸"
        "无所不包。去年，这类申请变成了每季度一次。随后，不同公司开始提出更具体的"
        "请求，比如所有与应急道路警示灯相关的采购记录。这些有针对性的查询现在每月"
        "甚至更频繁地到来。",
    ),
}


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    titles = load(T_JSON)
    summaries = load(S_JSON)
    for key, (title_zh, summary_zh) in FIXES.items():
        titles[key] = title_zh
        summaries[key] = summary_zh
    save(T_JSON, titles)
    save(S_JSON, summaries)

    news = load(NEWS)
    fixed = 0
    for it in news["items"]:
        fix = FIXES.get(it.get("title"))
        if not fix:
            continue
        it["title_zh"], it["summary_zh"] = fix
        it["translated"] = True
        it["method"] = "manual"
        fixed += 1
    save(NEWS, news)
    print("定稿条目数:", fixed)


if __name__ == "__main__":
    main()
