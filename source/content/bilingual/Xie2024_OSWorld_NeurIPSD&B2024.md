---
title: "OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks in Real Computer Environments"
title_zh: "OSWorld:在真实计算机环境中评测多模态智能体的开放式任务能力"
authors: "Tianbao Xie et al."
venue: "NeurIPS 2024 D&B · HKU, CMU, Salesforce Research & U. Waterloo"
kind: paper
importance: recommended
tags: "计算机使用智能体, 基准测试, 多模态, GUI 智能体, 执行式评估, 开放环境"
summary: 首个可扩展的真实计算机环境基准:369 个跨应用真实任务、可复现初始状态与执行式评估脚本;人类完成 72.36%,最强模型仅 12.24%。
---

## 导读

本文属于 CS 329Z 第 11 周"开放问题"专题。前三周的课程从记忆、工具使用讲到多智能体系统,而这一讲把问题拉回一个更根本的尺度:如果智能体的终极目标是在我们的电脑上替我们干活,它们现在到底行不行?OSWorld 给出了第一份系统的答卷。

在此之前的智能体基准存在两大空白:要么只有演示数据、没有可执行环境(Mind2Web、AITW 等),其非执行式评估假设每个任务只有一种解法,会错误惩罚其他正确路径;要么环境被限制在单一应用或领域(WebArena 限于网页、InterCode 限于代码),无法反映真实计算机使用的多样与复杂——真实工作流经常横跨多个应用、同时使用 GUI 与 CLI。OSWorld 是第一个**可扩展的真实计算机环境**:基于虚拟机技术支持 Ubuntu、Windows、macOS,允许自由的原始键鼠控制,支持任务初始状态配置、基于执行的评估与交互式学习。在其上构建的基准包含 369 个(另有 43 个 Windows 补充任务)来自真实用户场景的计算机任务,每个都配初始状态配置与定制评估脚本(共 134 个独特评估函数)。对 GPT-4V、Gemini、Claude-3、CogAgent 等一众 LLM/VLM 智能体的评测结果触目惊心:人类 72.36% vs 最好模型 12.24%,差距主要在 GUI 定位(grounding)与操作知识。对任何关心计算机使用智能体、基准设计或"评估如何驱动领域进步"的人,OSWorld 都是必知的工作——后来的 Anthropic Computer Use、OpenAI Operator 等系统都以它为标准评测场之一。

## 全文对照翻译

以下为论文正文(标题、摘要、第 1–7 节至结论与致谢,对应 arXiv v2 版第 1–18 页)的逐段中英对照翻译。英文段一律按 PDF 原文收录(仅将换行合并为连续段落,并修正 PDF 提取的断词与空格伪影,如 OSW ORLD → OSWorld);每段英文之后紧跟完整中文译文;图表题原样收录并附中文说明,任务统计与基线结果表转为 markdown;References 及其后的附录 A–D 不收录,文末附译注。

::: en
OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks in Real Computer Environments

Tianbao Xie♠ Danyang Zhang♠ Jixuan Chen♠ Xiaochuan Li♠ Siheng Zhao♠ Ruisheng Cao♠ Toh Jing Hua♠ Zhoujun Cheng♠ Dongchan Shin♠ Fangyu Lei♠ Yitao Liu♠ Yiheng Xu♠ Shuyan Zhou♣ Silvio Savarese♡ Caiming Xiong♡ Victor Zhong♢ Tao Yu♠

♠The University of Hong Kong ♣CMU ♡Salesforce Research ♢University of Waterloo

Preprint. Under review. arXiv:2404.07972v2 [cs.AI] 30 May 2024
:::

**标题与作者**:《OSWorld:在真实计算机环境中评测多模态智能体的开放式任务能力》。作者:Tianbao Xie、Danyang Zhang、Jixuan Chen、Xiaochuan Li、Siheng Zhao、Ruisheng Cao、Toh Jing Hua、Zhoujun Cheng、Dongchan Shin、Fangyu Lei、Yitao Liu、Yiheng Xu、Tao Yu(♠香港大学)、Shuyan Zhou(♣CMU)、Silvio Savarese、Caiming Xiong(♡Salesforce Research)、Victor Zhong(♢滑铁卢大学)。本文件为 arXiv 预印本 v2(arXiv:2404.07972v2 [cs.AI],2024 年 5 月 30 日;该文正式发表于 NeurIPS 2024 Datasets & Benchmarks Track)。

### 摘要(Abstract)

::: en
Autonomous agents that accomplish complex computer tasks with minimal human interventions have the potential to transform human-computer interaction, significantly enhancing accessibility and productivity. However, existing benchmarks either lack an interactive environment or are limited to environments specific to certain applications or domains, failing to reflect the diverse and complex nature of real-world computer use, thereby limiting the scope of tasks and agent scalability. To address this issue, we introduce OSWorld, the first-of-its-kind scalable, real computer environment for multimodal agents, supporting task setup, execution-based evaluation, and interactive learning across various operating systems such as Ubuntu, Windows, and macOS. OSWorld can serve as a unified, integrated computer environment for assessing open-ended computer tasks that involve arbitrary applications. Building upon OSWorld, we create a benchmark of 369 computer tasks involving real web and desktop apps in open domains, OS file I/O, and workflows spanning multiple applications. Each task example is derived from real-world computer use cases and includes a detailed initial state setup configuration and a custom execution-based evaluation script for reliable, reproducible evaluation. Extensive evaluation of state-of-the-art LLM/VLM-based agents on OSWorld reveals significant deficiencies in their ability to serve as computer assistants. While humans can accomplish over 72.36% of the tasks, the best model achieves only 12.24% success, primarily struggling with GUI grounding and operational knowledge. Comprehensive analysis using OSWorld provides valuable insights for developing multimodal generalist agents that were not possible with previous benchmarks. Our code, environment, baseline models, and data are publicly available at https://os-world.github.io.
:::

能在极少人工干预下完成复杂计算机任务的自主智能体(autonomous agents),有望变革人机交互(human-computer interaction),显著提升可访问性与生产力。然而,既有基准要么缺乏交互式环境,要么局限于特定应用或领域的环境,无法反映真实世界计算机使用的多样性与复杂性,从而限制了任务范围与智能体的可扩展性。为解决这一问题,我们引入 OSWorld——首个可扩展的、面向多模态智能体(multimodal agents)的真实计算机环境,支持跨 Ubuntu、Windows、macOS 等多种操作系统的任务设置(task setup)、基于执行的评估(execution-based evaluation)与交互式学习(interactive learning)。OSWorld 可作为一个统一、集成的计算机环境,用于评估涉及任意应用的开放式(open-ended)计算机任务。在 OSWorld 之上,我们创建了一个包含 369 个计算机任务的基准:任务涉及开放域中的真实网页与桌面应用、操作系统(OS)文件 I/O,以及横跨多个应用的工作流。每个任务样例都源自真实世界计算机使用案例,并包含详细的初始状态设置配置(initial state setup configuration)与定制的基于执行的评估脚本,以保证评估可靠、可复现。对最先进的基于 LLM/VLM 的智能体在 OSWorld 上的广泛评估,揭示了它们作为计算机助手的严重不足:人类可完成 72.36% 以上的任务,而最好的模型只达到 12.24% 的成功率,主要困于 GUI 定位(grounding)与操作知识。基于 OSWorld 的综合分析提供了以往基准无法提供的、对开发多模态通用智能体(generalist agents)的宝贵洞察。我们的代码、环境、基线模型与数据全部公开于 https://os-world.github.io 。

### 1 引言(Introduction)

::: en
Humans interact with computers to perform essential tasks in the digital realm, including web browsing, video editing, file management, data analysis, and software development. These task workflows often involve multiple applications through graphical user interfaces (GUI) and command line interfaces (CLI). Autonomous digital agents, powered by advancements in large vision-language models (VLMs), have the potential to revolutionize how we interact with computer environments [28, 44, 1]. By following high-level natural language instructions, these agents can make digital interactions more accessible and vastly increase human productivity. However, a major challenge in developing such multimodal agents is the absence of a benchmark based on a real interactive environment that covers the diversity and complexity of real-world computer use across various operating systems, interfaces, and applications, consequently restricting task scope and agent scalability.
:::

人类通过计算机完成数字世界中的核心任务,包括浏览网页、剪辑视频、管理文件、数据分析与软件开发。这些任务工作流往往通过图形用户界面(graphical user interface, GUI)与命令行界面(command line interface, CLI)横跨多个应用。由大型视觉-语言模型(large vision-language models, VLMs)的进展所驱动的自主数字智能体,有望革命化我们与计算机环境的交互方式 [28, 44, 1]。通过跟随高层自然语言指令,这些智能体可以让数字交互更易用,并大幅提升人类生产力。然而,开发这类多模态智能体的一个主要挑战,是缺乏一个基于真实交互环境、覆盖跨各种操作系统、界面与应用的真实世界计算机使用多样性与复杂性的基准,这进而限制了任务范围与智能体的可扩展性。

::: en
Previous benchmarks provide datasets of demonstrations without executable environments [9, 40, 21]. Their non-execution-based evaluation assumes a single solution for each task and wrongfully penalizes alternative correct solutions. These benchmarks also miss opportunities for essential agent development methods like interactive learning and real-world exploration. Building realistic interactive environments is a major challenge in developing multimodal agents. Prior work that introduce executable environments simplify the observation and action spaces of human-computer interaction and limit task scope within specific applications or domains, such as web navigation in a few domains [44, 30, 58, 66], coding [57] and the combination [32, 54, 34]. Agents developed in these restricted environments cannot comprehensively cover computer tasks, lacking the support of evaluating tasks in complex, real-world scenarios that require navigating between applications and interfaces in open domains (task examples in e.g., Fig. 1).
:::

以往的基准只提供演示数据集而无可执行环境 [9, 40, 21]。其非执行式评估(non-execution-based evaluation)假设每个任务只有单一解法,会错误惩罚替代的正确解。这些基准也错失了交互式学习、真实世界探索等关键智能体开发方法的机会。构建逼真的交互式环境是开发多模态智能体的一大挑战。已有的引入可执行环境的工作简化了人机交互的观察空间(observation space)与动作空间(action space),并把任务范围限制在特定应用或领域之内,例如少数几个域中的网页导航 [44, 30, 58, 66]、编程 [57] 及其组合 [32, 54, 34]。在这些受限环境中开发出的智能体无法全面覆盖计算机任务,缺乏对"在开放域中需要在应用与界面之间导航"的复杂真实场景任务进行评估的支持(任务示例见图 1)。

[图 1: Figure 1: OSWorld is a first-of-its-kind scalable, real computer environment for multimodal agents, supporting task setup, execution-based evaluation, and interactive learning across operating systems. It can serve as a unified environment for evaluating open-ended computer tasks that involve arbitrary apps (e.g., task examples in the above Fig). We also create a benchmark of 369 real-world computer tasks in OSWorld with reliable, reproducible setup and evaluation scripts.]

中文说明:图 1 为 OSWorld 总览。右侧为 OSWorld 环境:基于一台或多台虚拟机(Virtual Machine(s)),包含任务初始状态设置配置(Task Initial State Setup Config)、任意应用(Arbitrary Apps)与操作系统接口(OS Interfaces);智能体(如 GPT-4V)接收任务指令与观察(截图 screenshot、无障碍树 a11y-tree),经输入(input)与预测(predict)生成键盘鼠标(keyboard/mouse)动作(Action)。左侧给出两个任务示例——任务指令 1:「用所提供文件夹里我最近几天的交易记录更新记账表」(Task instruction 1: Update the bookkeeping sheet with my recent transactions over the past few days in the provided folder.);任务指令 2:「……(贪吃蛇游戏细节略)……你能帮我调整一下代码,让蛇真的能吃到食物吗?」(Task instruction 2: ...some details about snake game omitted… Could you help me tweak the code so the snake can actually eat the food?)。任务完成后,环境获取最终状态(get env state),进行基于执行的评估(Execution-based Evaluation)。图题:OSWorld 是首个可扩展的、面向多模态智能体的真实计算机环境,支持跨操作系统的任务设置、基于执行的评估与交互式学习;它可作为评估涉及任意应用的开放式计算机任务的统一环境,作者并在其上构建了 369 个真实世界计算机任务的基准,配有可靠、可复现的设置与评估脚本。

::: en
To address this gap, we introduce OSWorld, the first-of-its-kind scalable, real computer environment designed for the development of multimodal agents capable of executing a wide range of real computer tasks beyond isolated interfaces and applications. This executable environment allows free-form raw keyboard and mouse control of real computer applications and supports initial task state configuration, execution-based evaluation, and interactive learning across mainstream operating systems (e.g., Ubuntu, Windows, macOS). As shown in Fig. 1, OSWorld enables evaluation of open-ended computer tasks that involve arbitrary applications, ranging from image viewing to software functionality integration and programming. Thus, OSWorld can serve as a unified, real computer environment that allows users to define their agent tasks without the need to build application/domain-specific simulated environments.
:::

为弥补这一缺口,我们引入 OSWorld——首个可扩展的真实计算机环境,专为开发能够执行远超孤立界面与应用的、广泛真实计算机任务的多模态智能体而设计。这一可执行环境允许对真实计算机应用进行自由形式的原始键鼠控制,并支持跨主流操作系统(如 Ubuntu、Windows、macOS)的初始任务状态配置、基于执行的评估与交互式学习。如图 1 所示,OSWorld 能够评估涉及任意应用的开放式计算机任务,从图片查看到软件功能集成与编程。因此,OSWorld 可以作为一个统一的真实计算机环境,允许用户定义自己的智能体任务,而无需构建应用/领域专用的模拟环境。

::: en
Building upon OSWorld, we create a benchmark with 369 real-world computer tasks that involve widely-used web and desktop apps in open domains, OS file I/O, and multi-app workflows through both GUI and CLI. Each task example is based on real-world computer use cases experienced by real users and often requires interactions with multiple applications and interfaces. To ensure reliable, reproducible assessment within the OSWorld environment, 9 authors with computer science backgrounds carefully annotate each example with an initial state setup configuration to simulate human work in progress and a custom execution-based evaluation script to verify task completion. Our benchmark has a total of 134 unique evaluation functions, which are orders of magnitude larger than prior work [66], showcasing the complexity, diversity, and evaluation challenges of tasks in our benchmark. The human performance study indicates that task examples from OSWorld are more time-consuming and challenging compared to those in prior work.
:::

在 OSWorld 之上,我们创建了一个包含 369 个真实世界计算机任务的基准,这些任务通过 GUI 与 CLI 涉及开放域中广泛使用的网页与桌面应用、操作系统文件 I/O 以及多应用工作流。每个任务样例都基于真实用户经历的真实世界计算机使用案例,且常常需要与多个应用和界面交互。为了在 OSWorld 环境内保证可靠、可复现的评估,9 位具有计算机科学背景的作者为每个样例精心标注:一份模拟"人类工作进行到一半"的初始状态设置配置,以及一个验证任务是否完成的定制基于执行的评估脚本。我们的基准总共有 134 个独特的评估函数,比以往工作 [66] 高出数个数量级,展示了本基准任务的复杂性、多样性与评估挑战。人类性能研究表明,OSWorld 的任务样例比以往工作的样例更耗时、更具挑战。

