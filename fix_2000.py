"""本轮（20:00 例行巡检）修复脚本。

做三件事：
    1) 把 data/summaries_fix_2000.py 中的人工核对结果合并进正式覆盖表
       （data/summaries_override.json），使其在后续每轮调度中持续生效
       （server.py 的 apply_summary_overrides 会自动回填，不会被模型译文覆盖）；
    2) 对全部英文条目跑一遍确定性重清洗（_clean_zh + _restore_terms），
       让本轮新增的「开放模式/开放型号→开放模型」「标准标题→评分标准」
       「原子峡谷→Atomic Canyon」「终端 X→Terminal X」
       「代码运输→代码发布」「没有现实性→官方暂未提供」
       「出口尚未公开→导出尚未公开」等规则作用于存量译文；
    3) 重生成 Markdown 摘要报告。

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
OVERRIDE_FILE = os.path.join(BASE, "data", "titles_override.json")
SUMMARY_OVERRIDE_FILE = os.path.join(BASE, "data", "summaries_override.json")

sys.path.insert(0, os.path.join(BASE, "data"))
from summaries_fix_2000 import SUMMARY_OVERRIDES    # noqa: E402

BYLINE_ZH_RE = re.compile(
    r"由[A-Za-z][A-Za-z.\- ]*(?:，\s*[A-Za-z][A-Za-z.\- ]*)*$"
)


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

    # ---- 1) 合并人工覆盖表（键以英文原标题为唯一标识）----
    titles = _load(OVERRIDE_FILE, {})
    summaries = _load(SUMMARY_OVERRIDE_FILE, {})
    new_t = new_s = 0
    for k, v in SUMMARY_OVERRIDES.items():
        if summaries.get(k) != v:
            new_s += 1
        summaries[k] = v
    with open(OVERRIDE_FILE, "w", encoding="utf-8") as f:
        json.dump(titles, f, ensure_ascii=False, indent=1)
    with open(SUMMARY_OVERRIDE_FILE, "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=1)

    # ---- 2) 确定性重清洗：让新增术语规则作用于存量译文 ----
    cleaned = 0
    for it in items:
        if it.get("lang") != "en":
            continue
        t = translate._clean_zh(it.get("title_zh") or "")
        s = translate._clean_zh(it.get("summary_zh") or "")
        if it.get("title"):
            t = translate._restore_terms(t, it["title"])
        if it.get("summary"):
            s = translate._restore_terms(s, it["summary"])
        s = BYLINE_ZH_RE.sub("", s).strip()
        if t != it.get("title_zh") or s != it.get("summary_zh"):
            cleaned += 1
            it["title_zh"] = t
            it["summary_zh"] = s

    # ---- 3) 应用覆盖表（人工核对结果优先于规则结果）----
    applied_t = applied_s = 0
    for it in items:
        key = it.get("title") or ""
        if titles.get(key) and it.get("title_zh") != titles[key]:
            it["title_zh"] = titles[key]
            it["translated"] = True
            applied_t += 1
        if summaries.get(key) and it.get("summary_zh") != summaries[key]:
            it["summary_zh"] = summaries[key]
            it["translated"] = True
            applied_s += 1

    data["items"] = items
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)

    print("[fix_2000] 覆盖表合并：标题 共 %d 条，摘要 +%d 条（共 %d）"
          % (len(titles), new_s, len(summaries)), flush=True)
    print("[fix_2000] 确定性重清洗 %d 条，应用人工标题覆盖 %d 条，人工摘要覆盖 %d 条"
          % (cleaned, applied_t, applied_s), flush=True)

    report.main()
    print("[fix_2000] 报告已重生成", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
