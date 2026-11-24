# -*- coding: utf-8 -*-
"""06:00 例行巡检质量修复（2026-11-25）。

修复 NLLB 硬伤：Anthropic→「人类化」、Liquid AI→「液态 AI」、
Maple→「果公司」、artifacts→「文物」、英文原样残留等。
人工定稿写入 JSON 覆盖表源，再回填 data/news.json 并重生报告。
随后由 scripts/regen_overrides.py 同步到代码层 manual_overrides.py。
"""
import json
import os
import shutil
import subprocess

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "news.json")
T_JSON = os.path.join(BASE, "data", "titles_override.json")
S_JSON = os.path.join(BASE, "data", "summaries_override.json")

TITLE_FIX = {
    "Anthropic Lets Claude Users Install AI-Built Tools as Desktop Apps":
        "Anthropic 允许 Claude 用户将 AI 构建的工具安装为桌面应用",
    "Maple raises $5.3M to build AI products that protect your data, even from itself":
        "Maple 融资 530 万美元，打造能保护用户数据、甚至防止公司自身访问的 AI 产品",
    "Ambarella Brings Liquid AI Models to Edge Chips for Physical AI":
        "Ambarella 将 Liquid AI 模型引入边缘芯片，赋能物理 AI",
    "Anthropic Launches Linked Billing Beta for Claude API Apps":
        "Anthropic 推出 Claude API 应用「关联账单」测试版",
    "Jensen Huang says he’s willing to return as Nvidia CEO":
        "黄仁勋表示愿意重返 Nvidia CEO 岗位",
    "Liquid AI Releases d1.2 and d1.2-ultra: Omnimodal Decision Models That Top the AA Decision Index":
        "Liquid AI 发布 d1.2 与 d1.2-ultra：登顶 AA 决策指数的全模态决策模型",
    "Liquid AI Releases LiquidCodec, a 74M-Parameter Streaming Audio Codec":
        "Liquid AI 发布 LiquidCodec：7400 万参数的流式音频编解码器",
    "Anthropic Lets Customers Self-Host Claude Managed Agents":
        "Anthropic 允许客户自建 Claude 托管智能体",
    "Anthropic turns Claude into a full workspace with Plugins, spreadsheets, whiteboards, and soon Meeting notes":
        "Anthropic 将 Claude 打造成集插件、电子表格、白板及即将上线的会议记录于一体的完整工作空间",
    "LiveX brings engaging, AI-powered intelligent human-sized avatar kiosks to retail and airport sites":
        "LiveX 将 AI 驱动的等身智能头像自助终端引入零售与机场",
}

