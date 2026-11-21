# -*- coding: utf-8 -*-
"""2026-11-21 21:00 例行巡检：修复本轮新增 3 条的 NLLB 机翻缺陷。

本轮 21:00 调度（含 refresh）新增 3 条，均存在硬伤：
  #1 20:13 Marktechpost「Meet Thinking Machines」→ 误译「见面思考机」（Meet 谓语当成名词），
     公司名 Thinking Machines 应保留；摘要品牌/术语多处失真。
  #2 21:00 Wired「The Outages Are Just Getting Started」→ 误译「报名刚刚开始」
     （Outages 服务中断被当成报名/注册），应为「服务中断才刚刚开始」。
  #3 19:46 Marktechpost「OpenAI Ships...」→ 误译「OpenAI 船舶」（Ships 发布被当成船），
     摘要「全双模型/无效会议/染色扩展」等多处失真。

按既有巡检策略：同引擎全量重译会重复同样错误并覆盖既有人工定稿，
故只人工定稿本轮 3 条，并写入覆盖表（data JSON + 代码层 manual_overrides），
保证下一轮调度重跑时不被模型译文覆盖回去。
"""
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")
PY_FILE = os.path.join(BASE, "manual_overrides.py")

FIXES = {
    "Meet Thinking Machines Inkling 2 Mini: 26B Looped MoE Runs on a 32GB Mac": (
        "Thinking Machines 发布 Inkling 2 Mini：260 亿参数循环 MoE，可在 32GB Mac 上运行",
        "Thinking Machines Lab 发布了 Inkling 2 Mini——一款开放权重的循环 Transformer，总参数 264 亿。"
        "该模型对每个 token 重复使用其中间层 3 次，而非堆叠更多权重，"
        "使检查点体积控制在约 20GB，足以在 32GB 内存的 Mac 或单台 NVIDIA DGX Spark 上运行。"
        "对开发者而言，Inkling 2 Mini 是本地运行智能体编程、工具调用与文档处理任务的选项。"
        "模型以 Apache 2.0 许可证在 Hugging Face 上开放，并在 Tinker 平台提供托管推理与微调。"
        "要点速览——规模：总参数 264 亿、激活参数 34 亿（结合循环后每 token 有效参数 54 亿），"
        "上下文最高 100 万 token。运行硬件：32GB 及以上内存的 Apple 芯片、单台 NVIDIA DGX Spark，"
        "或 32GB 以上显存的 GPU。GGUF 构建由 Unsloth 与 llama.cpp 提供。"
        "性能：在 Artificial Analysis 指数上得分 20.1，与 Qwen3.8-27B 持平（自报数据）；"
        "最佳成绩为 SWE-bench Verified（仅 bash）79.2%。",
    ),
    "The Outages Are Just Getting Started": (
        "服务中断才刚刚开始",
        "人工智能正迫使企业更快地修补系统，因为攻击者正争相利用新发现的漏洞。"
        "欢迎来到互联网大面积中断的地狱。",
    ),
    "OpenAI Ships GPT-Live-1.1 for Voice Agents, Cuts Idle Cost to $0.02/Min": (
        "OpenAI 推出面向语音智能体的 GPT-Live-1.1，将闲置成本降至每分钟 0.02 美元",
        "OpenAI 已在 API 中提供 GPT-Live-1.1，模型 ID 为 gpt-live-1.1。"
        "GPT-Live-1.1 是一款面向多语言对话的全双工语音模型，可以边说边听。"
        "OpenAI 团队表示，它在各种语言中的口音更自然、更一致，任务完成也更可靠。"
        "此次发布还新增了待机（standby）计费状态，针对会话闲置时段收费更低；"
        "对运行语音智能体的团队而言，通话中的等待时间成本由此降低。"
        "要点速览——规模：实时会话默认上下文窗口为 128,000 token。运行方式：仅限 OpenAI 云端，"
        "通过 v1/live/sessions 接入，客户端以 WebRTC 或 WebSocket 连接，不开放权重、无量化版本。"
        "性能：OpenAI 称其在口音、转录、字母与数字处理以及任务完成方面均优于 GPT-Live-1。",
    ),
}


def put_override(path, key, value):
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        d = json.load(f)
    d[key] = value
    with open(path, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)


def upsert_py_dict(src, dict_name, mapping):
    marker = dict_name + " = {"
    start = src.index(marker) + len(marker)
    end = src.index("\n}", start)
    body = src[start:end]
    for en in mapping:
        pat = re.compile(r"^\s*'" + re.escape(en) + r"'.*$", re.M)
        body = pat.sub("", body)
    additions = ""
    for en, zh in mapping.items():
        additions += "\n    %r: %r," % (en, zh)
    return src[:start] + body.rstrip("\n") + additions + "\n" + src[end:]


def main():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    n = 0
    for it in data.get("items", []):
        t = it.get("title")
        if t in FIXES:
            zh_t, zh_s = FIXES[t]
            it["title_zh"] = zh_t
            it["summary_zh"] = zh_s
            it["translated"] = True
            it["method"] = "nllb+manual"
            n += 1

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    for en, (zh_t, zh_s) in FIXES.items():
        put_override(T_JSON, en, zh_t)
        put_override(S_JSON, en, zh_s)

    if os.path.exists(PY_FILE):
        with open(PY_FILE, "r", encoding="utf-8") as f:
            src = f.read()
        src = upsert_py_dict(src, "TITLE_OVERRIDES",
                             {en: zh_t for en, (zh_t, _) in FIXES.items()})
        src = upsert_py_dict(src, "SUMMARY_OVERRIDES",
                             {en: zh_s for en, (_, zh_s) in FIXES.items()})
        with open(PY_FILE, "w", encoding="utf-8") as f:
            f.write(src)

    import report
    report.main()

    print("[fix_2100_patrol] 已定稿 %d 条（data + 覆盖表 + 代码层 + 报告）" % n)
    return 0 if n == len(FIXES) else 1


if __name__ == "__main__":
    raise SystemExit(main())
