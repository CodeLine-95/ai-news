# -*- coding: utf-8 -*-
"""19:00 例行巡检译文定稿。

NLLB 对专有名词存在稳定误译（Anthropic→「人文」、Ant Group→「团/子集团」、
Ship→「船」），原样重译仍会复现，因此走既有的人工覆盖表三层回填：
1) data/news.json 立即回填
2) data/titles_override.json / data/summaries_override.json 持久层
3) scripts/regen_overrides.py 同步到 manual_overrides.py 代码层（随发布生效）
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

FIXES = {
    "Ant Group Releases LingSante-3.1-flash: An Open-Weight MoE Model with 560B Total Parameters and 25B Activations per Token": {
        "title_zh": "蚂蚁集团发布 LingSante-3.1-flash：开放权重 MoE 模型，总参数 560B、每 Token 激活 25B",
        "summary_zh": (
            "蚂蚁集团开源了 LingSante 系列医疗与健康 AI 模型，该系列是健康应用 Afu 背后的技术底座。"
            "旗舰模型 LingSante-3.1-flash 采用开放权重，总参数 560B、每 token 激活约 25B，"
            "按 MIT 许可证发布，支持 100 万 token 上下文窗口。在新的 InclusionMed 评测中，"
            "它在开放模型中得分最高。该模型可自托管，面向临床推理、医疗搜索与工具调用智能体训练。"
            "要点：自托管模型，面向临床推理、医疗搜索和工具使用智能体；规模为 560B 总参数、"
            "每 token 约 25B 激活（MoE），100 万 token 上下文；可在多 GPU 服务器运行，"
            "参考 SGLang 配置为 8×H200 或 4×GB300，并提供 MXFP4 量化检查点；"
            "在医疗推理与医疗智能体方面表现强劲，在通用编程与 CLI 智能体任务上较弱。"
        ),
    },
    "Anthropic Introduces Claude Ship to Review, Fix, and Approve Pull Requests by Policy": {
        "title_zh": "Anthropic 推出 Claude Ship：按团队策略审查、修复并批准拉取请求",
        "summary_zh": (
            "Anthropic 在 Claude Team 与 Enterprise 计划中推出 Claude Ship——"
            "一组可审查 GitHub 拉取请求、推送修复代码，并按团队策略批准变更的智能体。"
        ),
    },
    "Robotics startup Embo raises $110 million in seed funding to build world-model AI for robots": {
        "title_zh": "机器人初创公司 Embo 完成 1.1 亿美元种子融资，打造面向机器人的世界模型 AI",
        "summary_zh": (
            "Embo 完成 1.1 亿美元种子融资，用于构建基于世界模型的通用机器人大脑。"
            "其 AI 从互联网视频中学习物理世界的运作方式，并在仿真环境中练习运动技能。"
            "Google DeepMind、Meta 与 MIT 的研究人员参与创立，通用机器人 AI 竞赛正在加速。"
        ),
    },
    "Anthropic Launches Claude Meetings Beta for Live Video Calls": {
        "title_zh": "Anthropic 推出 Claude Meetings 测试版，支持实时视频通话",
        "summary_zh": (
            "Anthropic 于 2026 年 11 月 12 日开始面向 Team 与 Enterprise 计划推出 Claude Meetings 测试版，"
            "让 Claude 作为可见参与者加入视频通话，回答问题并将讨论整理为笔记、待办事项和可编辑文档。"
            "通话中，参会者可口头或通过聊天向 Claude 提问。默认情况下 Claude 以文字作答，"
            "并可在获得相关人员许可后使用已连接的工具。"
        ),
    },
    "Anthropic Files Preliminary IPO Terms as Investors Commit $26B": {
        "title_zh": "Anthropic 提交 IPO 初步条款，投资者承诺 260 亿美元",
        "summary_zh": (
            "AI 开发商 Anthropic 于 2026 年 11 月 10 日提交修订后的首次公开募股条款，"
            "涉及 8.25 亿股 A 类股，预计每股 70 至 78 美元，并附带 260 亿美元的或有私募配售。"
            "Anthropic 将出售 801,351,354 股，售股股东另出售 23,648,646 股，二级销售所得不归 Anthropic 所有。"
            "按 78 美元上限计算，基础发行总额约 643.5 亿美元（按披露股数乘以该价格计算）；"
            "Anthropic 的主发行部分在扣除承销折扣与费用前约募资 625 亿美元。"
        ),
    },
    "Flagship Pioneering Launches London Lab to Build AI-Native Companies": {
        "title_zh": "Flagship Pioneering 在伦敦设立实验室，孵化 AI 原生公司",
        "summary_zh": (
            "Flagship Pioneering 于 2026 年 11 月 16 日宣布，将在伦敦设立 Flagship Origination Lab, U.K.，"
            "初期投入 1 亿英镑。该实验室将构思、测试、资助并孵化 AI 原生平台公司，"
            "是 Flagship 在美国之外首个专门的公司创建单元。伦敦团队隶属于 Flagship Labs，"
            "将聚焦人类与行星健康及其他科学与技术前沿。"
        ),
    },
}


def main():
    path = os.path.join(DATA, "news.json")
    with open(path, encoding="utf-8") as f:
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
            print("fixed:", it.get("date"), it.get("time"), en)

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
    with open(path, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    print("changed:", changed, "/", len(FIXES))
    print("title overrides:", len(tov), "summary overrides:", len(sov))


if __name__ == "__main__":
    main()
