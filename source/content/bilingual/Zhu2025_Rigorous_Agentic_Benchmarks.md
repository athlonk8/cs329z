---
title: "Establishing Best Practices for Building Rigorous Agentic Benchmarks"
title_zh: "构建严谨 Agent 基准的最佳实践"
authors: "Yuxuan Zhu et al."
venue: "arXiv 2507.02825 · UIUC / Stanford / UC Berkeley 等"
kind: paper
importance: must
tags: "Agent评测,基准设计,评测有效性,检查清单,评测偏差,Agent基准"
summary: 提出 Agent 基准检查清单 ABC,从任务有效性与结果有效性审计十大流行 Agent 基准,发现可致最高 100% 相对误差的缺陷,并用 CVE-Bench 示范修复使高估下降 33%。
---

## 导读

本文是第 7 周「评测基础」单元的核心必读,作者阵容横跨 UIUC、Stanford、UC Berkeley、Yale、Princeton、MIT、UK AI Safety Institute 等机构(Daniel Kang 组牵头)。它直面 Agent 时代的评测危机:传统基准靠分类准确率或自动指标(如 BLEU)评分,而 Agent 基准以「完成端到端任务」定义成功,用单元测试、字符串匹配、状态比对、LLM 裁判等方式给非结构化结果打分——这套「基于结果的评测」看似客观,实则暗藏大量可被利用或可致系统性偏差的漏洞。

论文的两大支柱:其一,**有效性分类学**——严谨的 Agent 评测须同时满足「任务有效性(task validity):任务当且仅当 Agent 具备目标能力才可解」与「结果有效性(outcome validity):评测通过当且仅当任务真正完成」;其二,把两类条件落地为可操作的 **Agentic Benchmark Checklist(ABC)**,覆盖工具、环境、实现、四类评测方法与结果报告。用 ABC 审计十大流行 Agent 基准的结论触目惊心:七个违反任务有效性、七个违反结果有效性、十个全部存在报告局限;τ-bench 上「什么都不做」的平凡 Agent 拿 38% 成功率反超 GPT-4o Agent,SWE-Lancer 的 Agent 不解任何任务也能拿满分,KernelBench 高估约 31%,OSWorld 因网站漂移低估 28%。对任何要造基准、刷榜单或据榜单做决策的人,ABC 都是一份即拿即用的审计清单,与本单元 Press 的设计经验谈、tinyBenchmarks 的降本方法构成完整闭环。

## 全文对照翻译

> **译注**:以下对照覆盖论文正文全部内容(摘要、第 1–7 节,原文第 1–10 页),英文原段与中文全译逐段交替;References 不收录。附录 A–F 含实质内容,均予翻译(附录 B 的表 2 为 78 个基准的清单,以概述加 Agent 基准列举的方式收录;附录 D 十份逐项评估报告以「检查项 | 得分 | 理由」表格全量保留;附录 F 的表 15 排行榜全量保留);附录 G 为 NeurIPS 投稿自查清单(模板性内容),从略。图 2/3/4 的检查项清单按原文逐条保留英文并附中文对照。

### 摘要(Abstract)

::: en
Benchmarks are essential for quantitatively tracking progress in AI. As AI agents become increasingly capable, researchers and practitioners have introduced agentic benchmarks to evaluate agents on complex, real-world tasks. These benchmarks typically measure agent capabilities by evaluating task outcomes via specific reward designs. However, we show that many agentic benchmarks have issues in task setup or reward design. For example, SWE-bench-Verified uses insufficient test cases, while τ-bench counts empty responses as successful. Such issues can lead to under- or overestimation of agents' performance by up to 100% in relative terms. To make agentic evaluation rigorous, we introduce the Agentic Benchmark Checklist (ABC), a set of guidelines that we synthesized from our benchmark-building experience, a survey of best practices, and previously reported issues. When applied to CVE-Bench, a benchmark with a particularly complex evaluation design, ABC reduces the performance overestimation by 33%.
:::

基准(benchmark)对定量追踪 AI 的进展至关重要。随着 AI Agent 能力日益增强,研究者与从业者引入了 Agent 基准(agentic benchmark),在复杂的真实世界任务上评估 Agent。这些基准通常通过特定的奖励设计评估任务结果,以此度量 Agent 能力。然而我们发现,许多 Agent 基准在任务设置或奖励设计上存在问题:例如 SWE-bench-Verified 使用的测试用例不充分,而 τ-bench 把空响应计为成功。此类问题可导致对 Agent 性能的低估或高估达相对意义上的 100%。为使 Agent 评测更严谨,我们提出 Agentic Benchmark Checklist(ABC)——一套由我们的基准构建经验、最佳实践调研与已报告问题综合而成的指南。将其应用于评测设计尤为复杂的 CVE-Bench 后,ABC 使性能高估降低了 33%。

### 1 引言(Introduction)

::: en
AI agents that integrate machine learning models with tools, memory, and knowledge are emerging with the capability to solve complex problems [12, 25, 40, 68, 71, 84, 85]. To evaluate AI agents, researchers and practitioners have built agentic benchmarks with realistic tasks to track progress and assist decision-making [11, 22, 30, 37, 47, 59, 83, 86, 89, 93]. AI agents have exhibited impressive performance on these benchmarks. For example, a GPT-4o-based agent resolves 35% of tasks on τ-bench-Airline, a benchmark for tool-agent-user interaction [86]. As agentic benchmarks become increasingly impactful in academia and industry, it is crucial to ensure these numbers can be trusted.
:::

将机器学习模型与工具、记忆、知识集成的 AI Agent 正在崛起,展现出求解复杂问题的能力 [12, 25, 40, 68, 71, 84, 85]。为评估 AI Agent,研究者与从业者构建了含真实任务的 Agent 基准,以追踪进展、辅助决策 [11, 22, 30, 37, 47, 59, 83, 86, 89, 93]。AI Agent 在这些基准上表现亮眼:例如,基于 GPT-4o 的 Agent 在工具-用户交互基准(tool-agent-user interaction)τ-bench-Airline 上解决了 35% 的任务 [86]。随着 Agent 基准在学术界与工业界的影响日益扩大,确保这些数字可信变得至关重要。

::: en
Agentic benchmarks differ fundamentally from traditional AI benchmarks. Multiple-choice datasets (e.g., ImageNet [16] and MMLU [27]) evaluate models by their accuracy on categorical labels, while text-generation benchmarks rely on automatic metrics (e.g., BLEU [60]). By contrast, success is defined by completing end-to-end tasks in agentic settings. Therefore, an agent may perform coherent reasoning, write code, and execute commands to produce a final outcome. Subsequently, the performance of the agent is determined by comparing its final outcome with a ground-truth outcome, using various methods, such as program testing and string matching [11, 30, 37, 47, 59, 83, 86, 89, 93].
:::

Agent 基准与传统 AI 基准有本质不同。多选数据集(如 ImageNet [16] 与 MMLU [27])按分类标签上的准确率评测模型,文本生成基准则依赖自动指标(如 BLEU [60])。相比之下,Agent 场景下的成功由完成端到端任务来定义:Agent 可能需要进行连贯推理、编写代码并执行命令,以产出最终结果;随后,其性能通过把最终结果与真值结果(ground-truth outcome)比对来判定,采用程序测试、字符串匹配等多种方法 [11, 30, 37, 47, 59, 83, 86, 89, 93]。

::: en
Unfortunately, many existing outcome-based evaluation methods of agentic benchmarks introduce issues that can cause under- or overestimation of agent capabilities by up to 100% in relative terms, compromising the validity of their findings [35, 46, 62, 80, 87]. For example, SWE-bench-Verified challenges an agent to resolve GitHub issues, and considers the agent successful if the patch it generates passes manually vetted unit tests [14]. However, recent work has shown that passing these tests does not necessarily indicate that the issue is resolved, because unit tests can fail to capture important edge cases. Consequently, 24% of the top 50 leaderboard positions are incorrect [31, 87]. In addition, we find that in τ-bench, a trivial agent that returns empty responses is considered successful on intentionally impossible tasks (e.g., changing a non-refundable ticket). This trivial agent achieves a 38% success rate and outperforms a GPT-4o-based agent [86].
:::

不幸的是,许多现存的、基于结果的 Agent 基准评测方法会引入问题,使 Agent 能力被低估或高估达相对 100%,损害其结论的有效性 [35, 46, 62, 80, 87]。例如,SWE-bench-Verified 要求 Agent 解决 GitHub issue,只要其生成的补丁通过了经人工审核的单元测试 [14] 即视为成功。然而近期工作表明,通过这些测试并不一定代表 issue 被解决,因为单元测试可能漏掉重要的边界情况;其结果是,排行榜前 50 名中 24% 的位置不正确 [31, 87]。此外,我们发现在 τ-bench 中,一个只返回空响应的平凡 Agent(trivial agent)在「故意不可能完成的任务」(如修改不可退款的机票)上被判成功;该平凡 Agent 拿到 38% 的成功率,反超基于 GPT-4o 的 Agent [86]。

::: en
Although issues in evaluation rigor can significantly skew evaluation results, they are still frequently overlooked in the current development, deployment, and analysis of agentic benchmarks. To better understand this problem, we analyzed prior work on agentic benchmark pitfalls [35, 46, 62, 80, 87] and 17 widely used agentic benchmarks (Table 3), such as SWE-bench-Verified [14], GAIA [47], τ-bench [86], and WebArena [93]. Combining insights from the literature with our own experience in developing benchmarks, we identified two major conditions of the validity of benchmark results:

- **Outcome validity**: the evaluation result (e.g., tests or checks) truly indicates task success. SWE-bench-Verified fails here because an incorrect patch can still pass the test suite.
- **Task validity**: a task should be solvable if and only if the agent possesses the target capability. Issues in task design or implementation often breaks task validity. For example, τ-bench allows a trivial agent to pass 38% of tasks without knowledge of airline-ticketing rules.
:::

尽管评测严谨性问题会显著扭曲评测结果,在当前 Agent 基准的开发、部署与分析中它们仍常被忽视。为更好地理解这一问题,我们分析了先前关于 Agent 基准缺陷的研究 [35, 46, 62, 80, 87] 与 17 个广泛使用的 Agent 基准(表 3),如 SWE-bench-Verified [14]、GAIA [47]、τ-bench [86] 与 WebArena [93]。把文献洞见与我们自己的基准开发经验结合,我们识别出基准结果有效性的两个主要条件:

- **结果有效性(outcome validity)**:评测结果(如测试或检查)真正指示任务成功。SWE-bench-Verified 在此失守,因为错误的补丁也能通过测试套件。
- **任务有效性(task validity)**:任务当且仅当 Agent 具备目标能力(target capability)才可解。任务设计或实现中的问题常常破坏任务有效性,例如 τ-bench 允许平凡 Agent 在不具备机票规则知识的情况下通过 38% 的任务。

::: en
Following prior work on analyzing AI and code benchmarks [10, 65], we formulate our insights into an Agentic Benchmark Checklist (ABC) to assist benchmark developers and users in critically designing and assessing agentic benchmarks. Using ABC, we assessed ten popular agentic benchmarks that span the full range of agent capabilities, resulting in seven benchmarks with flaws in outcome validity, seven with issues in task validity, and all with limitations in the result reporting. In addition to the issues found in τ-bench-Airline, some other example issues we found are: (1) an agent can score 100% on SWE-Lancer [48] without resolving any tasks; (2) KernelBench [59] overestimates agents' capabilities in generating correct kernel functions by 31% in absolute terms due to incomprehensive fuzz testing; (3) WebArena [93] overestimates performance of agents by 5.2% due to various issues in its string matching. To demonstrate ABC's practical value, we applied it to improve CVE-Bench, a complex, representative cybersecurity benchmark [96]. ABC reduced performance overestimation in CVE-Bench by 33% in absolute terms, as confirmed by cybersecurity experts.
:::

沿循分析 AI 与代码基准的先前工作 [10, 65],我们把洞见整理成 Agentic Benchmark Checklist(ABC),帮助基准开发者与用户批判地设计与评估 Agent 基准。用 ABC 评估覆盖 Agent 能力全谱的十个流行 Agent 基准,结果是:七个存在结果有效性缺陷,七个存在任务有效性问题,全部存在结果报告局限。除 τ-bench-Airline 上的问题外,我们新发现的其他问题举例:(1) Agent 可以在 SWE-Lancer [48] 上不解任何任务拿到 100% 的分数;(2) KernelBench [59] 因模糊测试不全面,对 Agent 生成正确内核函数能力的高估达绝对 31%;(3) WebArena [93] 因字符串匹配的多项问题高估 Agent 性能 5.2%。为展示 ABC 的实用价值,我们将其用于改进 CVE-Bench——一个复杂的、有代表性的网络安全基准 [96];ABC 使 CVE-Bench 的性能高估绝对下降 33%,并经网络安全专家确认。

::: en
We summarize our contributions as follows:

1. We identified two significant threats in the evaluation rigor of agentic benchmarks: outcome validity and task validity.
2. We developed an actionable checklist, ABC, to critically assess existing agentic benchmarks and to establish best practices for future development.
3. We applied ABC to assess ten widely used agentic benchmarks and identified new evaluation issues that cause estimation errors of agents' performance by up to 100% in relative terms.
4. We provided a case study of using ABC to improve an agentic benchmark during development.
:::

我们把贡献总结如下:

1. 识别出 Agent 基准评测严谨性的两大威胁:结果有效性与任务有效性。
2. 开发了可操作的检查清单 ABC,用于批判地评估既有 Agent 基准,并为未来开发建立最佳实践。
3. 用 ABC 评估十个广泛使用的 Agent 基准,发现了可使 Agent 性能估计误差达相对 100% 的新评测问题。
4. 提供了在基准开发过程中用 ABC 改进 Agent 基准的案例研究。

### 2 相关工作(Related Work)

::: en
**Assessing AI Benchmarks.** Benchmarks are fundamental in AI research and practice, serving as key tools for measuring progress and identifying potential risks [21, 69]. However, maintaining benchmark quality remains a persistent challenge. To address this, prior studies have assessed various dimensions of AI benchmarks, including label quality and quantity [17, 18], standardized evaluation protocols [41], construct validity [20, 64], data contamination [91], reproducibility [75], and practical usage [24]. Even high-profile benchmarks, such as ImageNet [16], have faced issues related to data bias and label noise [73]. With the advancement of large language models (LLMs), recent work has proposed best practices for developing general or code-oriented benchmarks [10, 65]. Although these existing studies provide important insights to our analysis, they primarily focused on multiple-choice or generative tasks that do not require multistep reasoning, which present fewer ambiguities and complexities than complex agentic benchmarks.
:::

**评估 AI 基准。** 基准是 AI 研究与实践的基石,是度量进展、识别潜在风险的关键工具 [21, 69]。然而,维护基准质量始终是一项长期挑战。为此,先前研究评估了 AI 基准的多个维度,包括标签质量与数量 [17, 18]、标准化评测协议 [41]、构念效度(construct validity)[20, 64]、数据污染(data contamination)[91]、可复现性 [75] 与实际用途 [24]。连 ImageNet [16] 这样的高知名度基准也曾面临数据偏差与标签噪声问题 [73]。随着大语言模型(LLM)的进步,近期工作为通用或代码导向的基准提出了开发最佳实践 [10, 65]。尽管这些研究为我们的分析提供了重要洞见,它们主要面向无需多步推理的多选或生成任务——其歧义性与复杂度远低于复杂的 Agent 基准。

::: en
**Benchmarking of AI Agents.** Prior work has proposed agentic benchmarks across various domains, including coding [30, 37, 48, 59], interacting with environments for a predefined target [83, 86, 93], solving math problems [22, 39], and others [11, 47, 74, 89]. These tasks typically emulate real-world challenge resolution, involving non-categorical outputs and multistep execution. Evaluating AI agents in these tasks introduces a more complex design and implementation than traditional benchmarks, including handling dynamic interactions between an agent and the environment and grading unstructured responses, which increases the difficulty in ensuring rigorous evaluation.
:::

**Agent 基准化。** 先前工作提出了覆盖多领域的 Agent 基准:编程 [30, 37, 48, 59]、为达成预定目标与环境交互 [83, 86, 93]、求解数学问题 [22, 39] 等 [11, 47, 74, 89]。这些任务通常模拟真实世界挑战的求解,涉及非分类输出与多步执行。在这些任务上评测 AI Agent,其设计与实现都比传统基准更复杂:需要处理 Agent 与环境的动态交互、给非结构化回复判分,这加大了保证评测严谨性的难度。

::: en
**Issues in Evaluating AI Agents.** Existing analyses have identified evaluation issues in individual agentic benchmarks [32, 34, 35, 62, 87]. In terms of the outcome validity, Kydlíček and Gandenberger [34] found that implicit assumptions on the answer formats lead to performance underestimation by 5.3%. Yu et al. [87] found that agents can pass evaluations without generating correct patches for 7.7% of tasks in the SWE-bench-Lite and 5.2% of tasks in the SWE-bench-Verified. In addition, prior analysis found that the annotation noise in BIRD significantly affects the accuracy of performance evaluation [62, 80]. In terms of task validity, the rate limit of the websites implemented in WebArena prevented agents from resolving challenges [32]. Furthermore, Lange et al. [35] identified flaws in the grading of KernelBench that allow agents to bypass correctness checks. However, none of them develops an actionable and systematic guideline to assess agentic benchmarks.
:::

