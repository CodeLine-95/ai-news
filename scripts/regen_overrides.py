"""从 JSON 源重新生成 manual_overrides.py（代码层覆盖表）。

manual_overrides.py 必须随代码发布走（部署端 data/ 是持久卷，
JSON 覆盖表不会随发布更新），但它体积大、条目多，人工直接编辑
极易破坏字典结构（曾出现闭合括号丢失导致整个模块无法导入）。

本脚本以 data/titles_override.json 与 data/summaries_override.json
为数据源，重新生成结构完整的 manual_overrides.py：
    python3.11 scripts/regen_overrides.py

用法约定：先运行 fix_XXXX.py 把人工定稿合并进 JSON 覆盖表，
再运行本脚本同步到代码层。
"""
import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")
OUT = os.path.join(BASE, "manual_overrides.py")

HEADER = '''# -*- coding: utf-8 -*-
"""人工核对覆盖表（代码层，随发布生效）。

背景：data/ 目录在部署端是持久卷，data/titles_override.json 与
data/summaries_override.json 不会随代码发布更新，导致人工修好的译文
在线上被模型译文覆盖。本模块把人工核对结果固化为纯代码，
由 server.py 在每轮调度时合并进覆盖表，优先级高于 JSON 表与模型译文。

注意：本文件由 scripts/regen_overrides.py 自动生成，请勿手工编辑，
以免破坏字典结构。键为英文原标题。
"""

TITLE_OVERRIDES = {
'''

MID = '''}

SUMMARY_OVERRIDES = {
'''


def main():
    with open(T_JSON, "r", encoding="utf-8") as f:
        titles = json.load(f)
    with open(S_JSON, "r", encoding="utf-8") as f:
        summaries = json.load(f)

    out = [HEADER]
    for k, v in titles.items():
        out.append("    %r: %r,\n" % (k, v))
    out.append(MID)
    for k, v in summaries.items():
        out.append("    %r: %r,\n" % (k, v))
    out.append("}\n")

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("".join(out))
    print("[regen] 已生成 %s（标题 %d 条 / 摘要 %d 条）"
          % (OUT, len(titles), len(summaries)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
