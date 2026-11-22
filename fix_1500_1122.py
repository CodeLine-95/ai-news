# -*- coding: utf-8 -*-
"""2026-11-22 15:00 巡检：修复本轮新增 2 条 InfoQ AI 译文的 NLLB 机翻硬伤。

1) AWS Lambda《AWS Lambda Now Runs GPU Inference with 48 Concurrent
   Invocations Sharing One Model per GPU》(14:27)
   缺陷 a：「每 GPU 共享 48 个同步调用，每 GPU 共享一个模型」——
          "Concurrent Invocations" 是「并发调用」不是「同步调用」，
          且「每 GPU 共享」重复出现，语义冗余。
   缺陷 b：摘要「可共享每 GPU，vLLM 和 SGLang 基图像的最大 48 个同时调用」
          语序错乱；"base images" 是「基础镜像」不是「基图像」；
          "90-minute asynchronous timeouts" 是「90 分钟异步超时」。
   缺陷 c：「第一次实践测试报告了八分钟的发布，没有响应流」——
          "first hands-on tests" 是「首批上手测试」，
          "no response streaming" 是「不支持响应流式传输」。

2) Google《Google Announces Agent Compute Engine for Secure AI Agent
   Execution》(14:30)
   缺陷 a：「凭证，API 密钥和 OAuth 刷新 token」中英混排、标点用英文逗号。
   缺陷 b：「使用外部智能体网关来验证请求并注入所需的秘密」——
          "Agent Gateway" 为产品名应保留，secrets 在此为「密钥」。

本脚本把人工定稿写入 data/news.json 与 JSON 覆盖表，
再由 scripts/regen_overrides.py 固化到代码层 manual_overrides.py。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

AWS_TITLE = ("AWS Lambda Now Runs GPU Inference with 48 Concurrent "
             "Invocations Sharing One Model per GPU")
GOOGLE_TITLE = "Google Announces Agent Compute Engine for Secure AI Agent Execution"

TITLE_FIX = {
    AWS_TITLE:
        "AWS Lambda 现支持 GPU 推理：每块 GPU 可由 48 个并发调用共享同一模型",
    GOOGLE_TITLE:
        "Google 发布 Agent Compute Engine，为 AI 智能体提供安全执行环境",
}

SUMMARY_FIX = {
    AWS_TITLE:
        "AWS Lambda 现已通过 Lambda Managed Instances 在 EC2 G 系列 GPU "
        "实例上运行事件函数，每块 GPU 最多支持 48 个并发调用共享同一模型，"
        "提供无需编写处理器代码的 vLLM 与 SGLang 基础镜像，并将异步超时"
        "延长至 90 分钟。计费方式为实例价格外加 9.75% 服务费；首批上手"
        "测试报告显示发布耗时约八分钟，且不支持响应流式传输。",
    GOOGLE_TITLE:
        "Google 近日宣布推出 Agent Compute Engine——一项在隔离微虚拟机"
        "（microVM）中运行 AI 智能体的托管服务，具备检查点功能，可暂停与"
        "恢复执行环境。该设计将凭证、API 密钥与 OAuth 刷新令牌置于智能体"
        "沙盒之外，由外部 Agent Gateway 对请求进行认证并注入所需的密钥。",
}


def main():
    with open(DATA, "r", encoding="utf-8") as f:
        data = json.load(f)
    items = data.get("items", [])

    targets = [it for it in items if it.get("title") in TITLE_FIX]
    if len(targets) != 2:
        print("[fix_1500] 目标条目数异常：%d，跳过" % len(targets))
        return 1

    for it in targets:
        it["title_zh"] = TITLE_FIX[it["title"]]
        it["summary_zh"] = SUMMARY_FIX[it["title"]]
        it["translated"] = True
        it["method"] = "nllb+manual"
        print("[定稿] %s\n    -> %s" % (it["title"], it["title_zh"]))

    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

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

    print("[fix_1500] 覆盖表 标题 %d 条 / 摘要 %d 条" % (len(to), len(so)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
