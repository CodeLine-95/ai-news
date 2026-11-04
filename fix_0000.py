"""2026-11-02 00:00 例行巡检修复脚本（确定性，不加载模型）。

做三件事：
    1) 把 data/titles_fix_0000.py 与 data/summaries_fix_0000.py 中的人工核对
       结果合并进正式覆盖表（data/titles_override.json /
       data/summaries_override.json），使其在后续每轮调度中持续生效
       （server.py 的 apply_*_overrides 会自动回填）；
       同时本轮定稿已固化进代码层 manual_overrides.py，随发布走，
       不依赖部署端持久卷。
    2) 对全部英文条目跑一遍确定性重清洗（_clean_zh + _restore_terms）；
    3) 重生成 Markdown 摘要报告。

全程不加载翻译模型（纯确定性处理），不会与后台调度器抢内存，
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
from titles_fix_0000 import TITLE_OVERRIDES          # noqa: E402
from summaries_fix_0000 import SUMMARY_OVERRIDES      # noqa: E402

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

    titles = _load(OVERRIDE_FILE, {})
    summaries = _load(SUMMARY_OVERRIDE_FILE, {})

    new_t = 0
    for k, v in TITLE_OVERRIDES.items():
        if titles.get(k) != v:
            if k not in titles:
                new_t += 1
            titles[k] = v

    new_s = 0
    for k, v in SUMMARY_OVERRIDES.items():
        if summaries.get(k) != v:
            if k not in summaries:
                new_s += 1
            summaries[k] = v

    with open(OVERRIDE_FILE, "w", encoding="utf-8") as f:
        json.dump(titles, f, ensure_ascii=False, indent=1)
    with open(SUMMARY_OVERRIDE_FILE, "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=1)

    items = data.get("items", [])
    cleaned = applied_t = applied_s = 0
    for it in items:
        en = (it.get("title") or "").strip()
        if not en:
            continue

        if it.get("lang") == "en":
            for field in ("title_zh", "summary_zh"):
                zh = it.get(field) or ""
                src = it.get("title") if field == "title_zh" else it.get("summary")
                if zh:
                    new_zh = translate._clean_zh(zh)
                    new_zh = translate._restore_terms(new_zh, src or "")
                    new_zh = translate._fix_cjk_latin_spacing(new_zh)
                    if new_zh != zh:
                        it[field] = new_zh
                        cleaned += 1

        if titles.get(en):
            v = translate._fix_cjk_latin_spacing(titles[en])
            if it.get("title_zh") != v:
                it["title_zh"] = v
                it["translated"] = True
                applied_t += 1
        if summaries.get(en):
            v = translate._fix_cjk_latin_spacing(summaries[en])
            if it.get("summary_zh") != v:
                it["summary_zh"] = v
                it["translated"] = True
                applied_s += 1

    data["items"] = items
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)

    print("[fix_0000] 覆盖表合并：标题 +%d 条（共 %d），摘要 +%d 条（共 %d）"
          % (new_t, len(titles), new_s, len(summaries)), flush=True)
    print("[fix_0000] 确定性重清洗 %d 条，应用人工标题覆盖 %d 条，人工摘要覆盖 %d 条"
          % (cleaned, applied_t, applied_s), flush=True)

    report.main()
    print("[fix_0000] 报告已重生成", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
