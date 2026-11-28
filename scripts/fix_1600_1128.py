# -*- coding: utf-8 -*-
"""16:00 巡检：定稿本轮新增 1 条 NLLB 机翻硬伤。

问题：Azure AI Gateway 被误译为「亚洲人工智能网关」（Azure -> Asia），
且摘要中 Microsoft / private networking 等术语机翻腔明显。
本脚本把人工定稿合并进 data/ 的 JSON 覆盖表，并直接回填 news.json，
随后由 regen_overrides.py 同步到代码层 manual_overrides.py。

键从 news.json 的英文原标题读取，避免手写弯引号造成键不匹配。
"""
import json
import os
import shutil
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")
NEWS = os.path.join(BASE, "data", "news.json")

PREFIX = "Azure AI Gateway Reaches General Availability"

TITLE_ZH = "Azure AI 网关作为独立服务正式上线"

SUMMARY_ZH = (
    "微软宣布 Azure AI 网关（Azure AI Gateway）作为独立 Azure 服务正式上线，"
    "用于统一管理跨供应商 AI 模型与 MCP 工具的访问。免费套餐为每个网关每月提供 "
    "10,000 次请求；付费计费自 2027 年 1 月 1 日起开始；专用网络仍处于预览阶段。"
)


def merge(path, updates, suffix):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    shutil.copyfile(path, path + suffix)
    before = len(data)
    data.update(updates)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print("[fix] %s: %d -> %d" % (os.path.basename(path), before, len(data)))


def main():
    with open(NEWS, "r", encoding="utf-8") as f:
        news = json.load(f)
    items = news.get("items", [])
    hits = [it for it in items if (it.get("title") or "").startswith(PREFIX)]
    if not hits:
        raise SystemExit("[fix] 未找到目标条目，终止")
    en = hits[0]["title"].strip()
    print("[fix] 目标英文标题:", en)

    shutil.copyfile(NEWS, NEWS + ".bak.1600patrol1128")
    for it in hits:
        it["title_zh"] = TITLE_ZH
        it["summary_zh"] = SUMMARY_ZH
        it["translated"] = True
        it["method"] = "nllb+manual"
    with open(NEWS, "w", encoding="utf-8") as f:
        json.dump(news, f, ensure_ascii=False, indent=2)

    merge(T_JSON, {en: TITLE_ZH}, ".bak.1600patrol1128")
    merge(S_JSON, {en: SUMMARY_ZH}, ".bak.1600patrol1128")

    import report
    report.main()
    print("[fix] 已回填 news.json 并重建摘要报告")


if __name__ == "__main__":
    main()
