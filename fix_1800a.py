# -*- coding: utf-8 -*-
"""2026-11-02 18:00 例行巡检：人工定稿新增条目的直译痕迹。

问题条目：
  'The agentic web is here'
  （MIT Tech Review, 2026-11-02 17:35）

  离线模型译文缺陷：
    1) "World Wide Web" 被逐词直译成「世界网络」——中文通用写法是「万维网」；
    2) "Scientific American"（杂志名）译成「科学美国」，缺「人」字；
    3) "the Semantic Web"（语义网，Web 三大流派之一）译成「语义网络」，
       与普通的"语义网络/neural network"混淆；
    4) "At the turn of the millennium"（千年之交）被拆译成「千一百年之际」；
    5) 标题 "The agentic web is here" 译成「智能体网络在这里」，
       属于逐字硬译，中文不成立；
    6) 整体为长句直译腔："他与两位同事一起发表了一篇文章在…杂志上"
       ——中文语序应为"在《科学美国人》杂志上发表了一篇文章"。

根因修复（translate.py）：
    新增 _PROPER_NOUN_FIXES + _fix_proper_nouns()，用正则带负向前查修复
    专有名词直译（世界网络→万维网、科学美国→科学美国人、
    语义网络→语义网、千一百年之际→千年之交），
    并挂进 _restore_terms() 主流程，对存量条目确定性生效。

处理：写入人工定稿标题 + 摘要覆盖，并回写数据。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

EN = "The agentic web is here"
ZH_TITLE = "智能体网络已到来"
ZH_SUMMARY = (
    "2001 年，在发明万维网十年后，蒂姆·伯纳斯-李提出了一个新的愿景。"
    "他与两位同事在《科学美国人》杂志上发表了一篇文章，"
    "在其中勾勒出他所说的「语义网」："
    "一个由自主软件智能体来导航的互联网，"
    "能够满足我们的任何需求，而不必再让我们自己费心折腾浏览器和搜索引擎。"
    "为了说明这可能是什么样子，伯纳斯-李和同事们举了一个例子："
    "一对兄妹用他们的智能体为母亲自动查找并预约物理治疗，"
    "既确保该治疗在保险覆盖范围内，又兼顾各自繁忙的日程。"
    "在千年之交，这个愿景看起来还相当不切实际："
    "Google 也才刚上线没几年，大多数人还在用拨号连接上网。"
)


def main():
    for path, val in ((T_JSON, ZH_TITLE), (S_JSON, ZH_SUMMARY)):
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
        if d.get(EN) != val:
            d[EN] = val
            with open(path, "w", encoding="utf-8") as f:
                json.dump(d, f, ensure_ascii=False, indent=2)
            print("[fix_1800a] 已更新覆盖表:", os.path.basename(path))

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    hit = 0
    for it in data.get("items", []):
        if it.get("title") == EN:
            it["title_zh"] = ZH_TITLE
            it["summary_zh"] = ZH_SUMMARY
            it["translated"] = True
            hit += 1
            print("[fix_1800a] 已回写:", EN)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("[fix_1800a] 已回写数据 %d 条" % hit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