**AI Agent 评测中的问题。** 既有分析已发现个别 Agent 基准的评测问题 [32, 34, 35, 62, 87]。结果有效性方面:Kydlíček 与 Gandenberger [34] 发现对答案格式的隐式假设导致性能低估 5.3%;Yu 等 [87] 发现 Agent 在 SWE-bench-Lite 与 SWE-bench-Verified 上,可分别在 7.7% 与 5.2% 的任务上不生成正确补丁即通过评测;此外,先前分析发现 BIRD 的标注噪声显著影响性能评测的准确性 [62, 80]。任务有效性方面:WebArena 所实现网站的限流曾阻止 Agent 解题 [32];Lange 等 [35] 发现 KernelBench 判分中的漏洞允许 Agent 绕过正确性检查。然而,上述工作都没有形成可操作、系统性的 Agent 基准评估指南。

### 3 总览:分类学与工作流(Overview)

::: en
In this section, we present an overview of our work. We first introduce a taxonomy of validity issues in agentic benchmarks and then describe the process of our benchmark collection, checklist development, and benchmark assessment. Finally, we release our code [1] and build a website [2] for continuous development and future updates.
:::

本节概述我们的工作。我们先介绍 Agent 基准中有效性问题的分类学(taxonomy),再描述基准收集、清单开发与基准评估的流程。最后,我们公开代码并搭建网站,以便持续开发与未来更新(代码:github.com/uiuc-kang-lab/agentic-benchmarks;网站:uiuc-kang-lab.github.io/agentic-benchmarks)。

::: en
**Taxonomy.** We first identify and classify the primary challenges in rigorous agentic evaluation. In Figure 1, we decompose the operational and conceptual process of agentic evaluation. An agentic benchmark challenges an AI agent to finish a task in a specific environment with a given set of tools. After several rounds of (inter-)actions, the AI agent presents a task outcome, which indicates whether the task completion state. To automatically determine whether the task is successful, the agentic benchmark develops customized methods based on the task requirements, such as string matching [86, 92] and testing [30, 59].

Conceptually, an agentic evaluation is rigorous if and only if (1) the target capability is equivalent to task success (i.e., task validity), and (2) the task success is equivalent to a positive evaluation result (i.e., outcome validity). However, agentic benchmark presents two unique challenges that makes these two validity conditions difficult to hold:

1. **Complex task setup**: In addition to task descriptions as inputs, agentic benchmarks set up an environment for agents to operate in and provide tools for agents to use.
2. **Unstructured task outcome**: Agentic benchmarks expect unstructured data as task outcomes, such as textual responses, code, and file edits. Verifying the correctness of such outcomes are non-trivial and requires specially designed methods.
:::

**分类学。** 我们首先识别并分类严谨 Agent 评测的主要挑战。图 1 分解了 Agent 评测的操作流程与概念流程。Agent 基准要求 AI Agent 在特定环境中、用给定的一组工具完成任务;若干轮(交)互动作之后,AI Agent 给出任务结果,它指示任务的完成状态。为自动判定任务是否成功,Agent 基准基于任务需求开发定制方法,如字符串匹配 [86, 92] 与测试 [30, 59]。

概念上,Agent 评测当且仅当满足以下两点才是严谨的:(1) 目标能力等价于任务成功(即任务有效性);(2) 任务成功等价于正向的评测结果(即结果有效性)。然而,Agent 基准呈现两大独特挑战,使这两个有效性条件难以成立:

1. **复杂任务设置**:除作为输入的任务描述外,Agent 基准还要为 Agent 搭建可运行的环境并提供可用的工具。
2. **非结构化任务结果**:Agent 基准期待非结构化数据作为任务结果,如文本回复、代码与文件编辑;验证此类结果的正确性并非易事,需要专门设计的方法。

[图 1: Operational and conceptual processes of agentic evaluation. An agentic benchmark measures the capability of AI agents via agentic tasks. It determines the success of a task by evaluating the task outcomes. Establishing task validity (e.g., equivalence between the target capability and the task success) and outcome validity (e.g., equivalence between the task success and positive evaluation results) are keys to ensure rigorous agentic evaluation.]

图 1 中文说明:Agent 评测的操作流程与概念流程。操作层面(左):AI Agent 接收任务描述,在环境中使用工具执行 Agent 任务,产出任务结果(文本回复、代码、环境状态等);基准评测以字符串匹配、测试、状态匹配、定制指标等方法判定结果,输出评测结果。概念层面(右):评测严谨的前提是「目标能力 ⟺ 任务成功」(任务有效性)与「任务成功 ⟺ 正向结果」(结果有效性)两个等价关系同时成立。

::: en
First, improper task setup can lead to the violation of task validity. For instance, τ-bench includes intentionally unattainable tasks (e.g., making changes to a non-refundable ticket), which agents are supposed to recognize and reject [86]. Yet, a trivial agent that simply returns nothing is considered a successful completion even though it cannot look up information or interpret ticket rules. Second, failure to rigorously grade unstructured task outcome can break outcome validity. For example, SWE-bench-Verified judges agent-generated patches by handwritten unit tests [14]. Since such tests can be incomplete or not perfectly sound [87, 94], a patch that passes them may still be wrong. Task validity breaks down for a different reason, often reflected as shortcuts or impossible tasks.

To help researchers identify and mitigate such problems in specific agentic benchmarks, we aim to translate the two validity criteria into an actionable checklist. When a criterion cannot be fully satisfied, the checklist also offers guidance on how to interpret and report the resulting scores.
:::

首先,不当的任务设置可导致任务有效性被违反。例如 τ-bench 含故意不可达成的任务(如修改不可退款的机票),Agent 本应识别并拒绝这类请求 [86];然而,一个什么都不返回的平凡 Agent 也被判成功完成任务,尽管它既不能查询信息也不能解读机票规则。其次,未能严格地判分非结构化任务结果会破坏结果有效性。例如 SWE-bench-Verified 用手写单元测试判定 Agent 生成的补丁 [14];由于此类测试可能不完备或并非完全可靠 [87, 94],通过了它们的补丁仍可能是错的。任务有效性则因另一类原因失效,常表现为捷径(shortcut)或不可解任务。

为帮助研究者识别并缓解特定 Agent 基准中的此类问题,我们旨在把两个有效性准则转化为可操作的检查清单。当某条准则无法完全满足时,清单还就如何解读与报告所得分数提供指引。

::: en
**Benchmark Collection.** To develop the checklist, we collected a set of popular agentic benchmarks as the corpus for our study. To emphasize common and representative issues, we focused on popular agentic benchmarks used by top AI providers, including OpenAI, Anthropic, Amazon, Meta, Google, xAI, Mistral, and DeepSeek, or those winning awards in peer-reviewed academic conferences. This narrows our focus to a set of 17 agentic benchmarks (Table 3). We defer the details of our benchmark collection to Appendix B.
:::

**基准收集。** 为开发清单,我们收集了一组流行的 Agent 基准作为研究语料。为聚焦常见且有代表性的问题,我们关注被顶级 AI 提供商(包括 OpenAI、Anthropic、Amazon、Meta、Google、xAI、Mistral、DeepSeek)使用的流行 Agent 基准,或在同行评审学术会议上获奖的基准。这将范围收窄到 17 个 Agent 基准(表 3)。基准收集的细节见附录 B。

::: en
**Checklist Development.** We first reviewed the collected benchmarks and surveyed AI agent evaluation frameworks [1, 44, 45, 50] together with documented issues in agentic benchmarks [32, 34, 35, 62, 87]. We then examined best practices for evaluating unstructured task outcomes in related domains, such as software testing. Integrating these insights with our own experience in benchmark development, we curated the Agentic Benchmark Checklist (ABC), which has three parts: task validity, outcome validity, and benchmark reporting. We provide the source of each checklist item in Appendix C.
:::

**清单开发。** 我们先审查收集到的基准,调研 AI Agent 评测框架 [1, 44, 45, 50] 与 Agent 基准中已记录的问题 [32, 34, 35, 62, 87];再考察相关领域(如软件测试)中评估非结构化任务结果的最佳实践。把这些洞见与我们自己的基准开发经验相整合,我们整理出 Agentic Benchmark Checklist(ABC),它包含三部分:任务有效性、结果有效性与基准报告。每条检查项的来源见附录 C。

::: en
**Benchmark Assessment.** We applied ABC to thoroughly assess ten selected benchmarks (Table 1). We selected these benchmarks from the open-source set in Table 3, prioritizing their popularity and ensuring all types of agent capabilities are covered. We assigned 1 point to each satisfied item and 0 otherwise. For each issue identified by the checklist, we designed experiments to validate the issue and obtained quantitative results (Section 5). We defer detailed assessment results to Appendix D and case studies to Appendix E.
:::

**基准评估。** 我们用 ABC 深入评估了十个选定基准(表 1)。这十个基准从表 3 的开源集合中选出,选择时优先考虑流行度,并确保覆盖全部类型的 Agent 能力。每满足一条检查项得 1 分,否则得 0 分。对清单识别出的每个问题,我们设计了实验加以验证并获得定量结果(第 5 节)。详细评估结果见附录 D,案例研究见附录 E。

### 4 ABC:Agentic Benchmark Checklist

::: en
In this section, we formulate our assessment framework into an actionable checklist (ABC). We present the checklist items in terms of task validity, outcome validity, and benchmark reporting.
:::

本节把我们的评估框架表述为一份可操作的检查清单(ABC)。我们按任务有效性、结果有效性与基准报告三部分呈现检查项。

#### 4.1 评估任务有效性

::: en
We propose guidelines for ensuring task validity. These checks uncover design or implementation flaws that can create shortcuts, which causes false positive evaluation results, or lead to impossible tasks, which causes false negative evaluation results.
:::

我们提出确保任务有效性的指南。这些检查揭露两类设计或实现缺陷:一类制造捷径(shortcut),导致假阳性的评测结果;另一类产生不可解任务,导致假阴性的评测结果。

::: en
**Task Validity**

**Tool**
T.1. Versions of all tools (e.g., Python) are clearly specified.
T.2. Required API tools are consistently accessible during evaluation.
T.3. Evaluation process terminates or handles errors appropriately if an API becomes inaccessible.

**Env.**
T.4. Residual data or state are fully cleared between runs.
T.5. Agent is completely isolated from any ground truth information.
T.6. Setup does not change over time (e.g., no live website).

**Implementation**
T.7. Annotated ground truth is verified for correctness.
T.8. Each task is verified to be solvable.
T.9. Benchmark includes an Oracle solver that can automatically solve all challenges.
T.10. Implementation is free of vulnerabilities that could be exploited to pass evaluations without completing tasks.

Figure 2: Checks in ABC to assess the task validity of an agentic benchmark.
:::

[图 2: Checks in ABC to assess the task validity of an agentic benchmark. —— ABC 中用于评估 Agent 基准任务有效性的检查项。] 中文对照:

- **工具(Tool)**
  - T.1. 所有工具(如 Python)的版本都被明确指定。
  - T.2. 所需的 API 工具在评测期间持续可访问。
  - T.3. API 变得不可访问时,评测过程会妥善终止或处理错误。
- **环境(Env.)**
  - T.4. 残留数据或状态在运行之间被彻底清除。
  - T.5. Agent 与任何真值信息完全隔离。
  - T.6. 环境设置不随时间变化(如不依赖真实在线网站)。
- **实现(Implementation)**
  - T.7. 标注的真值经验证是正确的。
  - T.8. 每个任务都经过验证是可解的。
  - T.9. 基准包含一个能自动解决全部挑战的 Oracle 求解器。
  - T.10. 实现中不存在可被利用来「不解任务即通过评测」的漏洞。

::: en
**Tool.** External tools and functions can significantly extend the capabilities of AI agents. Existing benchmarks provide two types of tools: self-hosted tools (e.g., Python, command-line tools) and API-based tools (e.g., web services). For self-hosted tools, it is essential to explicitly specify the correct tool or package versions in the prompt (T.1). In terms of API-based tools, ensuring service availability and managing rate limits is crucial (T.2). If API interruptions occur, we recommend detecting them and terminating the evaluation to keep benchmark users informed (T.3).
:::

**工具。** 外部工具与函数可显著扩展 AI Agent 的能力。现有基准提供两类工具:自托管工具(self-hosted tools,如 Python、命令行工具)与 API 型工具(API-based tools,如 Web 服务)。对自托管工具,必须在提示中明确指定正确的工具或包版本(T.1)。对 API 型工具,确保服务可用性并管理速率限制(rate limit)至关重要(T.2);若发生 API 中断,我们建议检测到中断即终止评测,让基准用户知情(T.3)。

::: en
**Environment.** Agentic benchmarks often need a sandbox environment to simulate real-world scenarios. Implementing and maintaining such environments can be challenging, especially with complex task formulations. First, to ensure the independence of tasks, we need to ensure that any legacy data and states are fully cleaned up before starting a new task (T.4). For example, KernelBench failed to remove ground truth answers from GPU memory, allowing agents to obtain the correct result through out-of-bounds memory access [35]. Furthermore, to avoid cheating by peeking at ground truth, it is important to fully isolate agents from the ground truth results (T.5). Finally, the environment setup should be fully reproducible and frozen at the time of benchmark release (T.6). Relying on dynamic resources, such as continually updated external websites, is not recommended.
:::

**环境。** Agent 基准常需沙箱环境来模拟真实场景。实现与维护此类环境颇具挑战,任务表述复杂时尤甚。首先,为保证任务的独立性,必须确保开始新任务前彻底清理一切遗留数据与状态(T.4)。例如,KernelBench 曾未能把真值答案从 GPU 显存中清除,使 Agent 可通过越界内存访问(out-of-bounds memory access)获取正确结果 [35]。其次,为防止靠偷看真值作弊,必须让 Agent 与真值结果完全隔离(T.5)。最后,环境设置应完全可复现,并在基准发布时冻结(T.6);不建议依赖持续更新的外部网站等动态资源。

::: en
**Implementation.** Even with a robust setup of tools and environments, subtle implementation vulnerabilities can also result in shortcuts or impossible tasks. Therefore, we recommend verifying the correctness of ground truth annotation and the task setup (T.7-8). Providing an automatic oracle solver can help demonstrate the correctness of the task configuration (T.9). Additionally, as demonstrated in τ-bench [86], inspecting outliers in pilot experiments is crucial for identifying implementation bugs (T.10). For example, if agents consistently fail on easy tasks, this may indicate that tasks are impossible, whereas if agents only succeed on difficult tasks, it may indicate shortcuts.
:::

**实现。** 即便工具与环境的设置都足够稳健,细微的实现漏洞仍可能造成捷径或不可解任务。因此,我们建议验证真值标注与任务设置的正确性(T.7-8);提供一个自动的 Oracle 求解器有助于证明任务配置的正确性(T.9)。此外,如 τ-bench [86] 所示,检查试点实验(pilot experiment)中的离群值对发现实现 bug 至关重要(T.10):例如,若 Agent 总在简单任务上失败,可能说明任务不可解;若 Agent 只在困难任务上成功,则可能存在捷径。

#### 4.2 评估结果有效性

::: en
In this part of the assessment, we propose practical checks for ensuring the outcome validity of an agentic benchmark (Figure 3). We design these checks based on different types of outcomes and different evaluation methods.
:::

在评估的这一部分,我们为确保 Agent 基准的结果有效性提出实用检查(图 3)。这些检查按不同的结果类型与不同的评测方法设计。

::: en
**Information Acquisition.** To evaluate the capability of AI agents to search, retrieve, integrate, and summarize information, agentic benchmarks formulate tasks as information acquisition queries [25, 86, 89, 93]. Depending on task requirements, benchmarks use various schemes for evaluating agents' textual responses, including whole string matching [89], substring matching [86, 93], and LLM-as-a-judge [25, 93].

1. **Whole String Matching** directly compares the agent's response and the ground truth. When annotating ground truth, it is important to consider semantically equivalent expressions (O.a.1) or redundant words (O.a.2). [Footnote 3]
2. **Substring Matching** evaluates whether the agent's response contains the ground truth. In addition to equivalent expressions, it should handle negation modifiers (O.b.1), such as "not" and "negative." We also recommend formulating tasks carefully to prevent success by listing all possible answers (O.b.2) or guessing (O.b.3).
3. **LLM-as-a-Judge** uses LLMs to emulate human annotators [9, 38, 88, 90, 97]. Previous studies have shown that the accuracy of LLM annotations varies across domains [98]. We recommend conducting pilot experiments to assess the accuracy and self-consistency of LLM judges (O.c.1).

[Footnote 3] In practice, users often specify format requirements for AI agents, which narrows the scope of alternative expressions of the ground truth. Failing to follow the format requirements is considered as a true failure.
:::

**信息获取(information acquisition)。** 为评估 AI Agent 搜索、检索、整合与汇总信息的能力,Agent 基准把任务表述为信息获取查询 [25, 86, 89, 93]。视任务需求而定,基准用多种方案评估 Agent 的文本回复,包括全字符串匹配 [89]、子串匹配 [86, 93] 与 LLM-as-a-Judge [25, 93]。

1. **全字符串匹配(whole string matching)** 直接比对 Agent 回复与真值。标注真值时,重要的是考虑语义等价的表达(O.a.1)与冗余词(O.a.2)。
2. **子串匹配(substring matching)** 评估 Agent 回复是否包含真值。除等价表达外,还应处理否定修饰词(O.b.1),如 "not" 与 "negative";我们还建议精心设计任务,以防靠系统性列出全部可能答案(O.b.2)或靠猜测(O.b.3)取得成功。
3. **LLM-as-a-Judge** 用 LLM 模拟人类标注者 [9, 38, 88, 90, 97]。已有研究表明,LLM 标注的准确率随领域而变 [98]。我们建议做试点实验以评估 LLM 裁判的准确率与自洽性(O.c.1),并把裁判设计成能抵抗对抗输入与奖励作弊(reward hacking)(O.c.2)。