::: en
We extensively evaluate state-of-the-art LLM and VLM-based agent baselines, including the GPT-4V series [39], the Gemini series [49, 41], the Claude-3 Opus [3] and the Qwen-Max [5], as well as Mixtral [19], Llama-3 [35] and CogAgent [17] from the open-source community. The performance of these experiments ranges from 0.99% to 12.24%, with subsets of applications even reaching 0%, for workflow tasks that involve cooperation from multiple apps, the highest performance of the baseline agent is only 6.57%. This indicates that current LLMs and VLMs are far from capable of serving as computer assistants (§4.2). Results also show that while additional knowledge such as the accessibility tree and Set-of-Mark (§4.1) can be helpful, it can also lead to potential misguidance and varies across models. We also observe performance changes in these agents compared to consistent human performance across different types of computer tasks. Analysis reveals that VLM-based agents struggle to ground on screenshots to predict precise coordinates for actions, tend to predict repetitive actions, are unable to handle noise from unexpected application windows and exhibit limited knowledge of basic GUI interactions and domain-specific features of apps (§5.2, §5.4). Feeding higher resolution and more trajectory history can help improve the performance by even doubling while requiring longer context length and efficient modeling (§5.2). We open-source OSWorld environment and benchmark, including environment initial state setup, reliable evaluation scripts, documentation, and our implementation of baseline models to promote research towards the goal of generalist capable computer agents 1. Future work can focus on enhancing VLM GUI grounding abilities, including interaction commonsense knowledge, higher-resolution support, and coordinates accuracy for more robust GUI interactions. Additionally, efforts can be made to improve agent architectures to better handle complex computer tasks through exploration, memory, and reflection. (脚注 1:https://os-world.github.io)
:::

我们广泛评估了最先进的基于 LLM 与 VLM 的智能体基线,包括 GPT-4V 系列 [39]、Gemini 系列 [49, 41]、Claude-3 Opus [3] 与 Qwen-Max [5],以及来自开源社区的 Mixtral [19]、Llama-3 [35] 和 CogAgent [17]。这些实验的性能从 0.99% 到 12.24% 不等,某些应用子集甚至达到 0%;对于需要多个应用配合的工作流任务,基线智能体的最高性能只有 6.57%。这表明当前 LLM 与 VLM 远不能胜任计算机助手(§4.2)。结果还表明,无障碍树(accessibility tree)与 Set-of-Mark 等额外知识(§4.1)虽然有帮助,也可能带来潜在误导,且效果因模型而异。与人类在不同类型计算机任务上一致的性能相比,我们还观察到这些智能体的表现起伏变化。分析揭示:基于 VLM 的智能体难以在截图上定位(ground)以预测动作的精确坐标、倾向预测重复动作、无法处理来自意外应用窗口的噪声,并且对基本 GUI 交互与应用领域特性知识有限(§5.2、§5.4)。输入更高分辨率与更多轨迹历史(trajectory history)可帮助提升性能、甚至使其翻倍,但需要更长的上下文长度与高效建模(§5.2)。我们开源 OSWorld 环境与基准,包括环境初始状态设置、可靠评估脚本、文档以及我们实现的基线模型,以推动面向"有通用能力的计算机智能体"这一目标的研究(脚注 1:https://os-world.github.io )。未来工作可以聚焦于增强 VLM 的 GUI 定位能力,包括交互常识知识、更高分辨率支持与坐标精度,以实现更鲁棒的 GUI 交互。此外,还可以努力改进智能体架构,使其通过探索(exploration)、记忆(memory)与反思(reflection)更好地处理复杂计算机任务。

### 2 OSWorld 环境(OSWorld Environment)

::: en
In this section, we will introduce the task definition of autonomous agents, the components and implementation of the OSWorld environment, and the supported observation and action spaces.
:::

本节将介绍自主智能体的任务定义、OSWorld 环境的组件与实现,以及所支持的观察空间与动作空间。

#### 2.1 任务定义(Task Definition)

::: en
An autonomous digital agent task can be formalized as a partially observable Markov decision process (POMDP) (S, O, A, T, R) with state space S, observation space O (§2.3, including natural language I), action space A (§2.4), transition function T : S×A→S, and reward function R : S×A→ R. Given current observation ot∈O (a natural language instruction observation and a screenshot observation (e.g., computer screenshot), accessibility (a11y) tree, or their combination according to facilities available), an agent generates executable action at∈A (e.g., clicking on the certain pixel of the screen — .click(300, 540, button='right'), press key combination — .hotkey('ctrl', 'alt', 't')), which results in a new state st+1∈S (e.g., current Desktop environment) and a new partial observation ot+1∈O (e.g., current screenshot). The interaction loop repeats until an action that marks termination (DONE or FAIL, see Sec. 2.4) is generated or the agent reaches the max number of steps (e.g., 15 in our experiments). In this version of OSWorld, we implement an execution-based reward function R : S×A→ [0, 1] (§2.2.3). The reward function awards a value of 1 or a positive decimal under 1 at the final step if the state transitions meet the expectations of the task objective (i.e., the goal is successfully achieved or partially achieved), or if the agent accurately predicts failure for an infeasible task. In all other scenarios, it returns 0.
:::

自主数字智能体任务可以被形式化为部分可观察马尔可夫决策过程(partially observable Markov decision process, POMDP)(S, O, A, T, R):其中包含状态空间 S、观察空间 O(§2.3,含自然语言 I)、动作空间 A(§2.4)、状态转移函数 T : S×A→S,以及奖励函数 R : S×A→ ℝ。给定当前观察 ot∈O(自然语言指令观察,以及截图观察(如计算机截图)、无障碍(accessibility, a11y)树或按可用设施取其组合),智能体生成可执行动作 at∈A(例如点击屏幕上的某个像素——`.click(300, 540, button='right')`,按组合键——`.hotkey('ctrl', 'alt', 't')`),该动作导致新状态 st+1∈S(如当前桌面环境)与新的部分观察 ot+1∈O(如当前截图)。交互循环不断重复,直到生成标记终止的动作(DONE 或 FAIL,见第 2.4 节),或智能体达到最大步数(我们的实验中为 15 步)。在本版 OSWorld 中,我们实现了基于执行的奖励函数 R : S×A→ [0, 1](§2.2.3)。若状态转移满足任务目标的期望(即目标被成功达成或部分达成),或智能体对不可行任务准确预测了失败,奖励函数在最后一步给出 1 或小于 1 的正小数;在所有其他情形下返回 0。

#### 2.2 真实计算机环境基础设施(Real Computer Environment Infrastructure)

::: en
OSWorld is an executable and controllable environment that supports task initialization, execution-based evaluation, and interactive agent learning in a range of real operating systems (e.g., Ubuntu, Windows, macOS) using virtual machine techniques, shown in the middle and right of Fig. 2. Virtual machine offers a safe isolated environment and prevents the agent resulting in irreversible damaging effect on the real host machine. The snapshot feature also enables efficient reset of the virtual environment. The environment is configured through a config file (shown in the left of Fig. 2) for interface initialization during the initialization phase (including downloading files, opening software, adjusting interface layout) (§2.2.2, highlighted with red in Fig. 2), post-processing during the evaluation phase (activating certain windows, saving some files for easy retrieval of information, highlighted with orange), and acquiring files and information for evaluation (such as the final spreadsheet file for spreadsheet tasks, cookies for Chrome tasks, highlighted with yellow in Fig. 2), as well as the evaluation functions and parameters used (§2.2.3, highlighted with green in Fig. 2). See App. A.1 for more details.
:::

OSWorld 是一个可执行、可控的环境,利用虚拟机(virtual machine)技术在一系列真实操作系统(如 Ubuntu、Windows、macOS)上支持任务初始化、基于执行的评估与交互式智能体学习,见图 2 中间与右侧。虚拟机提供了安全隔离的环境,防止智能体对真实宿主机造成不可逆的破坏性影响。快照(snapshot)功能还支持虚拟环境的高效重置。环境通过配置文件(config file,见图 2 左侧)进行配置,覆盖:初始化阶段的界面初始化(包括下载文件、打开软件、调整界面布局)(§2.2.2,图 2 中以红色高亮);评估阶段的后处理(激活某些窗口、保存一些文件以便取回信息,橙色高亮);获取评估所需的文件与信息(如表格任务的最终表格文件、Chrome 任务的 cookies,图 2 中以黄色高亮);以及所使用的评估函数与参数(§2.2.3,图 2 中以绿色高亮)。更多细节见附录 A.1。

[图 2: Figure 2: Overview of the OSWorld environment infrastructure. The environment uses a configuration file for initializing tasks (highlighted in red), agent interaction, post-processing upon agent completion (highlighted in orange), retrieving files and information (highlighted in yellow), and executing the evaluation function (highlighted in green). Environments can run in parallel on a single host machine for learning or evaluation purposes. Headless operation is supported.]

中文说明:图 2 为 OSWorld 环境基础设施总览。左侧为配置文件示例(以"更新记账表"任务为例,配置含 instruction、config(红色,任务初始化)、evaluator(含橙色 postconfig、黄色 result/expected、绿色 func/options),整理如下):

```json
{
  "instruction": "Please update my bookkeeping sheet with the recent transactions from the provided folder, detailing my expenses over the past few days.",
  "config": [
    {"type": "download", "parameters": {"files": [
      {"path": "/home/user/Desktop/my_bookkeeping.xlsx", "url": "https://drive.google.com/uc?id=xxxx"},
      {"path": "/home/user/Desktop/receipt_0.jpeg", "url": "https://drive.google.com/uc?id=xxxx"}, ...]}},
    {"type": "open", "parameters": {"path": "/home/user/Desktop/my_bookkeeping.xlsx"}}
  ],
  "evaluator": {
    "postconfig": [{"type": "activate_window",
                    "parameters": {"window_name": "my_bookkeeping.xlsx - LibreOffice Calc", ...}],
    "result":   {"type": "vm_file", "path": "/home/user/Desktop/my_bookkeeping.xlsx", "dest": "my_bookkeeping.xlsx"},
    "expected": {"type": "cloud_file", "path": "https://drive.google.com/uc?id=xxx", "dest": "my_bookkeeping_gold.xlsx"},
    "func": "compare_table",
    "options": {"rules": [{"type": "sheet_fuzzy", "sheet_idx0": "RNSheet1", "sheet_idx1": "ENSheet1",
                           "rules": [{"range": ["A1:A8", ...]}]}]}
  }
}
```

右侧为环境组件:宿主机上的 Coordinator(协调器)接受 Config,与多台虚拟机(VM 1、…)交互;每台虚拟机内有虚拟机平台(Virtual Machine Platform)、虚拟机控制接收器(Virtual Machine Control Receiver)与虚拟机控制器(Virtual Machine Controller,经 vmrun 命令、Flask 命令执行设置与后处理);Task Manager(任务管理器)下辖 Setup Interpreter(设置解释器)与 Evaluation Interpreter(评估解释器,通过执行 eval scripts 得到 Reward);Simulator(模拟器)负责屏幕捕获(screen capture)与无障碍树(accessibility tree);Getter 与 Metrics 负责取回状态、文件与信息(status, files, infos…)。智能体与平台之间以观察(observations)与动作(actions)交互。图题:环境使用一份配置文件完成任务初始化(红色高亮)、智能体交互、智能体完成后的后处理(橙色高亮)、文件与信息取回(黄色高亮)以及评估函数执行(绿色高亮);多台环境可并行运行于单台宿主机上以用于学习或评估,并支持无头(headless)运行。

##### 2.2.1 总览(Overview)

::: en
OSWorld environment runs on the host machine. Its Coordinator accepts a configuration file at the initialization of a computer task, runs commands to automatically create a virtual machine instance, and initializes the required state for the task through the Task Manager. The configuration file specifies the snapshot of the virtual machine to be used (which stores the complete state of a computer at a certain moment and can be restored to this state at any time) and also indicates the information needed for setup (such as downloading files and opening some software, making some additional settings, etc.). Once the environment is set up, agents start to interact with the environment, receiving observations such as screenshots, the accessibility (a11y) tree, and customized streams such as terminal outputs. Agents subsequently generate executable actions (e.g., .click(300, 540)) that manipulate the keyboard and mouse. Each action of the agent is input into the environment as a code string, and the environment's Simulator executes them in the virtual machine. After the completion of a task, the Task Manager performs post-processing (such as file saving, or reopening certain apps) according to the task's post-config, retrieves data to the host machine (fetching images or configuration files from the virtual machine or cloud, etc.), and then runs evaluation scripts to assess the completion of the task. Multiple virtual machines can run simultaneously on a single host machine, thereby parallelizing training and evaluation.
:::

OSWorld 环境运行在宿主机上。其 Coordinator(协调器)在计算机任务初始化时接受一份配置文件,运行命令自动创建虚拟机实例,并通过 Task Manager(任务管理器)初始化任务所需的状态。配置文件指定要使用的虚拟机快照(它存储一台计算机在某一时刻的完整状态,且可随时恢复到该状态),并指明设置所需的信息(如下载文件、打开某些软件、做一些额外设置等)。环境就绪后,智能体开始与环境交互,接收诸如截图、无障碍(a11y)树以及终端输出等定制流作为观察。随后智能体生成可执行动作(如 `.click(300, 540)`)来操纵键盘与鼠标。智能体的每个动作以代码字符串的形式输入环境,由环境的 Simulator(模拟器)在虚拟机中执行。任务完成后,Task Manager 按该任务的 post-config 进行后处理(如保存文件或重新打开某些应用),把数据取回宿主机(从虚拟机或云端获取图像或配置文件等),然后运行评估脚本评估任务的完成情况。单台宿主机上可以同时运行多个虚拟机,从而并行化训练与评估。

##### 2.2.2 初始任务环境设置(Initial Task Environment Setup)

::: en
Many real-world scenarios requiring assistance occur not at the beginning of digital activities, such as right after launching an application or when a computer has just been started, but rather at intermediate stages, such as when certain software is already open or the computer has experienced a crash. Therefore, we aim to simulate these intermediate states as closely as possible to replicate real-world scenarios. The naturalness we bring in also leads to more challenges for agents to model and explore. We adopted a hybrid approach for configuration instead of solely relying on example-wise snapshots for restoration since it would store much unnecessary hardware state information, resulting in each example requiring gigabytes of space. The procedure is divided into three stages: start the VM emulator, prepare files (download the files or scripts from the cloud, etc. optional), and execute preprocessing commands (open files or tabs, change the window size, etc. optional). We provide convenient APIs to configure initial conditions and world settings, standardizing our tasks to make this process user-friendly and easily extendable for scaling. For more details on setup see App. B.5.
:::

许多需要帮助的真实场景并非发生在数字活动的起点——比如刚启动一个应用、或电脑刚开机——而是发生在中间阶段,比如某些软件已经打开、或电脑刚经历过一次崩溃。因此,我们尽可能贴近地模拟这些中间状态,以复刻真实世界场景。我们引入的这种自然性也给智能体的建模与探索带来了更多挑战。配置上我们采用混合方式,而非仅依赖逐例快照来恢复——后者会存储大量不必要的硬件状态信息,导致每个样例需要数 GB 的空间。流程分为三个阶段:启动虚拟机模拟器;准备文件(从云端下载文件或脚本等,可选);执行预处理命令(打开文件或标签页、改变窗口大小等,可选)。我们提供便捷的 API 来配置初始条件与世界设置,将任务标准化,使这一过程对用户友好、且易于扩展规模化。设置的更多细节见附录 B.5。

##### 2.2.3 基于执行的评估(Execution-Based Evaluation)

::: en
Evaluating the successful execution of general computer tasks presents a significant challenge, as these tasks defy reduction to a uniform pattern or measurement by a single metric. To ensure a thorough assessment, we design example-specific evaluation metrics including pre-setup, post-processing, and dedicated functions, tailored to the software in use and the task's specific requirements. This involves interpreting the software's internal files, utilizing specific packages, and preemptively setting up scaffolding based on the software's permissions (e.g., opening remote debugging ports for Chrome and VLC, creating extensions for VS Code). Occasionally, this process may also require assistance from reverse engineering tools, such as for decrypting account information in Thunderbird.
:::

评估通用计算机任务是否成功执行是一个重大挑战,因为这些任务无法被归结为统一模式、也无法用单一度量来衡量。为确保评估充分,我们设计逐例专属的评估指标,包括前置设置(pre-setup)、后处理(post-processing)与专用函数(dedicated functions),针对所用软件与任务的具体需求量身定制。这涉及解读软件的内部文件、使用特定的软件包,并依据软件权限预先搭好脚手架(scaffolding)(例如为 Chrome 与 VLC 打开远程调试端口、为 VS Code 创建扩展)。有时这一过程还需要逆向工程(reverse engineering)工具的辅助,例如解密 Thunderbird 中的账户信息。

表 1:标注评估脚本示例(Table 1: Examples of our annotated evaluation scripts, which involve retrieving data from configuration files, the environment, and the cloud, and executing functions to assess functional correctness and obtain results. The example-wise evaluation facilitates the diversity of tasks and reliable evaluation of complex, real-world, open-ended tasks.)——初始状态列为环境截图(此处从略),每例给出任务指令原文与评估脚本(简化版,以代码块保留):

例 1 — 任务指令:「你能帮我把 Amazon 可能保存的所有 cookies 清理掉,给我的电脑做个大扫除吗?」(Can you help me clean up my computer by getting rid of all the cookies that Amazon might have saved?)

```python
cookie_data = get_cookie_data(env)
rule = {"type": "domains", "domains": [".amazon.com"]}
is_cookie_deleted(cookie_data, rule)
```

例 2 — 任务指令:「把 “Sheet 1” 重命名为 “LARS Resources”。然后复制一份,把副本放到 “Sheet 2” 之前,并在名称后追加后缀 “(Backup)”,……」(Rename "Sheet 1" to "LARS Resources". Then make a copy of it. Place the copy before "Sheet 2" and rename it by appending a suffix "(Backup)", ...)

```python
result = get_file(env)
expected = get_file(cloud)
rules = [{"type": "sheet_name"},
         {"type": "sheet_data", "sheet_idx0": 0, "sheet_idx1": 1}...]
compare_table(result, expected, rules)
```

例 3 — 任务指令:「我已经为还没交学费的人起草了一封邮件提醒。请帮我从缴费记录里查到他们的邮箱,并添加到收件人栏。」(I've drafted an e-mail reminder for those who haven't paid tuition. Please help me to check out their e-mails from the payment record and add to the receiver field.)

```python
tree = get_a11y_tree(env)
rules = [{"selectors": ["tool-bar[attr|id=MsgHeadersToolbar] label[name=To] "
                        "[attr|class=\"address-pill\"]> label[attr|class=\"pill-label\"] "
                        "[name*=\"fox@someuniversity.edu...]"]}]
check_a11y_tree(tree, rules)
```

::: en
As a result, we construct a vast collection of functions that make final wrangling and retrieve files and data information of varying types, categories, and granularities from the cloud and software from virtual machines as well as evaluation functions covering different aspects and their combinations, inputting this information as parameters to assess the outcomes. We show some evaluation examples in Tab. 1., demonstrate the retrieval of cookie data from virtual machines, obtaining files from both virtual machines and cloud services, fetching the current runtime interface's accessibility tree from the virtual machines, and determining success based on this information whether Amazon's cookies have been deleted, whether the generated table is accurate, and whether the correct interface has been accessed. Need to note when the type of task has real-time characteristics (such as the number of citations of someone's paper, the content of blogs, etc.), we include dynamic functions (such as crawler scripts) inside getter to obtain the real-time values at the moment of evaluation and then use them to compare with the results obtained by the agent upon task completion. See more in App. B.6.
:::

由此,我们构建了一个庞大的函数库:从云端以及虚拟机中的软件获取不同类型、类别与粒度的文件与数据信息以做最终整理(wrangling),以及覆盖不同侧面及其组合的评估函数,把这些信息作为参数输入来评估结果。我们在表 1 中展示了一些评估示例,演示了:从虚拟机取回 cookie 数据;同时从虚拟机与云端服务获取文件;从虚拟机获取当前运行界面的无障碍树;并基于这些信息判断 Amazon 的 cookies 是否已被删除、生成的表格是否准确、以及是否访问了正确的界面。需要注意,当任务类型具有实时特性时(如某人论文的引用数、博客的内容等),我们在 getter 内置动态函数(如爬虫脚本),在评估时刻获取实时数值,再用它们与智能体任务完成后得到的结果比较。详见附录 B.6。

#### 2.3 观察空间(Observation Space)

::: en
The observation space in OSWorld contains a complete screenshot of the desktop screen, including the mouse's position and shape, various application windows, files, and folders that are opened in different sizes and orders, maintaining the same perception as a human. Also, to be aligned with previous agent-building web and mobile research [30, 27, 9, 66] that provide and support the use of the webpage's DOM and app's view hierarchy, OSWorld also provides XML-format accessibility (a11y) tree (obtained via ATSPI 2 on Ubuntu, via PyWinAuto on Windows, etc.), which can support additional information for modeling. These raw observations allow rich interactions between multiple applications but induce challenges in long-horizon decision-making from high-resolution images (e.g., 4k screenshots) and structured long text (e.g., accessibility trees). For more detailed information on observation space, refer to App. A.2.
:::

OSWorld 的观察空间包含桌面屏幕的完整截图,其中含鼠标的位置与形状、各应用窗口、以不同大小与顺序打开的文件与文件夹,与人类的感知保持一致。同时,为了与以往提供并支持使用网页 DOM 与应用视图层级(view hierarchy)的网页/移动智能体构建研究对齐 [30, 27, 9, 66],OSWorld 还提供 XML 格式的无障碍(a11y)树(Ubuntu 上经 ATSPI 2、Windows 上经 PyWinAuto 等获取),可为建模提供额外信息。这些原始观察支持多应用之间的丰富交互,但也带来挑战:需要从高分辨率图像(如 4K 截图)与长结构化文本(如无障碍树)中进行长程决策(long-horizon decision-making)。观察空间的更多细节见附录 A.2。(脚注 2:https://docs.gtk.org/atspi2/ )

#### 2.4 动作空间(Action Space)

表 2:OSWorld 中鼠标与键盘动作 A 的部分示例(Table 2: Some examples of the mouse and keyboard actions A in OSWorld. See App. A.3 for the complete list.)——完整列表见附录 A.3:

| 函数 | 说明 |
| --- | --- |
| `moveTo(x, y)` | 将鼠标移动到指定坐标。 |
| `click(x, y)` | 在指定坐标处点击。 |
| `write('text')` | 在当前光标位置输入指定文本。 |
| `press('enter')` | 按下 Enter 键。 |
| `hotkey('ctrl', 'c')` | 执行 Ctrl+C 组合键(复制)。 |
| `scroll(200)` | 向上滚动 200 个单位。 |
| `scroll(-200)` | 向下滚动 200 个单位。 |
| `dragTo(x, y)` | 将鼠标拖拽到指定坐标。 |
| `keyDown('shift')` | 按住 Shift 键。 |
| `keyUp('shift')` | 释放 Shift 键。 |
| `WAIT` | 智能体决定等待。 |
| `FAIL` | 智能体判定任务不可行。 |
| `DONE` | 智能体判定任务已完成。 |

::: en
Action space A in OSWorld encompasses all mouse and keyboard actions, including movement, clicks (left-key, right-key, multiple clicks), dragging, keystrokes, hotkeys, and others, covering all human-computer action space. Some action examples are shown in Tab. 2 and the complete action list can be found in Appendix A.3. We use the widely used mouse and keyboard control library pyautogui 3 for our action space. This library leverages the high-level programming language Python to replicate and replay various human inputs into computers through code, allowing us to construct a universal and complete representation of actions. The agent must generate syntax-correct pyautogui Python code to predict valid actions. Basic actions, such as press and moveTo, can be integrated within program structures, such as for-loops, significantly improving the expressiveness of an action. Timing is also crucial, as highlighted in previous studies on mobile devices [50], as well as the ability to determine whether a task is infeasible or completed. Therefore, we add three special actions named WAIT, FAIL, and DONE to enhance the aforementioned action spaces. Previous efforts towards creating domain-specific agents, such as MiniWoB++ [44, 30], CC-Net [18], and WebArena [66, 22], have defined action spaces that include clicks and typing, as well as some actions specially designed for web browsing. However, they do not model all possible actions on a computer, leading to limitations when attempting actions like right-clicking and clicking with the ctrl key held to select items. This imposes an upper bound on agent learning capabilities.
:::

OSWorld 的动作空间 A 涵盖所有鼠标与键盘动作,包括移动、点击(左键、右键、多击)、拖拽、按键、组合键等,覆盖全部人机动作空间。部分动作示例见表 2,完整动作列表见附录 A.3。我们使用广泛使用的键鼠控制库 pyautogui 作为动作空间(脚注 3:https://pyautogui.readthedocs.io/en/latest/ )。该库借助高级编程语言 Python,通过代码复现并重放人类向计算机输入的各类操作,使我们可以构建通用而完整的动作表示。智能体必须生成语法正确的 pyautogui Python 代码来预测有效动作。press、moveTo 等基础动作可以嵌入 for 循环等程序结构之中,显著提升单个动作的表达力。时机(timing)同样关键,正如以往移动设备研究所强调的 [50];判断任务是否不可行或是否已完成的能力也很重要。因此,我们加入了三个名为 WAIT、FAIL、DONE 的特殊动作来增强上述动作空间。以往打造领域专用智能体的工作,如 MiniWoB++ [44, 30]、CC-Net [18] 与 WebArena [66, 22],所定义的动作空间只包括点击与输入,以及一些专为网页浏览设计的动作。然而,它们并未建模计算机上所有可能的动作,导致在尝试"右键点击""按住 Ctrl 键点击以选择条目"这类动作时受限。这给智能体的学习能力设下了上限。

### 3 OSWorld 基准(OSWorld Benchmark)

::: en
We introduce the OSWorld benchmark, which encompasses 369 real computing tasks defined and executed on Ubuntu. Additionally, we provide a set of 43 tasks for Windows built on the OSWorld environment. 4 The environment preparation, annotation process, data statistics, and human performance are described in this section.
:::

我们引入 OSWorld 基准,它包含在 Ubuntu 上定义与执行的 369 个真实计算任务。此外,我们基于 OSWorld 环境提供一套 43 个 Windows 任务(脚注 4:因版权问题,这些 Windows 任务需要用户进一步激活)。本节介绍环境准备、标注流程、数据统计与人类性能。

#### 3.1 操作系统与软件环境(Operating System and Software Environments)

::: en
OSWorld supports real operating systems, including Windows, macOS, and Ubuntu, for the development of automated computer agents. For development purposes, we offer an extensive set of examples on Ubuntu and its open-source applications, leveraging their open-source nature and more accessible APIs for task setting and evaluation. We also provide annotated testing examples for Windows, focusing on applications with similar functionalities. For the first time, our real OS environments enable us to define all kinds of computer tasks, including those that involve interacting with multiple applications (e.g., Chrome and file manager) and interfaces (GUIs and CLIs). Considering availability, the strength of the user community, and diversity, we mainly focus on eight representative applications as well as the basic ones system provide: Chrome for web browsing, VLC for media playback, Thunderbird for email management, VS Code as a coding IDE, and LibreOffice (Calc, Writer, and Impress) for handling spreadsheets, documents, and presentations respectively, GIMP for image editing, and other basic OS apps like terminal, file manager, image viewer, and PDF viewer. Each example drawn from these applications separate or in combination showcases distinct operational logic and necessitates skills including commonsense knowledge, high-resolution perception, mastery of software shortcuts, and the precise controlling of mouse and keyboard movements. For more details, check App. B.1 and B.2.
:::

OSWorld 支持真实操作系统,包括 Windows、macOS 与 Ubuntu,用于开发自动化计算机智能体。出于开发目的,我们在 Ubuntu 及其开源应用上提供了大量样例,利用其开源性质与更易用的任务设置和评估 API。我们也为 Windows 提供了标注好的测试样例,聚焦功能相似的应用。我们的真实 OS 环境首次使我们能够定义各类计算机任务,包括那些涉及多应用交互(如 Chrome 与文件管理器)与多界面(GUI 与 CLI)的任务。综合考虑可用性、用户社区实力与多样性,我们主要聚焦八个代表性应用以及系统自带的基础应用:Chrome 用于网页浏览,VLC 用于媒体播放,Thunderbird 用于邮件管理,VS Code 作为编码 IDE,LibreOffice(Calc、Writer、Impress)分别用于处理表格、文档与幻灯片,GIMP 用于图像编辑,以及终端、文件管理器、图片查看器与 PDF 查看器等其他 OS 基础应用。从这些应用中单独或组合抽取的每个样例都展现出不同的操作逻辑,所需技能包括常识知识、高分辨率感知、软件快捷键的掌握,以及对鼠标键盘移动的精确控制。更多细节见附录 B.1 与 B.2。

#### 3.2 任务(Tasks)

::: en
We create a benchmark suite of 369 real-world computer tasks on Ubuntu environment collected from authors and diverse sources such as forums, tutorials, guidelines, etc., to show the capability for open-ended task creation within OSWorld. Each example is carefully annotated with a natural language instruction, a setup configuration with corresponding files and setup actions for initialization of initial states upon our provided VM image, and a manually crafted evaluation script to check if the task is successfully executed. We also adapt 43 tasks from the Ubuntu set for analytic usage on Windows. Overall, it takes 9 computer science students (all student authors) over 3 months, consuming approximately 1800 man-hours (650 hours on single-app tasks, 750 hours on workflow tasks and 400 hours for double-checking).
:::

我们在 Ubuntu 环境上创建了一个包含 369 个真实世界计算机任务的基准套件,任务收集自作者以及论坛、教程、指南等多种来源,以展示 OSWorld 中开放式任务创建的能力。每个样例都被精心标注:自然语言指令;一份设置配置(含对应文件与设置动作),基于我们提供的 VM 镜像初始化初始状态;以及一个手工制作的评估脚本,用于检查任务是否成功执行。我们还将 Ubuntu 任务集中的 43 个任务改编用于 Windows 上的分析。总体上,9 名计算机专业学生(均为学生作者)投入超过 3 个月,耗费约 1800 人时(单应用任务 650 小时、工作流任务 750 小时、复查 400 小时)。

::: en
Task instructions and scenarios To draw the most diverse and close-to-reality usage cases, we explore several types of resources, including official guidelines & tutorials, video pieces giving tips and tutorials on the Internet (e.g., TikTok and YouTube), how-to websites (e.g., WikiHow), Q&A forums (e.g., Reddit, Quora, Superuser, & StackOverflow), formal video courses (e.g., Coursera and Udemy), and publicly-available personal blogs & guidelines. The detailed resources used in our benchmark are listed in App. B.3. The examples are selected by judging their popularity, helpfulness, and diversity, revealed by the views and votes. Meanwhile, we notice that it is challenging to find enough examples on the internet for tasks that involve the collaboration of multiple software applications. Therefore, the authors conducted extensive brainstorming, combining some existing examples or drawing inspiration from daily-life scenarios, to compile the tasks. The instructions and task-related files are then crafted from these real-world guidelines and questions by the authors. After the selection, each example will be cross-checked by the other two authors on the feasibility, ambiguity, and alignment with the source. We not only collect tasks that can be finished, but also collect the infeasible ones that are inherently impossible to be completed due to deprecated features or hallucinated features raised by real users, which results in 30 infeasible examples in our benchmark. Additionally, to demonstrate the unification ability of OSWorld environment for the creation of open-ended computer tasks, we also integrate 84 examples from other benchmarks focusing on single-application or domain-specific environments such as NL2Bash [29], Mind2Web [9], SheetCopilot [25], PPTC [14], and GAIA [36]. Refer to App. B.4 for more details and B.8 for sampled examples for the showcase. A total of about 400 man-hours were spent to collect these examples.
:::

**任务指令与场景(Task instructions and scenarios)**:为汲取最多样、最贴近现实的使用案例,我们探索了几类资源:官方指南与教程;互联网上提供技巧与教程的短视频(如 TikTok 与 YouTube);how-to 网站(如 WikiHow);问答论坛(如 Reddit、Quora、Superuser 与 StackOverflow);正式视频课程(如 Coursera 与 Udemy);以及公开的个人博客与指南。基准所用的详细资源列于附录 B.3。样例通过浏览量与投票所反映的受欢迎度、实用性与多样性来筛选。同时我们注意到,在互联网上为"涉及多个软件应用协作"的任务找到足够示例颇具挑战。因此,作者进行了大量头脑风暴,组合一些现有示例、或从日常生活场景汲取灵感来汇编任务。指令与任务相关文件随后由作者从这些真实世界指南与问题中精心制作。选定之后,每个样例由另外两位作者就可行性、歧义性与对来源的忠实度进行交叉检查。我们不仅收集可以完成的任务,也收集不可行的任务——因功能弃用(deprecated features)或真实用户提出的幻觉功能(hallucinated features)而本质上无法完成的任务——这带来了基准中的 30 个不可行样例。此外,为展示 OSWorld 环境对创建开放式计算机任务的统一能力,我们还从聚焦单应用或领域专用环境的其他基准整合了 84 个样例,如 NL2Bash [29]、Mind2Web [9]、SheetCopilot [25]、PPTC [14] 与 GAIA [36]。更多细节见附录 B.4,样例展示见 B.8。收集这些样例总共花费约 400 人时。

::: en
Initial state setup configs To construct the initial state, we prepare the files required for the task and set up the initial state. For the files, we try to obtain them from the sources of the tasks we found, or, in cases where the files are not publicly available, we recreate them as realistically as possible based on scenarios. For the initial state setup, we also developed some functions based on the APIs of software and OS to control the opening and resizing of software windows and reimplement some functions that are difficult to achieve with APIs using pyautogui. For different tasks, we write configs to set the files and initial steps in the virtual machine and verify them in the environment. For example, the setup stage (highlighted in red color, keyed as "config") in Figure 2 involves downloading files into the virtual machine to prepare a close-to-reality initial environment, and then opening the file of interest with the corresponding application. The setup steps for each example take about 1 man-hours to construct.
:::

**初始状态设置配置(Initial state setup configs)**:为构建初始状态,我们准备任务所需的文件并设置初始状态。文件方面,我们尽量从所找到的任务来源获取;在文件不公开的情况下,我们依据场景尽可能逼真地重建。初始状态设置方面,我们还基于软件与操作系统的 API 开发了一些控制软件窗口打开与调整大小的函数,并用 pyautogui 重新实现了一些难以用 API 实现的函数。对不同任务,我们编写配置在虚拟机中设置文件与初始步骤,并在环境中验证。例如,图 2 中的设置阶段(红色高亮,键为 "config")涉及向虚拟机下载文件以准备贴近现实的初始环境,然后用相应应用打开目标文件。每个样例的设置步骤约需 1 人时来构建。

::: en
Execution-based evaluation For each task, we select the appropriate getter functions, evaluator function, and parameters to compose the configuration file. The getter function is used to extract key components (e.g., the modified file, the text contents displayed in a window element) from the final state of the environment, and the evaluator function assesses success based on the extracted key components. If a function does not exist, we will construct it and add it to the function library of the environment. After completing each evaluation, the annotator conducts initial tests with self-designed test cases. Then, in the human evaluation and experiment running phases, each example is further scrutinized and iterated upon by different individuals three times from the perspective of alignment with the instruction and correctness under different solutions. As a result, we implement nearly sample-specific executable evaluation scripts, resulting in a total of 134 unique evaluation functions for assessing functional correctness—significantly more than the previous benchmarks. The average time spent on developing the evaluation for an example and its examination amounts to approximately 2 man-hours from graduate students.
:::

**基于执行的评估(Execution-based evaluation)**:对每个任务,我们选择合适的 getter 函数、评估(evaluator)函数与参数来组成配置文件。getter 函数用于从环境最终状态中提取关键组件(如被修改的文件、某窗口元素中显示的文本内容),评估函数则基于提取出的关键组件判定成败。若某个函数不存在,我们就构建它并加入环境的函数库。每份评估完成后,标注者用自设计的测试用例做初步测试。随后,在人类评估与实验运行阶段,每个样例又从"与指令对齐"和"不同解法下的正确性"两个角度被不同的人复查并迭代三轮。最终,我们实现了接近逐例专属的可执行评估脚本,共 134 个用于评估功能正确性的独特评估函数——显著多于以往基准。每个样例的评估开发及其检查平均耗费研究生约 2 人时。

::: en
Quality control Once annotation is finished, each example is attempted by two authors who did not participate in annotating that specific example, acting as agents to complete the task. This process evaluates the current example's quality and provides feedback to the annotators (such as unclear instructions or inability to complete the task, crashes in corner cases, serious instances of false positives and negatives, etc.), and involves joint revisions and supplements. During experiments for human performance and baselines, we further fixed examples found to have issues, dedicating over 400 man-hours for four rounds of checks. Further investment of time and a more red teaming could further reduce false positives and negatives, which we will leave to future work.
:::

**质量控制(Quality control)**:标注完成后,每个样例由两位未参与该样例标注的作者充当智能体实际尝试完成任务。这一过程评估当前样例的质量并向标注者提供反馈(如指令不清或任务无法完成、边角情况(corner case)崩溃、严重的假阳性与假阴性等),并进行共同修订与补充。在人类性能与基线实验期间,我们进一步修复了被发现有问题的样例,四轮检查投入超过 400 人时。投入更多时间与更多红队测试(red teaming)可以进一步减少假阳/假阴,我们将其留作未来工作。

#### 3.3 数据统计(Data Statistics)

表 3:OSWorld 关键统计(Table 3: Key statistics in OSWorld. The "Supp. tasks" refers to the Windows-based tasks, that could only be used after activation due to copyright restrictions.):

| 统计项 | 数量 |
| --- | --- |
| 任务总数(Ubuntu) | 369(100%) |
| — 多应用工作流(Multi-App Workflow) | 101(27.4%) |
| — 单应用(Single-App) | 268(72.6%) |
| — 整合自其他基准(Integrated) | 84(22.8%) |
| — 不可行任务(Infeasible) | 30(8.1%) |
| 补充任务(Windows,Supp. tasks) | 43 |
| 初始状态(Initial States) | 302 |
| 评估脚本(Eval. Scripts) | 134 |

[图 3: Figure 3: Distribution of task instructions in OSWorld based on the app domains and operation types to showcase the content intuitively.]

中文说明:图 3 按应用域(app domains)与操作类型(operation types)直观展示 OSWorld 任务指令的分布。按应用域聚类的占比为:Office 31.7%、Workflow 27.4%、Daily 21.1%、Professional 13.3%、OS 6.5%(合计 100%)。图中还按操作类型细分标注了各子类占比(数值转写自原图):Files 2.2%、Settings 2.4%、Terminal 1.9%、Visualization 1.9%、Processing 7.0%、Tab. formatting 3.8%、Slide settings 4.1%、Slide editing 8.7%、Doc. settings 1.6%、Doc. editing 4.6%、Image ops 7.0%、Configuration 3.8%、Code assist 2.4%、File ops 8.1%、Multimedia 4.6%、Data analysis 8.9%、Misc. 5.7%、Settings 5.7%、Info query 4.1%、Shopping 2.7%、Account ops 1.6%、Email ops 2.4%、Video control 4.6%、OS 6.5%。

::: en
Statistics To facilitate the analysis and comprehension of the agent's capabilities, we cluster the examples into the software categories. Specifically, these categories include OS, Office (LibreOffice Calc, Impress, Writer), Daily (Chrome, VLC Player, Thunderbird), Professional (VS Code and GIMP), and Workflow (tasks involving multiple apps). The main statistics of OSWorld are presented in Tab. 3 and Fig. 3, showcasing the outline and a broad spectrum of tasks. Specifically, OSWorld contains a total of 369 tasks (and an additional 43 tasks on Windows for analysis), with the majority (268 tasks or 72.6%) aiming at single application functionalities and a remarkable section of workflow-related tasks (101 tasks or 27.4%). The dataset's diversity is further affirmed by the inclusion of tasks considered infeasible, totaling 30 tasks or 8.1% of the dataset. Additionally, a total of 84 tasks (22.8%) are integrated from related datasets, highlighting the dataset's applicability in universal modeling. Remarkably, the dataset incorporates 302 distinct initial states and 134 different evaluation scripts, underscoring the comprehensive approach towards evaluating the tasks' complexity and requirements. More statistic details are available in App. B.4.
:::

**统计(Statistics)**:为便于分析与理解智能体能力,我们将样例按软件类别聚类。具体类别包括:OS;Office(LibreOffice Calc、Impress、Writer);Daily(Chrome、VLC Player、Thunderbird);Professional(VS Code 与 GIMP);以及 Workflow(涉及多应用的任务)。OSWorld 的主要统计见表 3 与图 3,展示了任务的整体轮廓与广泛谱系。具体而言,OSWorld 共 369 个任务(另有 43 个 Windows 任务用于分析),其中大部分(268 个,即 72.6%)面向单一应用功能,还有数量可观的工作流相关任务(101 个,即 27.4%)。数据集的多样性进一步体现在包含被视为不可行的任务,共 30 个、占数据集的 8.1%。此外,共 84 个任务(22.8%)整合自相关数据集,凸显了数据集在通用建模上的适用性。值得注意的是,数据集纳入了 302 个不同的初始状态与 134 个不同的评估脚本,凸显了对任务复杂性与需求的全面评估方式。更多统计细节见附录 B.4。

表 4:不同数字智能体评测环境的对比(Table 4: Comparison of different environments for benchmarking digital agents.)——各列含义:任务实例数与模板数(如适用,任务由模板经配置实例化而来)(# Instances (# Templates));是否提供可控可执行环境(Control. Exec. Env.);在开放域中添加涉及任意应用新任务的容易程度(Environment Scalability);是否支持多模态智能体评估(Multimodal Support);是否支持并包含跨应用任务(Cross-App);能否从中间初始状态启动任务(Intermediate Init. State);基于执行的评估函数数量(# Exec.-based Eval. Func.):

| 基准 | # 实例(# 模板) | 可控可执行环境? | 环境可扩展性? | 多模态支持? | 跨应用? | 中间初始状态? | # 基于执行的评估函数 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GAIA [36] | 466 | ✗ | - | ✗ | ✗ | ✗ | 0 |
| MIND2WEB [9] | 2350 | ✗ | - | ✓ | ✗ | ✓ | 0 |
| WEBLINX [33] | 2337 | ✗ | - | ✓ | ✗ | ✓ | 0 |
| PIXEL HELP [27] | 187 | ✗ | - | ✓ | ✗ | ✗ | 0 |
| METAGUI [47] | 1125 | ✗ | - | ✓ | ✗ | ✗ | 0 |
| AITW [40] | 30k | ✗ | - | ✓ | ✗ | ✓ | 0 |
| OMNI ACT [21] | 9802 | ✗ | - | ✓ | ✗ | ✓ | 0 |
| AGENT BENCH [32] | 1091 | 多环境隔离(Multi-isolated) | ✗ | ✗ | ✗ | ✗ | 7 |
| INTER CODE [57] | 1350(3) | Code | ✗ | ✗ | ✗ | ✗ | 3 |
| MINI WOB++ [30] | 125 | Web | ✗ | ✓ | ✗ | ✗ | 125 |
| WEBSHOP [58] | 12k(1) | Web | ✗ | ✓ | ✗ | ✗ | 1 |
| WEBARENA [66] | 812(241) | Web | ✗ | ✓ | ✗ | ✗ | 5 |
| VISUALWEBARENA [22] | 910(314) | Web | ✗ | ✓ | ✗ | ✗ | 6 |
| WORK ARENA [10] | 23k(29) | Web | ✗ | ✓ | ✗ | ✓ | 7 |
| WIKI HOW [61] | 150(16) | Mobile | ✗ | ✓ | ✗ | ✗ | 16 |
| ASSIST GUI [13] | 100 | ✗ | ✗ | ✓ | ✗ | ✓ | 2 |
| OSWORLD(本文) | 369 | Computer | ✓ | ✓ | ✓ | ✓ | 134 |

(注:PDF 提取文本中 OSWorld 行缺失一列数值;据论文正文"构造中间初始状态作为任务设置"的描述,该行"中间初始状态"应为 ✓,此处据此补齐。)

::: en
Comparison with existing benchmarks OSWorld is compared with a number of existing benchmarks in Table 4. OSWorld utilizes raw mouse and keyboard actions that is universal to the computer environment, rather than focusing on specific computer applications (e.g., a browser [66, 9]), with multimodal observation including screenshot (Multimodal Support column). This universal action space enables the constructed agents to handle general tasks in the digital world. Our executable environment allows agents to freely explore during both the learning and evaluation phases, rather than providing only static demonstrations to evaluate an agent's prediction of the next step (Executable Env. column). Moreover, it does not solely focus on interactions within a single app but also considers interactions across multiple apps and the overall task (Cross-App column). Unlike many evaluations that offer the same evaluation script or a few scripts for a certain type of task, the OSWorld benchmark provides example-wise, execution-based evaluation for tasks. Specifically, the total of 134 unique execution-based evaluation functions in our benchmark is significantly more than previous work, demonstrating the complexity, diversity, and evaluation challenges of tasks in our benchmark (# Exec.-based Eval. Func. column). It also allow us to freely choose open-ended tasks and scale to new environments, rather than struggling in crafting new ones. Constructing intermediate initial states as task setup increases realism and poses challenges to the agents' exploration capabilities (Intermediate Init. State column).
:::

**与既有基准的比较(Comparison with existing benchmarks)**:表 4 将 OSWorld 与若干既有基准进行比较。OSWorld 采用对计算机环境通用的原始鼠标键盘动作,而非聚焦于特定计算机应用(如浏览器 [66, 9]),并采用包括截图在内的多模态观察(多模态支持列)。这一通用动作空间使构建出的智能体能够处理数字世界中的一般任务。我们的可执行环境允许智能体在学习与评估两个阶段自由探索,而不是只提供静态演示来评估智能体对下一步动作的预测(可执行环境列)。此外,它不只关注单一应用内的交互,还考虑跨多个应用以及整体任务的交互(跨应用列)。与许多"对某一类任务只提供同一份或少数几份评估脚本"的评估不同,OSWorld 基准为任务提供逐例的、基于执行的评估。具体来说,我们基准中 134 个独特的基于执行的评估函数显著多于以往工作,展示了本基准任务的复杂性、多样性与评估挑战(基于执行的评估函数数列)。它还允许我们自由选择开放式任务并扩展到新环境,而不必艰难地新造环境。构造中间初始状态作为任务设置提升了真实性,并对智能体的探索能力提出挑战(中间初始状态列)。

#### 3.4 人类性能(Human Performance)

::: en
We conduct human evaluations on each example in our dataset, with annotators being computer science major college students who possess basic software usage skills but have not been exposed to the samples or software before. We recorded the time required to complete each example and whether their completion of the example was correct. For comparison, we also sampled 100 examples from WebArena [66] under the same evaluation setup. As illustrated, tasks from our dataset generally required more time to complete, with a median completion time of 111.94 seconds (compared to 35.38 seconds in WebArena), and a significant number of examples distributed at 900 seconds or even more. In terms of accuracy, the human performance on our tasks was approximately 72.36%, significantly lower than the 88% observed on the pure web task dataset. These findings highlight the complexity and challenge of tasks in our dataset, which demand more time and effort. The lower accuracy rate further indicates that our tasks require a higher level of understanding and proficiency, underscoring the need for advanced models and techniques to tackle them effectively.
:::

我们对数据集中的每个样例进行了人类评估,标注者为具备基础软件使用技能、但此前未接触过这些样例或软件的计算机专业大学生。我们记录了完成每个样例所需的时间,以及他们的完成是否正确。作为对比,我们还在相同评估设置下从 WebArena [66] 抽取了 100 个样例。如图所示,我们数据集的任务通常需要更多时间来完成,完成时间中位数为 111.94 秒(WebArena 为 35.38 秒),且有相当数量的样例分布在 900 秒甚至更久。准确率方面,人类在我们任务上的性能约为 72.36%,显著低于在纯网页任务数据集上观察到的 88%。这些发现凸显了我们数据集中任务的复杂性与挑战性——它们需要更多时间与精力。更低的准确率进一步表明,我们的任务需要更高层次的理解与熟练度,凸显了需要先进的模型与技术才能有效应对。

[图 4: Figure 4: Human operation time and accuracy on OSWorld and WebArena.]

中文说明:图 4 对比人类在 OSWorld 与 WebArena 上的操作时长与准确率。左图为完成时间分布(横轴为人类操作时长,0–900 秒):OSWorld(We ours)的中位数为 111.94 秒,WebArena 的中位数为 35.38 秒,且 OSWorld 有大量样例的完成时间达到 900 秒甚至更久;右图为准确率(纵轴 30–90%):WebArena 约 88%,OSWorld 约 72.36%。

### 4 基线评测:LLM 与 VLM 智能体(Benchmarking LLM and VLM Agent Baselines)

::: en
In this section, we present the implementation details and experimental settings for several state-of-the-art LLM and VLM agent baselines on OSWorld benchmark, as well as their performance.
:::

本节介绍若干最先进 LLM 与 VLM 智能体基线在 OSWorld 基准上的实现细节与实验设置,以及它们的性能。

#### 4.1 LLM 与 VLM 智能体基线(LLM and VLM Agent Baselines)

::: en
We adopt state-of-the-art LLM and VLM from open-source representatives such as Mixtral [19], CogAgent [17] and Llama-3 [35], and closed-source ones from GPT, Gemini, Claude and Qwen families on OSWorld, to serve as the foundation of agent. We also explore methods such as the Set-of-Marks aided approach [56, 11], which has been demonstrated to improve spatial capabilities for visual reasoning. Our prior experiments following VisualWebArena [22] adopt few-shot prompting, which involves using (observation, action) pairs as few-shot examples and inputting the current observation to generate the action, but this resulted in poor performance (success rate of 2.79% under pure-screenshot setting). We attribute the result to a lack of history encoding and change in the prompting scheme. Therefore, in the experiments, we opt to utilize the context window by providing the most recent 3 observations and actions in chat mode, i.e., alternating between "user" prompts and "assistant" prompts, instead of the (observation, action) pairs. We use a temperature of 1.0 and top-p of 0.9 and truncate from the beginning of the input if still exceeding the max tokens limit required by the models. The prompts used in the experiments are provided in App. C.1. We heuristically request the agents to complete the tasks within a max step limit of 15, which is enough for most tasks. We present a summary of the results in Tab. 5 and analysis in Sec. 4.2. We implement the following four types of input settings on LLM and VLM.
:::

我们采用来自开源社区的代表模型——如 Mixtral [19]、CogAgent [17] 与 Llama-3 [35]——以及 GPT、Gemini、Claude 与 Qwen 家族的闭源模型作为 OSWorld 上的最先进 LLM 与 VLM,充当智能体的基座。我们还探索了 Set-of-Marks 辅助方法 [56, 11] 等技术,它已被证明能提升视觉推理的空间能力。我们先前遵循 VisualWebArena [22] 的实验采用 few-shot 提示(few-shot prompting)——用(观察, 动作)对作为 few-shot 示例、输入当前观察来生成动作——但效果很差(纯截图设置下成功率仅 2.79%)。我们把这一结果归因于历史编码的缺失与提示方案的差异。因此,实验中我们选择利用上下文窗口,以聊天模式提供最近 3 轮观察与动作,即 "user" 提示与 "assistant" 提示交替,而非(观察, 动作)对。我们使用温度 1.0、top-p 0.9,若仍超过模型所需的最大 token 限制则从输入开头截断。实验所用提示见附录 C.1。我们启发式地要求智能体在最大步数限制 15 步内完成任务,这对大多数任务足够。我们在表 5 中汇总结果,在 §4.2 中给出分析。我们在 LLM 与 VLM 上实现了以下四种输入设置。

::: en
Accessibility tree We aim to evaluate whether the current advanced text-based language models can reason and ground themselves in the context to generate the correct action. Since the original XML format of accessibility tree contains millions of tokens, caused by countless elements, redundant attributes, and a mass of markups, we opt to filter out non-essential elements and attributes, and represent the elements in a more compact tab-separated table format. To be specific, we filter the elements by their tag, visibility, availability, existence of text or image contents, etc. The detailed filtering method is elaborated on in App. C.3. Only the tag, name, text, position, and size of the remaining elements are kept and concatenated by tab character in the input. As the raw coordinates are provided within the accessibility tree, the LLM is required to ground its action predictions to accurate coordinates.
:::

**无障碍树(Accessibility tree)**:我们旨在评估当前先进的文本语言模型能否在上下文中推理并定位自身,以生成正确的动作。由于无障碍树的原始 XML 格式包含数百万 token——由无数元素、冗余属性与大量标记造成——我们选择过滤掉非必要的元素与属性,并以更紧凑的制表符分隔表格格式表示元素。具体来说,我们按元素的标签、可见性、可用性、是否存在文本或图像内容等对元素进行过滤,详细过滤方法见附录 C.3。输入中只保留剩余元素的标签、名称、文本、位置与大小,并以制表符连接。由于无障碍树内提供了原始坐标,LLM 需要将其动作预测定位(ground)到准确的坐标上。

::: en
Screenshot This is the input format that is closest to what humans perceive. Without special processing, the raw screenshot of the virtual machine is directly sent to the VLM. The VLM is to understand the screenshot and predict correct actions with precise coordinates. The raw resolution of the screen is set to 1920×1080. In order to investigate the impact of input resolution, ablation studies are also conducted with different resolutions by manually downsampling the screenshot.
:::

**截图(Screenshot)**:这是最接近人类感知的输入格式。无需特殊处理,虚拟机的原始截图直接发送给 VLM。VLM 要理解截图并预测带精确坐标的正确动作。屏幕的原始分辨率设为 1920×1080。为研究输入分辨率的影响,我们还通过人工降采样截图,做了不同分辨率下的消融研究(ablation studies)。

::: en
Screenshot + accessibility tree To check if a combination with the accessibility tree can improve the capacity of VLM for spatial grounding, we take this setting by inputting both raw screenshots and a simplified accessibility tree.
:::

**截图 + 无障碍树(Screenshot + accessibility tree)**:为检验与无障碍树的组合能否提升 VLM 的空间定位(spatial grounding)能力,我们采用此设置,同时输入原始截图与简化后的无障碍树。

::: en
Set-of-Marks Set-of-Marks (SoM) [56] is an effective method for enhancing the grounding capabilities of VLMs such as GPT-4V, by segmenting the input image into different sections and marking them with annotations like alphanumerics, masks, or boxes. We leverage the information from the filtered accessibility tree and mark the elements on the screenshot with a numbered bounding box. Following VisualWebArena [22] and UFO [59], we further combine the annotated screenshot with the text metadata from accessibility tree, including the index, tag, name, and text of the elements 5. Instead of predicting precise coordinates, the VLM is supposed to specify the action object by its number index, which will be mapped into our action space by post-processing. Ablation studies are also conducted with different resolutions for SoM setting.
:::

**Set-of-Mark(Set-of-Marks, SoM)**:SoM [56] 是一种增强 GPT-4V 等 VLM 定位能力的有效方法,通过把输入图像分割成不同区块,并以字母数字、掩码或方框等标注加以标记。我们利用过滤后无障碍树的信息,把元素以带编号的边界框标注在截图上。遵循 VisualWebArena [22] 与 UFO [59],我们进一步把标注后的截图与来自无障碍树的文本元数据结合,包括元素的索引、标签、名称与文本(脚注 5:该元数据与单用 a11y 树设置所提供的相似但略有不同——具体来说,坐标与大小被替换为元素索引)。VLM 不再预测精确坐标,而是通过编号索引指定动作对象,再由后处理映射到我们的动作空间。SoM 设置下也做了不同分辨率的消融研究。

表 5:基线 LLM 与 VLM 智能体在 OSWorld 上的成功率,按任务类别分组(Table 5: Success rates of baseline LLM and VLM agents on OSWorld, grouped by task categories: OS, Office (LibreOffice Calc, Impress, Writer), Daily (Chrome, VLC Player, Thunderbird), Professional (VS Code and GIMP) and Workflow (tasks involving multiple apps), for gaining insights from interfaces and operation logic. See App. C.1 and C.5 for more details.):

| 输入 | 模型 | OS | Office | Daily | Profess. | Workflow | Overall |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A11y tree | Mixtral-8x7B | 12.50% | 1.01% | 4.79% | 6.12% | 0.09% | 2.98% |
| | Llama-3-70B | 4.17% | 1.87% | 2.71% | 0.00% | 0.93% | 1.61% |
| | GPT-3.5 | 4.17% | 4.43% | 2.71% | 0.00% | 1.62% | 2.69% |
| | GPT-4 | 20.83% | 3.58% | 25.64% | 26.53% | 2.97% | 12.24% |
| | Gemini-Pro | 4.17% | 1.71% | 3.99% | 4.08% | 0.63% | 2.37% |
| | Gemini-Pro-1.5 | 12.50% | 2.56% | 7.83% | 4.08% | 3.60% | 4.81% |
| | Qwen-Max | 29.17% | 3.58% | 8.36% | 10.20% | 2.61% | 6.87% |
| | GPT-4o | 20.83% | 6.99% | 16.81% | 16.33% | 7.56% | 11.36% |
| Screenshot | CogAgent | 4.17% | 0.85% | 2.71% | 0.00% | 0.00% | 1.11% |
| | GPT-4V | 12.50% | 1.86% | 7.58% | 4.08% | 6.04% | 5.26% |
| | Gemini-ProV | 8.33% | 3.58% | 6.55% | 16.33% | 2.08% | 5.80% |
| | Gemini-Pro-1.5 | 12.50% | 6.99% | 2.71% | 6.12% | 3.60% | 5.40% |
| | Claude-3-Opus | 4.17% | 1.87% | 2.71% | 2.04% | 2.61% | 2.42% |
| | GPT-4o | 8.33% | 3.58% | 6.07% | 4.08% | 5.58% | 5.03% |
| Screenshot + A11y tree | CogAgent | 4.17% | 0.85% | 2.71% | 0.62% | 0.09% | 1.32% |
| | GPT-4V | 16.66% | 6.99% | 24.50% | 18.37% | 4.64% | 12.17% |
| | Gemini-ProV | 4.17% | 4.43% | 6.55% | 0.00% | 1.52% | 3.48% |
| | Gemini-Pro-1.5 | 12.50% | 3.58% | 7.83% | 8.16% | 1.52% | 5.10% |
| | Claude-3-Opus | 12.50% | 3.57% | 5.27% | 8.16% | 1.00% | 4.41% |
| | GPT-4o | 41.67% | 6.16% | 12.33% | 14.29% | 7.46% | 11.21% |
| Set-of-Mark | CogAgent | 4.17% | 0.00% | 2.71% | 0.00% | 0.53% | 0.99% |
| | GPT-4V | 8.33% | 8.55% | 22.84% | 14.28% | 6.57% | 11.77% |
| | Gemini-ProV | 4.17% | 1.01% | 1.42% | 0.00% | 0.63% | 1.06% |
| | Gemini-Pro-1.5 | 16.67% | 5.13% | 12.96% | 10.20% | 3.60% | 7.79% |
| | Claude-3-Opus | 12.50% | 2.72% | 14.24% | 6.12% | 4.49% | 6.72% |
| | GPT-4o | 20.83% | 3.58% | 3.99% | 2.04% | 3.60% | 4.59% |
| Human Performance(人类性能) | | 75.00% | 71.79% | 70.51% | 73.47% | 73.27% | 72.36% |

#### 4.2 结果(Results)

::: en
LLMs and VLMs are still far from being digital agents on real computers. The results from Table 5 show that when only using screenshots as input and adopting pyautogui as the code space, the success rate of the model is only 5.26% to 5.80% even with the strongest VLMs GPT-4V and Gemini-Pro-vision. Meanwhile, the most advanced batch of language models, when using the a11y tree as input, has a success rate ranging from 2.37% to 12.24%. Overall, these figures of performance are significantly lower than the human-level performance which is 72.36% overall for individuals not familiar with the software. These gaps indicate that current LLMs and VLMs may still have a significant gap from humans in performance, necessitating further research in this area. Another surprising finding is that although Claude-3 Opus is reported to be competitive with GPT-4V on common benchmarks [2], it falls far behind when used as a digital agent in OSWorld. We will present a qualitative analysis and infer reasons in Sec. 5.4.
:::

**LLM 与 VLM 距离成为真实计算机上的数字智能体还很远。**表 5 的结果显示:当只用截图作为输入、采用 pyautogui 作为代码空间时,即便是最强的 VLM——GPT-4V 与 Gemini-Pro-Vision——模型成功率也仅为 5.26% 到 5.80%。同时,最先进的一批语言模型用 a11y 树作为输入时,成功率在 2.37% 到 12.24% 之间。总体而言,这些性能数字显著低于人类水平——不熟悉这些软件的人整体可达 72.36%。这些差距表明,当前 LLM 与 VLM 在性能上可能与人类仍有显著差距,需要该领域的进一步研究。另一个意外发现是:尽管 Claude-3 Opus 据报道在常见基准上与 GPT-4V 相当 [2],在 OSWorld 上作为数字智能体使用时却远远落后。我们将在 §5.4 给出定性分析并推断原因。

::: en
Agent performance has much higher variance than human across different types of computer tasks. OSWorld is capable of simulating and evaluating the various software types and combination scenarios involved in people's daily lives in an open-ended manner. We observe performance based on software type grouping and find that agents based on LLMs show significant differences across different subsets. As shown in Table 5, performance tends to be better in tasks oriented towards CLI interfaces (such as OS-type tasks) compared to those based on GUI (such as Office tasks involving clicks on spreadsheet interfaces and document processing). Moreover, the biases between different models and settings are inconsistent, with gaps even exceeding 20%; another point is that performance on workflow-type tasks involving multiple software is far below the figures on a single software, generally below 5%. However, human performance is consistent across these tasks, fluctuating around 70% without exceeding a 5% variance, forming a significant contrast with the models. This suggests that the way humans understand and complete tasks may differ significantly from the current logic and methods based on LLMs and VLMs.
:::

**智能体性能在不同类型计算机任务上的方差远高于人类。**OSWorld 能够以开放式方式模拟并评估人们日常生活中涉及的各种软件类型与组合场景。我们按软件类型分组观察性能,发现基于 LLM 的智能体在不同子集上差异显著。如表 5 所示,面向 CLI 接口的任务(如 OS 类任务)性能往往好于基于 GUI 的任务(如涉及表格界面点击与文档处理的 Office 任务)。此外,不同模型与设置之间的偏好并不一致,差距甚至超过 20%;另一点是,涉及多个软件的工作流类任务的表现远低于单一软件上的数字,普遍低于 5%。而人类性能在这些任务上保持一致,在 70% 上下波动、方差不超过 5%,与模型形成鲜明对比。这暗示人类理解与完成任务的方式,可能与当前基于 LLM 与 VLM 的逻辑和方法存在显著差异。

::: en
A11y tree and SoM's effectiveness varies by models. The a11y tree contains some attribute information of visible elements, including window position and size, as well as some semantic labels of the window. The performance gap illustrated in Table 5 between GPT-4V and Claude-3 with additional a11y tree information and under a pure screenshot setup suggests that it still has significant room for improvement in accurately perceiving and reasoning GUI elements. Conclusions are reversed for Gemini-Pro. While applying SoM setting, there is a decline for GPT-4V in performance compared to directly providing the model with screenshots and a11y tree inputs, which contradicts the widely shown effectiveness of SoM in classic image understanding tasks [56], as well as in application areas like web agents [65, 16]. We speculate that this is due to the tasks performed within operating systems having higher resolution and much more elements, (e.g., the cells in a spread table), leading to a significant amount of noise that counteracts the auxiliary role of bounding boxes. Some tasks also require detailed operation on coordinate-level, which cannot be modeled by the bounding box that SoM marks.
:::

**a11y 树与 SoM 的有效性因模型而异。**a11y 树包含可见元素的一些属性信息,包括窗口位置与大小,以及窗口的一些语义标签。表 5 所示的、GPT-4V 与 Claude-3 在"附加 a11y 树信息"与"纯截图设置"之间的性能差距表明,其在精确感知与推理 GUI 元素方面仍有很大的改进空间。对 Gemini-Pro 则结论相反。在应用 SoM 设置时,GPT-4V 的性能相比"直接提供截图与 a11y 树输入"出现下降,这与 SoM 在经典图像理解任务 [56] 以及网页智能体等应用领域 [65, 16] 中被广泛证明的有效性相悖。我们推测,这是因为操作系统内执行的任务分辨率更高、元素也多得多(如表格中的单元格),导致大量噪声抵消了边界框的辅助作用。一些任务还需要坐标级别的精细操作,这无法被 SoM 标注的边界框所建模。

::: en
VLM agents with screenshot-only setting show lower performance, but it should be the ultimate configuration in the long run. The setting that relies solely on screenshots exhibits the lowest performance, at only 5.26%, among all. Surprisingly, it still achieves a decent outcome when managing workflow tasks (involving multiple applications) that involve multiple applications. Despite the performance, it is worth mentioning that this is the only configuration that does not require additional information, such as an accessibility (a11y) tree, making it concise and in alignment with intuitive human perception since the a11y tree may not be well-supported across all software or cannot be obtained under noisy conditions (e.g., when the agent is restricted to viewing the computer through peripheral screens), and the massive amount of tokens contained in the a11y tree (even just the leaf nodes can have tens of thousands of tokens) can also impose an additional inference burden on the model. Future work on purely vision-based agents could lead to stronger generalization capabilities and, ultimately, the potential for integration with the physical world on a larger scale.
:::

**纯截图设置的 VLM 智能体性能较低,但长期来看应是终极配置。**仅依赖截图的设置在所有配置中表现最低,只有 5.26%。令人惊讶的是,在处理涉及多个应用的工作流任务时,它仍然取得了不错的结果。抛开性能不谈,值得一提的是,这是唯一不需要诸如无障碍(a11y)树等额外信息的配置,使其简洁且与人类的直观感知一致——因为 a11y 树并非在所有软件上都得到良好支持,或在噪声条件下无法获得(例如当智能体被限制只能通过外围屏幕"观看"电脑时),而且 a11y 树所包含的海量 token(即使只有叶子节点也可能有数万 token)还会给模型带来额外的推理负担。未来在纯视觉智能体上的工作有望带来更强的泛化能力,并最终带来在更大范围内与物理世界整合的潜力。

### 5 分析(Analysis)

::: en
In this section, we aim to delve into the factors influencing the performance of VLMs in digital agent tasks and their underlying behavioral logic. We will investigate the impact of task attributes (such as difficulty, feasibility, visual requirement, and GUI complexity), input measurements (such as screenshot resolution, the influence of trajectory history, and the effect of UI layout), explore whether there are patterns in the agent's performance across different operating systems, and make a qualitative analysis in the aspect of models, methods, and humans. All experiments, unless specifically mentioned otherwise, are conducted using GPT-4V under the Set-of-Mark setting. Some takeaways from the analysis are: 1) higher screenshot resolution typically leads to improved performance; 2) encoding more a11y (text) trajectory history can boost performance, while not working for screenshots (image); 3) current VLMs are not adept at image-based trajectory history context; 4) current VLM agents are not robust to UI layout and noise; 5) the performance of VLM agents across OS is in strong correlation; 6) VLM agents have common error types like mouse-clicking inaccuracies, limited domain knowledge, and more types discussed in Sec. 5.4.
:::

本节旨在深入探究影响 VLM 在数字智能体任务中性能的因素及其底层行为逻辑。我们将考察任务属性(如难度、可行性、视觉需求与 GUI 复杂性)的影响、输入度量(如截图分辨率、轨迹历史的影响、UI 布局的影响),探索智能体在不同操作系统上的表现是否存在规律,并从模型、方法与人类的角度做定性分析。除特别说明外,所有实验均使用 Set-of-Mark 设置下的 GPT-4V。分析的部分要点是:1) 更高的截图分辨率通常带来性能提升;2) 编码更多 a11y(文本)轨迹历史可以提升性能,但对截图(图像)无效;3) 当前 VLM 并不擅长利用图像形式的轨迹历史上下文;4) 当前 VLM 智能体对 UI 布局与噪声不鲁棒;5) VLM 智能体跨操作系统的性能强相关;6) VLM 智能体存在常见的错误类型,如鼠标点击不准、领域知识有限等,更多类型在 §5.4 讨论。

