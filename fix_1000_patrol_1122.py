# -*- coding: utf-8 -*-
"""10:00 例行巡检：人工定稿 1 条 NLLB 机翻硬伤。

本轮平台重启后首轮补抓自动新增条目（Marktechpost / TensorLean）：
  - "Lean-based verifier" 被译成「基于 Len 的验证器」（工具名拼写错误）
  - "tensor-level math spec" 被译成「子级数学规范」（语义错误）
  - "data race" 被译成「数据竞赛」（并发术语错误）

固化覆盖三层（与历次巡检一致）：
1) data/news.json 内条目直接回填
2) data/titles_override.json / data/summaries_override.json（JSON 层）
3) 再运行 scripts/regen_overrides.py 同步到 manual_overrides.py（代码层）
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

FIXES = [
    {
        "match": "columbia-certik-tensorlean-formal-verification-gpu-kernels",
        "title_zh": "哥伦比亚大学与 CertiK 团队推出 TensorLean：面向 GPU 内核形式化验证的框架",
        "summary_zh": (
            "来自哥伦比亚大学和 CertiK 的研究人员推出了 TensorLean——一个在 PTX 层面对 GPU 内核进行"
            "形式化验证的框架。TensorLean 是基于 Lean 的验证器，可证明编译后的内核符合张量级数学规范。"
            "研究团队检查了 149 个内核实例，涵盖 FlashAttention-2/-3/-4 以及 DeepGEMM 的全部内核，"
            "其中 83 个被证明正确，其余 66 个暴露出 38 个正确性缺陷。要点速览：规模——1800 行 PTX "
            "解析器；规范共 10,278 行，对应 151,285 行内核源码，比例接近 1:15；运行于 16 核工作站，"
            "可检查针对 A100、H100 和 B200 编译的 PTX 内核；性能——149 个内核实例中 83 个验证通过，"
            "在 6 个项目中发现 38 个缺陷；亮点——捕获了一处在 17,760 次测试运行中从未出现的 "
            "FlashAttention-4 数据竞争。"
        ),
    },
]


def main():
    with open(os.path.join(DATA, "news.json"), encoding="utf-8") as f:
        db = json.load(f)
    items = db["items"] if isinstance(db, dict) else db

    tpath = os.path.join(DATA, "titles_override.json")
    spath = os.path.join(DATA, "summaries_override.json")
    tov = json.load(open(tpath, encoding="utf-8")) if os.path.exists(tpath) else {}
    sov = json.load(open(spath, encoding="utf-8")) if os.path.exists(spath) else {}

    changed = 0
    for fx in FIXES:
        hit = None
        for it in items:
            if fx["match"].lower() in (it.get("link") or "").lower():
                hit = it
                break
        if not hit:
            print("MISS:", fx["match"])
            continue
        en = hit["title"]
        hit["title_zh"] = fx["title_zh"]
        hit["summary_zh"] = fx["summary_zh"]
        hit["translated"] = True
        hit["method"] = "nllb+manual"
        tov[en] = fx["title_zh"]
        sov[en] = fx["summary_zh"]
        changed += 1
        print("fixed:", hit.get("date"), hit.get("time"), en, "->", fx["title_zh"])

    with open(tpath, "w", encoding="utf-8") as f:
        json.dump(tov, f, ensure_ascii=False, indent=2)
    with open(spath, "w", encoding="utf-8") as f:
        json.dump(sov, f, ensure_ascii=False, indent=2)
    with open(os.path.join(DATA, "news.json"), "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    print("changed:", changed, "/", len(FIXES))


if __name__ == "__main__":
    main()
