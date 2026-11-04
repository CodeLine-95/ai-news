# -*- coding: utf-8 -*-
"""17:00 例行巡检（第三批）：人工定稿新增的直译痕迹条目。

问题条目：
  'Marble Cognition Raises $3.75M Pre-Seed to Build AI Coworkers That Learn by Observing'
  （Unite.AI, 17:00）

  离线模型译文缺陷：
    1) 公司名 Marble Cognition 被逐词意译成「理石认知」；
    2) pre-seed 被译成「预种资金」，创投语境应为「种子前轮融资」；
    3) "automating office work" 译成「机动化办公工作」——「机动化」
       是机械领域术语，办公自动化应写「自动化办公」；
    4) "never captured in a formal specification" 译成「从未被正式
       规范中捕获」——「捕获」是生硬的直译，应为「记录下来」；
    5) "AI coworkers" 译成「人工智能合作伙伴」——原文强调「同事」，
       与前文 "employees" 呼应。

根因修复（translate.py）：
    TERM_FIXES 补入「理石认知」→「Marble Cognition」与
    「预种资金 / 预种子」→「种子前轮融资」。

处理：写入人工定稿标题 + 摘要覆盖，并回写数据。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

EN = ("Marble Cognition Raises $3.75M Pre-Seed to Build AI Coworkers "
      "That Learn by Observing")
ZH_TITLE = "Marble Cognition 获 375 万美元种子前轮融资，打造通过观察学习的 AI 同事"
ZH_SUMMARY = (
    "自动化办公室工作最困难的部分，往往发生在 AI 智能体迈出第一步之前："
    "弄清楚员工究竟在做什么。一条工作流可能横跨收件箱、电子表格和多个业务应用，"
    "其中那些例外情况只有团队心里明白，却从未被记录成正式规范。"
    "Marble Cognition 已获得 375 万美元种子前轮融资，"
    "要把这些沉淀在流程里的运营知识转化为 AI 同事。"
    "本轮融资由 Heartcore 与 Seedcamp 联合领投。"
)


def main():
    for path, val in ((T_JSON, ZH_TITLE), (S_JSON, ZH_SUMMARY)):
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
        if d.get(EN) != val:
            d[EN] = val
            with open(path, "w", encoding="utf-8") as f:
                json.dump(d, f, ensure_ascii=False, indent=2)
            print("[fix_1700b] 已更新覆盖表:", os.path.basename(path))

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    hit = 0
    for it in data.get("items", []):
        if it.get("title") == EN:
            it["title_zh"] = ZH_TITLE
            it["summary_zh"] = ZH_SUMMARY
            it["translated"] = True
            hit += 1
            print("[fix_1700b] 已回写:", EN[:60])
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("[fix_1700b] 已回写数据 %d 条" % hit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