#### 5.1 按任务难度、可行性与涉及应用数划分的性能(Performance by Task Difficulty, Feasibility and App Involved)

::: en
We analyze the success rate across several additional subsets of tasks, as summarized in Tab. 6 and will be discussed in the following sections.
:::

我们分析了若干额外任务子集上的成功率,汇总于表 6,并在以下小节讨论。

表 6:GPT-4V(SoM)在不同类型任务上的成功率(Table 6: Success rate (SR) of GPT-4V (SoM) across different types of tasks.):

| 任务子集 | 占总量比例 | 成功率(↑) |
| --- | --- | --- |
| Easy(易) | 28.72% | 16.78% |
| Medium(中) | 40.11% | 13.12% |
| Hard(难) | 30.17% | 4.59% |
| Infeasible(不可行) | 8.13% | 16.67% |
| Feasible(可行) | 91.87% | 13.34% |
| Single-App(单应用) | 72.63% | 13.74% |
| Multi-App Workflow(多应用工作流) | 27.37% | 6.57% |

::: en
Task difficulty We categorize the tasks based on the time required for human completion into three groups: 0∼60s (Easy), 60s∼180s (Medium), and greater than 180 seconds (Hard), as an indicator of difficulty. Across these groups, the model's success rate drops as the required time increases, with tasks taking longer than 180 seconds becoming almost impossible to complete (considering we have infeasible examples for agent's luckiness), whereas human performance across these three groups is 84.91%, 81.08% and 49.57%, showing a slight decline of the same trend but not to the extent of being unachievable.
:::

