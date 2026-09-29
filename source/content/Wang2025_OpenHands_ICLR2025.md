---
title: "OpenHands: An Open Platform for AI Software Developers as Generalist Agents"
title_zh: "OpenHands:AI 软件开发者通用智能体的开放平台"
authors: Xingyao Wang, Boxuan Li, Yufan Song, et al. (Graham Neubig 组)
venue: "ICLR 2025 · UIUC / CMU / Yale / All Hands AI 等"
kind: paper
importance: recommended
tags: 开源平台,CodeAct,沙箱,事件流,通用智能体
summary: 开源智能体开发平台(前 OpenDevin):事件流架构 + Docker 沙箱运行时 + 代码即动作(CodeAct)+ AgentSkills 工具库 + 多智能体委派,同一 CodeAct 智能体在软件工程、网页、辅助任务 15 个基准上零改动的通用表现。
---

## 导读

本文是第 9 周「编程智能体」的平台级论文(ICLR 2025,Neubig 组 + All Hands AI)。如果说 SWE-agent 揭示了"智能体-计算机接口(ACI)"的重要性,OpenHands 回答的是下一层问题:**一套让社区能一起开发、安全执行、统一评测智能体的开放基础设施**。它的设计立场鲜明——人类改变世界最强大的方式是软件,所以让智能体"像人类开发者那样"用写代码、跑命令、浏览网页来行动。技术上四大件:(1)**事件流架构**(Action/Observation 追加式历史,UI/智能体/环境三方共享);(2)**Docker 沙箱运行时**(bash + IPython + Playwright 浏览器,任意镜像可装 action execution API);(3)**CodeAct 动作空间**(用执行代码代替 JSON 函数调用,足够通用且可自造工具)+ AgentSkills 可扩展技能库;(4)**多智能体委派**(AgentDelegateAction)。评测覆盖 15 个基准:同一个 CodeAct 智能体不改系统提示,在 SWE-bench Lite 26%、WebArena 15.3%、GPQA 52% 等三类任务上都具竞争力——专基线各有单项更强,但通用性无人能敌。MIT 协议、188+ 贡献者、32K star,是学术与工业都能直接用的底座。

## 论文精读

### 摘要(全译)

软件是人类手中最强大的工具之一,它让熟练的程序员能以复杂而深刻的方式与世界交互。与此同时,得益于 LLM 的进步,能与周围环境交互并施加改变的 AI 智能体也在快速发展。本文介绍 OpenHands(原 OpenDevin)——一个用于开发强大而灵活的 AI 智能体的平台,这些智能体以与人类开发者相似的方式与世界交互:编写代码、与命令行交互、浏览网页。我们描述该平台如何支持:实现新智能体、与沙箱化代码执行环境的安全交互、多智能体协作,以及评测基准的整合。基于已整合的基准,我们在 15 个有挑战的任务上评测智能体,包括软件工程(如 SWE-Bench)与网页浏览(如 WebArena)等。OpenHands 以宽松的 MIT 协议开源,是横跨学界与工业界、拥有 188+ 贡献者 2.1K+ 贡献的社区项目。

### 1. 引言

- 背景之争:智能体框架(AutoGPT/LangChain/MetaGPT/AutoGen 等)已有不少,但普遍缺件:与世界的接口(基于 JSON 函数调用或代码执行)、运行环境、人机/机机通信机制。
- **核心立场**:人类与世界交互最强大的方式是软件;围绕软件开发、使用、部署已有成熟的工具链,因此**软件是 AI 智能体与世界复杂交互的理想接口**。但随之三个难题:如何让智能体在复杂软件系统中有效创建与修改代码?如何给它们即时收集信息(调试、取任务上下文)的工具?如何确保开发安全、避免对用户系统的副作用?
- OpenHands 五大特性:事件流交互机制(§2.1)、Docker 沙箱运行时(bash + 浏览器 + IPython)(§2.2)、类真人软件工程师的环境接口(§2.3)、多智能体委派(§2.4)、评测框架(§4)。附带可直接使用的实现:10+ 智能体的 Agent Hub、聊天式 UI(可视化智能体动作、实时反馈)、15 个评测基准。初始灵感来自 Devin,但社区贡献使其早已超出软件工程范畴。