SUMMARY_FIX = {
    "Anthropic Lets Claude Users Install AI-Built Tools as Desktop Apps":
        "Anthropic 于 2026 年 11 月 24 日宣布，Claude 用户可在 macOS 和 Windows 上以测试版形式将「制品」（Artifacts）安装为桌面应用。这些应用拥有独立的窗口和图标，正向免费和付费用户推出，并可请求访问文件、程序、通知及其他操作系统功能。制品是 Claude 生成的设计、文档、仪表盘和小型交互工具，可在对话旁打开进行编辑与分享。",
    "Maple raises $5.3M to build AI products that protect your data, even from itself":
        "这家初创公司的加密 AI 架构旨在防止包括公司自身在内的任何一方访问用户的私人数据。",
    "Ambarella Brings Liquid AI Models to Edge Chips for Physical AI":
        "Ambarella 与 Liquid AI 于 2026 年 11 月 24 日宣布战略合作，将 Liquid 的基础模型与 Ambarella 低功耗 CVflow 边缘架构结合，让智能体 AI 直接运行在与物理世界交互的设备上。Liquid 基础模型现已上线 Ambarella 开发者区的 Cooper 模型花园，开发者可直接在 Ambarella 芯片上运行这些模型构建应用。",
    "Anthropic Launches Linked Billing Beta for Claude API Apps":
        "Anthropic 于 2026 年 11 月 17 日推出关联账单（Linked billing）测试版，允许开发者把应用中产生的 Claude API 用量费用记到客户自己的 Claude 组织账上。客户关联组织后，开发者可在每次请求时选择由客户还是自己付费。Anthropic 的用户资料文档对身份识别与付款作了区分。",
    "Jensen Huang says he’s willing to return as Nvidia CEO":
        "据《华尔街日报》报道，上周辞去 Nvidia CEO 职务的黄仁勋在声明中表示，如果董事会希望他回归，他愿意重新出任 CEO。黄仁勋称：「自我离开以来，我看到 Nvidia 员工、投资者、商业伙伴和客户纷纷呼吁我回归担任 CEO。如果董事会认为我的回归符合股东、员工、公司和美国的利益，我将很荣幸回应这些呼声并重返 CEO 岗位。」",
    "Liquid AI Releases d1.2 and d1.2-ultra: Omnimodal Decision Models That Top the AA Decision Index":
        "Liquid AI 刚刚发布 d1.2 和 d1.2-ultra。决策模型不生成文本，而是针对一组固定答案返回经过校准的概率。Liquid AI d1.2 决策模型家族现支持文本、图像和音频输入，并新增 5 种答案类型。d1.2-ultra 在 Artificial Analysis 决策指数 v2.1 上获得 75 分，为该指数上决策模型的最高分。参数规模未公开；每问最多 65,536 个输入 token，每次调用最多 128 个问题；仅通过托管 Liquid API 提供，权重尚未开放（Liquid AI 称会在「某个时候」开放）。性能方面，d1.2-ultra 得 75 分、d1.2 得 69 分；最佳校准表现为 d1.2-ultra 在 13 个基准上的校准误差低至 0.8 个百分点（Liquid AI 自测）。",
    "Liquid AI Releases LiquidCodec, a 74M-Parameter Streaming Audio Codec":
        "Liquid AI 发布了 LiquidCodec——其 LFM3-Audio-2B 与 LFM3-Omni-2B 模型背后的音频编解码器。LiquidCodec 是一个约 7400 万参数的流式语音分词器：先把语音转成语言模型可预测的 token，再将这些 token 还原为音频。Liquid AI 的目标有两个：让 token 易于预测、让还原为语音的速度足够快。权重已在 Hugging Face 开放。规格：约 7400 万参数（模型卡标注 7360 万）、24 kHz 音频、12.5 Hz 帧率、12 个码本；可在单 CPU 线程上运行（在 Apple M4 Max 笔记本上以 FP32 测试），也可通过 Transformers 在 CUDA GPU 上运行，并提供用于 llama.cpp 的 Q4_0、Q4_K_M 和 Q8_0 GGUF 构建。性能：在全部 8 个测试集上，相比 X-Codec 2、NanoCodec 和 Mimi 取得最佳 ViSQOL 与最低 mel 距离；在 1 个 CPU 线程上达到约 361 倍实时编码速度（编码 RTF 0.0028，Mimi 为 0.0361）。",
    "Anthropic Lets Customers Self-Host Claude Managed Agents":
        "Anthropic 于 2026 年 11 月 12 日推出自建（self-hosted）Claude Managed Agents，允许客户在自己的云账户或本地数据中心运行完整服务及其沙箱。智能体、会话与会话历史存储在该基础设施上，模型请求则可发往选定的推理服务商。Anthropic 此前的自建沙箱方案只是把智能体的工具执行迁移到客户系统，智能体本身仍由 Anthropic 运行。",
    "Anthropic turns Claude into a full workspace with Plugins, spreadsheets, whiteboards, and soon Meeting notes":
        "Anthropic 正在为 Claude 增加表格（Sheets）、白板（Whiteboards）和交互式连接器（Interactive Connectors），让 Adobe、Atlassian 等合作伙伴可把自家应用直接嵌入 Claude。Anthropic 表示，能加入通话并做记录的 Claude Meetings 即将推出。Anthropic 正一步步把 Claude 变成团队的中央工作平台，把众多其他应用汇聚到一处。",
    "LiveX brings engaging, AI-powered intelligent human-sized avatar kiosks to retail and airport sites":
        "总部位于帕洛阿尔托的 LiveX AI Inc. 是一家为零售与酒店场景打造交互式体验 AI 智能体的公司，今日发布 AI City——由其自助终端驱动的等身、拟人 AI 主持人。该公司产品目前已部署在 100 多个场所，通过等身人形头像在零售、科技、酒店与娱乐领域与顾客互动。",
}


def main():
    # 备份
    for path in (DATA, T_JSON, S_JSON):
        shutil.copy2(path, path + ".bak.0600patrol1125")

    with open(T_JSON, encoding="utf-8") as f:
        titles = json.load(f)
    with open(S_JSON, encoding="utf-8") as f:
        summaries = json.load(f)
    titles.update(TITLE_FIX)
    summaries.update(SUMMARY_FIX)
    with open(T_JSON, "w", encoding="utf-8") as f:
        json.dump(titles, f, ensure_ascii=False, indent=2)
    with open(S_JSON, "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)

    # 回填数据
    with open(DATA, encoding="utf-8") as f:
        data = json.load(f)
    n = 0
    for it in data["items"]:
        t = it.get("title")
        if t in TITLE_FIX:
            it["title_zh"] = TITLE_FIX[t]
            it["summary_zh"] = SUMMARY_FIX.get(t, it.get("summary_zh"))
            it["translated"] = True
            it["method"] = "manual"
            n += 1
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # 重生报告
    subprocess.run(["python3.11", os.path.join(BASE, "report.py")], check=True)

    # 同步代码层覆盖表
    subprocess.run(
        ["python3.11", os.path.join(BASE, "scripts", "regen_overrides.py")],
        check=True,
    )
    print("[fix0600] 回填条目 %d 条，标题覆盖表 %d，摘要覆盖表 %d"
          % (n, len(titles), len(summaries)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