**任务难度(Task difficulty)**:我们按人类完成所需时间把任务分为三组:0~60 秒(Easy)、60~180 秒(Medium)与大于 180 秒(Hard),作为难度指标。在这些分组中,模型成功率随所需时间增加而下降,耗时超过 180 秒的任务几乎无法完成(考虑到我们还备有不可行样例供智能体"碰运气"),而人类在这三组上的性能分别是 84.91%、81.08% 与 49.57%,呈相同趋势的轻微下降,但不至于无法完成。

::: en
Feasibility We also divide tasks into groups of tasks infeasible (e.g., deprecated features or hallucinated features) and tasks feasible, which requires the agents to have the ability to judge based on their own knowledge and exploration results. As shown in Tab. 6, we observe that agents currently perform slightly better in terms of infeasibility (16.67% to 13.34%), but overall, they are at a relatively low level. It is noteworthy that we also observe in some methods and settings (such as under the pure screenshot setting with the Gemini-Pro model), agents tend to easily output FAIL and refuse to continue trying. This situation leads to some false positives in infeasible tasks. The focus needs to be on improving overall performance.
:::

**可行性(Feasibility)**:我们还将任务分为不可行(如功能弃用或幻觉功能)与可行两组,这要求智能体有能力基于自身知识与探索结果做出判断。如表 6 所示,我们观察到智能体目前在不可行任务上表现稍好(16.67% 对 13.34%),但整体仍处于较低水平。值得注意的是,我们还观察到在某些方法与设置下(如纯截图设置下的 Gemini-Pro 模型),智能体倾向轻易输出 FAIL、拒绝继续尝试。这种情况在不可行任务上造成了一些假阳性。重点应放在提升整体性能上。