### 2. OpenHands 架构

**2.1 智能体定义与实现**:
- **状态与事件流**:状态封装执行所需的全部信息;核心是**事件流**——按时间顺序排列的历史动作与观察集合(含智能体自身动作与用户指令/反馈),另含 LLM 累计成本、多智能体委派元数据等辅助信息。
- **动作(Action)**:受 CodeAct 启发的通用原语——`IPythonRunCellAction`(沙箱内执行任意 Python)、`CmdRunAction`(bash 命令)、`BrowserInteractiveAction`(BrowserGym 式浏览 DSL)。**用编程语言做动作空间**,强大到可以用任何形式的工具(Python 函数、REST API…),又可靠易维护;同时兼容 JSON 函数调用式智能体(用 PL 定义工具再暴露成 function calling),甚至支持**智能体自己造工具**(生成 Python 函数)。
- **观察(Observation)**:环境变化(执行结果、用户消息)。
- **实现新智能体**:核心就是一个 `step(state)` 函数——读事件史 → LLM 生成回复 → 解析成动作返回。抽象让用户专注智能体逻辑,不必操心动作执行(§2.2)。最简实现仅约 25 行(图 3)。

**2.2 智能体运行时**:
- **Docker 沙箱**:每任务会话起一个安全隔离的容器;OpenHands 通过容器内运行的 REST API(action execution API)执行事件流中的动作并回传观察;用户工作目录可配置挂载进沙箱。
- **Action Execution API** 维护三件套:(1) 连接 OS 的 bash shell;(2) Jupyter IPython 服务器(交互式 Python);(3) 基于 Playwright 的 Chromium 浏览器(BrowserGym 动作原语:导航、点击、输入、滚动),观察返回 HTML/DOM/可访问性树/截图/标签页等富信息。
- **任意 Docker 镜像支持**:构建机制把 action execution API 安装进用户提供的任意镜像——智能体可在任意 OS 与软件环境中工作。

**2.3 智能体技能(AgentSkills):可扩展的 ACI**:
- 承认 SWE-Agent 的教训(精心设计的 ACI 至关重要),但维护一大堆专用工具是艰巨的工程挑战,还要让不同智能体实现都能用。
- 方案:**AgentSkills**——一个 Python 包,工具(函数)自动导入 IPython 环境;"定义工具 = 写个 Python 函数"的门槛极低;所有智能体都能通过 `IPythonRunCellAction` 使用。
- **收录哲学**(明确不做什么):不包裹每个 Python 包再"教"智能体用(LLM 本来就懂 pandas 读 CSV);只在 (1) LLM 直接写代码不易做到(如按行编辑代码)或 (2) 需调用外部模型(语音转文字、代码编辑模型)时才加新技能。
- 现有技能:改编自 SWE-Agent 与 Aider 的 `edit_file`(按行改文件)、`scroll_up/down`、多模态文档读取(`parse_image` 用 VLM、`parse_pdf`)等。

**2.4 智能体委派**:`AgentDelegateAction` 把子任务委派给另一个智能体——如通用 CodeActAgent 把网页浏览任务委派给专门的 BrowsingAgent。

### 3. Agent Hub:社区智能体集散地

- **CodeActAgent**(默认通用智能体):每步可 (1) 自然语言对话(向人类求澄清/确认)或 (2) 执行代码完成任务(bash/Python/浏览器 DSL);v1.5+ 可编辑文件、浏览网页、运行程序。
- **BrowsingAgent**:WebArena 式但改进了观察与动作、零样本提示的网页智能体基线。
- **GPTSwarm Agent**:可优化图构建智能体系统(节点=操作,边=协作通信)。
- **Micro Agent**:复用通用智能体的大部分实现、只加专门化提示的轻量特化智能体——社区分享"对特定场景有效的提示"。

### 4. 评测(15 个基准)

