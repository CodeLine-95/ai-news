# -*- coding: utf-8 -*-
"""2026-11-23 17:00 例行巡检：定稿本轮新增 1 条 NLLB 机翻硬伤。

Marktechpost《Meta TLX Brings Warp-Group GPU Control to Triton on Hopper,
Blackwell, AMD》(16:24)：NLLB 标题译成「Meta TLX 带来了 Warp-Group GPU
控制在 Hopper，Blackwell，AMD 上的 Triton」，语序生硬且把平台与语言关系
译反（应为「为 Triton 带来 GPU 控制，支持这些平台」）；摘要把 TMA/cluster
误作「障碍，TMA 和集群」、speedup 误作「加速度」、TL;DR 粘连成
「Triton.TL;DR」。按官方技术报告定稿标题与摘要。

覆盖三层：news.json 回填 + JSON 覆盖表 + manual_overrides.py（regen）。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

TITLE_FIX = {
    "Meta TLX Brings Warp-Group GPU Control to Triton on Hopper, Blackwell, AMD":
        "Meta TLX 为 Triton 带来 Warp-Group 级 GPU 控制，支持 Hopper、Blackwell 与 AMD",
}

SUMMARY_FIX = {
    "Meta TLX Brings Warp-Group GPU Control to Triton on Hopper, Blackwell, AMD": (
        "Meta 发布了一份关于 TLX（Triton Low-Level Extensions，Triton 底层扩展）的详细报告，"
        "这是支撑 Meta 生产环境机器学习内核的 GPU 编译器扩展。Meta TLX 是 Triton 的一个扩展，"
        "向 Python 内核开放 warp group（线程束组）、barrier（屏障）、TMA 和 cluster（集群）等能力，"
        "面向 NVIDIA Hopper、Blackwell 以及 AMD MI300、MI350 系列 GPU。对内核工程师而言，其意义"
        "在于无需离开 Triton 即可获得 CUDA 级别的控制力。核心要点：它是 Triton 的扩展，而非一门"
        "新语言；一个 Blackwell GEMM 大约只需 200 行 Python 级 Triton 代码；运行平台包括 NVIDIA "
        "Hopper（H100）、Blackwell（B200、GB200）以及 AMD MI300、MI350 系列；采用 MIT 许可证。"
        "性能方面，在 6 种 H100 FP16 GEMM 形状上达到 cuBLAS 的 -0.9% 至 +3.7% 区间；最佳成绩是"
        "在 H100 线性压缩内核上实现 4 倍加速（用于广告推理，Meta）。"
    ),
}


def main():
    db = json.load(open(DATA, encoding="utf-8"))
    items = db["items"] if isinstance(db, dict) else db
    changed = 0
    for it in items:
        en = (it.get("title") or "").strip()
        if en not in TITLE_FIX:
            continue
        it["title_zh"] = TITLE_FIX[en]
        it["summary_zh"] = SUMMARY_FIX[en]
        it["translated"] = True
        it["method"] = "nllb+manual"
        changed += 1
        print("fixed:", it.get("date"), it.get("time"), en[:60])
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    titles = json.load(open(T_JSON, encoding="utf-8"))
    summaries = json.load(open(S_JSON, encoding="utf-8"))
    added_t = added_s = 0
    for k, v in TITLE_FIX.items():
        if titles.get(k) != v:
            titles[k] = v
            added_t += 1
    for k, v in SUMMARY_FIX.items():
        if summaries.get(k) != v:
            summaries[k] = v
            added_s += 1
    with open(T_JSON, "w", encoding="utf-8") as f:
        json.dump(titles, f, ensure_ascii=False, indent=2)
    with open(S_JSON, "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)

    print("[fix_1700_1123] news.json 回填 %d 条；标题定稿 %d / 摘要定稿 %d" %
          (changed, added_t, added_s))
    print("[fix_1700_1123] 覆盖表 %d / %d 条" % (len(titles), len(summaries)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