::: en
Number of apps involved We also examined the performance based on whether the task involved apps software or within a single app. As shown in Tab. 6, the average performance for tasks involving a single app is low, at 13.74%, but still more than double the 6.57% observed for subsets of tasks involving workflows across multiple apps. Within single-app scenarios, tasks involving GUI-intensive Office apps generally performed the worst, with subsets such as LibreOffice Calc often scoring zero (we show more detailed results in App. C.5). These findings highlight the need for improved collaboration capabilities between software and enhanced proficiency in specific scenarios.
:::

**涉及应用数(Number of apps involved)**:我们还依据任务涉及多个应用软件还是单一应用考察了性能。如表 6 所示,单应用任务的平均性能较低,为 13.74%,但仍是对"跨多应用工作流"任务子集观察到的 6.57% 的两倍以上。在单应用场景中,涉及 GUI 密集型 Office 应用的任务总体表现最差,LibreOffice Calc 等子集经常得 0 分(更详细的结果见附录 C.5)。这些发现凸显了改进软件间协作能力与提升特定场景熟练度的必要性。

#### 5.2 多模态观察差异下的性能(Performance by Multimodal Observation Variances)

::: en
Higher screenshot resolution typically leads to improved performance Despite the significant progress in display technology (1080P, 2K, and 4K), most VLMs are still trained on data far below these resolutions. We select the screenshot-only input and SoM setting to test the method's performance under different screen input down-sampling ratios (i.e., 0.2, 0.4, 0.6 and 0.8 of the original resolution), to evaluate the impact of resolution changes on model recognition ability and accuracy. The output coordinates of the model for the screenshot setting are still expected to align with the original resolution (i.e., 1080P). The effects of varying input resolutions on performance are shown in Figure 5. For inputs based on pure screenshots, it is observed that an increase in resolution directly correlates with enhanced performance. This issue may arise from the discrepancy between the resolution of the screenshot and the coordinates of the output. However, the scenario slightly differs on SoM. Interestingly, a reduction in resolution to 768×432 (down-sampling ratio of 0.4) leads to an improvement in the agent's performance and further diminishing the resolution even more to a down-sampling ratio of 0.2 results in a noticeable decline in performance.
:::

