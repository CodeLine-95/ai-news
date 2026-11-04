# -*- coding: utf-8 -*-
"""07:00 例行巡检：人工定稿新增的 1 条低质量译文。

问题条目：
  'Aramco Acquires 49% HUMAIN Stake With $2.6B Cash, AI Assets'
  （Unite.AI, 06:36）

  模型把沙特国家石油公司 Aramco 音译成「亚伦科」「阿拉姆科」「阿兰科」
  三个不同写法，人工智能公司 HUMAIN 被译成「HUMAN」（语义完全跑偏，
  读者会误以为是指「人类」），金额 "SAR 9.9 billion ($2.6 billion)"
  被误译成「202.6 年贡献约 99 亿沙拉」，年份 2026 被写成「202.6」，
  数字与专有名词全部失真。

处理：写入人工定稿标题 + 摘要覆盖，并回写数据。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

EN_TITLE = "Aramco Acquires 49% HUMAIN Stake With $2.6B Cash, AI Assets"
ZH_TITLE = "沙特阿美以 26 亿美元现金收购 HUMAIN 49% 股权，含 AI 资产"
ZH_SUMMARY = (
    "沙特公共投资基金（PIF）与沙特阿美（Aramco）于 2026 年 11 月 1 日宣布交易完成："
    "沙特阿美通过一家全资子公司收购人工智能公司 HUMAIN 的 49% 股权，PIF 保留 51% 持股。"
    "根据沙特阿美新闻中心发布的交割公告，此次交易的支付方式为："
    "沙特阿美向 HUMAIN 转让关键 AI 资产，并于 2026 年注入约 99 亿沙特里亚尔"
    "（约合 26 亿美元）现金。"
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
            print("[fix_0700] 已更新覆盖表:", os.path.basename(path))

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
    print("[fix_0700] 已回写数据 %d 条" % hit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