- 覆盖三类:**软件**(SWE-Bench 修 GitHub issue、HumanEvalFix 修 bug、BIRD text-to-SQL、BioCoder 生信代码、ML-Bench、Gorilla APIBench、ToolQA)、**网页**(WebArena、MiniWoB++)、**杂项辅助**(GAIA、GPQA、AgentBench、MINT、EDA、ProofWriter)。对比对象限定为"不针对基准内容做手工提示工程的开源可复现基线"。
- **总览(表 3)**:同一个 CodeActAgent **不改系统提示**,三类任务全部有竞争力——这对比各专用基线(只为某类任务设计优化)意义突出。
- **软件工程(表 4 节选)**:
  - SWE-bench Lite(300 例,无提示):CodeActAgent v1.8 + claude-3.5-sonnet 达 **26.0%**(成本 $1.10/例),对比 SWE-Agent 18.0%(gpt-4-1106)、AutoCodeRover 19.0%、Aider 26.3%、Moatless 26.7%、Agentless 27.3%——OpenHands 与最强专用方案同档;
  - HumanEvalFix(Python,0-shot):**79.3%**(gpt-4o),远超所有非智能体方法(StarCoder2-15B 48.6%),接近 SWE-Agent 87.7%(但那是 1-shot 带演示轨迹);
  - ML-Bench:**76.5%**(gpt-4o)超 Aider 64.4% 与 SWE-Agent 42.6%;BIRD 47.3%;Gorilla APIBench 36.4%(专用微调的 Gorilla 75.0% 仍占优);ToolQA 47.2% 超 ReAct 43.1%。
- **网页与辅助**:WebArena 15.3%(对比 WebArena 原版 14.4%、训练过的 AutoWebGLM 18.2%);GPQA 53.1%(gpt-4o,v1.5)、52.0%(claude-3.5-sonnet);GAIA 上 GPTSwarm 32.1% 超 AutoGPT 13.2%。
- 结论:OpenHands 智能体未必每类都第一,但**通用性**(同一智能体、零改动跨三类任务)是设计目标所在;平台同时给出每例美元成本(如 SWE-bench $1.10、HumanEvalFix $0.14),全量 SWE-bench 2294 例约需 $6.9k。

### 5. 相关框架对比与影响

- 表 1 对比 11 个框架(AutoGPT、LangChain、MetaGPT、AutoGen、AutoCodeRover、SWE-Agent 等)在 9 个维度(标准化工具库、内置沙箱与代码执行、内置浏览器、多智能体协作、人机协作、AgentHub、评测框架、框架自身 QC):**OpenHands 是唯一全绿的通用框架**。
- 社区规模:MIT 协议、32K star、188+ 贡献者;定位为学术研究与工业应用的公共底座。

## 要点速览

- 一句话:OpenHands = 事件流架构 + Docker 沙箱(bash/IPython/浏览器)+ CodeAct 动作空间 + AgentSkills 工具库 + 多智能体委派 + 15 基准评测框架的开源智能体平台。
- **事件流**是中枢:Action/Observation 追加式历史,UI、智能体、运行时三方读写同一流——人可以随时打断/反馈,多智能体天然共享上下文。
- **代码即动作(CodeAct)**:用执行代码代替枚举 JSON 工具;覆盖面最广、可靠易维护,智能体还能自己写函数造工具;需要 JSON function calling 体验时也能包装提供。
- **AgentSkills 收录哲学**:LLM 已会的(如 pandas)不重复造轮子;只加"直接写代码做不到"或"需外部模型"的技能——这是工具设计的反直觉但正确原则。
- 安全模型:所有执行隔离在每会话的 Docker 沙箱;action execution API 可装进任意镜像 → 任意软件环境。
- 评测要点:同一 CodeActAgent 零改动横跨 SWE-bench Lite 26% / WebArena 15.3% / GPQA 52%;附每例成本,评测可复现。
- 与课程关联:与 SWE-bench(基准)、SWE-agent(ACI 思想来源,其 edit_file 等被 AgentSkills 吸收)构成编程智能体三角;其"通用 vs 专用"的张力呼应第 5 周 Neubig 的"别小看单智能体系统"之辩(Neubig 正是本文共同作者)。