**更高的截图分辨率通常带来性能提升。**尽管显示技术已显著进步(1080P、2K 与 4K),大多数 VLM 的训练数据分辨率仍远低于这些水平。我们选择纯截图输入与 SoM 设置,测试方法在不同屏幕输入降采样比例(即原始分辨率的 0.2、0.4、0.6 与 0.8 倍)下的性能,以评估分辨率变化对模型识别能力与精度的影响。截图设置下,模型输出的坐标仍期望与原始分辨率(即 1080P)对齐。不同输入分辨率对性能的影响见图 5。对于基于纯截图的输入,观察到分辨率的提高与性能提升直接相关。这一问题可能源于截图分辨率与输出坐标之间的不一致。但 SoM 上的情形略有不同:有趣的是,把分辨率降到 768×432(降采样比 0.4)反而提升了智能体的性能,而进一步把分辨率降到降采样比 0.2 则导致性能明显下降。

[图 5: Figure 5: The effect of downsampling on the screenshot on performance with down-sampling ratios of 0.2, 0.4, 0.6 and 0.8 and run on a subset (10%) of examples.]

中文说明:图 5 在 10% 样例子集上考察截图降采样对性能的影响,横轴为降采样比例(0.2、0.4、0.6、0.8、1.0),纵轴为成功率(%),比较 GPT-4V 在 SoM 与纯截图(Screenshot)两种设置下的曲线:纯截图下性能随比例(分辨率)提高而上升;SoM 下在 0.4(768×432)处出现峰值,降至 0.2 则明显下滑。

::: en
Longer text-based trajectory history context improves performance, unlike screenshot-only history, but poses efficiency challenges The main experiment revealed the decisive role of the a11y tree in performance within the current technological context. Even when we retain key attribute elements based on heuristic rules (keep nodes with tags of the document, item, button, heading, label, etc.), LLMs still require a sufficiently large context to process this information effectively. To further understand this, we sample some a11y tree observations from OSWorld and conducted the statistical analysis, as shown in Figure 6. The analysis indicates that a context length of 6000 is needed to accommodate about 90% of cases for a single observation. However, relying solely on current observations inherently leads to agents making repeated errors. Therefore, we include current observations as well as past N rounds of observations and actions in the constructed prompts (see appendix for more details), to explore the impact on agent performance when N is set to 1, 2, 3, and all where we put as much context as we can. The experimental results (as shown in Figure 7) show the performance increase with more history context for SoM. Future work on constructing models with enhanced capabilities for longer context support and understanding reasoning, improving model efficiency, and designing new agent architectures for efficient memory storage will have a significant impact on digital agents. However, we also note that the inclusion of additional trajectory history does not enhance performance under the pure screenshot setting. This suggests that contemporary advanced VLMs might not be as adept at extracting robust contextual information from images as they are from textual data. Strengthening this capability to harness information from images constitutes an important avenue for future enhancements.
:::

**更长的文本轨迹历史可提升性能(与仅截图的历史不同),但带来效率挑战。**主实验揭示了当前技术背景下 a11y 树对性能的决定性作用。即使我们基于启发式规则保留了关键属性元素(保留标签为 document、item、button、heading、label 等的节点),LLM 仍需要足够大的上下文才能有效处理这些信息。为进一步理解这一点,我们从 OSWorld 中抽样了一些 a11y 树观察并做了统计分析,见图 6。分析表明,要容纳约 90% 案例的单次观察,需要约 6000 的上下文长度。然而,只依赖当前观察本质上会导致智能体反复犯错。因此,我们在构造的提示中纳入当前观察以及过去 N 轮的观察与动作(更多细节见附录),探索 N 设为 1、2、3 与"全部"(即尽可能多地放入上下文)时对智能体性能的影响。实验结果(如图 7 所示)显示,SoM 设置下性能随历史上下文增多而上升。未来在以下方面的工作将对数字智能体产生重大影响:构建具备更强长上下文支持与理解推理能力的模型、提升模型效率,以及为高效记忆存储设计新的智能体架构。然而,我们也注意到,纳入更多轨迹历史在纯截图设置下并不能提升性能。这表明当代先进的 VLM 从图像中提取鲁棒上下文信息的能力,可能不如从文本数据中那样出色。强化这种从图像中获取信息的能力,是未来改进的重要方向。

[图 6: Figure 6: The length distribution of a11y tree as observation from sampled trajectories.]

中文说明:图 6 为抽样轨迹中 a11y 树观察的长度分布,横轴为 token 数(0–12000),纵轴为频率密度(%);分布高度右偏,第 90 百分位为 6343.60 token,即约 90% 的单次 a11y 树观察不超过约 6000 token。

[图 7: Figure 7: The effect of length of history on performance with the history encoding length of 1, 2, 3, and > 3 and run on a subset (10%) of examples.]

中文说明:图 7 在 10% 样例子集上考察历史编码长度的影响,横轴为历史轨迹长度(1、2、3、>3),纵轴为成功率(%),比较 GPT-4V 在 SoM 与纯截图两种设置下的曲线:SoM 下性能随历史变长而上升;纯截图下增加历史无提升。

::: en
VLM agents struggle with perturbation of position and size of application windows and irrelevant information We continue to adopt the SoM setting and sample a subset of 28 tasks that agents relatively well perform (with a success rate of 50.79%) in OSWorld. At the beginning of each task, we introduce disturbances to the windows by 1) changing the position of the window; 2) changing the size of the window to the minimal; 3) opening some irrelevant software and maximizing them to clutter the screen. This process generates several times more samples from the subset of tasks to observe their performance. We find current agents are not robust in handling all these changes, which leads to a performance drop to over 60% to even 80%. Surprisingly, we find agents can switch the window to a certain degree but fail to maximize the window as an intermediate step and are stuck on other things. This suggests that while agents possess some capability to navigate between windows, they lack a comprehensive strategy for managing window states effectively.
:::

**VLM 智能体难以应对应用窗口的位置与大小扰动以及无关信息。**我们继续采用 SoM 设置,从 OSWorld 中抽取智能体表现相对较好的 28 个任务子集(成功率 50.79%)。在每个任务开始时,我们对窗口引入扰动:1) 改变窗口位置;2) 把窗口大小改为最小;3) 打开一些无关软件并将其最大化以堆满(clutter)屏幕。该过程从任务子集生成了数倍的样例以观察其性能。我们发现当前智能体在应对所有这些变化时都不鲁棒,导致性能跌落超过 60% 甚至 80%。令人惊讶的是,我们发现智能体能在一定程度上切换窗口,却不能把"将窗口最大化"作为中间步骤来完成,而是卡在其他事情上。这表明智能体虽然具备一定的窗口间导航能力,但缺乏有效管理窗口状态的完整策略。

[图 8: Figure 8: Decline in performance due to window perturbations.]

中文说明:图 8 为窗口扰动导致的性能下降(柱状图,纵轴为成功率 %),四根柱的数值(依提取顺序转写)为:Position(改变窗口位置)36.5、Size(窗口缩到最小)15.04、Clutter(无关软件最大化遮挡)25.39、Original(原始无扰动)50.79——即相对原始成功率出现约六至八成的跌幅,与正文"性能跌落超过 60% 甚至 80%"的表述一致。

#### 5.3 跨操作系统的性能(Performance across Different Operating Systems)

::: en
Another key challenge in building universal digital agents is ensuring that these agents can maintain efficient and consistent performance across different operating system environments. The differences between OS and their software ecosystems can significantly impact an agent's observation and action spaces, leading to performance uncertainties. Here, we explore and analyze the correlation between the success of agents in completing tasks on Windows after migrating from Ubuntu using examples from OSWorld. We enhance the functionality of the OSWorld environment to support setting up initial experiment states, final evaluations, and obtaining observations such as the a11y tree and screenshots in Windows OS. Additionally, we have made example-wise fine-tuning modifications to the existing subset in OSWorld for migration to Windows. We conduct evaluations using the GPT-4V screenshot-only method and present the correlation of performance across the two operating systems. As shown in Tab. 7, the model's performance on Ubuntu and Windows is 4.88% and 2.55%, respectively, with a correlation coefficient of 0.7, despite the differences in their observation spaces. This implies that insights and methodologies developed within the OSWorld framework can be effectively transferred to Windows environments with a high degree of reliability.
:::

