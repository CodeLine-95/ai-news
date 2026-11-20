# -*- coding: utf-8 -*-
"""18:00 例行巡检：人工定稿本轮新增条目的译文。

问题条目：
  'QCon San Francisco 2026: The Future of Apache Iceberg'
  （InfoQ AI, 17:17）

  离线模型（NLLB-200）产出的译文有四处缺陷：
    1) 标题「阿帕奇冰山」——Apache Iceberg 是 Apache 软件基金会的开源
       表格式（table format），属专有技术名词，应保留品牌名并补注，
       直译成「冰山」会让中文读者无法识别；
    2) 摘要「重新设计表表元数据」——"table metadata" 误译为叠字「表表」，
       应为「表元数据」；
    3) 摘要「支持更频繁的写作」——"writes" 在数据库语境指「写入」操作，
       译成「写作」属词义误判；
    4) 摘要「亚帕奇冰 berg」「Apache 冰 berg」「开放桌面格式规格」——
       Iceberg 被中英混杂拆裂，且 "open table format" 误译为「桌面格式」，
       应为「开放表格式」。

处理：写入人工定稿标题 + 摘要覆盖，并回写数据。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

EN = "QCon San Francisco 2026: The Future of Apache Iceberg"
ZH_TITLE = "QCon 旧金山 2026：Apache Iceberg 的未来"
ZH_SUMMARY = (
    "Apache Iceberg V4 提议重新设计表元数据，以提升可扩展性并支持更频繁的写入操作，"
    "同时引入数据管理与模式演进（schema evolution）方面的新能力。"
    "Apache Iceberg 联合创始人、Databricks 技术团队成员 Daniel Weeks 在 QCon 旧金山"
    "大会上介绍了这一开放表格式规范的第四个版本的演讲。"
)


def main():
    for path, val in ((T_JSON, ZH_TITLE), (S_JSON, ZH_SUMMARY)):
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
        if d.get(EN) != val:
            d[EN] = val
            with open(path, "w", encoding="utf-8") as f:
                json.dump(d, f, ensure_ascii=False, indent=2)
            print("[fix_1800] 已更新覆盖表:", os.path.basename(path))

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    hit = 0
    for it in data.get("items", []):
        if it.get("title") == EN:
            it["title_zh"] = ZH_TITLE
            it["summary_zh"] = ZH_SUMMARY
            it["translated"] = True
            it["method"] = "nllb+manual"
            hit += 1
            print("[fix_1800] 已回写:", EN[:60])
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("[fix_1800] 已回写数据 %d 条" % hit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
