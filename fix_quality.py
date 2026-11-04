"""质量修复脚本：修复历史条目译文的两类问题。

问题一：术语未还原
    早期译文生成时术语表尚未包含某些规则（如 Anthropic 被意译成「人类公司」、
    Claude 被拼成「Clode」、token 被译成「代币」、frontier 译成「边界」）。
    这些无需重新翻译模型即可修复：对已有译文重新执行一遍术语还原。

问题二：长摘要被截断
    NLLB 单次生成上限 max_new_tokens=300，900 字符的英文摘要只译出开头约
    270 字符，末尾关键事实（如「成功率 56%→75%」）整段丢失。
    判据：英文摘要中的数值在中文译文中缺失，即判定为截断，需分块重译。

用法：
    python3 fix_quality.py            # 术语还原 + 截断摘要重译
    python3 fix_quality.py --dry-run  # 只体检，不写库
注意：运行前请先停止 server.py，避免两者争写 data/news.json。
"""
import argparse
import json
import os
import re
import sys

import translate
import report

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "news.json")
OVERRIDE_FILE = os.path.join(BASE, "data", "titles_override.json")


def _numbers(text):
    return re.findall(r"\d+(?:[.,]\d+)*", text or "")


def _norm_nums(text):
    """把数值按数量级归一化，用于跨语言比对。

    中文侧「3000亿」对应英文「300 billion」，字面数字不同但语义一致。
    因此比对前把两侧都折算成统一单位（亿）再比，避免把已修正的量级
    误判为「漏译」。
    """
    out = set()
    for m in re.finditer(r"(\d+(?:[.,]\d+)*)\s*(亿|万)", text or ""):
        try:
            val = float(m.group(1).replace(",", ""))
        except ValueError:
            continue
        val = val * (1.0 if m.group(2) == "亿" else 0.0001)
        out.add(_key(val))
    for m in re.finditer(r"\d+(?:[.,]\d+)*", text or ""):
        out.add(m.group(0))
    return out


def _key(v):
    return ("%.4f" % float(v)).rstrip("0").rstrip(".")


def _acceptable_keys(text):
    """对每个英文数值，给出它在中文侧可接受的等价写法集合。

    例：「9.06 billion」→ 可接受 {"9.06", "90.6"}（后者是折算成「亿」后的值）。
    """
    pairs = []
    scaled = {}
    for m in re.finditer(
        r"(\d+(?:[.,]\d+)*)\s*(trillion|billion|million|thousand)\b",
        text or "", re.IGNORECASE,
    ):
        try:
            val = float(m.group(1).replace(",", ""))
        except ValueError:
            continue
        mult = translate._SCALE_WORDS.get(m.group(2).lower())
        if mult:
            scaled.setdefault(m.group(1), set()).add(_key(val * mult))
    for m in re.finditer(r"\d+(?:[.,]\d+)*", text or ""):
        n = m.group(0)
        acc = {n, _key(float(n.replace(",", "")))}
        acc |= scaled.get(n, set())
        pairs.append((n, acc))
    return pairs


def detect_truncated(en, zh):
    """判断译文是否因生成上限而被截断。

    判据：英文摘要里的数值在中文译文中找不到对应值，且缺失面较大。
    两侧按数量级归一化（「300 billion」≡「3000亿」视为命中）。
    要求至少缺失 2 个数值，避免把「Q3 → 第三季度」这类正常换算误判。
    """
    if not en or not zh:
        return False
    pairs = _acceptable_keys(en)
    if not pairs:
        return False
    zh_keys = _norm_nums(zh)
    missing = [n for n, acc in pairs if not (acc & zh_keys)]
    # 至少缺 2 个数值才判定为截断（单个小数字缺失多为正常换算）
    return len(missing) >= 2 and len(missing) >= max(2, len(pairs) // 2)


def apply_term_restore(items):
    """对已有译文重新执行术语还原，返回被修改的条目数。"""
    changed = 0
    for it in items:
        if it.get("lang") != "en":
            continue
        en_title = it.get("title") or ""
        en_sum = it.get("summary") or ""
        for en_field, zh_field in (("title", "title_zh"), ("summary", "summary_zh")):
            en = en_title if en_field == "title" else en_sum
            zh = it.get(zh_field) or ""
            if not zh:
                continue
            fixed = translate._restore_terms(zh, en)
            if fixed != zh:
                it[zh_field] = fixed
                changed += 1
                print("术语还原 [%s] %s -> %s" % (
                    it.get("date"), zh[:30], fixed[:30]), flush=True)
    return changed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="只体检不写库")
    args = ap.parse_args()

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    items = data.get("items", [])

    # --- 体检 ---
    truncated = [
        it for it in items
        if it.get("lang") == "en"
        and detect_truncated(it.get("summary") or "", it.get("summary_zh") or "")
    ]
    print("术语还原待处理条目 = %d" % len(items))
    print("疑似截断摘要条目 = %d" % len(truncated), flush=True)
    for it in truncated:
        print("  - %s %s | %s" % (
            it.get("date"), it.get("time"), (it.get("title") or "")[:50]), flush=True)

    if args.dry_run:
        return 0

    # --- 1) 术语还原 ---
    changed = apply_term_restore(items)
    print("术语还原修改字段 = %d" % changed, flush=True)

    # --- 2) 截断摘要分块重译 ---
    if truncated:
        print("翻译引擎加载中 ...", flush=True)
        translate.translate_list(["warmup"])
        for it in truncated:
            en = it.get("summary") or ""
            zh, method = translate.translate_list_chunked([en], beams=2)
            if zh and zh[0]:
                it["summary_zh"] = zh[0]
                it["method"] = method
                print("重译: %s | %s" % (
                    (it.get("title") or "")[:40], zh[0][:50]), flush=True)

    # --- 3) 人工标题优先 ---
    overrides = {}
    if os.path.exists(OVERRIDE_FILE):
        try:
            with open(OVERRIDE_FILE, "r", encoding="utf-8") as f:
                overrides = json.load(f)
        except Exception:
            overrides = {}
    applied = 0
    for it in items:
        manual = overrides.get((it.get("title") or "").strip())
        if manual and (it.get("title_zh") or "") != manual:
            it["title_zh"] = manual
            it["translated"] = True
            applied += 1
    if applied:
        print("恢复人工标题 = %d" % applied, flush=True)

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    report.main()
    print("fix_quality done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
