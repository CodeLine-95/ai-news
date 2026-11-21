# -*- coding: utf-8 -*-
"""03:00 例行巡检：人工定稿 llm-gemini 0.38.1 版本号条目的 NLLB 漏译。

写入三层覆盖表（与项目既有约定一致）：
  1) manual_overrides.py 代码层（随代码发布走）
  2) data/titles_override.json / data/summaries_override.json（持久卷）
  3) data/news.json 直接回填（即时生效）
"""
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
EN_TITLE = "llm-gemini 0.38.1"
ZH_TITLE = "llm-gemini 0.38.1 发布：Gemini 4 Hydrogen/Neon 新增 xhigh 推理档"
ZH_SUMMARY = (
    "发布：llm-gemini 0.38.1。Gemini 4 Carbon 只支持 low、medium、high 三档推理级别，"
    "但 Gemini 4 Hydrogen 和 Gemini 4 Neon 都额外提供了一档 xhigh。"
    "我之前把这两款模型加入 llm-gemini 插件时漏掉了这一档，这个修订版本已经修复。"
    "Hydrogen 上的 xhigh 设置效果显著——我更新了 Gemini 4 对比表："
    "Hydrogen 在 high 档下输出 5,311 个 token、花费 3.99 美分；"
    "同一模型切到 xhigh 后输出 31,477 个 token、花费 23 美分。"
)
ITEM_ID = "94beefe89615ac23f8df21e0ff2cb8a1"


def upsert_py(path, dict_name, key, value):
    """在 manual_overrides.py 的字典字面量中插入/更新一个条目（保持格式）。"""
    with open(path, "r", encoding="utf-8") as f:
        src = f.read()
    marker = f"{dict_name} = {{"
    start = src.index(marker) + len(marker)
    m = re.search(r"\n\}\n", src[start:])
    end = start + m.start() + 1
    block = src[start:end]
    pat = re.compile(r"(\s*)" + re.escape(repr(key)) + r"\s*:\s*.*?(?=,\n|\n\})", re.S)
    if pat.search(block):
        block = pat.sub(lambda mm: f"{mm.group(1)}{key!r}: {value!r}", block, count=1)
    else:
        block = block.rstrip() + f"\n    {key!r}: {value!r},\n"
    src = src[:start] + block + src[end:]
    with open(path, "w", encoding="utf-8") as f:
        f.write(src)


def main():
    py_path = os.path.join(BASE, "manual_overrides.py")
    upsert_py(py_path, "TITLE_OVERRIDES", EN_TITLE, ZH_TITLE)
    upsert_py(py_path, "SUMMARY_OVERRIDES", EN_TITLE, ZH_SUMMARY)
    print("已写入 manual_overrides.py")

    for fname, val in [
        ("titles_override.json", ZH_TITLE),
        ("summaries_override.json", ZH_SUMMARY),
    ]:
        p = os.path.join(BASE, "data", fname)
        d = json.load(open(p, encoding="utf-8"))
        d[EN_TITLE] = val
        with open(p, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
        print(f"已写入 {fname}")

    p = os.path.join(BASE, "data", "news.json")
    d = json.load(open(p, encoding="utf-8"))
    items = d.get("items", d) if isinstance(d, dict) else d
    hit = 0
    for it in items:
        if it.get("id") == ITEM_ID or (it.get("title") or "").strip() == EN_TITLE:
            it["title_zh"] = ZH_TITLE
            it["summary_zh"] = ZH_SUMMARY
            it["translated"] = True
            it["method"] = "manual"
            hit += 1
    with open(p, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
    print(f"news.json 回填 {hit} 条；当前总数={len(items)}，已译={sum(1 for i in items if i.get('translated'))}")


if __name__ == "__main__":
    main()
