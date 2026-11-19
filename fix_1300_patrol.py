# -*- coding: utf-8 -*-
"""13:00 巡检修复：Nutrient 数据提取 API 条目 NLLB 机翻硬伤人工定稿。

硬伤（11:23 条目）：
- "maps fields onto your JSON schema" 被误译为「提取地图领域到 JSON 图案中」
  （maps 误读为地图、schema 误译为图案），语义崩坏
- "split, classify and form endpoints" 被误译为「分类，分类和形式终点」
  （split 误译为分类、endpoints 误译为终点）
- "confidence" 误译为「信心」（应为置信度），"TL;DR Size" 误译为「尺寸」
- "your own servers" 误译为「您自己的服务器」语义尚可，但「果 Mac」为
  "an Apple silicon Mac" 的断裂误译

覆盖三层（与历史巡检一致）：
1) data/news.json 内条目直接回填（立即生效）
2) data/titles_override.json / data/summaries_override.json（持久卷 JSON 层）
3) 运行 scripts/regen_overrides.py 同步到 manual_overrides.py（代码层）
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

FIXES = {
    "Nutrient Data Extraction API: JSON Matching Your Schema With Per-Field Citations and Confidence": {
        "title_zh": "Nutrient 数据提取 API：按自定义结构匹配 JSON，并对每个字段附上引用与置信度",
        "summary_zh": "大型语言模型会把从文档中提取的错误值当作事实呈现给你，这种错误代价高昂，尤其是在据此做决策时。Nutrient 数据提取 API 正是针对这一问题。它能将 PDF、扫描件、图像和 Office 文件解析为空间 JSON 或 Markdown；Extract 可把文档中的字段映射到你的 JSON 结构，而拆分、分类和表单端点则为文档处理流程提供实用的基础能力。每个提取值都通过边界框、匹配标签和置信度分数锚定到页面上。Nutrient（原 PSPDFKit）在 MCP 服务器、智能体技能、Mac 应用和 SDK 背后运行同一套引擎。速览 规模：一个托管 API，提供 4 种解析模式及自动路由。运行环境：Nutrient 云、通过 SDK 部署在你自己的服务器，或 Apple 芯片 Mac。试用方式：Studio——一个用于配置并测试解析、提取、分类、拆分和表单填写的浏览器工作区。",
    },
}


def main():
    with open(os.path.join(DATA, "news.json"), encoding="utf-8") as f:
        db = json.load(f)
    items = db["items"] if isinstance(db, dict) else db
    changed = 0
    for it in items:
        en = (it.get("title") or "").strip()
        if en in FIXES:
            fx = FIXES[en]
            it["title_zh"] = fx["title_zh"]
            it["summary_zh"] = fx["summary_zh"]
            it["translated"] = True
            it["method"] = "nllb+manual"
            changed += 1
            print("fixed:", it.get("date"), it.get("time"), en[:60])

    tpath = os.path.join(DATA, "titles_override.json")
    spath = os.path.join(DATA, "summaries_override.json")
    tov = json.load(open(tpath, encoding="utf-8")) if os.path.exists(tpath) else {}
    sov = json.load(open(spath, encoding="utf-8")) if os.path.exists(spath) else {}
    for en, fx in FIXES.items():
        tov[en] = fx["title_zh"]
        sov[en] = fx["summary_zh"]
    with open(tpath, "w", encoding="utf-8") as f:
        json.dump(tov, f, ensure_ascii=False, indent=2)
    with open(spath, "w", encoding="utf-8") as f:
        json.dump(sov, f, ensure_ascii=False, indent=2)
    with open(os.path.join(DATA, "news.json"), "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    print("changed:", changed, "/", len(FIXES))
    print("title overrides:", len(tov), "summary overrides:", len(sov))


if __name__ == "__main__":
    main()
