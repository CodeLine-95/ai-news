# -*- coding: utf-8 -*-
"""2026-11-25 13:00 巡检：定稿 12:10 新增的 Unite.AI 条目。

NLLB 直译把标题译成「9/4 绑定对矩阵乘法」，摘要出现「复杂数量」「无比矩阵
乘法指数」「数学操作乘以」等生硬表达。本脚本写入人工定稿，随后由
scripts/regen_overrides.py 固化到 manual_overrides.py（随发布生效）。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

TITLE_EN = "OpenAI Preprint Reports 9/4 Bound for Matrix Multiplication"

TITLE_FIX = {
    TITLE_EN: "OpenAI 预印本报告：复矩阵乘法指数上界为 9/4",
}

SUMMARY_FIX = {
    TITLE_EN: (
        "OpenAI 发布预印本，报告了复数域矩阵乘法指数的上界为 9/4。"
        "手稿日期为 2026 年 10 月 2 日，论文文件在代码仓库的首次提交日期为 "
        "2026 年 10 月 6 日。论文研究的是 ω，即渐近矩阵乘法指数："
        "满足如下条件的 τ 的下确界——对任意正数 ε，当 n 趋于无穷时，"
        "矩阵乘法需要 O_ε(n^(τ+ε)) 次标量算术运算。"
        "定理 1.1 指出，对任意正数 ε，两个 n×n 复矩阵可用 "
        "O_ε(n^(9/4+ε)) 次算术运算完成相乘，且算法及其常数可依赖于 ε。"
    ),
}


def main():
    with open(T_JSON, "r", encoding="utf-8") as f:
        titles = json.load(f)
    with open(S_JSON, "r", encoding="utf-8") as f:
        summaries = json.load(f)

    at = AS = 0
    for k, v in TITLE_FIX.items():
        if titles.get(k) != v:
            titles[k] = v
            at += 1
    for k, v in SUMMARY_FIX.items():
        if summaries.get(k) != v:
            summaries[k] = v
            AS += 1

    with open(T_JSON, "w", encoding="utf-8") as f:
        json.dump(titles, f, ensure_ascii=False, indent=2)
    with open(S_JSON, "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)

    print("[fix_1300] 标题定稿 %d 条 / 摘要定稿 %d 条" % (at, AS))
    print("[fix_1300] 覆盖表共 标题 %d / 摘要 %d" % (len(titles), len(summaries)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
