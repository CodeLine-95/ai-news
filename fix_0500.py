# -*- coding: utf-8 -*-
"""05:00 例行巡检：人工定稿新增的 1 条低质量译文。

问题条目：
  'AI can make tech CEOs' lives easier. What about everyone else?'（TechCrunch, 04:57）
    模型译文把 tone deaf 直译成「如此听」，语义在「听」处被截断，
    读起来是半句话。摘要整体也不通顺。
处理：写入人工定稿标题 + 摘要覆盖，并回写数据与报告。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

EN_TITLE = "AI can make tech CEOs’ lives easier. What about everyone else?"
ZH_TITLE = "AI 可以让科技公司 CEO 的生活更轻松，那其他人呢？"
ZH_SUMMARY = (
    "在《Equity》这期节目中，我们讨论了为什么科技公司 CEO 的公开发言"
    "有时听起来会那么「不合时宜」（tone deaf）——当一家公司把 AI 包装成"
    "自家产品力的一部分，而它的用户、员工或普通用户所关心的却是另一回事时，"
    "两者之间的落差就会变得格外刺眼。"
)


def main():
    for path, key, val in (
        (T_JSON, EN_TITLE, ZH_TITLE),
        (S_JSON, EN_TITLE, ZH_SUMMARY),
    ):
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
        if d.get(key) != val:
            d[key] = val
            with open(path, "w", encoding="utf-8") as f:
                json.dump(d, f, ensure_ascii=False, indent=2)
            print("[fix_0500] 已更新覆盖表:", os.path.basename(path))

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    hit = 0
    for it in data.get("items", []):
        if it.get("title") == EN_TITLE:
            it["title_zh"] = ZH_TITLE
            it["summary_zh"] = ZH_SUMMARY
            it["translated"] = True
            hit += 1
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("[fix_0500] 已回写数据 %d 条" % hit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
