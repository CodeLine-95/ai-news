# -*- coding: utf-8 -*-
"""07:00 巡检：定稿本轮新增 4 条译文（NLLB 漏译专名/语义偏差）。

把人工定稿合并进 data/ 的 JSON 覆盖表；随后运行
python3.11 scripts/regen_overrides.py 同步到代码层 manual_overrides.py。
"""
import json
import os
import shutil

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

TITLES = {
    "S&P considers Nvidia credit downgrade over governance and ‘key man’ risks":
        "标普考虑因治理及「关键人物」风险下调英伟达信用评级",
    "Google’s patent for custom AI video feeds paints a bleak picture of entertainment’s future":
        "谷歌定制 AI 视频信息流专利，勾勒娱乐业未来的黯淡图景",
    "Fireworks AI Adds Tencent’s Hy4 Flash to Its Serverless API":
        "Fireworks AI 将腾讯 Hy4 Flash 上线其无服务器 API",
    "Tempus AI Secures $385M Term Loan Facility to Fund Personalis Deal":
        "Tempus AI 获得 3.85 亿美元定期贷款融资，用于推进 Personalis 收购",
}

SUMMARIES = {
    "S&P considers Nvidia credit downgrade over governance and ‘key man’ risks":
        "信用评级机构标普可能将英伟达（Nvidia）的信用评级下调至 AA-，为第四高评级。",
    "Google’s patent for custom AI video feeds paints a bleak picture of entertainment’s future":
        "去年，谷歌申请了一项名为 My Channel 的系统专利，旨在基于其掌握的用户信息，"
        "生成充满个性化 AI 视频与广告的信息流。该专利已被驳回，但谷歌仍可能上诉或重新提交修订版本，"
        "届时这种「怪物」或许真会进入市场。",
    "Fireworks AI Adds Tencent’s Hy4 Flash to Its Serverless API":
        "Fireworks AI 于 2026 年 11 月 25 日将腾讯开放权重的 Hy4 Flash 接入其无服务器 API。"
        "标准版定价为每百万输入 token 0.07 美元、每百万输出 token 0.281 美元。"
        "官方公布的基准测试将该模型定位为面向专业工作与智能体任务的低成本选择。"
        "缓存输入价格为每百万 token 0.003 美元；另提供优先版，服务面向全球开放。",
    "Tempus AI Secures $385M Term Loan Facility to Fund Personalis Deal":
        "根据 8-K 文件，Tempus AI 于 2026 年 11 月 25 日签署高级担保信贷协议，"
        "获得 3.85 亿美元定期贷款承诺与 1.15 亿美元循环信贷承诺，用于资助尚在推进的 Personalis 收购交易。"
        "另据 2026 年 11 月 24 日的决定，Tempus 选择向 Personalis 股东支付约 6 亿美元现金，"
        "并发行约 9 亿美元的 Tempus A 类普通股。",
}


def merge(path, updates):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    shutil.copyfile(path, path + ".bak.0700patrol1126")
    before = len(data)
    data.update(updates)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print("[fix] %s: %d -> %d" % (os.path.basename(path), before, len(data)))


if __name__ == "__main__":
    merge(T_JSON, TITLES)
    merge(S_JSON, SUMMARIES)