构建通用数字智能体的另一个关键挑战,是确保这些智能体能在不同操作系统环境间保持高效且一致的性能。操作系统及其软件生态之间的差异会显著影响智能体的观察与动作空间,带来性能上的不确定性。这里,我们使用 OSWorld 中的样例,探索并分析智能体"从 Ubuntu 迁移到 Windows 后完成任务的成功率"之间的相关性。我们增强了 OSWorld 环境的功能,以支持在 Windows 操作系统上设置初始实验状态、进行最终评估,以及获取 a11y 树与截图等观察。此外,我们对 OSWorld 中的现有子集做了逐例的微调修改,以迁移到 Windows。我们用 GPT-4V 纯截图方法进行评估,并给出两个操作系统上性能的相关性。如表 7 所示,模型在 Ubuntu 与 Windows 上的性能分别为 4.88% 与 2.55%,相关系数为 0.7——尽管两者的观察空间存在差异。这意味着在 OSWorld 框架内得到的洞察与方法,可以以较高的可靠度有效迁移到 Windows 环境。

表 7:跨操作系统的模型性能与相关性比较(Table 7: Comparison of model performance and correlation across operating systems.):

| 操作系统 | 成功率(%) | 相关系数 |
| --- | --- | --- |
| Ubuntu | 4.88 | 0.7(两系统间) |
| Windows | 2.55 | 0.7(两系统间) |

#### 5.4 定性分析(Qualitative Analysis)

::: en
In this section we highlight representative examples of success, failure, and surprising outcomes, alongside a comparative study between GPT-4V and Claude-3 agents, to elucidate the unique challenges and insights our environment introduces. See App. D for more details.
:::

本节我们突出展示成功、失败与令人惊讶结果的代表性案例,并进行 GPT-4V 与 Claude-3 智能体的对比研究,以阐明我们的环境带来的独特挑战与洞察。更多细节见附录 D。

::: en
Success and failure cases We find agents, particularly based on GPT-4V, can successfully solve tasks that involve complex problem-solving or creative thinking, showcasing the advanced understanding and processing capabilities of the model already. One successful task is shown in the first row of Figure 9. The agent is requested to extract subtitle files from the video stream and save them locally. The agent first divides the screen into two parts, with the VLC application window on the left and the terminal window open on the right, and uses the ffmpeg command twice. The first use removes the subtitles embedded in the original video, and the second use saves the extracted subtitles locally.
:::

**成功与失败案例(Success and failure cases)**:我们发现,尤其是基于 GPT-4V 的智能体,能够成功解决涉及复杂问题求解或创造性思考的任务,展示了模型已具备的先进理解与处理能力。图 9 第一行展示了一个成功任务:智能体被要求从视频流中提取字幕文件并保存到本地。智能体首先把屏幕分成两部分——左侧为 VLC 应用窗口、右侧打开终端窗口——并两次使用 ffmpeg 命令:第一次去除原视频中内嵌的字幕,第二次把提取出的字幕保存到本地。

[图 9: Figure 9: The agent successfully understood the complex task instructions, extracted the subtitle file from the video, and generated a pure video without embedded subtitles.]

