# -*- coding: utf-8 -*-
"""16:00 例行巡检：人工定稿本轮新增条目的译文。

问题条目：
  'ADNOC Signs Multi-Year Deal With OpenAI and G42 to Deploy Frontier AI'
  （Unite.AI, 15:07）

  离线模型（NLLB-200）产出的译文有四处缺陷：
    1) 标题「亚诺克」——ADNOC（阿布扎比国家石油公司）被音译成
       「亚诺克」，读者完全无法识别是哪家公司；
    2) 标题「用于部署边境 AI」——frontier AI 被译成「边境 AI」，
       在中文里读作「地理边境」，与 AI 语境的「前沿」语义完全相反；
    3) 标题「亚诺克签署了与 OpenAI 和 G42 签署多年协议」——
       英文 "Signs ... Deal With" 被译成「签署了与……签署」，
       谓语重复，是病句结构；
    4) 摘要「连接和协调跨界 AI 智能体」——同样是 frontier AI 的误译，
       且「见证了签署协议」表述生硬。

根因修复（translate.py）：
    - BRAND_TERMS 补入「亚诺克 / 阿德诺克」变体，TERM_FIXES 补入
      「边境 AI」「跨界 AI」→「前沿 AI」规则（触发词 frontier）；
    - 新增 _fix_signing_wording：把「签署了与……签署」折叠为
      「与……签署」，仅在英文原文同时含 sign 与 deal 时生效；
    - 新增 _normalize_cjk_parens：中文语境统一全角括号，
      与站内既有 68 处全角括号风格对齐。

处理：写入人工定稿标题 + 摘要覆盖，并回写数据。
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

EN = "ADNOC Signs Multi-Year Deal With OpenAI and G42 to Deploy Frontier AI"
ZH_TITLE = "ADNOC 与 OpenAI、G42 签署多年协议，部署前沿 AI"
ZH_SUMMARY = (
    "阿布扎比国家石油公司 ADNOC 于 2026 年 11 月 2 日在阿布扎比国际能源展会"
    "（ADIPEC）上宣布与 OpenAI、G42 建立多年合作伙伴关系，成为首家部署 "
    "OpenAI Frontier 的能源企业。OpenAI Frontier 是用于连接并协调复杂业务场景中"
    "前沿 AI 智能体的平台。阿布扎比王储、阿布扎比执行委员会主席谢赫哈雷德·本·"
    "穆罕默德·本·扎伊德·阿尔纳希安见证了协议签署仪式。"
)


def main():
    for path, val in ((T_JSON, ZH_TITLE), (S_JSON, ZH_SUMMARY)):
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
        if d.get(EN) != val:
            d[EN] = val
            with open(path, "w", encoding="utf-8") as f:
                json.dump(d, f, ensure_ascii=False, indent=2)
            print("[fix_1600] 已更新覆盖表:", os.path.basename(path))

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    hit = 0
    for it in data.get("items", []):
        if it.get("title") == EN:
            it["title_zh"] = ZH_TITLE
            it["summary_zh"] = ZH_SUMMARY
            it["translated"] = True
            hit += 1
            print("[fix_1600] 已回写:", EN[:60])
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("[fix_1600] 已回写数据 %d 条" % hit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
