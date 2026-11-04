# -*- coding: utf-8 -*-
"""修复存量英文摘要中因 HTML 实体丢失而残缺的所有格撇号。

背景：
    fetcher._clean() 原先用 _ENT_RE 把所有 HTML 实体替换成空格，
    而 &#8217;（右撇号 U+2019）正是绝大多数英文所有格（X's）的载体。
    结果是摘要里出现「EASE s total equity」「the world s first」这类
    缺撇号的残缺英文——站点「看翻译原文」功能展示的就是这段坏原文，
    同时也让 NLLB 少了一个重要的语义线索（所有格）。

修复：
    1) fetcher._clean() 改为先 html.unescape 再剥标签（本次已改），
       新抓取的条目不再产生该问题；
    2) 本脚本对存量 data/news.json 做一次性回填：把「单词 + 空格 + s」
       还原为「单词's」。仅在「s 前是单个词、后接正常内容」时替换，
       并排除少量确实不需要撇号的英文（如 "is a" 不会被误伤——
       判定要求词尾为 s 且后接非空格内容）。

用法：
    python3.11 fix_apostrophe.py
"""
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "news.json")

# 「<单词> s」→「<单词>'s」
# 要求：
#   - 单词以字母开头、长度 >= 2
#   - 后面的 s 是独立的词（\b 边界），避免 "is a" 这类被误改
_APOS_RE = re.compile(r"([A-Za-z][A-Za-z\.\-]{1,30}) s\b")


def fix_text(text):
    if not text:
        return text, 0
    if not re.search(r"[A-Za-z] s\b", text):
        return text, 0
    n = 0

    def _repl(m):
        nonlocal n
        n += 1
        return m.group(1) + "'s"

    out = _APOS_RE.sub(_repl, text)
    return out, n


def main():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    total = 0
    touched = 0
    for it in data.get("items", []):
        cnt = 0
        for field in ("title", "summary"):
            v = it.get(field)
            if not v:
                continue
            nv, n = fix_text(v)
            if n:
                it[field] = nv
                cnt += n
        if cnt:
            touched += 1
            total += cnt
            print("[fix_apostrophe] %s %s | %s" % (it.get("date"), it.get("time"), it.get("title", "")[:60]))

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("[fix_apostrophe] 共修复 %d 处，涉及 %d 条条目" % (total, touched))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