中文说明:图 9 展示一个成功案例。任务指令(Task Instruction):「我下载了一集《老友记》来练听力,但不知道怎么去掉字幕。请帮我把字幕从视频中去掉,并将其导出为 “subtitles.srt”,保存在与视频相同的目录下。」(I downloaded an episode of Friends to practice listening, but I don't know how to remove the subtitles. Please help me remove the subtitles from the video and export it as "subtitles.srt" and store it in the same directory as the video.)智能体的执行步骤:Step 1 `pyautogui.click(activities_x, activities_y)`(点击活动菜单);Step 2 `pyautogui.typewrite('terminal', interval=0.5)`(输入 terminal 打开终端);Step 3 `pyautogui.click(focus_x, focus_y)`(聚焦终端);Step 4 `pyautogui.typewrite('ffmpeg -i video.mp4 -map 0:s:0 subtitles.srt', interval=0.5)`(提取字幕并保存为 srt);Step 5 `pyautogui.typewrite('ffmpeg -i video.mp4 -c copy -sn no_subtitles_video.mp4', interval=0.5)`(生成无内嵌字幕的纯视频);Step 6: Done(完成)。图题:智能体成功理解了复杂的任务指令,从视频中提取出字幕文件,并生成了不含内嵌字幕的纯视频。

::: en
Despite the successes, there are notable failures that highlight the limitations of current models. In the task of "center-aligning the title of the document" (Fig. 10 line 1), the agent fails to ground the relatively simple requirement of "center alignment of texts", performing many useless actions such as selecting irrelevant words, opening irrelevant menus, etc. Moreover, we find that the agent lacks prior knowledge in using software, performing poorly in many specialized tasks (as shown in Fig. 16, with GIMP, LibreOffice Calc, and Chrome selected). Taking GIMP as an example, for the instruction "reduce brightness" the agent does not know which menu in the toolbar is for brightness adjustment and instead randomly tries until exhausting the maximum number of steps.
:::

尽管有这些成功,也有显著的失败凸显当前模型的局限。在"把文档标题居中对齐"的任务中(图 10 第 1 行),智能体无法定位"文本居中对齐"这一相对简单的要求,做出许多无用动作,如选中无关词语、打开无关菜单等。此外,我们发现智能体缺乏使用软件的先验知识,在许多专业任务上表现不佳(如图 16 所示,选取了 GIMP、LibreOffice Calc 与 Chrome)。以 GIMP 为例,对于"降低亮度"的指令,智能体不知道工具栏中哪个菜单用于亮度调整,只能随机尝试,直到耗尽最大步数。

::: en
Common errors by GPT-4V agents Among the 550 failed examples from different settings in our sample, more than 75% exist mouse click inaccuracies, which is the most common error. The agent fails to click the correct coordinates despite planning detailed and accurate steps in their code comments, indicating strong planning but weak execution capabilities. Mouse click inaccuracies lead to two other frequent errors: repetitive clicks and environmental noise dilemma. Repetitive clicks occur when the agent repeatedly misclicks, adjusts, and fails, consuming too many steps. Environmental noise arises from clicking unintended objects, causing pop-ups, or opening unrelated applications. Due to a lack of prior knowledge about most professional software, it falls into a mismatch dilemma between the actions taken and the current state, and don't know how to get back to normal. Moreover, the agent lacks basic human-like cognition of web pages, such as not closing pop-ups in real-world web pages or being attracted by advertisement content, which affects its original correct judgment. Failures also arise from misinterpretation of instructions and visual oversight, highlighting the need for improvement in language and visual processing. See App. D.2 for the specific execution process.
:::

**GPT-4V 智能体的常见错误(Common errors by GPT-4V agents)**:在我们抽样的、来自不同设置的 550 个失败样例中,超过 75% 存在鼠标点击不准,这是最常见的错误。智能体尽管在代码注释中规划了详细而准确的步骤,却点不到正确的坐标,表明其"规划强、执行弱"。鼠标点击不准又引发另外两类高频错误:重复点击(repetitive clicks)与环境噪声困境(environmental noise dilemma)。重复点击发生在智能体反复误点、调整、失败、消耗过多步骤之时。环境噪声则来自点到非预期对象、引发弹窗或打开无关应用。由于对大多数专业软件缺乏先验知识,智能体陷入"已执行动作与当前状态不匹配"的困境,且不知如何恢复正常。此外,智能体缺乏类人的网页基本认知,例如不会关闭真实网页中的弹窗、或被广告内容吸引,从而影响其原本正确的判断。失败也源于指令误解与视觉疏漏,凸显了语言与视觉处理上的改进需求。具体执行过程见附录 D.2。

::: en
Discrepancies in task difficulty between agent and human We identify notable disparities in the perceived difficulty of tasks between humans and AI agents. Tasks that are intuitively simple for humans often present substantial challenges to agents, and conversely, tasks that humans find demanding can be more straightforward for agents to execute. You can find more details in Fig. 19 and App. D.3.
:::

**智能体与人类之间的任务难度错位(Discrepancies in task difficulty between agent and human)**:我们发现人类与 AI 智能体对任务的感知难度存在显著差异。人类直觉上觉得简单的任务,对智能体往往构成重大挑战;反过来,人类觉得费劲的任务,对智能体的执行来说可能更为直接。更多细节见图 19 与附录 D.3。

[图 10: Figure 10: Screenshots of the three examples mentioned in the quality analysis. The first line is an example of GPT-4V failing at a very simple task, the second line is one example where agents face more difficulty than humans, and the third line is one example that is more difficult for humans than for agents.]

中文说明:图 10 给出定性分析中的三个示例(每行一例,含任务指令与执行步骤)。第 1 行——GPT-4V 在非常简单的任务上失败:任务指令「帮我把 LibreOffice 文档中的标题居中对齐」(help me center align the heading in LibreOffice.),步骤为 `pyautogui.click(focux_x, focus_y)` → `pyautogui.moveto(coor_x, coor_y)` → `pyautogui.click(menu_x, menu_y)` → Failed(无意义动作)。第 2 行——智能体比人类更困难的示例:任务指令「清除这份文档中所有的高亮标记」(erase all the highlighted marks in this document),步骤为点击 LibreOffice Writer → `pyautogui.mouseDown()` → `pyautogui.hotkey('ctrl', 'a')` → Failed(没找到正确入口)。第 3 行——人类比智能体更困难的示例:任务指令「用 GIMP 剪辑出视频的第 2 秒到第 4 秒」(use GIMP to cut out the 2s to 4s part of a video),步骤为 `pyautogui.hotkey('ctrl', 'atl', 't')`(打开终端)→ 点击 focus → `pyautogui.typewrite('ffmpeg -ss …', interval=0.05)` → Done,但未遵循指令(直接用 ffmpeg 而非 GIMP 完成)。图题:第一行是 GPT-4V 在极简单任务上失败的示例,第二行是智能体比人类更困难的示例,第三行是人类比智能体更困难的示例。

::: en
Tasks where humans outperform agents These tasks mainly involve text-based and design-related work, such as "bold the font on this slide and add notes" or "erase all the highlighted marks in this document" (Fig. 10 Line 2). Since the Internet lacks such fine-grained data as the software execution process, the agent also lacks the corresponding training process, so its grounding ability is not good enough. The lack of understanding of GUI logic also causes poor performance on operations like selecting and scrolling.
:::

**人类优于智能体的任务(Tasks where humans outperform agents)**:这些任务主要涉及文本与设计相关的工作,如"把这张幻灯片上的字体加粗并添加备注"或"清除这份文档中所有的高亮标记"(图 10 第 2 行)。由于互联网缺乏"软件执行过程"这类细粒度数据,智能体也缺乏相应的训练过程,因此其定位(grounding)能力不够好。对 GUI 逻辑理解的欠缺,也导致其在选择、滚动等操作上表现不佳。

::: en
Tasks where agents outperform humans Tasks that the agent considers simple but humans find difficult are concentrated in "code solvability tasks", such as "monitor the system CPU for 30s and output the results" and "force close a process". These tasks require little or no GUI interaction and can be completed by executing complex codes and instructions. It's worth noting that completing through code sometimes mismatches with human instructions. In the task "use GIMP to cut out the 2s to 4s part of a video" (Fig. 10 Line 3), the agent used "ffmpeg" command to complete the video cropping, ignoring the "use GIMP" requirement in the instructions.
:::

**智能体优于人类的任务(Tasks where agents outperform humans)**:智能体认为简单而人类觉得难的任务,集中在"代码可解"类任务,如"监控系统 CPU 30 秒并输出结果"与"强制结束一个进程"。这些任务几乎或完全不需要 GUI 交互,可以通过执行复杂的代码与指令来完成。值得注意的是,通过代码完成有时与人类指令不匹配:在"用 GIMP 剪辑出视频第 2 秒到第 4 秒"的任务中(图 10 第 3 行),智能体用 ffmpeg 命令完成了视频剪辑,无视了指令中"用 GIMP"的要求。

::: en
Surprisingly, we discovered that agents are as prone to inefficiency in mechanically repetitive tasks, such as copying, pasting, and batch editing of Excel sheets, as humans. Humans frequently commit careless errors during execution. The shortcomings in agents stem either from the absence of an API or from insufficient training data related to the API, hindering their ability to efficiently process tasks in batches. Furthermore, sluggish response times can cause tasks to either time out or surpass the maximum allowed steps.
:::

令人惊讶的是,我们发现智能体在机械重复的任务上与人一样容易低效,例如 Excel 表格的复制、粘贴与批量编辑。人类在执行中经常犯粗心错误;智能体的短板则要么源于缺少相应 API、要么源于与该 API 相关的训练数据不足,使其无法高效地批量处理任务。此外,迟缓的响应时间还可能导致任务超时或超出允许的最大步数。

::: en
Comparative analysis: Claude-3 vs. GPT-4V Although Claude outperforms GPT-4 in many benchmarks such as GSM8K, HumanEval, etc., in our main experiment, we find that Claude has an average lower accuracy rate compared to GPT-4V by 2.84% to 7.76%. We find that Claude can provide satisfactory high-level solutions, but its grounding ability contains hallucinations in detail. For instance, Claude would interpret double-clicking a file as selecting it instead of opening it, treat column B in LibreOffice Calc software as column C, and enter text in the VS Code text replacement box without clicking on global replace. This shows that Claude can align well with human planning in problem-solving, but lacks excellent grounding ability when it comes to execution. Details can be seen in Fig. 20 and App. D.4.
:::

**对比分析:Claude-3 对 GPT-4V(Comparative analysis: Claude-3 vs. GPT-4V)**:尽管 Claude 在 GSM8K、HumanEval 等许多基准上优于 GPT-4,但在我们的主实验中,我们发现 Claude 的平均准确率比 GPT-4V 低 2.84% 到 7.76%。我们发现 Claude 能给出令人满意的高层解决方案,但其定位能力在细节上存在幻觉(hallucinations)。例如,Claude 会把"双击文件"理解为"选中它"而非"打开它";把 LibreOffice Calc 软件中的 B 列当成 C 列;在 VS Code 的文本替换框中输入了文本却不点击全局替换。这表明 Claude 在问题求解上能与人类规划很好地对齐,但在执行环节缺乏优秀的定位能力。细节见图 20 与附录 D.4。

### 6 相关工作(Related Work)

::: en
Benchmarks for multimodal agents Testing digital interaction agents mainly spans coding environments, web scenarios, and mobile applications. In the coding domain, several works provide frameworks and datasets for evaluating agents across programming languages and software engineering activities [57, 20, 24, 45]. For web browsing, platforms have been developed for agents to interact with web interfaces through keyboard and mouse actions, alongside datasets focusing on open-ended web tasks and realistic web navigation [44, 30, 58, 9, 66, 22, 10]. Mobile device interaction research aims at improving accessibility, with simulators for mobile UI interactions and platforms dedicated to InfoUI tasks [27, 47, 51, 50, 40, 61, 53, 60, 52]. Further, environments connecting to real computers and datasets for GUI grounding, albeit without interactive capability, have emerged [13, 8, 38, 21, 48]. Comprehensive task evaluation across different aspects also sees innovations [32, 36]. Differing from previous endeavors focusing on singular environments or lacking executability, OSWorld integrates an interactive setup enabling agents to engage with operating systems openly, supported by a diverse array of tasks and precise evaluation scripts within a fully controllable setting, marking it as a competitive benchmarking realism and reliability, as well as an environment for learning and evaluating general-purpose digital agent (See Tab. 4 for comparison).
:::

**多模态智能体基准(Benchmarks for multimodal agents)**:对数字交互智能体的测试主要横跨编码环境、网页场景与移动应用。编码领域中,若干工作为跨编程语言与软件工程活动评估智能体提供了框架与数据集 [57, 20, 24, 45]。网页浏览方面,已开发出供智能体通过键鼠动作与网页界面交互的平台,以及聚焦开放式网页任务与真实网页导航的数据集 [44, 30, 58, 9, 66, 22, 10]。移动设备交互研究旨在提升可访问性,出现了移动 UI 交互模拟器以及面向 InfoUI 任务的专用平台 [27, 47, 51, 50, 40, 61, 53, 60, 52]。此外,还出现了连接真实计算机的环境与用于 GUI 定位的数据集,尽管不具备交互能力 [13, 8, 38, 21, 48]。跨不同侧面的综合任务评估也见到创新 [32, 36]。与以往"聚焦单一环境或缺乏可执行性"的努力不同,OSWorld 集成了交互式设置,在完全可控的环境、多样任务与精确评估脚本的支持下,使智能体能开放式地与操作系统交互,使其既是一个在真实性与可靠性上有竞争力的基准,也是学习与评估通用数字智能体的环境(对比见表 4)。

::: en
Vision-language models for multimodal agents Many existing works on GUI interaction utilize some form of structured data (such as HTML, accessibility trees, view hierarchies) as a grounding source [9, 15, 27, 37, 64, 46, 62, 66]. However, source code often tends to be verbose, non-intuitive, and filled with noise. In many cases, it is even inaccessible or unavailable for use, making multimodality or even vision-only perception a must. To take screenshots as input, there are already specialized, optimized multi-modal models available that are suited for tasks on web [4, 12, 18, 23, 43] and mobile devices [17, 63]. Additionally, general-purpose foundation models [5, 26, 31, 67] also demonstrate significant potential for multi-modal digital agents. The development of prompt-based methods [13, 16, 55, 65], as well as visual reasoning paradigms, have also further facilitated the performance of digital agents in web pages, mobile apps, and desktop. To investigate how well do current models and methods perform in digital agent tasks, our paper evaluates the results of text-only, vision-only, and multi-modal input as well as across multiple methods, demonstrating that existing multi-modal models are far from capable computer agents. Specifically, there is ample room for improvement in long-horizon planning, screenshot details perception, pixel coordinate locating, and world knowledge.
:::

**面向多模态智能体的视觉-语言模型(Vision-language models for multimodal agents)**:许多现有的 GUI 交互工作利用某种形式的结构化数据(如 HTML、无障碍树、视图层级)作为定位来源(grounding source)[9, 15, 27, 37, 64, 46, 62, 66]。然而,源码往往冗长、不直观且充满噪声;许多情况下甚至无法访问或不可用,这使多模态乃至纯视觉感知成为必须。就以截图作为输入而言,已有经过专门优化、适合网页 [4, 12, 18, 23, 43] 与移动设备 [17, 63] 任务的多模态模型;通用基础模型 [5, 26, 31, 67] 也展现出作为多模态数字智能体的巨大潜力。基于提示(prompt)的方法 [13, 16, 55, 65] 与视觉推理范式的发展,也进一步提升了数字智能体在网页、移动应用与桌面上的表现。为考察当前模型与方法在数字智能体任务中的表现究竟如何,本文评估了纯文本、纯视觉与多模态输入以及多种方法的结果,证明现有多模态模型远非合格的计算机智能体。具体而言,在长程规划(long-horizon planning)、截图细节感知、像素坐标定位与世界知识方面,都有很大的改进空间。

### 7 结论与未来工作(Conclusion and Future Work)

::: en
In conclusion, the introduction of OSWorld marks a significant step forward in the development of autonomous digital agents, addressing critical gaps in existing interactive learning environments. By providing a rich, realistic setting that spans multiple operating systems, interfaces, and applications, OSWorld not only broadens the scope of tasks digital agents can perform but also enhances their potential for real-world application. Despite the promise shown by advancements in vision-language models, evaluations within OSWorld reveal notable challenges in agents' abilities, particularly in GUI understanding and operational knowledge, pointing to essential areas for future research and development.
:::

总之,OSWorld 的推出标志着自主数字智能体发展的重要一步,弥补了现有交互式学习环境的关键缺口。通过提供横跨多操作系统、界面与应用的丰富真实环境,OSWorld 不仅拓宽了数字智能体可执行的任务范围,也提升了其在真实世界应用中的潜力。尽管视觉-语言模型的进展展现出前景,OSWorld 内的评估仍揭示了智能体能力上的显著挑战,尤其在 GUI 理解与操作知识方面,指明了未来研究与开发的关键领域。

::: en
We identify several potential directions for community development and progress toward general-purpose agents for computer operation:
:::

我们为社区发展、迈向计算机操作的通用智能体确定了若干潜在方向:

::: en
Enhancing VLM capabilities for efficient and robust GUI interactions For foundation model development, we need to boost the efficiency of our models, enabling them to process much longer contexts and perform inference computations efficiently, akin to the robotics community [6, 7] to better handle real-world cases. Enhancements in VLMs' GUI grounding capabilities that is robust to application windows changes and are also sought, focusing on the accurate understanding and generation of precise actions aligned with given instructions. Moreover, amplifying VLMs' ability to comprehend context in the form of images is a pivotal goal, since it is crucial to enable history encoding using images so that we can build memory and reflection upon that. These improvements may require more efforts in the upstream pre-training stage, downstream fine-tuning stage, and even in the model structure itself, as pointed out in previous work [9, 17, 33].
:::

**增强 VLM 高效鲁棒 GUI 交互的能力(Enhancing VLM capabilities for efficient and robust GUI interactions)**:就基础模型开发而言,我们需要提升模型的效率,使其能处理长得多的上下文并高效执行推理计算——类比机器人学界的做法 [6, 7]——以更好应对真实世界案例。还需要增强 VLM 的 GUI 定位能力,使其对应用窗口的变化鲁棒,聚焦于准确理解并生成与给定指令对齐的精确动作。此外,增强 VLM 以图像形式理解上下文的能力是一个关键目标,因为启用以图像进行的历史编码至关重要,我们才能在此基础上构建记忆与反思。这些改进可能需要在上游预训练阶段、下游微调阶段乃至模型结构本身投入更多努力,如以往工作所指出的 [9, 17, 33]。

::: en
Advancing agent methodologies for exploration, memory, and reflection The next-level approach encompasses designing more effective agent architectures that augment the agents' abilities to explore autonomously and synthesize their findings. The agents face challenges in leveraging lengthy raw observation and action records. It's fascinating to explore novel methods for encoding this history, incorporating efficient memory and reflection solutions to condense contextual information and aid the agent in extracting key information. Additionally, integrating knowledge grounding into (V)LLM agents through memory mechanisms is a promising avenue as well. Moreover, practice GUI assistants also require features of personalization and customization. These features rely on techniques such as user profiling and retaining memories from long-term user-assistant interactions. Additionally, crafting protocols specifically for digital agents operating within GUI and CLI interfaces aims at facilitating efficient actions is also an essential thing for the feasibility of general-purpose digital agents in the mid-short term.
:::

**推进面向探索、记忆与反思的智能体方法论(Advancing agent methodologies for exploration, memory, and reflection)**:下一层次的方法包括设计更有效的智能体架构,增强智能体自主探索并综合其所见的能力。智能体在利用冗长的原始观察与动作记录方面面临挑战。探索编码这些历史的新方法十分有趣——纳入高效的记忆与反思方案,以浓缩上下文信息、帮助智能体提取关键信息。此外,通过记忆机制把知识接地(knowledge grounding)整合进(V)LLM 智能体同样是一条有前景的途径。而且,实用的 GUI 助手还需要个性化与定制化特性,这些特性依赖用户画像(user profiling)、保留用户-助手长期交互记忆等技术。另外,为在 GUI 与 CLI 界面内操作的数字智能体专门打造协议、以便于高效执行动作,对中短期通用数字智能体的可行性而言也是重要之事。

::: en
Addressing the safety challenges of agents in realistic environments The safety of agents is a critical issue if applying a built agent in fully realistic environments, the developed universal digital agent could potentially be used to bypass CAPTCHA systems in the future, as noted in [42]. However, due to the currently limited capabilities of agents, we have not observed any harmful and damaging behaviors during our experiments, an automatic agent has the opportunity to damage patent rights, abuse accounts, attempt to exploit software vulnerabilities to create viruses, or engage in attacks. Currently, we adopt virtual machines to make it difficult for developing digital agents to cause irreversible damage to our host machines. However, there still lacks a reliable metric to assess the safety of an agent developed in an isolated environment. The current evaluation functions mainly focus on the results closely regarding the task instructions, assess only the correctness of task completion, and pay little attention to potential unnecessary damaging actions of agents. Owing to the complexity of a complete computer environment, we didn't work out an efficient way to detect the latent side effects of the agent. Consequently, how to assess and control potential behaviors in open and real environments through environmental constraints and agent training is an important further direction of research.
:::

**应对智能体在真实环境中的安全挑战(Addressing the safety challenges of agents in realistic environments)**:若把构建好的智能体部署到完全真实的环境中,智能体安全就是一个关键问题:如 [42] 所指出的,所开发的通用数字智能体未来可能被用于绕过 CAPTCHA 系统。不过,由于当前智能体能力有限,我们在实验中尚未观察到任何有害的破坏行为;一个自动化智能体有机会损害专利权、滥用账号、尝试利用软件漏洞制造病毒或发动攻击。目前,我们采用虚拟机,使开发中的数字智能体难以对宿主机造成不可逆损害。然而,仍缺乏可靠的指标来评估在隔离环境中开发出的智能体的安全性。当前的评估函数主要关注与任务指令密切相关的结果,只评估任务完成的正确性,很少关注智能体潜在的多余破坏动作。由于完整计算机环境的复杂性,我们没能找到检测智能体潜在副作用的高效方法。因此,如何通过环境约束与智能体训练来评估和管控开放、真实环境中的潜在行为,是未来研究的重要方向。

::: en
Expanding and refining data and environments for agent development In terms of datasets and environments, we can broaden the scope to cover more specialized domains, including real-sector needs in healthcare, education, industry, transportation, and personalized requirements. Efforts can be made to ensure our environment's seamless deployment across various hardware and software settings. The variance of a11y tree quality across different applications is also noticed. Although the problem is not remarkable in the applications currently included, there is no guarantee of that the application developers obey the a11y convention and offer clear and meaningful descriptions for GUI elements. More intelligent approaches to filter redundant a11y tree elements and to handle latently missing elements deserve careful investigation as well. We also highlight the necessity of a painless data collection method, allowing for the effortless acquisition of computer operation data and its transformation into agent capabilities.
:::

**扩展并完善智能体开发的数据与环境(Expanding and refining data and environments for agent development)**:在数据集与环境方面,我们可以拓宽范围以覆盖更多专门领域,包括医疗、教育、工业、交通等真实行业需求以及个性化需求。可以努力确保我们的环境在各种软硬件设置上无缝部署。我们也注意到不同应用之间 a11y 树质量的差异:尽管该问题在当前收录的应用中并不显著,但无法保证应用开发者遵守 a11y 规范并为 GUI 元素提供清晰、有意义的描述。更智能地过滤冗余 a11y 树元素、处理潜在缺失元素的方法,也值得仔细研究。我们还强调无痛(painless)数据采集方法的必要性——轻松获取计算机操作数据,并将其转化为智能体能力。

### 致谢(Acknowledgements)

::: en
We thank Sida Wang, Peter Shaw, Alane Suhr, Luke Zettlemoyer, Chen Henry Wu, Pengcheng Yin, Shunyu Yao, Xing Han Lu, Siva Reddy, Ruoxi Sun, Zhiyuan Zeng, Chengyou Jia, and Lei Li for their helpful feedback on this work.
:::

我们感谢 Sida Wang、Peter Shaw、Alane Suhr、Luke Zettlemoyer、Chen Henry Wu、Pengcheng Yin、Shunyu Yao、Xing Han Lu、Siva Reddy、Ruoxi Sun、Zhiyuan Zeng、Chengyou Jia 与 Lei Li 对本工作的有益反馈。

---

**译注**:本对照翻译覆盖论文正文部分——标题与作者、摘要、第 1 节(引言)、第 2 节(OSWorld 环境)、第 3 节(OSWorld 基准)、第 4 节(基线评测)、第 5 节(分析)、第 6 节(相关工作)、第 7 节(结论与未来工作)及致谢,对应 arXiv v2 版 PDF 第 1–18 页。其后的 **References(参考文献)与附录 A–D 未收录**:附录 A 为环境基础设施细节、观察空间(截图与无障碍树)与动作空间(pyautogui 完整动作列表、computer_13 变体);附录 B 为操作系统与软件选择、任务来源、样例收集、初始状态设置与评估配置细节及更多任务示例;附录 C 为基线超参数、提示词细节、无障碍树过滤、SoM 实现细节与完整结果表;附录 D 为成功/失败案例、GPT-4V 常见错误、难度错位与 Claude-3 对比的扩展定性分析。图表方面:图 2 的任务配置 JSON、表 1 的评估脚本以代码块保留;表 2–表 7(动作示例、任务统计、基准对比、主结果、子集成功率、跨 OS 对比)已转为 markdown 并保留全部数值;图 1、3–10 以图题加中文说明的方式收录。完整内容请查阅原文与项目主页 https://os-world.github.io 。

## 要点速览

- **动机**:已有智能体基准要么无可执行环境(非执行式评估惩罚替代正确解),要么局限于网页/代码等单一域;真实计算机使用是跨应用、跨 GUI/CLI 的,需要一个真实、可扩展的统一环境。
- **环境**:首个基于虚拟机的真实计算机环境,支持 Ubuntu/Windows/macOS;配置文件驱动"初始状态设置→交互→后处理→取回数据→执行评估"全流程;VM 提供安全隔离与快照重置,单机可并行多 VM、支持无头运行。
- **任务形式化**:POMDP;观察 = 截图/a11y 树/终端输出;动作 = pyautogui 代码(全部键鼠动作,可嵌入循环)+ WAIT/FAIL/DONE;奖励为执行式 [0,1](成功 1、部分达成正小数、准确识别不可行任务也可得分);实验最大 15 步。
- **基准构建**:369 个 Ubuntu 任务 + 43 个 Windows 任务;来源覆盖教程、论坛、视频课程等真实场景;每例标注初始状态配置与定制评估脚本;9 名作者 3 个月约 1800 人时(另有约 400 人时整合外部 84 例、超 400 人时四轮复查)。
- **任务构成**:单应用 268(72.6%)/ 多应用工作流 101(27.4%);不可行任务 30(8.1%);整合 NL2Bash、Mind2Web、SheetCopilot、PPTC、GAIA 共 84 例(22.8%);302 个初始状态、134 个独特评估函数(远超 WebArena 的 5、WebShop 的 1)。
- **人类基线**:完成时间中位数 111.94 秒(WebArena 35.38 秒),准确率 72.36%(WebArena 88%)——任务更难更耗时。
- **主结果**:全部基线成功率 0.99%–12.24%;最好为无障碍树输入的 GPT-4(12.24%);纯截图下 GPT-4V 仅 5.26%;多应用工作流最好仅 6.57%;LibreOffice Calc 子集经常 0 分;人类 72.36% 全面碾压且跨任务类型稳定(±5%),模型方差却极大。
- **输入法对比**:a11y 树对 GPT-4V 大幅加分(5.26%→12.17%)但对 Gemini 反而减分;SoM 在 OS 上因高分辨率、元素过多、噪声大而失效;纯截图虽最弱,但因无需额外信息、贴近人类感知,应是长期终极配置。
- **关键分析**:难度分组成功率 16.78%/13.12%/4.59%(人 84.91%/81.08%/49.57%);分辨率提升普遍涨分(SoM 在 0.4 倍降采样处最佳);文本历史越长越好但图像历史无效(90% 单观察约需 6000 token);窗口位置/大小/遮挡扰动使成功率从 50.79% 跌 60–80%;Ubuntu 4.88% vs Windows 2.55%,相关系数 0.7。
- **失败模式**:550 个失败样本中 >75% 有鼠标点击不准("规划强、执行弱"),派生重复点击与环境噪声困境;缺乏软件先验(GIMP 亮度菜单找不到);Claude-3 规划好但 grounding 幻觉多(双击当单击、B 列当 C 列);难度错位:人难的代码任务智能体易、人易的设计排版任务智能体难,且用 ffmpeg 替代"用 GIMP"这类偏离指令的行为值得警惕。
- **未来方向**:更强 GUI 定位与长上下文 VLM、探索/记忆/反思架构与个性化、真实环境安全评估(现有评估只看任务结果、不管副作用)、数据与环境扩展——其中"智能体安全度量缺失"与"操作数据无痛采集"正是本讲两篇论文(与下一篇 WebShop)所代表的基准研究仍在推进的开放问题。
