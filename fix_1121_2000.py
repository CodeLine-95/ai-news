# -*- coding: utf-8 -*-
"""2026-11-21 20:00 例行巡检：人工定稿 2 条 NLLB 机翻硬伤。

1) 19:19 Riemann hypothesis（The Decoder，本轮新增）：
   「莱曼/里曼假设」→「黎曼假设」；「人类声称」漏掉 Anthropic 主体；
   「全人类竞争的草案」语义错乱；「证据」→「证明」；「是否坚持」→「是否站得住脚」。
2) 02:13 13 Best Agent Gateways（Marktechpost，存量硬伤）：
   标题「1326 年」「康格，双」为数字/Kong、Bifrost 误译；
   摘要「过他们所看到的工具」漏「过滤」、「每次电话」→「每次调用」、
   「重量了 5 个标准」→「权衡 5 项标准」。

定稿写入 JSON 覆盖表（持久卷即时生效）+ 回填 news.json；
随后由 scripts/regen_overrides.py 同步代码层 manual_overrides.py。
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
    "Hours after Anthropic claims a Claude proof of the Riemann hypothesis, Stanford releases an all-human competing draft": (
        "Anthropic 声称用 Claude 证明黎曼假设数小时后，斯坦福发布了一份完全由人类完成的竞争性证明草稿",
        "Anthropic 数学家 Levent Alpöge 称，他用 Claude 证明了黎曼假设——数学界 167 年来最著名的未解难题——"
        "相关证明已在 Lean 中形式化，长达 25 万余页。仅数小时后，斯坦福研究人员便发表了一份独立的、"
        "完全由人类完成的竞争性证明。数学家目前正在核验这两份证明是否站得住脚。",
    ),
    "13 Best Agent Gateways in 2026 for MCP, A2A and LLM Traffic: Kong, Bifrost, AgentCore, Arcade": (
        "2026 年面向 MCP、A2A 与 LLM 流量的 13 款最佳智能体网关：Kong、Bifrost、AgentCore、Arcade",
        "智能体不再只是调用模型。它们通过 MCP 调用工具、通过 A2A 将任务委托给其他智能体，并在业务系统内执行操作。"
        "优秀的智能体网关正位于这条链路上，决定谁能做什么。本文从流量覆盖、身份、部署和价格四个维度对其中 13 款进行比较。"
        "什么是智能体网关？智能体网关是一个控制点，负责认证智能体、过滤其可见的工具，并记录每一次调用。"
        "普通的 LLM 网关只路由模型请求。智能体网关则增加了 MCP 工具治理、智能体身份，以及越来越多的 A2A 流量控制。"
        "下面的排名为编辑整理，权衡 5 项标准：流量覆盖、身份与授权、部署选项、成熟度与价格透明度。"
        "13 款最佳智能体网关排名：1. Kong AI Gateway——Kong 通过一个统一控制面管理 LLM、MCP 与 A2A 流量。",
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
    """在 manual_overrides.py 的指定字典中插入/替换条目（保持字典结构）。"""
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

    # 重新生成摘要报告，保持与网站数据一致
    import report
    report.main()

    print("[fix_1121_2000] 已定稿 %d 条（data + 覆盖表 + 代码层 + 报告）" % n)
    return 0 if n == len(FIXES) else 1


if __name__ == "__main__":
    raise SystemExit(main())