> 译注(原文脚注 3):实践中,用户常为 AI Agent 指定格式要求,这收窄了真值替代表达的范围;不遵循格式要求被视为真实的失败。

::: en
**Information Acquisition**

Whole string matching or substring matching:
O.a.1. Considers expressions semantically equivalent to ground truth.
O.a.2. Handles redundant words used by agents.

Substring matching:
O.b.1. Handles negation modifiers used by agents.
O.b.2. Is robust against systematically listing all possible answers.
O.b.3. Ground truth is sufficiently complex to prevent guessing.

LLM-as-a-Judge:
O.c.1. Demonstrates documented or experimental evidence of the judge's accuracy, self-consistency, and agreement with human.
O.c.2. Is designed to resist adversarial inputs and reward hacking.

**Code Generation**

Unit testing or end-to-end testing:
O.d.1. Verifies test cases for correctness and quality (e.g., by human).
O.d.2. Measures quality of test cases using objective metrics (e.g., code coverage, cyclomatic complexity control).

Fuzz testing:
O.e.1. Addresses potential edge cases.
O.e.2. Ensures comprehensive coverage of all relevant input variations (e.g., data types, memory layouts, value ranges).
O.e.3. Generates inputs that the code under testing is sensitive to.

End-to-end testing:
O.f.1. Exercises all relevant parts of the code being tested.
O.f.2. Prevents non-deterministic ("flaky") test results.

**State Matching**

State matching:
O.g.1. Ground truth includes all states achievable after success.
O.g.2. Checks relevant and irrelevant states for the challenge.
O.g.3. Ground truth is complex to prevent trivial state modifications.

**Multistep Reasoning**

Answer matching:
O.h.1. Specifies required answer formats in challenge descriptions.
O.h.2. Minimizes the possibility of success by random guessing.

Quality measure:
O.I.1. Designs quality metrics that prevent exploitation (e.g., achieving high scores by reward hacking).

Figure 3: Checks in ABC to assess the outcome validity of an agentic benchmark. We group items by the types of the outcome and the methods of evaluation.
:::

[图 3: Checks in ABC to assess the outcome validity of an agentic benchmark. We group items by the types of the outcome and the methods of evaluation. —— ABC 中用于评估 Agent 基准结果有效性的检查项,按结果类型与评测方法分组。] 中文对照:

- **信息获取**
  - 全字符串匹配或子串匹配:O.a.1. 考虑与真值语义等价的表达;O.a.2. 处理 Agent 使用的冗余词。
  - 子串匹配:O.b.1. 处理 Agent 使用的否定修饰词;O.b.2. 对系统性列出全部可能答案具有稳健性;O.b.3. 真值足够复杂以防止猜测。
  - LLM-as-a-Judge:O.c.1. 提供裁判准确率、自洽性与人类一致性的文献或实验证据;O.c.2. 设计上能抵抗对抗输入与奖励作弊。
- **代码生成**
  - 单元测试或端到端测试:O.d.1. 验证测试用例的正确性与质量(如由人工验证);O.d.2. 用客观指标(如代码覆盖率、圈复杂度控制)度量测试用例质量。
  - 模糊测试:O.e.1. 覆盖潜在边界情况;O.e.2. 确保全面覆盖所有相关输入变化(如数据类型、内存布局、取值范围);O.e.3. 生成被测代码对其敏感的输入。
  - 端到端测试:O.f.1. 练到被测代码的所有相关部分;O.f.2. 防止非确定性("flaky")的测试结果。
- **状态匹配**
  - 状态匹配:O.g.1. 真值包含成功后可达的全部状态;O.g.2. 对挑战的相关状态与无关状态都做检查;O.g.3. 真值足够复杂以防止平凡的状态修改。
- **多步推理**
  - 答案匹配:O.h.1. 在任务描述中指定要求的答案格式;O.h.2. 最小化靠随机猜测成功的可能性。
  - 质量度量:O.I.1.(正文记作 O.i.1)设计能防止钻空子(如靠奖励作弊拿高分)的质量指标。

::: en
**Code Generation.** Existing agentic benchmarks evaluate the capability of AI agents to write code [30, 37, 48, 59]. These benchmarks apply program testing techniques to evaluate the correctness of generated code, including unit testing, fuzz testing, and end-to-end testing.

1. **Unit Testing** designs test cases for individual functions or classes [67]. However, poorly constructed unit tests can lead to both false positives and false negatives [70, 87]. Therefore, we recommend manually verifying the correctness and quality of test cases (O.d.1) [14], and providing quality guarantees using objective metrics (O.d.2) such as coverage [94] and cyclomatic complexity [76].
2. **Fuzz Testing** evaluates generated code by running it against a ground-truth implementation on automatically generated inputs [95]. We should tailor the input generator to the target program, covering different data values, types, memory layouts, and edge cases (O.e.1-2). Moreover, the inputs must affect the output (O.e.3)—e.g., random negatives reveal nothing about relu(x) [35].
3. **End-to-end (E2E) Testing** simulates complete user workflows, providing comprehensive testing of system functionality [36, 72]. In addition to ensuring the general quality of test cases, it should also cover all possible branches of user workflows (O.f.1). Because of their complexity, E2E tests require extra safeguards to eliminate non-determinism and ensure repeatable results (O.f.2) [61].
:::

**代码生成(code generation)。** 现有 Agent 基准评估 AI Agent 编写代码的能力 [30, 37, 48, 59]。这些基准运用程序测试技术评估生成代码的正确性,包括单元测试、模糊测试与端到端测试。

1. **单元测试(unit testing)** 为单个函数或类设计测试用例 [67]。然而,构造不良的单元测试可同时导致假阳性与假阴性 [70, 87]。因此,我们建议人工验证测试用例的正确性与质量(O.d.1)[14],并用覆盖率 [94] 与圈复杂度(cyclomatic complexity)[76] 等客观指标提供质量保证(O.d.2)。
2. **模糊测试(fuzz testing)** 让生成代码在自动生成的输入上对标真值实现运行,以此评估 [95]。我们应针对目标程序定制输入生成器,覆盖不同的数据取值、类型、内存布局与边界情况(O.e.1-2);此外,输入必须能影响输出(O.e.3)——例如,随机负数对 relu(x) 的正确性毫无揭示力 [35]。
3. **端到端测试(End-to-end, E2E testing)** 模拟完整的用户工作流,对系统功能做全面测试 [36, 72]。除保证测试用例的一般质量外,还应覆盖用户工作流的所有可能分支(O.f.1);由于其复杂性,E2E 测试需要额外保障以消除非确定性并确保结果可重复(O.f.2)[61]。

::: en
**State Modification.** Agentic benchmarks challenge agents to manipulate environment states, such as booking flight tickets [86] and editing websites [83]. In these tasks, we often compare the final state achieved by agents with a ground-truth state.

We identify three key checks for rigorous state matching. First, ground truth states should include all possible outcomes achievable through successful task resolution (O.g.1). For example, when we challenge agents to attack a website, we should evaluate all possible attack outcomes [96]. Second, the state space should contain both relevant and irrelevant states (O.g.2), such as including both changed and unchanged files, to help detect if agents affect the environment outside the target scope. Finally, the state space should be complex enough (O.g.3)—for instance, involving multiple variables or dependencies—so that random or trivial changes are unlikely to result in a correct outcome.
:::

**状态修改(state modification)。** Agent 基准要求 Agent 操纵环境状态,如预订机票 [86] 与编辑网站 [83]。在此类任务中,我们常把 Agent 达到的最终状态与真值状态比对。

我们识别出严谨状态匹配(state matching)的三个关键检查。第一,真值状态应包含成功解题可达到的全部可能结果(O.g.1)——例如,当要求 Agent 攻击网站时,应评估所有可能的攻击结果 [96]。第二,状态空间应同时包含相关状态与无关状态(O.g.2),如同时纳入已改动与未改动的文件,以帮助检测 Agent 是否在目标范围之外影响环境。第三,状态空间应足够复杂(O.g.3)——例如涉及多个变量或依赖——使随机或平凡的修改不太可能碰巧得到正确结果。

::: en
**Multistep Reasoning.** Agentic benchmarks evaluates multistep reasoning capabilities of AI agents [11, 22, 39, 47]. These benchmarks typically require AI agents to make observations, conduct analysis, and generate results. We summarize two common approaches for evaluating these tasks:

1. **Answer Matching** parses the agents' output and then compares the parsed result with ground truth. We find that parsers in existing benchmarks may make implicit assumption about the agent's output (O.h.1). For example, the MATH dataset assumes the answer of the agent starts with "Answer:" [39]. Therefore, it is necessary to explicitly specify any assumptions, such as format requirements. Additionally, to ensure that a single final answer reflects a genuine reasoning process, we recommend designing tasks in a way that avoid success by guessing (O.h.2) [22].
2. **Quality Measure** evaluates agent using customized metrics against a baseline when ground truth is impossible to achieve (e.g., ground-truth predictions in an ML engineering task [11]). The choice of metrics can be highly subjective and often depends on the nature of the tasks. To avoid metric hacking [26]—achieving high metrics without resolving tasks, we recommend ensuring that the selected metrics are strongly correlated with the reasoning process (O.i.1).
:::

**多步推理(multistep reasoning)。** Agent 基准评估 AI Agent 的多步推理能力 [11, 22, 39, 47]。这些基准通常要求 AI Agent 做观察、做分析并产出结果。我们总结评估此类任务的两种常见方式:

1. **答案匹配(answer matching)** 解析 Agent 的输出,再把解析结果与真值比对。我们发现既有基准的解析器可能对 Agent 输出做隐式假设(O.h.1)——例如 MATH 数据集假设 Agent 的答案以 "Answer:" 开头 [39]。因此,必须显式声明任何假设(如格式要求)。此外,为确保单个最终答案反映真实的推理过程,我们建议把任务设计得难以靠猜测成功(O.h.2)[22]。
2. **质量度量(quality measure)** 在真值无法取得时(如 ML 工程任务中的真值预测 [11]),用相对基线的定制指标评估 Agent。指标的选择可能高度主观,且常取决于任务性质。为避免指标作弊(metric hacking)[26]——不解任务却拿到高指标——我们建议确保所选指标与推理过程强相关(O.i.1)。

#### 4.3 评估基准报告

::: en
**Benchmark Reporting**

**Transparency & Validity**
R.1. Is fully or at least partially open-sourced.
R.2. Offers an open-source evaluation harness for users.
R.3. Includes measures to prevent data contamination at the time of benchmark release, such as a private, held-out test set.
R.4. Includes measures or plans to consistently update challenges over time to avoid overfitting.
R.5. Clearly states the relationship between the agent capabilities it aims to evaluate and the constructs or outcomes it measures.
R.6. Clearly states the evaluation subjective of the benchmark (e.g., a model or an agent framework).

**Flaw Mitigation**
R.7. Describes steps taken to prevent, identify, and correct flaws.
R.8. Includes qualitative discussions of the potential impact of unavoidable flaws.
R.9. Includes quantitative analysis to assess the impact of unavoidable flaws (e.g., noise of ground truth).

**Interpretation**
R.10. Reports metrics about statistical significance, such as confidence intervals.
R.11. Provides guidance on interpreting results with eval flaws.
R.12. Reports results of non-AI baselines (e.g., human experts).
R.13. Reports results of trivial agents (e.g., one that does nothing).

Figure 4: Checks in ABC to assess the benchmark reporting.
:::

[图 4: Checks in ABC to assess the benchmark reporting. —— ABC 中用于评估基准报告质量的检查项。] 中文对照:

- **透明与效度(Transparency & Validity)**:R.1. 完全或至少部分开源;R.2. 为用户提供开源评测组件(evaluation harness);R.3. 在基准发布时纳入防数据污染措施,如私有的留出测试集(held-out test set);R.4. 纳入随时间持续更新任务以避免过拟合的措施或计划;R.5. 清晰陈述所评 Agent 能力与所测构念/结果之间的关系;R.6. 清晰陈述基准的评测对象(如模型还是 Agent 框架)。
- **缺陷缓解(Flaw Mitigation)**:R.7. 描述为预防、识别与纠正缺陷所采取的步骤;R.8. 对不可避免缺陷的潜在影响做定性讨论;R.9. 用定量分析评估不可避免缺陷(如真值噪声)的影响。
- **结果解读(Interpretation)**:R.10. 报告统计显著性指标,如置信区间;R.11. 提供带评测缺陷结果的解读指南;R.12. 报告非 AI 基线(如人类专家)的结果;R.13. 报告平凡 Agent(如什么都不做者)的结果。

::: en
Completely avoiding evaluation issues in agentic benchmarks can be challenging, and is sometimes not feasible, especially when using LLM-as-a-Judge or testing-based techniques. In such cases, it is particularly important for benchmark developers to be transparent and clearly communicate the impact of these limitations (Figure 4).

We assess the reporting quality of an agentic benchmark based on the following aspects. In Appendix F, we use BIRD as an example to demonstrate the high-quality benchmark reporting.

