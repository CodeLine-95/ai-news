# -*- coding: utf-8 -*-
"""2026-11-02 20:00 例行巡检：把本轮新增的确定性规则作用于存量译文。

背景
----
本轮新增了两类规则：
  1. zh_t2s.to_simplified()——繁 -> 简归一（挂在 _clean_zh 末尾）
  2. TERM_FIXES 智能体架构术语（context engine / memory stack / tiered
     memory / curated knowledge / context stuffing / building blocks 等）

这两类规则都是**确定性**的（不依赖模型），因此可以对全部存量译文
重跑一遍 _clean_zh + _restore_terms，让规则立即生效——
不必等下一轮调度重新翻译（那会浪费一次模型推理，
且模型重译可能引入新的随机偏差）。

人工定稿（fix_2000b.py 已写入的覆盖表）在最后一步应用，优先级最高。

全程不加载翻译模型（纯确定性处理），因此不会与后台调度器抢内存，
也不会触发 8GB cgroup 下的 OOM。

注意：运行前请先停止 server.py，避免与后台调度器争写 data/news.json。
"""
import json
import os
import re
import sys

import report
import translate

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "news.json")
TITLE_OVERRIDE = os.path.join(BASE, "data", "titles_override.json")
SUMMARY_OVERRIDE = os.path.join(BASE, "data", "summaries_override.json")

# 上一版 fix_2000.py 用来去掉译文尾部署名字样的规则，保留复用
BYLINE_ZH_RE = re.compile(
    r"由[A-Za-z][A-Za-z.\- ]*(?:，\s*[A-Za-z][A-Za-z.\- ]*)*$"
)


def _normalize_spacing(text):
    """规整人工覆盖译文中的中西文间距与括号风格。

    与 server.py 的同名函数保持一致。必须复用它——
    覆盖表里的文本是人工逐字定稿的，不经过 translate._clean_zh，
    因此半角括号（如「消费品包装 (CPG) 制造商」）会原样入库。
    直接把覆盖表原始值写回条目会让已修好的排版问题重新出现。
    """
    if not text:
        return text
    text = translate._fix_cjk_latin_spacing(text)
    text = translate._normalize_cjk_parens(text)
    return text


def _load(path, default):
    if not os.path.exists(path):
        return dict(default)
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception:
            return dict(default)


def main():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    items = data.get("items", [])

    titles = _load(TITLE_OVERRIDE, {})
    summaries = _load(SUMMARY_OVERRIDE, {})

    # ---- 1) 确定性重清洗：让本轮新规则作用于存量译文 ----
    cleaned = 0
    t2s_fixed = 0
    for it in items:
        if it.get("lang") != "en":
            continue
        old_t = it.get("title_zh") or ""
        old_s = it.get("summary_zh") or ""
        t = translate._clean_zh(old_t)
        s = translate._clean_zh(old_s)
        if it.get("title"):
            t = translate._restore_terms(t, it["title"])
        if it.get("summary"):
            s = translate._restore_terms(s, it["summary"])
        s = BYLINE_ZH_RE.sub("", s).strip()
        if t != old_t or s != old_s:
            cleaned += 1
            it["title_zh"] = t
            it["summary_zh"] = s
        # 单独统计繁简归一带来的修复条数（用于巡检报告）
        if translate.to_simplified(old_t) != old_t or \
                translate.to_simplified(old_s) != old_s:
            t2s_fixed += 1

    # ---- 2) 应用人工覆盖表（人工核对结果优先于规则结果）----
    # 注意：必须走 _normalize_spacing，与 server.py 的应用路径保持一致，
    # 否则覆盖表里的半角括号会绕过规范化重新写回条目。
    applied_t = applied_s = 0
    for it in items:
        key = it.get("title") or ""
        if titles.get(key):
            v = _normalize_spacing(titles[key])
            if it["title_zh"] != v:
                it["title_zh"] = v
                it["translated"] = True
                applied_t += 1
        if summaries.get(key):
            v = _normalize_spacing(summaries[key])
            if it["summary_zh"] != v:
                it["summary_zh"] = v
                it["translated"] = True
                applied_s += 1

    data["items"] = items
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("[fix_2000c] 确定性重清洗 %d 条（其中繁简归一修复 %d 条）"
          % (cleaned, t2s_fixed), flush=True)
    print("[fix_2000c] 应用人工标题覆盖 %d 条，人工摘要覆盖 %d 条"
          % (applied_t, applied_s), flush=True)

    report.main()
    print("[fix_2000c] 报告已重生成", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
