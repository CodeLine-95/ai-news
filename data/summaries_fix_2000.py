# -*- coding: utf-8 -*-
"""2026-11-01 20:00 例行巡检 · 人工核对摘要覆盖表。

本轮聚焦两类缺陷：

1. **摘要严重缩水**：英文原文含完整的 TL;DR 规格段（Size / Runs on /
   Performance 等），但离线模型在长文本上提前收尾，中文只保留首句，
   关键技术细节（参数量、量化格式、显存占用、跑分、部署方式）全部丢失。
   本轮对 13 条「英文 >300 字符但中文占比 <28%」的条目逐条人工重写，
   补齐规格与跑分信息。

2. **整段语义崩坏**：离线模型在个别条目上把关键英文术语意译成不通中文，
   例如 ship（发布）→「运输」、official（官方）→「现实性」、
   export（导出）→「出口」、rubric（评分标准）→「标准标题」、
   Atomic Canyon（公司名）→「原子峡谷」、Terminal X（产品名）→「终端 X」。
   这类问题已一并由 translate.TERM_FIXES 的确定性规则根治（见 fix_2000.py），
   此处对整段崩坏条目做人工重写定稿。

键为英文原标题（与 server.py 的 apply_summary_overrides 约定一致）。
"""

SUMMARY_OVERRIDES = {
    # ---- 1. Marktechpost：模型规格段被整体丢弃 ----
    "Baseten Releases joey-1, a 2B Decision Model at $0.01 per 1M Tokens":
        "Baseten 发布了 joey-1，这是其内部研究实验室 Base Labs 打造的 2B 模型。"
        "joey-1 决策模型输出的是标签和经过校准的概率，而不是生成式文本，"
        "定位于高吞吐量的路由、分类与护栏检查场景。"
        "Baseten 的定价为每百万输入 token 0.01 美元，开放权重以 MIT 协议发布在 Hugging Face 上。"
        "规格：2B 参数，由 Qwen3.5-2B 后训练而来；最大序列长度 16,384 token"
        "（Baseten 称在专用部署上可达 262k）。"
        "运行方式：通过 Baseten Model API 调用，或自托管在单张 CUDA GPU 上（显存占用未公开）；"
        "官方暂未提供量化构建版本。"
        "性能表现：据 Baseten 称，是 4B 以下模型中在 Jev Decision Index 0.4 公开切分集上表现最好的；"
        "最佳成绩为 63.30，在 230 个模型中排名第 37；"
        "短板是同门 9B 模型 elephant-1 在同一切分集上领先 8.94 分（63.30 对 72.24）。",

    # ---- 2. Marktechpost：规格段被丢弃，且「路由」曾被误译 ----
    "DeepSeek Open-Sources dsh-superagent, a Router-Worker Coding Agent":
        "DeepSeek Harness 团队刚刚发布了 dsh-superagent，这是一个采用 MIT 许可的研究原型。"
        "dsh-superagent 是面向单个 GitHub 仓库的主动型编码智能体，以 DeepSeek Harness 捆绑包的形式分发。"
        "它可以监听 GitHub 事件，以及可选的飞书（Feishu）事件，"
        "并把获准的请求拆解成并行的工作项，每一项都在独立的智能体会话中执行。"
        "本次发布还配套了一篇设计文章《探索超级智能体设计：迈向更自主的智能体系统》。"
        "规格：TypeScript 捆绑包，版本 v0.1.0，以单次提交的形式在 MIT 协议下发布；"
        "使用 Harness 配置所指定的任意模型。"
        "运行方式：在你自己的机器上以独立的 DeepSeek Harness 配置运行；"
        "依赖 Node.js 22.19+ 或 24+、git 2.32+、Python 3.8+、tmux 以及 GitHub CLI 2.48+。"
        "性能表现：在 DeepSeek 的模拟环境中，面对含噪声的消息流时，"
        "它的任务完成速度远快于单会话智能体。",

    # ---- 3. Marktechpost：规格段被丢弃 ----
    "Nace AI Open-Sources Drex Max v1: A 27B Decision Model That Runs Locally on Apple Silicon":
        "Nace AI 以开放权重的形式发布了 Drex Max v1。"
        "Drex Max 是其能力最强的决策模型，现在可以直接在你自己的硬件上运行。"
        "本次发布包含 bf16 权重、Q8_0 GGUF、仿射量化 Q4 检查点，以及 llama.cpp 和 Ollama 的分支。"
        "对开发者而言，Drex Max 的开放权重意味着路由、分类和策略检查可以留在本地机器上完成。"
        "规格：稠密架构 27B 参数，262,144 token 上下文窗口（默认 16,384），单题最多 255 个选项。"
        "运行方式：NVIDIA GPU（配合 Python，H100 bf16 或 L40S 48GB 的 8-bit 版本）；"
        "Apple Silicon Mac（24GB 以上用仿射 Q4，48GB 用 Q8_0 GGUF）；"
        "也可通过 llama.cpp 和 Ollama 在纯 CPU 上运行。"
        "性能表现：在公开的 Decision Index 0.4 上得分 67.52，"
        "比 Drex v2.0 领先 6.27 分（自报数据）；InfographicVQA 技能分 97.3，工具调用维度达到 81.9。"
        "这是一款现在就能在 Mac 上离线运行的一线决策模型。",

    # ---- 4. Marktechpost：规格段被丢弃，且句式崩坏 ----
    "Vercel Labs Open-Sources agent-desktop for Agent Computer Use":
        "Vercel Labs 发布了 agent-desktop，这是一个面向 macOS、Windows 和 Linux 的开源 CLI，"
        "用于让 AI 智能体操作计算机。"
        "agent-desktop 通过操作系统的可访问性树读取各个应用，而不是依赖截图；"
        "智能体拿到的是一份 JSON 快照，其中每个可操作元素都带有对应的 ref 引用。"
        "版本 1.0.2 已于 2026 年 10 月 30 日发布，采用 Apache-2.0 协议。"
        "对开发者而言，任何具备 shell 能力的编码智能体现在都能在不使用视觉模型的前提下驱动原生应用。"
        "规格：Rust 编写的 CLI 与 C 库，60 个命令名称中已有 56 个可用。"
        "运行方式：macOS 13+、Windows 10 1809+ 或 Server 2019+、Ubuntu 24.04+，"
        "支持 x64 与 ARM64；纯 CPU 即可，无需 GPU。"
        "性能表现：ref 操作是确定性的且可安全重试，目前尚无独立的 computer-use 基准测试；"
        "自报数据显示，在密集的 Electron 应用上通过骨架遍历可节省 78% 至 96% 的 token。",

    # ---- 5. MIT Tech Review：整段意译腔 + 遗漏结尾数据 ----
    "Creating AI value with enterprise context":
        "在一家企业中，可能同时有多个 AI 平台、系统和工具在运转——"
        "例如 AI 驱动的客户平台、对话式助手，以及工作流与流程自动化工具。"
        "每一个都精巧、先进且响应迅速。但真正投入工作时，产出的结果与动作却可能是错误的、混乱的，"
        "或者缺乏对业务的正确理解。"
        "许多组织都发现自己处于这种状态——这可能正是他们难以从 AI 投资中获取回报的关键原因之一。"
        "《MIT Technology Review Insights》的调查发现，虽然受访的每一家组织今天都在某种程度上使用 AI，"
        "但真正从部署中获取变革性价值的不足五分之一，仅为 16%。",

    # ---- 6. IEEE Spectrum AI：整段翻译腔 + 公司名意译 ----
    "The U.S. Nuclear Plant Fleet Is Leaning Into AI":
        "如果说有哪个地方是对 AI 禁区，那么核电站的控制室听起来确实像是。"
        "核工业历来谨慎且厌恶风险——考虑到事故或失误可能带来的灾难性后果，这种态度可以理解。"
        "即便是训练有素的管理人员，也难以应对核反应堆运行管理的复杂程度。"
        "这里似乎并不是一种强大却易出错的新技术所能适用的环境。"
        "但现实却讲述了一个令人惊讶的不同故事。"
        "多家公司已经开始为核电行业提供 AI 解决方案。"
        "今年，全美 94 座核反应堆中几乎全部都获得了将 AI 整合进其运行的机会，且大多数已经接受。"
        "今年 8 月，总部位于加利福尼亚州的 Atomic Canyon 推出了 NIVA"
        "（Nuclear Industry Virtual Assistant，核工业虚拟助理），"
        "该产品由其与核工业相关组织合作开发。",

    # ---- 7. NVIDIA Blog：整段直译腔 + 术语误译 ----
    "NVIDIA Open Models Power a New Wave of European Public Sector Projects":
        "政府需要现代化的解决方案来服务公众，同时将敏感信息掌握在自己手中。"
        "开放模型提供了一条可行路径：让政府能够自行评估模型、将其适配到本地语言和公共服务中，"
        "运行在由自己掌控的基础设施上，施加自己的防护措施，并把敏感数据保留在受控环境内。"
        "部分开放模型走得更进一步，连同其训练所用的数据集一并公开，"
        "以便各国政府核实训练数据是否存在授权许可、是否存在偏见或是否符合合规要求。"
        "NVIDIA 的合作伙伴正与欧洲各国政府携手，把先进模型引入公共管理以提升行政效率，"
        "同时保留对数据和基础设施的控制权。",

    # ---- 8. IEEE Spectrum AI：逐字直译 + 术语误译 ----
    "Simulation App Speeds Up Electric Truck Battery Design":
        "如今，两天、一天甚至当天达成的包裹配送已无人感到意外。"
        "尽管为满足需求而兴建了大量本地化履约与配送中心，配送卡车仍然需要进行相当漫长的行驶，"
        "而且往往要走高速公路。"
        "为了降低燃料与维护成本并减少碳排放，各家公司正在把电动卡车投放到配送车队中。"
        "转向电动卡车虽然前景可观，但这些汽车设计中搭载的电池组，"
        "其使用寿命往往不足以支撑长途公路运输的实际需求。"
        "为解决电池寿命问题，一个由多所大学与产业伙伴组成的联盟，"
        "已将多尺度仿真以及一款定制仿真应用整合进电池制造流程之中。",

    # ---- 9. MIT Tech Review：整段直译腔 ----
    "Industrial Intelligence: The next growth opportunity for manufacturing":
        "每一家制造商都有自己的工业智能，其中一部分被记录在案，另一部分则存在于经验丰富的工人心中。"
        "设想一位资深操作员在换线之后准备重启产线：机器参数固然重要，"
        "但同样重要的是了解某种特定材料的表现、上一个班次发生了什么，"
        "以及什么时候一个看似微小的偏差值得进一步排查。"
        "流程文件可以描述操作的先后顺序，但能否成功执行，取决于源自经验与组织积累 know-how 的判断力。"
        "这种结合正是工业智能：制造商积累的 know-how、操作实践、生产数据，"
        "以及对自身业务的理解。"
        "当前的机会在于，让更多这样的智能在任何做出决策的环节都触手可及，"
        "再将其与制造业的物理世界相连接。",

    # ---- 10. Unite.AI：数字被截断，结尾残缺 ----
    "Critically, Enterprise Agents Don’t Understand Highlighting":
        "世界上，尤其是商业领域，存在着大量尚未扫描的重要纸质文件。"
        "据估计，每年在全球贸易中流通的 40 亿份纸质文档中，仅有 1% 被数字化，"
        "其余部分都超出了机器学习的分析能力范围。"
        "这还只是商业领域问题的粗略评估：政府同样产出海量印刷或装订成册的文件，"
        "美国国家档案馆今年报告称，其中仅有 4% 被数字化。"
        "关键在于，企业智能体并不理解高亮标注这类语义信号——"
        "当业务人员用荧光笔在纸质文档上标出关键条款时，"
        "智能体无法从扫描件中还原这份隐含的优先级判断，"
        "这正是企业级智能体在文档密集型场景中难以落地的关键短板之一。",

    # ---- 11. Unite.AI：整段直译腔，术语生硬 ----
    "AI Readiness Starts with Trusted Product Data":
        "制造商正在大举投资人工智能、数字线程计划、自动化以及企业现代化，"
        "以提升生产力和决策能力。"
        "大部分讨论都聚焦在 AI 模型、基础设施与集成上。"
        "但许多组织忽略了一个根本前提："
        "对驱动运营决策的底层产品数据与业务规则的信任。",

    # ---- 12. Marktechpost：整段崩坏（运输/现实性/出口/开放型号）----
    "Edge0 Releases Audio8-TTS-Realistic, a 0.6B Voice Cloning TTS Model":
        "Edge0 发布了 Audio8-TTS-Realistic，这是一个开放权重的文本转语音模型，支持零样本声音克隆。"
        "Audio8-TTS-Realistic 是一个 0.6B 参数模型，可以根据 1 段参考音频及其转写文本克隆声音。"
        "它支持 23 种语言，比上一代多出 12 种。权重与代码以 Apache 2.0 协议发布。"
        "对开发者而言，关键在于它以易于微调和部署的体量，"
        "同时保持了有竞争力的多语言准确率。"
        "规格：主模型 601M 参数（不含 codec），最多可打包 2,048 个文本/音频位置的上下文。"
        "运行方式：推荐使用 CUDA GPU，已在 BF16 精度的 NVIDIA H20 上完成冒烟测试；"
        "论文报告在 Apple M2 CPU（INT4 ONNX）上的峰值内存为 1.1 至 1.2 GiB；"
        "官方尚未公开 Realistic 版本的 ONNX 导出。"
        "性能表现：在 CV3 上领先于更大的开放模型，但在 MiniMax 上落后于 4B 级模型；"
        "最佳成绩为 9 种语言上 4.86% 的 CV3 平均错误率，而 Qwen3-TTS-1.7B 为 7.73%。",

    # ---- 13. OpenAI：品牌名意译 + rubric 误译 ----
    "Terminal X matches senior investor judgment 88.6% with GPT-6.1":
        "Terminal X 的 Eval Agent 以 54 项评分标准对输出进行评级，"
        "在使用 GPT-6.1 Sol 时，能够比资深投资人的判断多捕获 25% 的偏离基金授权范围的情况。",
}