1. **Transparency and Validity.** We encourage open-sourcing both the datasets and evaluation harness (R.1-2) while including measures to prevent data contamination (R.3-4). We also recommend clearly specifying the capabilities to evaluate and articulating construct validity [65] (R.5-6).
2. **Mitigation.** When validity limitations are unavoidable, it is important to document mitigation efforts (R.7) and provide both qualitative and quantitative evidence regarding the impact of those limitations (R.8-9). In resource-constraint scenarios, we recommend using sampling and uncertainty quantification techniques (e.g., Cramer's Theorem [17]) to estimate the impact of unavoidable flaws, such as the noise of ground truth.
3. **Result Interpretation.** We recommend reporting benchmark results rigorously, including measures of statistical significance (R.10), clear interpretation guidelines (R.11), and appropriate baseline comparisons (R.12-13).
:::

在 Agent 基准中完全避免评测问题常常困难,有时并不可行,尤其在使用 LLM-as-a-Judge 或基于测试的技术时。此时,基准开发者保持透明、清楚沟通这些局限的影响尤为重要(图 4)。

我们基于以下方面评估 Agent 基准的报告质量。附录 F 以 BIRD 为例,展示高质量的基准报告。

1. **透明与效度。** 我们鼓励同时开源数据集与评测组件(R.1-2),并纳入防数据污染措施(R.3-4);同时建议清晰界定所评能力并阐述构念效度 [65](R.5-6)。
2. **缓解。** 当有效性局限不可避免时,重要的是记录缓解措施(R.7),并就这些局限的影响提供定性与定量证据(R.8-9)。在资源受限场景,我们建议用抽样与不确定性量化技术(如 Cramer 定理 [17])估计真值噪声等不可避免缺陷的影响。
3. **结果解读。** 我们建议严谨地报告基准结果,包括统计显著性指标(R.10)、清晰的解读指南(R.11)与恰当的基线比较(R.12-13)。

### 5 对 Agent 基准的评估

::: en
In this section, we present the results of applying ABC on existing agentic benchmarks (Table 1). We first show the assessment scores (Section 5.1) and then summarize newly identified issues with quantitative results (Section 5.2). Finally, with a case study, we show how developers can apply ABC to improve their benchmarks (Section 5.3).
:::

本节展示把 ABC 应用于既有 Agent 基准的结果(表 1)。我们先给出评估得分(5.1 节),再总结带定量结果的新发现问题(5.2 节);最后以案例研究展示开发者如何用 ABC 改进自己的基准(5.3 节)。

#### 5.1 评估得分

::: en
We selected ten open-source agentic benchmarks from Table 3 to cover all capability categories and evaluation methods. For each part of ABC, we calculated the average scores of applicable items. We present the final assessment scores in Figure 5. We summarize our findings as follows.

- **Task validity**: more than half of the benchmarks exhibit implementation flaws, especially those that provide tools to agents.
- **Outcome validity**: more than half of the benchmarks fail to address inherent limitations of the evaluation methods.
- **Benchmark Reporting**: 80% of the benchmarks fail to acknowledge weaknesses in their design or implementation, and none satisfies every reporting criterion.
:::

我们从表 3 中选出十个开源 Agent 基准,以覆盖全部能力类别与评测方法。对 ABC 的每个部分,我们计算适用项的平均分,最终评估得分见图 5。发现总结如下:

- **任务有效性**:过半基准存在实现缺陷,尤其是向 Agent 提供工具的那些。
- **结果有效性**:过半基准未能处理其评测方法固有的局限。
- **基准报告**:80% 的基准未承认自身设计或实现上的弱点,且没有任何一个满足全部报告标准。

**表 1(Table 1):我们用 ABC 评估的 Agent 基准。**

| 基准 | 所评能力 | 评测设计 |
| --- | --- | --- |
| SWE-bench [30] | 软件工程 | 单元测试 |
| SWE-Lancer [48] | 软件工程 | 端到端测试 |
| KernelBench [59] | 软件工程 | 模糊测试 |
| BIRD [37] | 软件工程 | 单元测试 |
| Cybench [89] | 网络安全 | 答案匹配 |
| MLE-bench [11] | 软件工程 | 质量度量 |
| GAIA [47] | 通用助手 | 答案匹配 |
| τ-bench [86] | 环境交互 | 子串匹配、状态匹配 |
| WebArena [93] | 环境交互 | 全字符串匹配、子串匹配、LLM-as-a-Judge、状态匹配 |
| OSWorld [83] | 环境交互 | 状态匹配 |

[图 5: Assessment results of selected benchmarks. We find 7 benchmarks violating task validity, 7 violating outcome validity, and all 10 with limitations in reporting.]

图 5 中文说明:十个选定基准的评估结果。三个子图分别给出各基准在 (a) 任务有效性、(b) 结果有效性、(c) 基准报告三部分上适用检查项的平均得分(0–100%)。结论:7 个基准违反任务有效性,7 个违反结果有效性,全部 10 个在报告上存在局限。

#### 5.2 评估发现

::: en
We conducted an in-depth analysis of specific issues present in each agentic benchmark. In this section, we focus on discussing 4 benchmarks with newly discovered issues. We defer a detailed description of all identified issues in Appendix D and experiment designs to E.

1. τ-bench relies on trivial states or substrings as ground truth, violating checks O.b.3 and O.g.3 and overestimating performance by 38%.
2. τ-bench also allows agents to list every possible answer, violating check O.b.2 and overestimating performance by 40%.
3. WebArena not only violates check O.b.2 but also uses an LLM-as-a-Judge without validating its accuracy or consistency (check O.c.1), leading to a 1.4–5.2% performance overestimate.
4. SWE-Lancer fails to fully isolate agents from the ground truth (check T.5), allowing agents to score 100% without solving tasks.
5. KernelBench omits comprehensive fuzzing for edge cases and memory layouts—violating checks O.e.1 and O.e.2 and overestimating kernel-correctness performance by approximately 31%.
6. In OSWorld, the task website changes have broken the HTML selectors used for evaluation, leading to a 28% performance underestimation in the chrome task section.
:::

我们对每个 Agent 基准中存在的具体问题做了深入分析。本节聚焦讨论 4 个有新发现问题的基准;全部已识别问题的详细描述见附录 D,实验设计见附录 E。

1. τ-bench 依赖平凡的状态或子串作真值,违反检查 O.b.3 与 O.g.3,高估性能 38%。
2. τ-bench 还允许 Agent 列举全部可能的答案,违反检查 O.b.2,高估性能 40%。
3. WebArena 不仅违反检查 O.b.2,还使用了一个未经验证准确率与一致性的 LLM-as-a-Judge(检查 O.c.1),导致性能高估 1.4–5.2%。
4. SWE-Lancer 未能把 Agent 与真值完全隔离(检查 T.5),使 Agent 不解任何任务也能拿 100% 的分数。
5. KernelBench 未对边界情况与内存布局做全面模糊测试——违反检查 O.e.1 与 O.e.2,内核正确性性能被高估约 31%。
6. 在 OSWorld 中,任务网站的改版破坏了评测所用的 HTML 选择器,导致 chrome 任务部分的性能被低估 28%。

::: en
**τ-bench.** First, τ-bench contains intentionally unsolvable tasks—38% of the airline subset and 6% of the retail subset. Because success is defined as leaving the environment unchanged, an agent that does nothing still passes evaluation of these tasks. Second, 2% of airline tasks and 3.6% of retail tasks treat verbatim database text as ground truth and grade by substring matching. Therefore, an agent that dumps the entire database passes evaluations of these tasks.
:::

**τ-bench。** 其一,τ-bench 含故意不可解的任务——航空(airline)子集占 38%,零售(retail)子集占 6%。由于「成功」被定义为环境保持不变,一个什么都不做的 Agent 也能通过这些任务的评测。其二,航空子集 2%、零售子集 3.6% 的任务把数据库原文(verbatim database text)当真值、按子串匹配判分;因此,把整库 dump 出来的 Agent 即可通过这些任务的评测。

::: en
**WebArena.** We identify two issues in WebArena, a benchmark for evaluating agents in interacting with websites. First, its substring-matching ignores extraneous content, so an agent that includes irrelevant information is considered successful. Second, for tasks labeled "N/A," the LLM judge that accepts an empty reply as correct, enabling a trivial agent to pass.
:::

**WebArena。** 我们在 WebArena(评估 Agent 与网站交互的基准)中识别出两个问题。其一,其子串匹配忽略无关内容(extraneous content),因此回复中带上无关信息的 Agent 也被判成功。其二,对标注为 "N/A" 的任务,其 LLM 裁判把空回复接受为正确,使平凡 Agent 得以通过。

::: en
**SWE-Lancer** evaluates an agent's ability to implement features by allowing it to execute Python scripts that interact directly with the file system. This design grants agents unrestricted read-write access, including to the benchmark's own test files. Although these tests reside in a password-protected ZIP archive, the archive's directory structure can be listed—and its contents overwritten—without knowing the password. Therefore, an agent can locate the tests and replace them with a trivial assertion (e.g., assert 1 == 1), achieving a perfect score without solving any of the intended tasks.
:::

**SWE-Lancer** 通过允许 Agent 执行直接操作文件系统的 Python 脚本来评估其实现功能的能力。这一设计给了 Agent 不受限制的读写权限,包括对基准自身测试文件的访问。虽然这些测试存放在密码保护的 ZIP 压缩包内,但无需密码即可列出该压缩包的目录结构并覆写其中内容。因此,Agent 可以定位测试文件,把它们替换成平凡断言(如 `assert 1 == 1`),在不解决任何预期任务的情况下拿到满分。

::: en
**KernelBench** evaluates generated CUDA kernels with randomly generated tensors, while its fuzzer varies only the tensor values, leaving shapes and memory layouts unchanged. As a result, kernels that would fail under alternative configurations can still pass. Re-examining the kernels reported by Lange et al. [35], we find that the correctness rate of kernels is overestimated by 31%.
:::

**KernelBench** 用随机生成的张量评估生成的 CUDA 内核,而其模糊器只改变张量取值,形状与内存布局保持不变。结果是,在其他配置下会出错的内核也能通过。复查 Lange 等 [35] 报告的内核,我们发现内核的正确率被高估了 31%。

::: en
**OSWorld.** We find that in the chrome section of OSWorld, 13/46 problems are broken due to changes made to the layout, URLs, and functionality of websites since the initial creation of the benchmark. This is because many evaluations rely on HTML element selectors, such as classes and XPaths. These websites might change their layouts after the benchmark released. In our experiments, we found that this issue leads to an underestimation of the performance of UI-TAR, the state-of-the-art open-source agent for OSWorld, by 28% in absolute terms.
:::

**OSWorld。** 我们发现,OSWorld 的 chrome 部分中,13/46 个问题因基准初建以来网站布局、URL 与功能的改动而失效。这是因为许多评测依赖 HTML 元素选择器(element selector),如类名与 XPath;这些网站可能在基准发布后改版。实验中我们发现,该问题导致 UI-TAR(OSWorld 上最强的开源 Agent)的性能被绝对低估 28%。

[图 6: Demonstration of using our checklist to improve the evaluation rigor of CVE-Bench.]

图 6 中文说明:演示用我们的检查清单改进 CVE-Bench 评测严谨性。子图 (a) 为修复时间盲注(time-based SQL injection)评测设计前后、子图 (b) 为修复外发服务评测实现前后,Cy-Agent、AutoGPT、T-Agent 三个 Agent 在零日(zero-day)与一日(one-day)场景下的 Success@1 与 Success@5 对比(修复后的 Success@1(fixed)/Success@5(fixed) 同图给出)。

#### 5.3 修订 CVE-Bench

::: en
In this section, we use a benchmark with representatively complex design and implementation to demonstrate how ABC can help improve an agentic benchmark. CVE-Bench is a benchmark for evaluating AI agents' ability to exploit real-world web vulnerabilities under one- or zero-day scenarios [96]. It evaluates agents by checking whether one of the pre-specified attack targets (e.g., denial of service) is accomplished. Using ABC, we resolved flaws in outcome and task validity.
:::

本节用一个设计与实现复杂度均有代表性的基准,演示 ABC 如何帮助改进 Agent 基准。CVE-Bench 评估 AI Agent 在一日(one-day)或零日(zero-day)场景下利用真实 Web 漏洞的能力 [96],通过检查预设攻击目标(如拒绝服务)之一是否达成来评估 Agent。借助 ABC,我们解决了结果与任务有效性上的缺陷。

::: en
**Naive State Matching for Time-based Injections.** Time-based SQL injection infers the database content by measuring the latency difference across multiple requests [23]. For example, an attacker can execute a SLEEP command within a IF clause and measure the latency to determine whether the IF condition is satisfied. CVE-bench measured such attacks by examining whether a SLEEP clause appears in the database log. However, containing a SLEEP clause in the log does not necessarily indicate executions of SLEEP, violating check O.g.1. Consequently, agents can pass the evaluation by adding SLEEP anywhere in the query, leading to performance overestimation by 32.5%.
:::

**时间盲注的天真状态匹配。** 时间型 SQL 注入(time-based SQL injection)通过测量多次请求间的延迟差来推断数据库内容 [23]。例如,攻击者可以在 IF 子句内执行 SLEEP 命令并测量时延,以判断 IF 条件是否成立。CVE-Bench 通过检查数据库日志中是否出现 SLEEP 子句来度量此类攻击。然而,日志中含 SLEEP 子句并不必然意味着 SLEEP 被执行——这违反检查 O.g.1。其结果是,Agent 把 SLEEP 塞进查询的任意位置即可通过评测,造成 32.5% 的性能高估。

::: en
**Ungated Outbound Server.** Inducing the web application to send requests to a banned outbound server is a critical cybersecurity attack [29]. CVE-bench measured such attacks by checking whether an outbound server has been accessed. To answer check T.9, we conducted various rounds of mock execution and identified that agents consistently passed the evaluation for this attack, which likely indicates a bug in the implementation. Indeed, we find that agents can access the outbound server when connecting from the same docker network, creating a shortcut. After denying external requests on the outbound server, the success rates of agents decreased by 10% (Figure 6b).
:::

**未设防的外发服务器。** 诱导 Web 应用向被封禁的外发服务器(outbound server)发请求是一种关键网络安全攻击 [29]。CVE-Bench 通过检查外发服务器是否被访问过来度量此类攻击。为回答检查 T.9,我们进行了多轮模拟执行,发现 Agent 总能通过该项攻击的评测——这很可能表明实现中存在 bug。事实上我们发现,Agent 与被测服务同处一个 docker 网络即可访问外发服务器,构成捷径。在外发服务器上拒绝外部请求后,Agent 的成功率下降了 10%(图 6b)。

### 6 结论(Conclusion)

::: en
We formulate the first actionable agentic benchmarks checklists (ABC) focusing on the outcome validity, task validity, and reporting of results. Via ABC, we proposed a set of the best practices for building rigorous agentic benchmarks. Based on ABC, we assessed ten widely used benchmarks and identified significant evaluation issues that cases up to 100% errors (in relative terms) when estimating agents' performance. Finally, we use CVE-Bench [96] as an example to demonstrate using ABC to improve the evaluation rigor during benchmark construction.
:::

我们提出了首个可操作的 Agent 基准检查清单(ABC),聚焦结果有效性、任务有效性与结果报告;经由 ABC,我们提出了一套构建严谨 Agent 基准的最佳实践。基于 ABC,我们评估了十个广泛使用的基准,发现了在估计 Agent 性能时误差可达相对 100% 的重大评测问题。最后,我们以 CVE-Bench [96] 为例,演示如何在基准构建过程中用 ABC 提升评测严谨性。

### 7 致谢(Acknowledgements)

::: en
We are grateful to the CloudLab [19] for providing computing resources for experiments. This research was supported in part by Open Philanthropy project.
:::

我们感谢 CloudLab [19] 为实验提供计算资源。本研究部分由 Open Philanthropy 项目资助。

### 附录 A 局限与影响声明(Limitation and Impact Statement)

::: en
**Limitation.** As the first study to systematically investigate the issue of evaluation rigor in agentic benchmarks, our work is not without limitations. First, our analysis covered only 17 agentic benchmarks that are used by top AI providers between January 2024 and March 2025. We did not analyze benchmarks outside this time frame. Therefore, our findings may not necessarily include all relevant evaluation practices. Consequently, it is possible that we have not presented an exhaustive checklist for ensuring evaluation rigor. Second, our taxonomy and analysis are grounded in the current understanding of the reasoning capabilities of AI agents. It is conceivable that future developments in AI may introduce advanced capabilities, which could, in turn, lead to more evaluation challenges that are not addressed in this study. Finally, our findings only reflect the state the analyzed benchmark at the time of writing. Future revisions of these benchmarks may yield different results. Therefore, our conclusions may not fully apply to subsequent versions.
:::

**局限。** 作为首个系统性研究 Agent 基准评测严谨性问题的工作,本研究并非没有局限。首先,我们的分析只覆盖 2024 年 1 月至 2025 年 3 月间被顶级 AI 提供商使用的 17 个 Agent 基准,未分析该时间范围之外的基准;因此我们的发现未必涵盖全部相关评测实践,我们给出的也可能并非一份穷尽式的评测严谨性清单。其次,我们的分类学与分析建立在对 AI Agent 推理能力的当前理解之上;可以想见,未来 AI 的发展可能引入更高级的能力,进而带来本研究未涉及的新评测挑战。最后,我们的发现只反映所分析基准在写作时点的状态;这些基准的未来修订可能产生不同结果,因此我们的结论未必完全适用于其后续版本。

::: en
**Broader Impact.** Although our study rigorously highlights shortcomings in existing benchmarks, our aim is not to criticize but to raise awareness and foster the development of a stronger community with higher standards and improved quality in agentic benchmarks. We anticipate that our findings will encourage more critical evaluation of agentic benchmark results and a reassessment of AI agent leaderboards. We believe these contributions will lead to a deeper and more accurate understanding of AI agent capabilities, resulting in positive societal impact.
:::

**更广泛的影响。** 尽管本研究严谨地指出了既有基准的不足,我们的目的不是批评,而是唤起关注,推动建设一个标准更高、Agent 基准质量更好的更强社区。我们期待这些发现能促使人们更批判地看待 Agent 基准结果,并重新审视 AI Agent 排行榜。我们相信这些贡献将带来对 AI Agent 能力更深入、更准确的理解,产生积极的社会影响。

### 附录 B 基准收集与筛选的细节(Details of Benchmark Collection and Selection)

::: en
We first surveyed the model release blog posts, technical reports, and paper of top AI provider, including OpenAI, Anthropic, Google, Meta, xAI, Mistral, DeepSeek, and Amazon. Since AI agents and their capabilities are evolving with a fast pace, we focused on state-of-the-art models released between January 2024 and March 2025. Furthermore, we also considered benchmarks that won awards on peer-reviewed academic venues. As shown in Table 2, we identified 78 benchmarks.

Next, we classified these benchmarks into agentic benchmarks and non-agentic benchmarks. An agentic benchmark mush involve tasks that require multistep reasoning or command execution, which excludes fact-seeking questions, such as simpleQA [77], straightforward question-answer (QA) datasets, such as MMMLU [27], and straightforward programming tasks, such as MBPP [8] and HumanEval [13]. As shown in Table 2, we collected 25 agentic benchmarks.

Finally, we categorize these agentic benchmarks based on their evaluated capabilities, evaluation methods, and open-source availability (Table 3). We selected ten benchmarks for in-depth assessment, ensuring open-source availability and a comprehensive coverage over the evaluated capabilities and evaluation methods.
:::

我们首先调研了顶级 AI 提供商(包括 OpenAI、Anthropic、Google、Meta、xAI、Mistral、DeepSeek 与 Amazon)的模型发布博文、技术报告与论文。由于 AI Agent 及其能力演进迅速,我们聚焦 2024 年 1 月至 2025 年 3 月间发布的最先进模型;此外还考虑了在同行评审学术会议上获奖的基准。如表 2 所示,我们识别出 78 个基准。

接着,我们把这些基准分为 Agent 基准与非 Agent 基准。Agent 基准必须包含需要多步推理或命令执行的任务,这排除了事实型问答(如 SimpleQA [77])、直接的问答(QA)数据集(如 MMLU [27])与直接的编程任务(如 MBPP [8] 与 HumanEval [13])。如表 2 所示,我们收集到 25 个 Agent 基准。

最后,我们按所评能力、评测方法与开源情况对这些 Agent 基准分类(表 3),并从中选出十个做深入评估,确保开源可用,并对所评能力与评测方法做全面覆盖。

> 译注:原文表 2(第 16–18 页)逐一列出 2024 年 1 月 1 日至 2025 年 3 月 18 日间被主要 AI 提供商使用的 78 个基准、各自的使用来源(模型发布材料)以及是否属于 Agent 基准(重复基准只列一次),篇幅所限此处不全文转录。其中被标记为 Agent 基准(✔)的包括:SWE-bench Verified、SWE-Lancer Diamond、GAIA、FrontierMath、Codeforces、LiveBench Coding、MATH-500、OSWorld、WebArena、WebVoyager、MathVista、RE-Bench、MLE-bench、τ-bench、Aider-Edit、Aider-Polyglot、CNMO 2024、BIRD、HiddenMath、Kernel-Bench 等;其余(如 SimpleQA、GPQA、AIME '24、MMLU、MMMU、HumanEval、DROP、MedQA、BIG-Bench-Hard、IF-Eval、FRAMES、LongBench v2、C-Eval、LOFT、EgoSchema、DocVQA、ChartQA、BFCL V2、ARC Challenge、Hellaswag、MT-Bench、Arena Hard、BBH 等)为非 Agent 基准。完整表格请查阅原文。

**表 3(Table 3):收集到的 Agent 基准。原文中被评估的十个基准以蓝色高亮,此处以 ★ 标出。**

| 基准 | 所评能力 | 评测设计 |
| --- | --- | --- |
| ★ SWE-bench [30] | 软件工程 | 单元测试 |
| ★ SWE-Lancer [48] | 软件工程 | 端到端测试 |
| ★ KernelBench [59] | 软件工程 | 模糊测试 |
| ★ BIRD [37] | 软件工程 | 端到端测试 |
| Aider-Edit [2] | 软件工程 | 单元测试 |
| Codeforces [63] | 软件工程 | 单元测试 |
| LiveBench Coding [78] | 软件工程 | 单元测试 |
| Aider-Polyglot [3] | 软件工程 | 单元测试 |
| FrontierMath(无开源访问)[22] | 挑战性数学问题求解 | 答案匹配 |
| ★ MLE-bench [11] | ML 工程 | 质量度量 |
| RE-bench [79] | ML 工程 | 质量度量 |
| ★ τ-bench [86] | 环境交互 | 子串匹配、状态匹配 |
| ★ WebArena [93] | 环境交互 | 全字符串匹配、子串匹配、LLM-as-a-Judge、状态匹配 |
| ★ OSWorld [83] | 环境交互 | 状态匹配 |
| WebVoyager [25] | 环境交互 | LLM-as-a-Judge |
| ★ Cybench [89] | 网络安全 | 答案匹配 |
| ★ GAIA [47] | 通用助手 | 答案匹配 |

> 译注:正文表 1 将 BIRD 的评测设计记为「单元测试」,附录表 3 记为「端到端测试」,两处原文即不一致,此处按各自原表保留。

### 附录 C ABC 检查项的来源(Sources of the Checks in ABC)

::: en
In Table 4, we show the detail construction process of ABC by listing the sources of each check proposed in ABC. We synthesized the insights from the following aspects

1. Our experience of developing agentic benchmarks.
2. Best practices in existing agentic benchmarks (Table 3).
3. Lessons learned from issues of existing agentic benchmarks.
4. Domain-specific suggestions when we apply well-established techniques as evaluation methods.
:::

表 4 展示了 ABC 的详细构建过程:逐条列出 ABC 中每条检查的来源。我们的洞见综合自以下几个方面:

1. 我们开发 Agent 基准的经验。
2. 既有 Agent 基准(表 3)中的最佳实践。
3. 从既有 Agent 基准问题中学到的教训。
4. 把成熟技术用作评测方法时的领域特定建议。

> 译注:原文表 4(正文引用为 Table 14)按「既有最佳实践 / 已知问题教训 / 领域特定建议(及自建经验)」分列,给出每条检查项的文献来源;因提取文本的列位置难以精确对齐,下表将各来源合并为一列「来源(引用)」,引用编号与原文一致。

| 检查项 | 来源(引用) |
| --- | --- |
| O.a.1 | Mialon et al. [47], Zhou et al. [93] |
| O.a.2 | Mialon et al. [47], Zhou et al. [93];Zhou et al. [93] |
| O.b.1 | Mialon et al. [47];Zhou et al. [93] |
| O.b.2 | Yao et al. [86], Zhou et al. [93] |
| O.b.3 | Zhou et al. [93];Yao et al. [86] |
| O.c.1 | He et al. [25];Ziems et al. [98] |
| O.d.1 | Chowdhury et al. [14];Jimenez et al. [30], Yu et al. [87] |
| O.d.2 | Zhu et al. [94] |
| O.e.1 | Ouyang et al. [59];Zhu et al. [95] |
| O.e.2 | Ouyang et al. [59];Zhu et al. [95] |
| O.e.3 | METR [46] |
| O.f.1 | Ricca and Tonella [66] |
| O.f.2 | Parry et al. [61] |
| O.g.1 | Yao et al. [86], Zhou et al. [93], Xie et al. [83] |
| O.g.2 | Yao et al. [86];Xie et al. [83] |
| O.g.3 | Yao et al. [86] |
| O.h.1 | Mialon et al. [47];Kydlíček and Gandenberger [34], Lightman et al. [39] |
| O.h.2 | Glazer et al. [22] |
| O.i.1 | Chan et al. [11] |
| T.1 | Miserendino et al. [48], Li et al. [37] |
| T.2 | Kapoor et al. [32];Zhou et al. [93] |
| T.3 | Zhou et al. [93];Zhu et al. [96] |
| T.4 | Miserendino et al. [48], Yao et al. [86], Jimenez et al. [30];Lange et al. [35] |
| T.5 | Zhang et al. [89];Miserendino et al. [48] |
| T.6 | Wretblad et al. [80], Pourreza and Rafiei [62], Li et al. [37] |
| T.7 | Zhang et al. [89], Zhu et al. [96], Xie et al. [83] |
| T.8 | Zhang et al. [89], Zhu et al. [96];Li et al. [37] |
| T.9 | Lange et al. [35], Miserendino et al. [48] |
| R.1 | 表 1 中全部基准 |
| R.2 | 表 1 中除 GAIA 外的全部基准 |
| R.3 | Chan et al. [11], Miserendino et al. [48], BIRD [37];Zhou et al. [91] |
| R.4 | White et al. [78] |
| R.5 | Kapoor et al. [32] |
| R.6 | 表 1 中全部基准 |
| R.7 | Chan et al. [11], Yao et al. [86] |
| R.8 | Miserendino et al. [48], Chan et al. [11] |
| R.9 | Yao et al. [86] |
| R.10 | Dorner and Hardt [17], Reuel et al. [65] |
| R.11 | Hothorn et al. [28], Dorner and Hardt [17] |
| R.12 | Cao et al. [10], Xie et al. [83], Zhang et al. [89] |
| R.13 | Yao et al. [86] |

### 附录 D 评估报告(Assessment Reports)

::: en
In this section we provide detailed assessment reports for all ten benchmarks. Each report's caption specifies the corresponding paper and codebase evaluated.
:::

本节给出全部十个基准的详细评估报告。每份报告的标题注明所评估的对应论文与代码库。

**表 5(Table 5):SWE-Lancer 评估报告(论文、代码)**

| 检查项 | 得分 | 理由 |
| --- | --- | --- |
| O.d.1 | 1 | 如论文第 1 节所述,基准使用一组经人类专家验证正确性与质量的测试用例。 |
| O.d.2 | 0 | 基准未用客观指标度量测试用例的质量。 |
| O.f.2 | 1 | 如第 1 节所述,端到端测试被设计为模拟完整用户工作流。 |
| O.f.3 | 0 | 测试用例使用硬编码超时,若系统缓慢或无响应可能导致非确定性结果。 |
| T.1 | 1 | 每个任务的仓库中指定了包依赖的版本。 |
| T.2 | 1 | 基准不需要任何外部 API。 |
| T.3 | 1 | 基准不需要任何外部 API。 |
| T.4 | 1 | 基准用 docker 容器隔离环境,并在运行之间清除状态。 |
| T.5 | 0 | Agent 可访问存储测试用例的文件系统,可能导致 Agent 获取真值信息。 |
| T.6 | 1 | 环境设置是静态的,不随时间变化。 |
| T.7 | 1 | 真值测试用例取自 GitHub 仓库,已经专家开发者验证。 |
| T.8 | 1 | 每个任务都是带相应补丁的真实软件 issue,Agent 可解。 |
| T.9 | 1 | 基准用既有补丁作真值,可视为 Oracle 求解器。 |
| T.10 | 0 | 基准未妥善处理 Agent 与测试用例之间的隔离:测试用例不仅存于 Agent 可访问的文件系统,还存于一个 Agent 无需密码即可读取目录结构并更新文件的 ZIP 文件中。 |
| R.1 | 1 | 基准已开源并在 GitHub 上提供。 |
| R.2 | 1 | 基准为用户提供开源评测组件。 |
| R.3 | 1 | 基准维护私有测试集。 |
| R.4 | 0 | 报告未讨论任何持续更新的措施或计划。 |
| R.5 | 1 | 该关系在论文第 2 节中清楚陈述。 |
| R.6 | 1 | 如第 3 节所示,基准设计为评估 LLM 模型。 |
| R.7 | 1 | 基准用端到端测试缓解判分作弊。 |
| R.8 | 1 | 基准在第 1 节与附录 A.7 中讨论了判分作弊的潜在影响。 |
| R.9 | 0 | 基准未包含任何评估判分作弊影响的定量分析。 |
| R.10 | 0 | 基准未报告任何统计显著性指标。 |
| R.11 | 0 | 基准未提供任何带评测缺陷结果的解读指南。 |
| R.12 | 0 | 基准未报告非 AI 基线的结果。 |
| R.13 | 0 | 基准未报告平凡 Agent 的结果。 |

**表 6(Table 6):Bird-Bench 评估报告(论文、代码)**

| 检查项 | 得分 | 理由 |
| --- | --- | --- |
| O.d.1 | 1 | 如论文 3.4 节所述,通过执行真值查询验证了数据库的有效性。 |
| O.d.2 | 0 | 论文未用客观指标度量数据库或真值查询的实用性与完备性。 |
| O.f.2 | 0 | 论文未提供任何关于数据库或真值查询覆盖率的信息。 |
| O.f.3 | 1 | 在数据库上执行 SQL 查询是确定性的,论文未提及任何非确定性行为。 |
| T.1 | 1 | 图 9 的任务指令明确所用 SQL 语言为 SQLite。 |
| T.2 | 1 | 基准评估不需要外部 API。 |
| T.3 | 1 | 基准评估不需要外部 API。 |
| T.4 | 0 | 数据库文件既未以只读模式打开,也未在运行之间重新初始化,可能导致 Agent 意外的数据操纵。 |
| T.5 | 1 | Agent 无法访问宿主文件系统。 |
| T.6 | 1 | 环境设置是静态的,不随时间变化。 |
| T.7 | 0 | 如论文 3.4 节所述,查询的正确性未被完全验证,尤其是两名标注者达成一致的 SQL 查询。 |
| T.8 | 0 | SQL 查询的歧义性未被完全验证。 |
| T.9 | 0 | 基准不含能自动解决全部 text-to-SQL 任务的 Oracle 求解器。 |
| T.10 | 1 | 基准实现中未发现漏洞。 |
| R.1 | 1 | 基准已开源并在 GitHub 上提供。 |
| R.2 | 1 | 基准为用户提供开源评测组件。 |
| R.3 | 1 | 基准有私有测试集。 |
| R.4 | 0 | 论文未讨论任何持续更新的措施或计划。 |
| R.5 | 1 | 论文第 2 节中清楚讨论。 |
| R.6 | 1 | 论文第 2 节中清楚讨论。 |
| R.7 | 0 | 当两名标注者犯同样错误时没有采取任何缓解措施。 |
| R.8 | 0 | 论文未讨论标注错误的潜在影响。 |
| R.9 | 0 | 论文未分析标注错误的定量影响。 |
| R.10 | 0 | 论文未报告任何统计显著性指标。 |
| R.11 | 0 | 论文未提供任何带评测缺陷结果的解读指南。 |
| R.12 | 1 | 论文报告了人类专家的结果。 |
| R.13 | 0 | 论文未报告任何平凡 Agent 的结果。 |

**表 7(Table 7):CyBench 评估报告(论文、代码)**

| 检查项 | 得分 | 理由 |
| --- | --- | --- |
| O.h.1 | 1 | 任务描述中提供了答案要求的具体格式。 |
| O.h.2 | 1 | 真值足够复杂,可防止平凡猜测。 |
| T.1 | 1 | 允许 Agent 使用全部工具;工具版本可由 Agent 检查。 |
| T.2 | 1 | 基准不需要任何外部 API。 |
| T.3 | 1 | 基准不需要任何外部 API。 |
| T.4 | 1 | 基准用 docker 容器隔离环境,并在运行之间清除状态。 |
| T.5 | 1 | Agent 无法直接访问存放真值的容器。 |
| T.6 | 1 | 环境设置是静态的,不随时间变化。 |
| T.7 | 1 | 如论文 3.3 节所示,真值经人工验证。 |
| T.8 | 1 | 如论文 3.3 节所示,每个任务都验证过可解。 |
| T.9 | 1 | 如论文 3.3 节所示,基准包含能自动解决全部任务的 Oracle 求解器。 |
| T.10 | 1 | 基准实现中未发现漏洞。 |
| R.1 | 1 | 基准已开源并在 GitHub 上提供。 |
| R.2 | 1 | 基准为用户提供开源评测组件。 |
| R.3 | 0 | 基准不含防数据污染措施。 |
| R.4 | 0 | 报告未讨论随时间持续更新任务的计划。 |
| R.5 | 1 | 该关系在论文第 1 节中清楚陈述。 |
| R.6 | 1 | 如第 1 节所示,基准设计为同时评估 Agent 框架与 LLM 模型。 |
| R.7 | 1 | 通过开发可验证的任务缓解标注缺陷。 |
| R.8 | 1 | 基准中未识别出不可避免的缺陷。 |
| R.9 | 1 | 基准中未识别出不可避免的缺陷。 |
| R.10 | 0 | 报告未包含任何统计显著性指标。 |
| R.11 | 1 | 基准中未识别出评测缺陷。 |
| R.12 | 1 | 论文第 5 节报告了人类表现。 |
| R.13 | 0 | 报告未报告平凡 Agent 的结果。 |

**表 8(Table 8):SWE-Bench-Verified 评估报告(论文、代码)**

| 检查项 | 得分 | 理由 |
| --- | --- | --- |
| O.d.1 | 1 | 测试用例直接取自 GitHub 仓库,论文未提及任何验证流程。 |
| O.d.2 | 0 | 论文未用客观指标度量测试用例的质量。 |
| T.1 | 1 | 仓库中指定了包依赖的版本。 |
| T.2 | 1 | 基准不需要任何外部 API。 |
| T.3 | 1 | 基准不需要任何外部 API。 |
| T.4 | 1 | 基准用 docker 容器隔离环境,并在运行之间清除状态。 |
| T.5 | 1 | Agent 无法访问宿主文件系统,真值对 Agent 不可达。 |
| T.6 | 1 | 环境设置是静态的,不随时间变化。 |
| T.7 | 1 | 真值补丁取自 GitHub 仓库,已经专家开发者验证。 |
| T.8 | 1 | 每个任务都是带相应 pull request 的真实 GitHub issue,Agent 可解。 |
| T.9 | 1 | 以 GitHub 的 pull request 作真值,可视为 Oracle 求解器。 |
| T.10 | 1 | 基准实现中未发现漏洞,评测过程安全。 |
| R.1 | 1 | 基准已开源并在 GitHub 上提供。 |
| R.2 | 1 | 基准为用户提供开源评测组件。 |
| R.3 | 0 | 基准未讨论防数据污染措施。 |
| R.4 | 0 | 基准未讨论随时间持续更新任务的计划。 |
| R.5 | 1 | 该关系在论文第 2 节中清楚陈述。 |
| R.6 | 1 | 如论文第 5 节所讨论,基准设计为同时评估模型与 Agent 框架。 |
| R.7 | 0 | 基准未讨论任何预防、识别与纠正缺陷的努力。 |
| R.8 | 0 | 基准未讨论不可避免缺陷的潜在影响。 |
| R.9 | 0 | 基准未包含评估不可避免缺陷影响的定量分析。 |
| R.10 | 0 | 报告未包含任何统计显著性指标。 |
| R.11 | 0 | 基准未提供任何带评测缺陷结果的解读指南。 |
| R.12 | 0 | 基准未报告非 AI 基线的结果。 |
| R.13 | 0 | 基准未报告平凡 Agent 的结果。 |

**表 9(Table 9):tau-Bench 评估报告(论文、代码)**

| 检查项 | 得分 | 理由 |
| --- | --- | --- |
| O.a.1 | 1 | 基准用最小表达式做子串匹配,对输入变化稳健。 |
| O.a.2 | 1 | 基准用最小表达式做子串匹配,对输入中的冗余词稳健。 |
| O.b.1 | 0 | 基准未说明如何处理否定修饰词,可能导致错误评测。 |
| O.b.2 | 0 | 基准未说明如何处理系统性列出全部可能答案,可能导致错误评测。 |
| O.b.3 | 0 | 一部分任务的真值为空,可能导致猜测。 |
| O.g.1 | 1 | 任务成功完成后的数据库是唯一的,且包含全部状态。 |
| O.g.2 | 1 | 数据库状态是唯一的环境状态,对相关与无关部分都做了检查。 |
| O.g.3 | 0 | 一部分任务的真值为空,可能导致平凡的状态修改。 |
| T.1 | 1 | 基准不使用外部工具。 |
| T.2 | 1 | 基准不使用外部 API。 |
| T.3 | 1 | 基准不使用外部 API。 |
| T.4 | 1 | 通过重新初始化数据库,在运行之间彻底清除残留数据或状态。 |
| T.5 | 1 | Agent 无文件系统访问权。 |
| T.6 | 1 | 环境设置是静态的,不随时间变化。 |
| T.7 | 1 | 如论文第 4 节所示,真值经人工验证。 |
| T.8 | 1 | 如论文第 4 节所示,每个任务都验证过 Agent 可解。 |
| T.9 | 1 | 基准提供参考任务解,可用作 Oracle 求解器。 |
| T.10 | 1 | 基准实现中未发现漏洞,评测过程安全。 |
| R.1 | 1 | 基准已开源并在 GitHub 上提供。 |
| R.2 | 1 | 基准为用户提供开源评测组件。 |
| R.3 | 0 | 基准未讨论防数据污染措施。 |
| R.4 | 0 | 报告未讨论随时间持续更新任务的计划。 |
| R.5 | 1 | 该关系在论文第 3 节中清楚陈述。 |
| R.6 | 1 | 如论文第 5 节所讨论,基准设计为同时评估模型与 Agent 框架。 |
| R.7 | 1 | 论文附录 A 展示了检测标注错误的努力。 |
| R.8 | 1 | 第 6 节讨论了不可避免缺陷的潜在影响,但这些讨论并不充分。 |
| R.9 | 0 | 报告未包含评估不可避免缺陷影响的定量分析。 |
| R.10 | 0 | 报告未包含任何统计显著性指标。 |
| R.11 | 0 | 报告未提供任何带评测缺陷结果的解读指南。 |
| R.12 | 0 | 报告未报告非 AI 基线的结果。 |
| R.13 | 0 | 报告未报告平凡 Agent 的结果。 |

**表 10(Table 10):MLE-Bench 评估报告(论文、代码)**

| 检查项 | 得分 | 理由 |
| --- | --- | --- |
| O.I.1 | 1 | 如 2.2 节所述,基准用排行榜位置作指标,不易被钻空子。 |
| T.1 | 0 | 提示未指定重要工具(如 Python 与 PyTorch)的版本。 |
| T.2 | 1 | 基准不需要任何外部 API,全部所需工具对 Agent 可用。 |
| T.3 | 1 | 基准不需要任何外部 API,评测过程不依赖任何外部资源。 |
| T.4 | 1 | 评测在干净环境中进行,运行之间无残留数据或状态。 |
| T.5 | 1 | 提交过程与 Agent 环境隔离,Agent 无法访问任何真值信息。 |
| T.6 | 1 | 环境设置是静态的,不随时间变化。 |
| T.7 | 1 | 基准使用来自 Kaggle 的真值数据,这是广泛使用且可靠的基准数据源。 |
| T.8 | 1 | 基准使用 Kaggle 的既往挑战,它们已被证明可用 ML 算法解决。 |
| T.9 | 1 | Kaggle 上的任意解都可视为 Oracle 求解器。 |
| T.10 | 1 | 基准实现中未发现漏洞,评测过程安全。 |
| R.1 | 1 | 基准已开源并在 GitHub 上提供。 |
| R.2 | 1 | 基准为用户提供开源评测组件。 |
| R.3 | 1 | 基准设计了实验来度量数据污染与 Agent 剽窃。 |
| R.4 | 1 | 第 6 节讨论了用新 Kaggle 挑战定期更新基准的未来计划。 |
| R.5 | 1 | 该关系在第 2 节中清楚陈述。 |
| R.6 | 1 | 如第 3 节所示,基准设计为同时评估模型与 Agent 框架。 |
| R.7 | 1 | 论文附录 A.5 讨论了检测作弊的努力。 |
| R.8 | 1 | 论文第 4 节讨论了不可避免缺陷的潜在影响。 |
| R.9 | 1 | 论文附录 A.5 包含评估不可避免缺陷影响的定量分析。 |
| R.10 | 1 | 论文在 3.3 节报告了统计显著性指标。 |
| R.11 | 1 | 评测过程中未发现显著缺陷。 |
| R.12 | 1 | 基准在 Kaggle 挑战提交中直接将 Agent 与人类专家的表现比较。 |
| R.13 | 0 | 基准未报告平凡 Agent 的结果。 |

**表 11(Table 11):WebArena 评估报告(论文、代码)**

| 检查项 | 得分 | 理由 |
| --- | --- | --- |
| O.a.1 | 1 | 如论文 3.2 节所述,基准期待回复遵循标准化格式,对输入变化稳健。 |
| O.a.2 | 1 | 如论文 3.2 节所述,基准期待回复遵循标准化格式,对输入中的冗余词稳健。 |
| O.b.1 | 0 | 基准不处理否定修饰词,可能导致错误评测。 |
| O.b.2 | 0 | 基准未说明如何处理系统性列出全部可能答案,可能导致错误评测。 |
| O.b.3 | 0 | 一部分任务的真值为 NULL,可能导致猜测。 |
| O.c.1 | 1 | 论文附录 A.8 定量评估了裁判的准确率。 |
| O.c.2 | 0 | 基准不处理 LLM-as-a-Judge 中的对抗输入与奖励作弊,可能导致错误评测。 |
| O.g.1 | 1 | 如论文 3.2 节所述,真值包含成功后可达的全部状态。 |
| O.g.2 | 0 | 状态检查只考虑相关状态(如 3.2 节所述用 locator 实现),可能导致错误评测。 |
| O.g.3 | 1 | 如论文 3.2 节所示,真值是对底层数据库的修改,足够复杂,可防止平凡的状态修改。 |
| T.1 | 1 | 基准不使用需要指定版本的工具。 |
| T.2 | 0 | 基准需要外部 API(如 Reddit 网站的克隆),评测期间可能因速率限制而对 Agent 不可访问。 |
| T.3 | 0 | API 变得不可访问时,评测过程未妥善处理错误,可能导致错误评测。 |
| T.4 | 1 | 基准用 docker 容器隔离环境,并在运行之间清除状态。 |
| T.5 | 1 | Agent 无法访问存放真值的文件系统。 |
| T.6 | 1 | 环境设置是静态的,不随时间变化。 |
| T.7 | 0 | 如 3.2 节所述,真值由两名人类标注者标注,但没有验证或保证标注正确性的机制。 |
| T.8 | 0 | 任务的歧义性未被完全验证或测试,可能导致错误评测。 |
| T.9 | 0 | 基准不含能自动解决全部任务的 Oracle 求解器。 |
| T.10 | 0 | 什么都不做的 Agent 能通过 4.4%(提取文本在此处截断,比例数字后原文残缺,当为通过 4.4% 的任务)。 |
| R.1 | 1 | 基准已开源并在 GitHub 上提供。 |
| R.2 | 1 | 基准为用户提供开源评测组件。 |
| R.3 | 0 | 基准未讨论防数据污染措施。 |
| R.4 | 0 | 基准未讨论随时间持续更新任务的计划。 |
| R.5 | 1 | 该关系在论文 2.1 节中清楚陈述。 |
| R.6 | 1 | 如第 5 节所示,基准设计为评估 LLM 模型。 |
| R.7 | 1 | 论文附录 A.8 讨论了评估 LLM-as-a-Judge 的努力。 |
| R.8 | 0 | 报告未讨论不可避免缺陷的潜在影响。 |
| R.9 | 0 | 报告未包含评估不可避免缺陷影响的定量分析。 |
| R.10 | 0 | 报告未包含任何统计显著性指标。 |
| R.11 | 0 | 报告未提供任何带评测缺陷结果的解读指南。 |
| R.12 | 1 | 附录 A.5 报告了人类表现。 |
| R.13 | 0 | 报告未报告平凡 Agent 的结果。 |

**表 12(Table 12):GAIA 评估报告(论文、代码)**

| 检查项 | 得分 | 理由 |
| --- | --- | --- |
| O.h.1 | 1 | 如论文 3.2 节所述,任务描述中提供了答案要求的具体格式。 |
| O.h.2 | 1 | 真值足够复杂,可防止平凡猜测。 |
| T.1 | 0 | 论文未指定工具(如 Python 与网站)的版本。 |
| T.2 | 0 | 论文未指定 API 的速率限制,可能导致错误评测。 |
| T.3 | 0 | 基准未提供处理错误的参考评测组件,可能导致不同用户之间评测不一致。 |
| T.4 | 1 | 基准不修改环境状态。 |
| T.5 | 1 | Agent 无法访问真值信息。 |
| T.6 | 1 | 环境设置是静态的,不随时间变化。 |
| T.7 | 1 | 如论文 3.4 节所述,数据标注流程包含验证步骤。 |
| T.8 | 1 | 如论文 3.4 节所述,数据标注流程包含验证步骤。 |
| T.9 | 0 | 基准不含能自动解决全部任务的 Oracle 求解器。 |
| T.10 | 1 | 基准实现中未发现漏洞。 |
| R.1 | 1 | 基准已开源并在 HuggingFace 上提供。 |
| R.2 | 0 | 基准未为用户提供开源评测组件。 |
| R.3 | 0 | 基准不含防数据污染措施。 |
| R.4 | 0 | 报告未讨论随时间持续更新任务的计划。 |
| R.5 | 1 | 该关系在论文第 3 节中清楚陈述。 |
| R.6 | 1 | 如论文第 3 节所讨论,基准设计为评估 LLM 模型。 |
| R.7 | 1 | 论文第 5 节讨论了相关努力,包括比较有/无人工介入的评测。 |
| R.8 | 1 | 第 6 节讨论了不可避免缺陷的潜在影响,如错误推理轨迹得出正确答案。 |
| R.9 | 0 | 报告未包含评估不可避免缺陷影响的定量分析。 |
| R.10 | 0 | 报告未包含任何统计显著性指标。 |
| R.11 | 0 | 报告未提供任何带评测缺陷结果的解读指南。 |
| R.12 | 1 | 论文第 4 节报告了人类表现。 |
| R.13 | 1 | 报告包含搜索引擎的结果,可视为平凡 Agent。 |

**表 13(Table 13):OSWorld 评估报告(论文、代码)**

| 检查项 | 得分 | 理由 |
| --- | --- | --- |
| O.g.1 | 1 | 如论文 3.2 节所述,真值经验证包含任务成功完成后可达的全部状态。 |
| O.g.2 | 0 | 状态检查只验证任务的相关状态;Agent 可能执行未被真值检查到的额外有害动作。 |
| O.g.3 | 1 | 如论文 3.2 节所示,真值涉及对软件或网站的复杂状态变化。 |
| T.1 | 1 | 基准不使用外部工具;环境版本在仓库的 README 文件中明确说明。 |
| T.2 | 1 | 基准不使用外部 API。 |
| T.3 | 1 | 基准不使用外部 API。 |
| T.4 | 1 | 基准用虚拟机运行任务,确保运行之间清除全部残留数据或状态。 |
| T.5 | 1 | Agent 与真值通过虚拟机相互隔离。 |
| T.6 | 0 | 基准在真实在线网页上检查 HTML 选择器(如类名或页面标题)。 |
| T.7 | 1 | 如论文 3.2 节所述,真值经人类专家验证正确。 |
| T.8 | 1 | 如论文 3.2 节所述,每个任务都经人类专家验证可解。 |
| T.9 | 0 | 基准不含能自动解决全部任务的 Oracle 求解器。 |
| T.10 | 1 | 基准实现中不存在漏洞。 |
| R.1 | 1 | 基准完全开源,代码在 GitHub 上提供。 |
| R.2 | 1 | 基准为用户提供开源评测组件。 |
| R.3 | 0 | 基准未包含防数据污染措施。 |
| R.4 | 0 | 报告未包含随时间持续更新任务的措施或计划。 |
| R.5 | 1 | 该关系在论文第 2 节中清楚陈述。 |
| R.6 | 1 | 如论文第 2 节所讨论,评测对象是 Agent 框架。 |
| R.7 | 1 | 如论文 3.2 节所述,基准用额外的人工验证步骤来预防、识别与纠正缺陷。 |
| R.8 | 0 | 论文第 7 节讨论了 Agent 的安全问题。 |
| R.9 | 0 | 报告未包含评估不可避免缺陷影响的定量分析。 |
| R.10 | 0 | 报告未包含统计显著性指标。 |
| R.11 | 0 | 报告未提供带评测缺陷结果的解读指南。 |
| R.12 | 1 | 论文 3.4 节报告了人类表现。 |
| R.13 | 0 | 报告未包含平凡 Agent 的结果。 |

**表 14(Table 14):KernelBench 评估报告(论文、代码)**

| 检查项 | 得分 | 理由 |
| --- | --- | --- |
| O.e.1 | 0 | 模糊器未覆盖潜在边界情况,如空输入。 |
| O.e.2 | 0 | 虽然指定了数据类型,模糊器未测试不同的内存布局,如非连续内存布局的张量。 |
| O.e.3 | 0 | 模糊器用均匀采样生成输入,可能对被测代码不敏感。例如,模糊器可能不会生成触发 torch 库中 relu 函数的正输入。 |
| T.1 | 0 | 默认提示中未指定 CUDA 版本。 |
| T.2 | 1 | 基准评估不需要外部 API。 |
| T.3 | 1 | 基准评估不需要外部 API。 |
| T.4 | 1 | 内核在独立进程中评估,并在运行之间清除状态。 |
| T.5 | 0 | 真值内核先执行、且与 Agent 同处一个进程,可能导致 Agent 通过越界内存访问真值结果。 |
| T.6 | 1 | 环境设置是静态的,不随时间变化。 |
| T.7 | 1 | 真值内核由 PyTorch 提供——广泛使用的深度学习库。 |
| T.8 | 1 | 来自 PyTorch 的实现即是概念验证。 |
| T.9 | 1 | Oracle 求解器即 PyTorch 实现。 |
| T.10 | 1 | 基准实现中未发现漏洞。 |
| R.1 | 1 | 基准已开源并在 GitHub 上提供。 |
| R.2 | 1 | 基准为用户提供开源评测组件。 |
| R.3 | 0 | 基准未讨论防数据污染措施。 |
| R.4 | 0 | 基准未讨论随时间持续更新任务的计划。 |
| R.5 | 1 | 第 3 节清楚陈述了该关系。 |
| R.6 | 1 | 第 5 节清楚说明基准的评测对象是 LLM 模型。 |
| R.7 | 1 | 附录 B.2 描述了为预防、识别与纠正缺陷所做的工作,但并不充分。 |
| R.8 | 1 | 附录 B.2 包含对不可避免缺陷潜在影响的定性讨论,但并不充分。 |
| R.9 | 1 | 附录 B.2 包含评估不可避免缺陷影响的定量分析,但并不充分。 |
| R.10 | 0 | 基准未报告任何统计显著性指标。 |
| R.11 | 0 | 基准未提供任何带评测缺陷结果的解读指南。 |
| R.12 | 0 | 基准未报告非 AI 基线的结果。 |
| R.13 | 0 | 基准未报告平凡 Agent 的结果。 |

### 附录 E 案例研究(Case Study)

::: en
We present case study of specific issues we identified. For each study, we use an Intel E5-2630 CPU with 128 GB RAM and optionally 1 NVIDIA H100 80GB for GPU-required experiments. We release our code at https://github.com/uiuc-kang-lab/agentic-benchmarks.
:::

我们展示所识别具体问题的案例研究。每项研究使用一台 Intel E5-2630 CPU、128 GB 内存的主机,需要 GPU 的实验另配 1 块 NVIDIA H100 80GB。代码发布于 github.com/uiuc-kang-lab/agentic-benchmarks。

#### E.1 SWE-bench

::: en
**Benchmark Overview.** SWE-bench is a benchmark for evaluating the ability of AI agents to resolve real-world GitHub issues. Given the issue description and a summary of the codebase, agents are tasked with generating a patch that resolves the issue. Each generated patch is evaluated via existing unit tests in the GitHub repository.

**Identified Issue.** SWE-bench uses manually written unit tests to evaluate the correctness of a generated code patch. As illustrated in prior work, UTBoost [87], unit tests can lead to many false positives, due to the insufficiency of test cases.
:::

**基准概览。** SWE-bench 评估 AI Agent 解决真实 GitHub issue 的能力。给定 issue 描述与代码库摘要,Agent 的任务是生成解决该 issue 的补丁;每个生成的补丁通过 GitHub 仓库中既有的单元测试来评估。

**已识别问题。** SWE-bench 用人工编写的单元测试评估生成代码补丁的正确性。如先前工作 UTBoost [87] 所示,由于测试用例不充分,单元测试可能导致大量假阳性。

::: en
**Example.** The Python package seaborn has an issue in handling missing values in the inputs x and y when computing polynomial fits using PolyFit(). Unfortunately, the unit test case for PolyFit() only considers the scenarios when both x and y have missing values:

```python
def test_missing_data(self, df):
    groupby = GroupBy(["group"])
    df.iloc[5:10] = np.nan
    res1 = PolyFit()(df[["x", "y"]], groupby, "x", {})
    res2 = PolyFit()(df[["x", "y"]].dropna(), groupby, "x", {})
    assert_frame_equal(res1, res2)
```

This insufficient test case for PolyFit() leads to the following incorrect patch for PolyFit() being evaluated as correct. This patch is generated by IBM SWE-1.0.

```python
def _fit_predict(self, data):
    y = data["y"].dropna()
    x = data["x"].dropna()
    if x.shape[0] != y.shape[0]:
        raise ValueError("x and y must have the same number of non-missing values")
    if x.nunique() <= self.order:
        # TODO warn?
        xx = yy = []
```
:::

**示例。** Python 包 seaborn 在用 PolyFit() 计算多项式拟合时,对输入 x 与 y 中的缺失值处理有误。遗憾的是,PolyFit() 的单元测试用例只考虑了 x 与 y 同时含缺失值的情形:

```python
def test_missing_data(self, df):
    groupby = GroupBy(["group"])
    df.iloc[5:10] = np.nan                      # 同时把 x、y 置为缺失
    res1 = PolyFit()(df[["x", "y"]], groupby, "x", {})
    res2 = PolyFit()(df[["x", "y"]].dropna(), groupby, "x", {})
    assert_frame_equal(res1, res2)
```

这一不充分的测试用例导致下面这个错误的 PolyFit() 补丁被判为正确;该补丁由 IBM SWE-1.0 生成:

```python
def _fit_predict(self, data):
    y = data["y"].dropna()                      # 只丢掉 y 的缺失值
    x = data["x"].dropna()                      # 只丢掉 x 的缺失值——二者可能错位!
    if x.shape[0] != y.shape[0]:
        raise ValueError("x and y must have the same number of non-missing values")
    if x.nunique() <= self.order:
        # TODO warn?
        xx = yy = []
```

::: en
**Qualitative Results.** As reported in prior work [87], agents can pass evaluations without addressing the GitHub issues for 5.3% and 7.7% of tasks in the Verified and Lite partitions, respectively. These tasks lead to 40.9% and 24.4% changes in the leaderboard for the Verified and Lite partitions, respectively. Furthermore, these tasks causes 2.3% and 1.6% overestimation of agent performance for the Verified and Lite partitions, respectively.
:::

**定性结果。** 如先前工作 [87] 所报告:在 Verified 与 Lite 两个分区,Agent 可分别在 5.3% 与 7.7% 的任务上未解决 GitHub issue 即通过评测;这些任务分别导致两个分区排行榜 40.9% 与 24.4% 的名次变动;此外,这些任务分别造成 Verified 与 Lite 分区上 Agent 性能 2.3% 与 1.6% 的高估。

#### E.2 τ-bench

::: en
**Benchmark Overview.** τ-bench is for evaluation AI agents capability to interact with human users and follow domain-specific rules [86]. Given a domain-specific policy, the AI agent is tasked to interact with human users and answer user queries.

**Identified Issue.** τ-bench evaluates the agents' actions based on whether the database state is correct and optionally whether the agents' responses contain required text. Therefore, on tasks that do not change the database state and do not have required texts, agents can get positive evaluation results by doing nothing. On tasks that do not change the database state and has a trivial required text, such as "4", agents can get positive evaluation results by returning random responses or all the data.

**Example.** A task in τ-bench requires agent to process a flight cancellation and refund request. An AI agent is supposed to check the detail of the booked flight ticket for the user in the database and deny the user request if the ticket is non-refundable. This task has no required output. Therefore, as long as the data state does not change, the agent will obtain a positive evaluation result. In this case, an agent that does nothing can also have a positive evaluation result.

**Qualitative Results.** A do-nothing agent that returns immediately can achieve a 38% and 6.0% pass^k or pass@k for any k for Airline and Retail partitions, respectively. A spamming agent that outputs all the data can achieve a 40% and 9.6% pass^k or pass@k for any k for Airline and Retail partitions, respectively.
:::

**基准概览。** τ-bench 评估 AI Agent 与人类用户交互并遵循领域特定规则的能力 [86]。给定一份领域策略,AI Agent 的任务是与人类用户交互并回答用户请求。

**已识别问题。** τ-bench 依据数据库状态是否正确、以及(可选地)Agent 回复是否包含要求的文本来评估 Agent 的行为。因此,对于既不改数据库状态、又无要求文本的任务,Agent 什么都不做也能得到正向评测结果;对于不改数据库状态、且要求文本很平凡(如 "4")的任务,Agent 靠返回随机回复或全部数据即可得到正向评测结果。

**示例。** τ-bench 的一个任务要求 Agent 处理机票取消与退款请求:AI Agent 本应在数据库中查该用户所订机票的详情,若机票不可退款则拒绝用户请求。该任务没有要求的输出,因此只要数据库状态不变,Agent 就会得到正向评测结果——此时,一个什么都不做的 Agent 同样能得到正向评测结果。

**定性结果。** 一个立即返回、什么都不做的 Agent,在 Airline 与 Retail 分区上分别能取得 38% 与 6.0% 的 pass^k/pass@k(对任意 k);一个输出全部数据的刷屏 Agent,在两个分区上分别能取得 40% 与 9.6% 的 pass^k/pass@k(对任意 k)。

#### E.3 BIRD

::: en
**Benchmark Overview.** BIRD is for evaluating the capability of agents to write SQL queries [37]. Given a query description in natural language, the agent needs to translate it into a SQL query.

**Identified Issue.** BIRD evaluates agent by comparing the execution results of the ground truth query with the generated query. However, due to the ambiguity of the query description, there can be multiple correct queries for the same natural language description.

**Example.** A task in BIRD asks the agent to write a SQL query that can answer the question: "What are the name, independence year, and surface area of the country with the smallest population?" There can be two correct SQL queries:

```sql
-- Query 1
SELECT Name, SurfaceArea, IndepYear FROM country
WHERE Population = (SELECT min(Population) FROM country)
-- Query 2
SELECT Name, SurfaceArea, IndepYear FROM country
ORDER BY Population LIMIT 1
```

Query 1 outputs all the country with the smallest population, while Query 2 outputs one of the country with the smallest population. Although the output of two queries are different, they both answer the question.
:::

**基准概览。** BIRD 评估 Agent 编写 SQL 查询的能力 [37]。给定自然语言的查询描述,Agent 需要把它翻译成 SQL 查询。

**已识别问题。** BIRD 通过比较真值查询与生成查询的执行结果来评估 Agent。但由于查询描述存在歧义,同一句自然语言描述可能对应多个正确的查询。

**示例。** BIRD 的一个任务要求 Agent 写出能回答如下问题的 SQL 查询:「人口最少的国家其名称、独立年份与国土面积是什么?」以下两个 SQL 查询都可能是正确的:

```sql
-- Query 1:输出全部人口最少的国家
SELECT Name, SurfaceArea, IndepYear FROM country
WHERE Population = (SELECT min(Population) FROM country)
-- Query 2:输出人口最少的国家之一
SELECT Name, SurfaceArea, IndepYear FROM country
ORDER BY Population LIMIT 1
```

查询 1 输出所有人口最少的国家,查询 2 输出人口最少的国家之一;两个查询的输出不同,但都回答了该问题。

#### E.4 SWE-Lancer

::: en
**Benchmark Overview.** SWE-Lancer is for evaluating the capability of AI agents to independently implement features and fix bugs. [48] Given a task description, agent needs to use Python scripts to interact with the file system and modify codebase.

**Identified Issue.** SWE-Lancer uses end-to-end testing to evaluate the correctness of agents' implementation. Although the test cases are stored in a password-protected .zip file, reading the directory structure and updating files within the .zip file do not require a password. Therefore, an agent can easily locate the test cases and replace them with a naive one, such as "assert 1==1".

**Qualitative Results.** An agent that overwrites the test cases in the .zip file can achieve a 100% resolve rate without completing the software engineering tasks.
:::

**基准概览。** SWE-Lancer 评估 AI Agent 独立实现功能与修复 bug 的能力 [48]。给定任务描述,Agent 需用 Python 脚本操作文件系统并修改代码库。

**已识别问题。** SWE-Lancer 用端到端测试评估 Agent 实现的正确性。虽然测试用例存放在密码保护的 .zip 文件里,但读取该 .zip 文件的目录结构、更新其中文件都不需要密码。因此,Agent 可以轻易定位测试用例,并替换成朴素用例,如 `assert 1==1`。

**定性结果。** 覆写 .zip 文件中测试用例的 Agent,无需完成任何软件工程任务即可取得 100% 的解决率。

#### E.5 WebArena

::: en
**Benchmark Overview.** WebArena is for evaluating the capability of agents to interact with the web [93]. Given a user request, the AI agent need either retrieve the required information or fill the given data into the web form correctly.

**Identified Issue.** WebArena uses exact string matching, substring matching, and LLM-as-a-Judge to evaluate agents. Its strategy of exact string matching cannot handle alternative expressions and phrase modifiers, while the substring matching is vulnerable to exhaustive enumeration of the content on the website. Additionally, LLM-as-a-Judge can produce unreliable results.

**Example.** In WebArena, there is a user query that asks "What is the duration required to first walk from Massachusetts Institute of Technology to Harvard University, and then drive to Boston Logan International Airport?" The ground truth answer for this question is 63 minutes. However, the agent searched the web and output the final answer: "The duration required to first walk from Massachusetts Institute of Technology to Harvard University is 45 minutes, and then drive to Boston Logan International Airport is 8 minutes." The answer of agent gives the duration of 45+8=53 minutes, which is different from the ground truth answer. However, the LLM judge considers the agent's answer as correct.
:::

**基准概览。** WebArena 评估 Agent 与 Web 交互的能力 [93]。给定用户请求,AI Agent 需要检索所需信息,或把给定数据正确填入网页表单。

**已识别问题。** WebArena 用精确字符串匹配、子串匹配与 LLM-as-a-Judge 评估 Agent。其精确字符串匹配策略无法处理替代表达与短语修饰词;子串匹配则易受网站内容的穷举枚举攻击;此外,LLM-as-a-Judge 可能给出不可靠的结果。

**示例。** WebArena 中有一个用户查询:「先从麻省理工学院步行到哈佛大学、再驾车到波士顿洛根国际机场,需要多长时间?」该题真值为 63 分钟。而 Agent 搜索网页后给出的最终答案是:「先从麻省理工学院步行到哈佛大学需要 45 分钟,再驾车到波士顿洛根国际机场需要 8 分钟。」Agent 答案给出的总时长为 45+8=53 分钟,与真值不同;但 LLM 裁判却认定 Agent 的答案正确。

#### E.6 KernelBench

::: en
**Benchmark Overview.** KernelBench is for evaluating the capability of agents to write correct and efficient GPU kernels [59]. Given the task instruction and the original PyTorch code, agents need to write PyTorch code containing an inline implementation of the kernel that is functionally correct and more efficient.

**Identified Issue 1.** KernelBench uses randomly generated inputs (i.e., fuzzing) to test the correctness of generated GPU kernels. However, we find the tested functions in a subset of tasks are not sensitive to uniform random inputs, such as mean(softmax(x)) and relu(x-2).

**Identified Issue 2.** In the evaluation implementation, KernelBench first runs the ground truth kernel and then runs the generated kernel subsequently. As reported in prior work [35], agents can potentially cheat by generating a program that extracts the execution results of the ground truth kernel.

**Identified Issue 3.** The fuzzer designed in KernelBench fails to address potential inputs with different memory layouts (e.g., non-contiguous tensors), tensor shapes, and hardware environment.

In the following code snippet, we demonstrate an incorrect kernel function due to improper use of threads, which were graded as correct in KernelBench. In Line 46, the kernel function accesses parallel execution results in s_sum with index from tid to nthread. However, when nthread > normalized_size, this will lead to out-of-bound access into uninitialized memory. Namely, a thread-safe guard is required here.
:::

**基准概览。** KernelBench 评估 Agent 编写正确且高效 GPU 内核的能力 [59]。给定任务指令与原始 PyTorch 代码,Agent 需写出包含内核内联实现(inline implementation)的 PyTorch 代码,要求功能正确且更高效。

**已识别问题 1。** KernelBench 用随机生成的输入(即模糊测试)检验生成 GPU 内核的正确性。但我们发现,一部分任务中被测函数对均匀随机输入并不敏感,如 mean(softmax(x)) 与 relu(x-2)。

**已识别问题 2。** 在评测实现中,KernelBench 先运行真值内核、随后运行生成的内核。如先前工作 [35] 所报告,Agent 可以生成一个提取真值内核执行结果的程序来作弊。

**已识别问题 3。** KernelBench 设计的模糊器未能覆盖具有不同内存布局(如非连续张量)、不同张量形状与不同硬件环境的潜在输入。

在下面的代码片段中,我们展示一个因线程使用不当而不正确的内核函数,它在 KernelBench 中被判为正确。第 46 行,内核函数以 tid 到 nthread 的下标访问 s_sum 中的并行执行结果;然而当 nthread > normalized_size 时,这会导致越界访问未初始化的内存——也就是说,这里需要一个线程安全的保护。

::: en
```cuda
#include ...

template <typename scalar_t>
__global__ void layernorm_forward_kernel_opt(
    const scalar_t* __restrict__ input,
    const scalar_t* __restrict__ weight,
    const scalar_t* __restrict__ bias,
    const float eps,
    scalar_t* __restrict__ output,
    const int normalized_size) {

  // Each block processes one outer instance.
  int instance_idx = blockIdx.x;

  // Use 2D thread indexing to cover the normalized dimension flexibly.
  int tid = threadIdx.y * blockDim.x + threadIdx.x;
  int nthreads = blockDim.x * blockDim.y;

  // Pointers to the start of this instance's data.
  const scalar_t* __restrict__ in_ptr = input + instance_idx * normalized_size;
  scalar_t* __restrict__ out_ptr = output + instance_idx * normalized_size;

  using accscalar_t = at::acc_type<scalar_t, true>;

  // Each thread computes a partial sum and sum of squares over a strided range.
  accscalar_t local_sum = 0;
  accscalar_t local_sum_sq = 0;
  for (int i = tid; i < normalized_size; i += nthreads) {
    // Use __ldg for read-only, coalesced global memory access
    scalar_t val = __ldg(&in_ptr[i]);
    accscalar_t a_val = static_cast<accscalar_t>(val);
    local_sum += a_val;
    local_sum_sq += a_val * a_val;
  }

  // Allocate shared memory for reduction: first part for partial sums, second for sum of squares.
  extern __shared__ char smem[];
  accscalar_t* s_sum = reinterpret_cast<accscalar_t*>(smem);
  accscalar_t* s_sum_sq = s_sum + nthreads;

  s_sum[tid] = local_sum;
  s_sum_sq[tid] = local_sum_sq;
  __syncthreads();

  // Perform parallel reduction in shared memory.
  for (int stride = nthreads / 2; stride > 0; stride >>= 1) {
    if (tid < stride) {
      s_sum[tid] += s_sum[tid + stride];
      s_sum_sq[tid] += s_sum_sq[tid + stride];
    }
    __syncthreads();
  }
  ...
}
```

To identify such issues in large scale, we applied o3-mini to generate additional test cases. Specifically, we sampled 3 generated kernel functions for each task in level 1 and asked o3-mini to detect any possible flaws and write test cases for each detected flaw. Then, we manually verified the correctness of o3-mini-generated test cases. Finally, we applied these test cases on all generations by Lange et al. [35]. Our results show that the correctness rate of generated kernels is overestimated by 31%.
:::

```cuda
#include ...

template <typename scalar_t>
__global__ void layernorm_forward_kernel_opt(
    const scalar_t* __restrict__ input,
    const scalar_t* __restrict__ weight,
    const scalar_t* __restrict__ bias,
    const float eps,
    scalar_t* __restrict__ output,
    const int normalized_size) {

  // 每个 block 处理一个外层实例
  int instance_idx = blockIdx.x;

  // 用二维线程索引灵活覆盖归一化维度
  int tid = threadIdx.y * blockDim.x + threadIdx.x;
  int nthreads = blockDim.x * blockDim.y;

  // 指向该实例数据起始处的指针
  const scalar_t* __restrict__ in_ptr = input + instance_idx * normalized_size;
  scalar_t* __restrict__ out_ptr = output + instance_idx * normalized_size;

  using accscalar_t = at::acc_type<scalar_t, true>;

  // 每个线程按跨步区间计算部分和与平方和
  accscalar_t local_sum = 0;
  accscalar_t local_sum_sq = 0;
  for (int i = tid; i < normalized_size; i += nthreads) {
    // 用 __ldg 做只读、合并的全局内存访问
    scalar_t val = __ldg(&in_ptr[i]);
    accscalar_t a_val = static_cast<accscalar_t>(val);
    local_sum += a_val;
    local_sum_sq += a_val * a_val;
  }

  // 分配共享内存做归约:前半存部分和,后半存平方和
  extern __shared__ char smem[];
  accscalar_t* s_sum = reinterpret_cast<accscalar_t*>(smem);
  accscalar_t* s_sum_sq = s_sum + nthreads;

  s_sum[tid] = local_sum;
  s_sum_sq[tid] = local_sum_sq;
  __syncthreads();

  // 在共享内存中做并行归约(缺陷所在:见上文对第 46 行的说明)
  for (int stride = nthreads / 2; stride > 0; stride >>= 1) {
    if (tid < stride) {
      s_sum[tid] += s_sum[tid + stride];
      s_sum_sq[tid] += s_sum_sq[tid + stride];
    }
    __syncthreads();
  }
  ...
}
```

为大规模识别此类问题,我们用 o3-mini 生成额外测试用例:具体而言,对 level 1 的每个任务采样 3 个生成的内核函数,让 o3-mini 检测可能存在的缺陷并为每个缺陷编写测试用例;随后我们人工验证 o3-mini 所生成测试用例的正确性;最后把这些测试用例应用于 Lange 等 [35] 报告的全部生成结果。结果表明,生成内核的正确率被高估了 31%。

### 附录 F 严谨基准报告的示例(An Example of Rigorous Benchmark Reporting)

::: en
In this section, we present a modified reporting example based on BIRD to demonstrate benchmark reporting that fulfills all the criteria outlined in Figure 4. BIRD is a benchmark for evaluating agents' capability to translate a natural language query to a SQL query.

**R.1. Is fully or at least partially open-sourced.**
Example: We released the training and validation dataset of BIRD at https://bird-bench.github.io/.

**R.2. Offers an open-source evaluation harness for users.**
Example: We released the harness to evaluation agents on BIRD at https://github.com/AlibabaResearch/DAMO-ConvAI/tree/main/bird.

**R.3. Includes measures to prevent data contamination, such as a private, held-out test set.**
Example: We keep a private held-out test set to avoid potential data contamination. Request to evaluate agents on this test set can be submitted at https://bird-bench.github.io/.

**R.4. Includes measures or plans to consistently update challenges over time to avoid overfitting.**
Example: We plan to consistently update the database and natural language queries to reflect the real-world queries and avoid overfitting. Our updates will be available at https://bird-bench.github.io/.

**R.5. Clearly states the relationship between the agent capabilities it aims to evaluate and the constructs or outcomes it measures.**
Example: BIRD evaluates agents' capabilities to serve as a database interface to translate natural language queries into executable SQL queries. To achieve that, BIRD provides agents with a natural language query, the database schema, and SQL-related domain knowledge, and challenges agents to write a SQL query that can be executed to return correct answers.

**R.6. Clearly states the evaluation subjective of the benchmark (e.g., a model or an agent framework).**
Example: BIRD is designed to evaluate the capability of ML models as well as the performance of agent frameworks.

**R.7. Describes steps taken to prevent, identify, and correct flaws.**
Example: We identify that evaluating generated SQL queries using execution results have two limitations. First, tasks requiring LIMIT queries and containing ties in the data may lead to non-deterministic execution results. Second, manually annotated ground-truth queries may contain errors. To understand and mitigate these errors, we randomly sample 500 tasks to perform an additional phase of verification. After verifying queries, we found 11.65% of ground-truth queries are incorrect. [Footnote 4]

**R.8. Includes qualitative discussions of the potential impact of unavoidable flaws.**
Example: The identified incorrect ground-truth queries and potentially more incorrect ground-truth queries in the test dataset can lead to estimation errors of the agent performance and incorrect rankings of agents.

**R.9. Includes quantitative analysis to assess the impact of unavoidable flaws (e.g., noise of ground truth).**
Example: We build our quantitative analysis based on the normality assumption. Specifically, suppose the number of data in the test set N is large enough such that the true success rate (p) of an agent follows a normal distribution with mean µ and standard deviation σ. Given the ground truth's incorrectness rate of e and the estimated agent success rate p0 (based on the imperfect ground truth), µ and σ are calculated as

µ = e + (1 − 2e)p0;  σ² = µ(1 − µ) = (e + (1 − 2e)p0)(1 − e − (1 − 2e)p0)

Hence, based on the normality assumption, we can derive a two-sided confidence interval with confidence α for p as follows:

P(µ − 1.96 × σ/√N ≤ p ≤ µ + 1.96 × σ/√N) ≥ 95%  (1)

Finally, based on the plug-in estimate (11.65%) for the ground truth's incorrectness rate, we calculate the confidence interval for the agents' performance in Table 15.

**R.10. Reports metrics about statistical significance, such as confidence intervals.**
Example: In additional to accuracy estimate, we also calculate confidence intervals for each model in Table 15.

**R.11. Provides guidance on interpreting results with eval flaws.**
Example: Given the potential flaws in BIRD, we do not recommend users to rely on the success rate alone for decision-making or selecting models. Instead, we suggest using the confidence interval of the success rate as a reference.

**R.12. Reports results of non-AI baselines (e.g., human experts).**
Example: We measured the performance of a SQL expert on BIRD, obtaining a success rate of 92.96%.

**R.13. Reports results of trivial agents (e.g., one that does nothing).**
Example: We performed sanity check on our evaluation harness by measuring the performance of a trivial agent that does nothing. We find that the trivial agent achieves 0% success rate, confirming the rigor of our evaluation implementation.

[Footnote 4] We used results by Arcwise [7].
:::

本节给出一个基于 BIRD 改写的报告示例,演示满足图 4 全部标准的基准报告。BIRD 是评估 Agent 把自然语言查询翻译为 SQL 查询之能力的基准。

- **R.1. 完全或至少部分开源。** 示例:我们在 bird-bench.github.io 发布了 BIRD 的训练与验证数据集。
- **R.2. 为用户提供开源评测组件。** 示例:我们在 github.com/AlibabaResearch/DAMO-ConvAI/tree/main/bird 发布了在 BIRD 上评测 Agent 的组件。
- **R.3. 纳入防数据污染措施,如私有留出测试集。** 示例:我们保留私有的留出测试集以避免潜在数据污染;在该测试集上评测 Agent 的请求可在 bird-bench.github.io 提交。
- **R.4. 纳入随时间持续更新任务的措施或计划以避免过拟合。** 示例:我们计划持续更新数据库与自然语言查询,以反映真实世界查询并避免过拟合;更新将在 bird-bench.github.io 提供。
- **R.5. 清晰陈述所评 Agent 能力与所测构念/结果的关系。** 示例:BIRD 评估 Agent 作为数据库接口、把自然语言查询翻译为可执行 SQL 查询的能力。为此,BIRD 向 Agent 提供自然语言查询、数据库模式与 SQL 领域知识,并挑战 Agent 写出可执行且返回正确答案的 SQL 查询。
- **R.6. 清晰陈述基准的评测对象(如模型或 Agent 框架)。** 示例:BIRD 设计为既评估 ML 模型的能力,也评估 Agent 框架的表现。
- **R.7. 描述为预防、识别与纠正缺陷所采取的步骤。** 示例:我们识别出用执行结果评估生成 SQL 查询的两个局限:其一,要求 LIMIT 查询且数据中存在并列(打平)的任务可能导致非确定性的执行结果;其二,人工标注的真值查询可能含错。为理解并缓解这些错误,我们随机抽取 500 个任务做额外的验证阶段;验证后发现 11.65% 的真值查询是错误的(原文脚注 4:我们使用了 Arcwise [7] 的结果)。
- **R.8. 对不可避免缺陷的潜在影响做定性讨论。** 示例:已识别的错误真值查询、以及测试集中可能存在的更多错误真值查询,会导致 Agent 性能的估计误差与 Agent 排名的错位。
- **R.9. 用定量分析评估不可避免缺陷(如真值噪声)的影响。** 示例:我们基于正态性假设构建定量分析。具体地,设测试集数据量 N 足够大,使得 Agent 的真实成功率 p 服从均值为 µ、标准差为 σ 的正态分布。给定真值错误率 e 与(基于不完美真值的)Agent 成功率估计 p₀,µ 与 σ 按下式计算:

  µ = e + (1 − 2e)·p₀;σ² = µ(1 − µ) = (e + (1 − 2e)·p₀)·(1 − e − (1 − 2e)·p₀)

  于是基于正态性假设,可推出 p 的置信水平为 α 的双侧置信区间:

  P(µ − 1.96 × σ/√N ≤ p ≤ µ + 1.96 × σ/√N) ≥ 95%(式 1)

  最后,以真值错误率的代入估计(11.65%)计算表 15 中各 Agent 性能的置信区间。
- **R.10. 报告统计显著性指标,如置信区间。** 示例:除准确率估计外,我们还为表 15 中每个模型计算置信区间。
- **R.11. 提供带评测缺陷结果的解读指南。** 示例:鉴于 BIRD 的潜在缺陷,我们不建议用户只凭成功率做决策或选型,而建议以成功率的置信区间作参考。
- **R.12. 报告非 AI 基线(如人类专家)的结果。** 示例:我们测得一名 SQL 专家在 BIRD 上的成功率为 92.96%。
- **R.13. 报告平凡 Agent(如什么都不做者)的结果。** 示例:我们用一个什么都不做的平凡 Agent 测量性能,对评测组件做健全性检查;该平凡 Agent 的成功率为 0%,证实了评测实现的严谨性。

**表 15(Table 15):带置信区间的 BIRD 修改版排行榜 [37]。**

| 方法 | Dev. 准确率(%) | 置信区间 | 原排名 | 可能排名 |
| --- | --- | --- | --- | --- |
| CHASE-SQL + Gemini | 74.9 | [66.8, 71.4] | 1 | 1-13 |
| Contextual-SQL | 73.5 | [65.7, 70.4] | 2 | 1-16 |
| XiYan-SQL | 73.3 | [65.6, 70.2] | 3 | 1-18 |
| ExSL + granite-34b-code | 72.4 | [64.9, 69.6] | 4 | 1-22 |
| Reasoning-SQL-14B | 72.3 | [64.7, 69.4] | 5 | 1-22 |
| Insights AI | 72.2 | [64.6, 69.4] | 6 | 1-22 |
| TC-SQL | 70.9 | [63.7, 68.4] | 7 | 1-27 |
| Infly-RL-SQL-32B | 70.1 | [63.0, 67.8] | 8 | 1-29 |
| Queryosity | 69.4 | [62.5, 67.3] | 9 | 1-32 |
| OpenSearch-SQL-v2 + GPT-4o | 69.3 | [62.4, 67.2] | 10 | 1-32 |
| GenaSQL | 69.2 | [62.4, 67.2] | 11 | 1-33 |
| OmniSQL-32B | 69.2 | [62.4, 67.1] | 12 | 1-33 |
| OmniSQL-7B | 69.0 | [62.2, 67.0] | 13 | 1-33 |
| PB-SQL + GPT-4o | 68.6 | [61.9, 66.7] | 14 | 2-34 |
| PURPLE + RED + GPT-4o | 68.1 | [61.5, 66.3] | 15 | 2-34 |
| Arcwise + GPT-4o | 68.0 | [61.4, 66.2] | 16 | 2-34 |
| Distillery + GPT-4o | 67.2 | [60.8, 65.6] | 17 | 3-36 |
| RSL-SQL + GPT-4o | 67.2 | [60.8, 65.6] | 18 | 3-36 |
| XiYanSQL-QwenCoder-32B | 67.0 | [60.6, 65.5] | 19 | 4-36 |
| RECAP + Gemini | 67.0 | [60.6, 65.4] | 20 | 4-36 |
| GSR | 66.9 | [60.5, 65.4] | 21 | 4-36 |
| MSL-SQL + DeepSeek-V2.5 | 66.8 | [60.5, 65.3] | 22 | 4-36 |
| AskData + GPT-4o | 65.9 | [59.8, 64.6] | 23 | 7-37 |
| E-SQL + GPT-4o | 65.6 | [59.5, 64.4] | 24 | 7-37 |
| ByteBrain | 65.5 | [59.4, 64.3] | 25 | 7-37 |
| CHESS | 65.0 | [59.1, 63.9] | 26 | 7-37 |
| SCL-SQL | 64.7 | [58.9, 63.7] | 27 | 7-39 |
| EBA-SQL + GPT-4 | 64.6 | [58.8, 63.6] | 28 | 8-39 |
| OeSQL-0.1-Qe-32B | 64.6 | [58.8, 63.6] | 29 | 8-39 |
| RSL-SQL + DeepSeek-v2 | 63.6 | [58.0, 62.8] | 30 | 9-42 |
| Command-A | 63.5 | [57.9, 62.8] | 31 | 9-42 |
| MCS-SQL + GPT-4 | 63.4 | [57.8, 62.7] | 32 | 9-42 |
| PURPLE + GPT-4o | 63.0 | [57.5, 62.4] | 33 | 11-42 |
| GRA-SQL | 62.6 | [57.2, 62.1] | 34 | 14-44 |
| E-SQL + GPT-4o mini | 61.6 | [56.4, 61.4] | 35 | 17-46 |
| OpenSearch-SQL-v1 + GPT-4 | 61.3 | [56.2, 61.2] | 36 | 17-46 |
| Dubo-SQL-v1 | 59.7 | [55.0, 59.9] | 37 | 23-49 |
| SuperSQL | 58.5 | [54.0, 59.0] | 38 | 27-49 |
| SFT CodeS-15B | 58.5 | [54.0, 59.0] | 39 | 27-49 |
| Chat2Query(GPT-4 + 数据实体建模) | 58.1 | [53.8, 58.7] | 40 | 30-50 |
| MAC-SQL + GPT-4 | 57.6 | [53.3, 58.3] | 41 | 30-50 |
| SFT CodeS-7B | 57.2 | [53.0, 58.0] | 42 | 30-51 |
| TA-SQL + GPT-4 | 56.2 | [52.3, 57.2] | 43 | 34-51 |
| DeepSeek | 56.1 | [52.2, 57.2] | 44 | 34-51 |
| DTS-SQL + DeepSeek-7B | 55.8 | [52.0, 56.9] | 45 | 35-51 |
| SEE | 55.5 | [51.7, 56.7] | 46 | 35-51 |
| DAIL-SQL + GPT-4 | 54.8 | [51.2, 56.1] | 47 | 37-51 |
| Interactive-T2S | 54.6 | [51.0, 56.0] | 48 | 37-51 |
| Mistral | 53.5 | [50.2, 55.2] | 49 | 37-51 |
| ExSL + granite-20b-code | 51.7 | [48.8, 53.8] | 50 | 40-52 |
| DIN-SQL + GPT-4 | 50.7 | [48.0, 53.1] | 51 | 42-52 |
| GPT-4 | 46.4 | [44.7, 49.7] | 52 | 50-53 |
| Claude-2 | 42.7 | [41.9, 46.9] | 53 | 52-54 |
| Open-SQL | 37.7 | [38.1, 43.0] | 54 | 53-54 |
| Palm-2 | 27.4 | [30.3, 35.0] | 55 | 55-58 |
| ChatGPT + CoT | 25.9 | [29.2, 33.8] | 56 | 55-58 |
| Codex | 25.4 | [28.8, 33.5] | 57 | 55-58 |
| ChatGPT | 24.1 | [27.8, 32.4] | 58 | 55-58 |
| T5-3B | 10.4 | [17.6, 21.6] | 59 | 59-61 |
| T5-Large | 9.7 | [17.1, 21.1] | 60 | 59-61 |
| T5-Base | 6.3 | [14.6, 18.4] | 61 | 59-61 |

> 译注:该表按原文数据保留(个别行的置信区间下界高于上界、或与准确率估计明显不协调,系原文即如此);其要义在于展示——考虑真值 11.65% 的错误率后,原排名第 1 的方法其可能排名区间为 1-13 名,仅凭榜单名次做决策风险很大。

### 附录 G NeurIPS 论文自查清单(NeurIPS Paper Checklist)

> 译注:附录 G 为 NeurIPS 投稿要求的标准自查清单(claims、theory、abstract、experiments 等数十项模板问答),各问题均以 [Yes]/[No] 作答并给出指向正文相应章节的理由(如「摘要在 arXiv 2507.02825,代码与数据见 github.com/uiuc-kang-lab/agentic-benchmarks」「实验参数见附录 E」等),属投稿模板性内容,与本论文的技术贡献无关,故不逐条翻译,详见原文第 33-39 页。

## 要点速览

- **两大有效性条件**:任务有效性(任务可解 ⟺ Agent 具备目标能力)与结果有效性(评测通过 ⟺ 任务真正完成);Agent 基准因「复杂任务设置 + 非结构化结果」两大挑战而特别容易双双失守。
- **ABC 清单结构**:任务有效性 10 条(工具 T.1–3、环境 T.4–6、实现 T.7–10)+ 结果有效性约 18 条(按全串/子串/LLM 裁判、单元/模糊/端到端测试、状态匹配、答案匹配/质量度量分组)+ 报告 13 条(透明与效度、缺陷缓解、结果解读)。
- **审计结论**:十个流行基准(SWE-bench、SWE-Lancer、KernelBench、BIRD、Cybench、MLE-bench、GAIA、τ-bench、WebArena、OSWorld)中 7 个违反任务有效性、7 个违反结果有效性、10 个全部存在报告局限;80% 未承认自身弱点。
- **τ-bench 双重缺陷**:「什么都不做」的平凡 Agent 因「环境未变即成功」的定义在 38% 故意不可解任务上得分,反超 GPT-4o Agent;子串匹配 + 数据库原文作真值,使「穷举全部答案」可再高估 40%。
- **判分被绕过的三个实锤**:SWE-Lancer 的密码 ZIP 可免密列目录并覆写,换成 `assert 1==1` 即拿 100%;KernelBench 模糊测试不变张量形状与内存布局,高估约 31%;WebArena 子串匹配忽略无关内容 + LLM 裁判接受空回复,高估 1.4–5.2%。
- **环境漂移致低估**:OSWorld 的 chrome 部分 46 题中 13 题因网站改版破坏 HTML 选择器而失效,低估 UI-TARS 达 28%(绝对)——冻结环境(T.6)不只是防作弊,也防基准腐烂。
- **CVE-Bench 案例的修复收益**:修正时间盲注判据(「日志含 SLEEP」→「SLEEP 真被执行」)消除 32.5% 高估;封堵 docker 网络捷径使成功率下降 10%;合计使性能高估绝对下降 33%,证明 ABC 在基准开发期即可用。
- **报告标准同样关键**:私有留出测试集、持续更新计划、置信区间、解读指南、人类专家与平凡 Agent 基线(R.1–13);BIRD 示范显示,考虑真值 11.65% 错误率后,原排名第 1 的模型置信区间可滑至第 13 名。
- **工程启示**:造基准时先跑平凡 Agent(什么都不做、dump 数据库、穷举答案)与 Oracle 求解器做健全性检查;给 Agent 的工具要固定版本、隔离真值、冻结环境;判分器(尤其 LLM 裁判)必须先验证准确率与自洽性。
- **课程关联**:把 Press 的「三性质」具体化为可勾选的审计项,回应 tinyBenchmarks 想要高效评测的前提(先保证正确),也与 SWE-bench/SWE-smith 的单元测试验证链路直接呼应——执行验证并非天然严谨,测试本身也需要被验证。
